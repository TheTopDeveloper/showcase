"""
Customer Support Agent
======================
Main agent implementation using OpenAI with MCP server tools.
Includes answer evaluation, regeneration, clarification, and personalization.
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT, COMPANY_NAME
from app.mcp_client import get_mcp_client


@dataclass
class AgentResponse:
    """Response from the agent."""
    message: str
    sources_used: List[str] = field(default_factory=list)
    tools_called: List[str] = field(default_factory=list)
    token_usage: Dict[str, int] = field(default_factory=dict)
    regenerations: int = 0


class CustomerSupportAgent:
    """Agentic customer support assistant using MCP server tools."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_prompt = SYSTEM_PROMPT
        self.mcp_client = get_mcp_client()
        self._tool_definitions = None
        self.customer_name: Optional[str] = None
        self.max_regenerations = 3
    
    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions from MCP server and convert to OpenAI format."""
        if self._tool_definitions is not None:
            return self._tool_definitions
        
        mcp_tools = self.mcp_client.list_tools()
        openai_tools = []
        
        for tool in mcp_tools:
            # Convert MCP tool to OpenAI function format
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", f"Call {tool['name']} tool"),
                    "parameters": tool.get("inputSchema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
            }
            openai_tools.append(openai_tool)
        
        self._tool_definitions = openai_tools
        return openai_tools
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract a name from user input using LLM."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract the person's name from the text. Return only the name, or 'none' if no name is found."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=20
            )
            name = response.choices[0].message.content.strip().lower()
            if name and name != "none" and len(name) > 1 and len(name) < 50:
                # Capitalize first letter of each word
                return " ".join(word.capitalize() for word in name.split())
            return None
        except:
            return None
    
    def _check_question_coherence(self, question: str) -> Tuple[bool, Optional[str]]:
        """Check if question is coherent and can be understood."""
        try:
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are evaluating if a customer question is coherent and understandable.

A question is INCOHERENT if:
- It's just random characters or gibberish (e.g., "asdfghjkl")
- It makes no grammatical sense
- It's completely unclear what the customer is asking

A question is COHERENT if:
- It's a real question, even if vague
- It asks for product recommendations, information, or help
- It's understandable, even if you need to ask follow-up questions

Return JSON: {"coherent": true/false, "clarification": "what to ask if incoherent"}
Only mark as incoherent if it's truly gibberish or completely unclear."""},
                    {"role": "user", "content": question}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            coherent = result.get("coherent", True)
            clarification = result.get("clarification")
            
            if not coherent:
                return False, clarification or "Could you please rephrase your question? I want to make sure I understand what you're looking for."
            return True, None
        except Exception as e:
            # If evaluation fails, assume coherent and proceed
            return True, None
    
    def _evaluate_answer(self, answer: str, question: str, tools_used: List[str]) -> Tuple[bool, Optional[str]]:
        """Evaluate if the answer is satisfactory."""
        try:
            # Skip evaluation for greeting responses (they're handled separately)
            if self._is_introduction_or_greeting(question):
                return True, None
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """Evaluate if the answer is satisfactory. Check:
1. Does it directly address the question?
2. Is it helpful and informative?
3. Is it polite and professional?
4. Does it avoid making up information?

IMPORTANT: If the question was just a greeting/introduction, the answer should be a warm welcome - that's satisfactory.

Return JSON: {"satisfactory": true/false, "reason": "why not satisfactory if false"}
If satisfactory=false, provide a brief reason."""},
                    {"role": "user", "content": f"Question: {question}\n\nAnswer: {answer}\n\nTools used: {', '.join(tools_used) if tools_used else 'none'}"}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            satisfactory = result.get("satisfactory", True)
            reason = result.get("reason")
            
            return satisfactory, reason
        except Exception as e:
            # If evaluation fails, assume satisfactory
            return True, None
    
    def _build_messages(self, user_message: str) -> List[Dict[str, Any]]:
        """Build the messages array for the API call."""
        # Enhance system prompt with customer name if available
        system_prompt = self.system_prompt
        if self.customer_name:
            system_prompt += f"\n\nIMPORTANT: The customer's name is {self.customer_name}. Use their name naturally in your responses to personalize the conversation."
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages
    
    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Execute a tool via MCP server."""
        try:
            result = self.mcp_client.call_tool(tool_name, tool_args)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    
    def _generate_response(self, messages: List[Dict[str, Any]], tool_definitions: List[Dict[str, Any]]) -> Tuple[str, List[str], List[str], Any]:
        """Generate a response using the LLM."""
        tools_called = []
        sources_used = []
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tool_definitions,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        while assistant_message.tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                tools_called.append(tool_name)
                tool_result = self._execute_tool(tool_name, tool_args)

                # Track sources based on tool type
                if tool_name in ["list_products", "get_product", "search_products"]:
                    sources_used.append("Product Catalog")
                elif tool_name in ["list_orders", "get_order", "create_order"]:
                    sources_used.append("Order System")
                elif tool_name in ["get_customer", "verify_customer_pin"]:
                    sources_used.append("Customer Database")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_definitions,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message

        final_response = assistant_message.content or "I apologize, but I couldn't generate a response."
        
        return final_response, tools_called, sources_used, response
    
    def _handle_unanswerable_question(self, question: str) -> str:
        """Generate a polite response for questions that can't be answered with available tools."""
        return f"""I apologize, but I'm not able to answer that question with the tools I have available. 

I can help you with:
• Finding products (monitors, printers, computer accessories)
• Getting product details, pricing, and availability
• Checking order status
• Placing new orders

For other questions or complex issues, please contact our support team at support@{COMPANY_NAME.lower().replace(' ', '')}.com, and they'll be happy to assist you!"""
    
    def _is_introduction_or_greeting(self, message: str) -> bool:
        """Check if message is just an introduction or greeting without a question."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """Determine if this message is:
