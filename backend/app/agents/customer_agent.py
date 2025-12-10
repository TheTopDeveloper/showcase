"""
Customer Support Agent
======================
Main agent implementation using OpenAI with function calling.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT
from app.tools.data_tools import TOOL_DEFINITIONS, TOOL_FUNCTIONS
from app.rag.vector_store import search_knowledge_base


@dataclass
class AgentResponse:
    """Response from the agent."""
    message: str
    sources_used: List[str] = field(default_factory=list)
    tools_called: List[str] = field(default_factory=list)
    token_usage: Dict[str, int] = field(default_factory=dict)


class CustomerSupportAgent:
    """Agentic customer support assistant with RAG and tool capabilities."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_prompt = SYSTEM_PROMPT
        self.tool_functions = {**TOOL_FUNCTIONS, "search_knowledge_base": search_knowledge_base}

    def _build_messages(self, user_message: str) -> List[Dict[str, Any]]:
        """Build the messages array for the API call."""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})
        return messages

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Execute a tool and return its result."""
        if tool_name not in self.tool_functions:
            return f"Error: Unknown tool '{tool_name}'"

        try:
            func = self.tool_functions[tool_name]
            result = func(**tool_args)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def chat(self, user_message: str) -> AgentResponse:
        """Process a user message and generate a response."""
        messages = self._build_messages(user_message)
        tools_called = []
        sources_used = []

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
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

                if tool_name == "search_knowledge_base":
                    sources_used.append("Knowledge Base (RAG)")
                elif tool_name in ["get_pricing_info", "compare_plans", "list_all_plans"]:
                    sources_used.append("Pricing Database")
                elif tool_name == "check_feature_availability":
                    sources_used.append("Features Database")
                elif tool_name == "get_support_resolution":
                    sources_used.append("Support Issues Database")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message

        final_response = assistant_message.content or "I apologize, but I couldn't generate a response."

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
            }
        )

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []

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