1. Just a greeting or introduction (e.g., "Hi", "Hello", "I'm John", "Hi there, I am Joshua")
2. A greeting/introduction WITH a question or request (e.g., "Hi, I need a printer")

Return JSON: {"is_intro_only": true/false}
Only return true if it's ONLY a greeting/introduction with no question or request."""},
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("is_intro_only", False)
        except:
            # If check fails, use simple heuristics
            message_lower = message.lower().strip()
            # Check if it's just a greeting pattern
            greeting_patterns = ["hi there", "hello", "hey", "hi, i am", "i am", "i'm", "my name is"]
            has_greeting = any(pattern in message_lower for pattern in greeting_patterns)
            has_question_words = any(word in message_lower for word in ["?", "what", "which", "how", "can you", "need", "want", "looking for"])
            return has_greeting and not has_question_words and len(message.split()) < 15
    
    def chat(self, user_message: str) -> AgentResponse:
        """Process a user message and generate a response."""
        # Extract and store customer name
        extracted_name = self._extract_name(user_message)
        is_first_interaction = not self.customer_name and extracted_name
        if extracted_name and not self.customer_name:
            self.customer_name = extracted_name
        
        # Check if this is just an introduction/greeting
        if self._is_introduction_or_greeting(user_message):
            if self.customer_name:
                greeting_response = f"Hello {self.customer_name}! Welcome to {COMPANY_NAME} support. I'm here to help you find the right products, check orders, and answer any questions you might have. How can I assist you today?"
            else:
                greeting_response = f"Hello! Welcome to {COMPANY_NAME} support. I'm here to help you find the right products, check orders, and answer any questions you might have. How can I assist you today?"
            
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": greeting_response})
            
            return AgentResponse(
                message=greeting_response,
                sources_used=[],
                tools_called=[],
                token_usage={},
                regenerations=0
            )
        
        # Check question coherence
        is_coherent, clarification = self._check_question_coherence(user_message)
        if not is_coherent:
            clarification_response = clarification or "Could you please rephrase your question? I want to make sure I understand what you're looking for."
            if self.customer_name:
                clarification_response = f"{self.customer_name}, {clarification_response.lower()}"
            
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": clarification_response})
            
            return AgentResponse(
                message=clarification_response,
                sources_used=[],
                tools_called=[],
                token_usage={},
                regenerations=0
            )
        
        # Get tool definitions for response generation
        tool_definitions = self._get_tool_definitions()
        
        # Note: We removed the strict pre-check for answerability because:
        # 1. Recommendation questions (e.g., "which printer should I get") CAN be answered
        #    by using list_products/search_products and then making recommendations
        # 2. The LLM with tools will naturally handle unanswerable questions
        # 3. The evaluation step will catch truly unsatisfactory answers
        
        # Generate initial response
        messages = self._build_messages(user_message)
        final_response, tools_called, sources_used, response = self._generate_response(messages, tool_definitions)
        
        # Evaluate and regenerate if needed
        regenerations = 0
        for attempt in range(self.max_regenerations):
            satisfactory, reason = self._evaluate_answer(final_response, user_message, tools_called)
            if satisfactory:
                break
            
            regenerations += 1
            # Regenerate with feedback
            messages.append({
                "role": "assistant",
                "content": final_response
            })
            messages.append({
                "role": "user",
                "content": f"The previous answer was not satisfactory: {reason}. Please provide a better answer."
            })
            
            final_response, tools_called, sources_used, response = self._generate_response(messages, tool_definitions)
        
        # Personalize response if customer name is available
        if self.customer_name:
            # Check if name is already mentioned in the response (avoid duplication)
            name_already_mentioned = self.customer_name.lower() in final_response.lower()
            
            # If this is first interaction, add welcome only if name not already mentioned
            if is_first_interaction and not name_already_mentioned:
                if not final_response.lower().startswith(("hi", "hello", "hey")):
                    final_response = f"Hello {self.customer_name}! {final_response}"
                else:
                    # Replace generic greeting with personalized one
                    words = final_response.split()
                    if words[0].lower() in ["hi", "hello", "hey"]:
                        final_response = f"Hello {self.customer_name}! " + " ".join(words[1:])
            # Otherwise, ensure name is used naturally if not already present
            elif not is_first_interaction and not name_already_mentioned:
                # Add name naturally at the beginning if response doesn't start with it
                if not final_response.startswith(self.customer_name):
                    final_response = f"{self.customer_name}, {final_response.lower()}"
        
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": final_response})

        if len(self.conversation_history) > 40:
            self.conversation_history = self.conversation_history[-40:]

        return AgentResponse(
            message=final_response,
            sources_used=list(set(sources_used)),
            tools_called=tools_called,
            token_usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            regenerations=regenerations
        )

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.customer_name = None

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()


_agent_sessions: Dict[str, CustomerSupportAgent] = {}


def get_agent(session_id: str) -> CustomerSupportAgent:
    """Get or create an agent for a session."""
    if session_id not in _agent_sessions:
        _agent_sessions[session_id] = CustomerSupportAgent()
    return _agent_sessions[session_id]


def clear_session(session_id: str):
    """Clear a session's agent."""
    if session_id in _agent_sessions:
        del _agent_sessions[session_id]
