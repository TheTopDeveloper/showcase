# TechStore Pro Customer Support Chatbot

A modern AI-powered customer support chatbot for **TechStore Pro**, a company that sells computer products (monitors, printers, accessories). Built with FastAPI, Next.js, and OpenAI GPT-4o-mini, integrated with an MCP (Model Context Protocol) server for product and order management.

## 🌐 Live Deployment

**Frontend UI:** [https://support-agent-ui-eulx4rfnwq-uc.a.run.app/](https://support-agent-ui-eulx4rfnwq-uc.a.run.app/)

**Backend API:** [https://support-agent-api-eulx4rfnwq-uc.a.run.app](https://support-agent-api-eulx4rfnwq-uc.a.run.app)

**API Documentation:** [https://support-agent-api-eulx4rfnwq-uc.a.run.app/docs](https://support-agent-api-eulx4rfnwq-uc.a.run.app/docs)

## 🎯 Project Overview

This chatbot helps customers:
- **Find Products** - Search and browse monitors, printers, and computer accessories
- **Get Product Details** - View specifications, pricing, and availability
- **Manage Orders** - Check order status and place new orders
- **Get Recommendations** - Receive personalized product recommendations based on needs

### Key Features

- ✅ **MCP Server Integration** - Uses Model Context Protocol for tool access
- ✅ **Answer Evaluation & Regeneration** - Ensures high-quality responses
- ✅ **Question Coherence Checking** - Handles unclear or incoherent questions gracefully
- ✅ **Personalization** - Extracts and uses customer names for personalized interactions
- ✅ **Modern UI** - Clean, responsive chat interface with gradient design
- ✅ **Session Management** - Maintains conversation context across interactions

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Frontend  │──────│   Backend   │──────│  MCP Server │
│   Next.js   │      │   FastAPI   │      │  (External) │
│   React     │      │   Python    │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ▼
                      ┌─────────────┐
                      │   OpenAI    │
                      │ GPT-4o-mini│
                      └─────────────┘
```

### Components

1. **Frontend** (`frontend/`)
   - Next.js 14 with React and TypeScript
   - Tailwind CSS for styling
   - Real-time chat interface
   - Session persistence

2. **Backend** (`backend/`)
   - FastAPI REST API
   - OpenAI GPT-4o-mini integration
   - MCP client for tool access
   - Answer evaluation and regeneration
   - Session management

3. **MCP Server** (External)
   - Provides product and order tools
   - JSON-RPC 2.0 protocol over HTTP
   - URL: `https://vipfapwm3x.us-east-1.awsapprunner.com/mcp`

## 🛠️ Technologies & Tools

### Backend Stack
- **FastAPI** - Modern Python web framework with async support
- **OpenAI API** - GPT-4o-mini for cost-effective LLM responses
- **httpx** - HTTP client for MCP server communication
- **Python 3.11+** - Runtime environment

### Frontend Stack
- **Next.js 14** - React framework with server-side rendering
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React Markdown** - Markdown rendering for responses

### AI & Evaluation Tools

#### Answer Evaluation System
The chatbot includes a sophisticated evaluation system that ensures response quality:

- **Evaluation Criteria:**
  - Does the answer directly address the question?
  - Is it helpful and informative?
  - Is it polite and professional?
  - Does it avoid making up information?

- **Regeneration Process:**
  - Evaluates each answer using LLM-based evaluator
  - Regenerates up to 3 times if unsatisfactory
  - Includes feedback about why previous answer was unsatisfactory
  - Tracks regeneration count in response metadata

- **Implementation:**
  ```python
  def _evaluate_answer(self, answer: str, question: str, tools_used: List[str]) -> Tuple[bool, Optional[str]]:
      # Uses GPT-4o-mini to evaluate answer quality
      # Returns (satisfactory: bool, reason: Optional[str])
  ```

#### Question Processing Tools

1. **Coherence Checker**
   - Detects incoherent or gibberish questions
   - Returns polite clarification requests
   - Prevents processing of meaningless input

2. **Introduction Detector**
   - Identifies greetings and introductions
   - Provides warm welcome responses
   - Extracts customer names for personalization

3. **Answerability Checker**
   - Validates questions can be answered with available tools
   - Provides helpful guidance when questions are out of scope

### MCP Server Tools

The MCP server provides 8 tools for product and order management:

**Product Tools:**
- `list_products(category, is_active)` - List products with filters
- `get_product(sku)` - Get detailed product information by SKU
- `search_products(query)` - Search products by name or description

**Customer Tools:**
- `get_customer(customer_id)` - Get customer information by ID
- `verify_customer_pin(email, pin)` - Verify customer identity

**Order Tools:**
- `list_orders(customer_id, status)` - List orders with filters
- `get_order(order_id)` - Get detailed order information
- `create_order(customer_id, items)` - Create new order with items

## 📋 Implementation Plan

### Phase 1: Backend Foundation
1. Set up FastAPI project with virtual environment
2. Implement MCP client using JSON-RPC 2.0 protocol
3. Build agent system with dynamic tool loading
4. Convert MCP tools to OpenAI function calling format

### Phase 2: API Endpoints
1. Create chat endpoint with session management
2. Implement session creation and clearing
3. Add admin endpoints for MCP tool listing
4. Add health check with MCP status

### Phase 3: Frontend Development
1. Set up Next.js project with TypeScript
2. Build chat UI with message display
3. Implement session persistence
4. Add loading states and error handling

### Phase 4: Agent Enhancements
1. **Answer Evaluation System**
   - Implement LLM-based answer evaluator
   - Add regeneration loop with feedback
   - Track regeneration count

2. **Question Processing**
   - Add coherence checking
   - Implement introduction detection
   - Handle unanswerable questions gracefully

3. **Personalization**
   - Extract customer names from messages
   - Store names for session personalization
   - Use names naturally in responses

### Phase 5: Integration & Testing
1. Connect frontend to backend
2. Test MCP integration end-to-end
3. Verify answer evaluation and regeneration
4. Test personalization features

### Phase 6: Deployment
1. Configure environment variables
2. Build Docker images
3. Deploy to GCP Cloud Run
4. Verify deployment and connectivity

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- OpenAI API key
- GCP account (for deployment)

### Local Development

**Backend:**
```powershell
# Windows PowerShell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY = "sk-your-key-here"
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access URLs:**
- Frontend UI: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## 🌐 Deployment to GCP Cloud Run

### Prerequisites
- GCP project with billing enabled
- `gcloud` CLI installed and authenticated
- Required APIs enabled (script handles this)

### Deployment Steps

**Windows (PowerShell):**
```powershell
# Set required environment variable
$env:OPENAI_API_KEY = "sk-your-key-here"

# Optional: Override MCP server URL (has default)
$env:MCP_SERVER_URL = "https://vipfapwm3x.us-east-1.awsapprunner.com"

# Deploy
cd deployment\gcp
.\deploy-gcp.ps1 -ProjectId "your-gcp-project-id"
```

**Linux/Mac (Bash):**
```bash
# Set required environment variable
export OPENAI_API_KEY="sk-your-key-here"

# Optional: Override MCP server URL (has default)
export MCP_SERVER_URL="https://vipfapwm3x.us-east-1.awsapprunner.com"

# Deploy
cd deployment/gcp
./deploy-gcp.sh your-gcp-project-id
```

### What Gets Deployed

**Backend Service:**
- FastAPI application
- MCP client integration
- Answer evaluation system
- Environment variables:
  - `OPENAI_API_KEY` (required)
  - `OPENAI_MODEL=gpt-4o-mini`
  - `MCP_SERVER_URL` (default or custom)
  - `CORS_ORIGINS` (auto-configured)

**Frontend Service:**
- Next.js application
- Pre-built with backend URL
- Environment variables:
  - `NEXT_PUBLIC_API_URL` (set during build)
  - `PORT=8080`

### Deployment Script Features

The deployment scripts automatically:
1. ✅ Set GCP project and enable required APIs
2. ✅ Build Docker images for backend and frontend
3. ✅ Deploy to Cloud Run with correct ports (8080)
4. ✅ Configure CORS to allow frontend-backend communication
5. ✅ Set all required environment variables
6. ✅ Provide deployment URLs and troubleshooting tips

### Deployment URLs

After successful deployment, the scripts will display:

- **Backend API URL**: `https://support-agent-api-{hash}-{region}.a.run.app`
- **Frontend UI URL**: `https://support-agent-ui-{hash}-{region}.a.run.app`

Where:
- `{hash}` is a unique identifier generated by Cloud Run
- `{region}` is your deployment region (e.g., `uc` for us-central1)

**Current Deployment URLs:**
- **Backend API**: [https://support-agent-api-eulx4rfnwq-uc.a.run.app](https://support-agent-api-eulx4rfnwq-uc.a.run.app)
- **Frontend UI**: [https://support-agent-ui-eulx4rfnwq-uc.a.run.app](https://support-agent-ui-eulx4rfnwq-uc.a.run.app)
- **API Documentation**: [https://support-agent-api-eulx4rfnwq-uc.a.run.app/docs](https://support-agent-api-eulx4rfnwq-uc.a.run.app/docs)

The frontend is automatically configured to connect to the backend URL during build.

### Post-Deployment Verification

**Using the deployed URLs:**

```bash
# Check backend health
curl https://support-agent-api-eulx4rfnwq-uc.a.run.app/health

# Check MCP tools
curl https://support-agent-api-eulx4rfnwq-uc.a.run.app/admin/mcp-tools

# Test chat
curl -X POST https://support-agent-api-eulx4rfnwq-uc.a.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What monitors do you have?"}'
```

## 🔧 Configuration

### Environment Variables

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional:**
- `OPENAI_MODEL` - Default: `gpt-4o-mini`
- `MCP_SERVER_URL` - Default: `https://vipfapwm3x.us-east-1.awsapprunner.com`
- `CORS_ORIGINS` - Auto-configured during deployment
- `PORT` - Set by Cloud Run (8080) or defaults to 8000

### MCP Server Configuration

The MCP server URL is configured in `backend/app/config.py`:
```python
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://vipfapwm3x.us-east-1.awsapprunner.com")
```

Override via environment variable if needed.

## 📊 Answer Evaluation System

### How It Works

1. **Generate Answer** - LLM generates initial response using MCP tools
2. **Evaluate Quality** - Separate LLM call evaluates the answer
3. **Check Criteria:**
   - Directly addresses the question
   - Helpful and informative
   - Polite and professional
   - Avoids making up information
4. **Regenerate if Needed** - Up to 3 regeneration attempts with feedback
5. **Return Best Answer** - Includes regeneration count in metadata

### Evaluation Metrics

- **Satisfactory Rate** - Percentage of answers passing evaluation on first try
- **Regeneration Count** - Tracked per response for monitoring
- **Token Usage** - Monitored for cost optimization

### Benefits

- ✅ Ensures high-quality responses
- ✅ Reduces hallucinations
- ✅ Improves customer satisfaction
- ✅ Provides transparency (regeneration count)

## 🧪 Testing

### Test MCP Connection
```bash
curl http://localhost:8000/admin/mcp-tools
```

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I am a small company of 3 employees, which printer would you suggest?"}'
```

### Test Answer Evaluation
Send a question and check the `regenerations` field in the response to see if evaluation triggered regeneration.

## 📁 Project Structure

```
showcase/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── customer_agent.py      # Main agent with evaluation
│   │   ├── mcp_client.py              # MCP server client
│   │   └── config.py                  # Configuration
│   ├── main.py                        # FastAPI application
│   ├── requirements.txt               # Python dependencies
│   └── Dockerfile                     # Docker configuration
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx            # Root layout
│   │   │   └── page.tsx              # Main page
│   │   ├── components/
│   │   │   └── ChatBot.tsx           # Chat interface
│   │   └── lib/
│   │       └── api.ts                # API client
│   ├── package.json                  # Node dependencies
│   └── Dockerfile                    # Docker configuration
└── deployment/
    └── gcp/
        ├── deploy-gcp.ps1            # PowerShell deployment script
        └── deploy-gcp.sh             # Bash deployment script
```

## 🎨 UI Features

- **Contained Layout** - Centered card design (not full-page)
- **Reduced Font Sizes** - Compact, readable text
- **Colorful Design** - Gradient headers and accents (blue → indigo → purple)
- **Responsive** - Works on mobile, tablet, and desktop
- **Modern UX** - Smooth animations and transitions

## 🔍 Key Design Decisions

### Why MCP Server?
- **Separation of Concerns** - Product/order data managed separately
- **Scalability** - Update tools without redeploying chatbot
- **Standard Protocol** - MCP provides consistent interface
- **Flexibility** - Easy to swap or add new tools

### Why GPT-4o-mini?
- **Cost-Effective** - Cheaper than GPT-4 while maintaining quality
- **Fast Responses** - Lower latency for better UX
- **Sufficient Capability** - Handles customer support queries well

### Why Answer Evaluation?
- **Quality Assurance** - Ensures responses meet standards
- **Reduces Errors** - Catches and fixes unsatisfactory answers
- **Transparency** - Tracks regeneration attempts
- **Continuous Improvement** - Feedback loop for better responses

### Why FastAPI + Next.js?
- **FastAPI** - Fast, modern Python framework with async support
- **Next.js** - React framework with excellent DX and performance
- **Type Safety** - TypeScript provides compile-time error checking
- **Modern Stack** - Industry-standard technologies

## 📝 API Endpoints

### Base URLs

**Local Development:**
- Backend API: `http://localhost:8000`
- Frontend UI: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

**Production (GCP Cloud Run):**
- Backend API: [https://support-agent-api-eulx4rfnwq-uc.a.run.app](https://support-agent-api-eulx4rfnwq-uc.a.run.app)
- Frontend UI: [https://support-agent-ui-eulx4rfnwq-uc.a.run.app](https://support-agent-ui-eulx4rfnwq-uc.a.run.app)
- API Docs: [https://support-agent-api-eulx4rfnwq-uc.a.run.app/docs](https://support-agent-api-eulx4rfnwq-uc.a.run.app/docs)

### Chat
- `POST /chat` - Main conversation endpoint
  - URL: `{BACKEND_URL}/chat`
  - Request: `{ "message": "string", "session_id": "string" (optional) }`
  - Response: `{ "response": "string", "session_id": "string", "sources_used": [], "tools_called": [], "regenerations": int }`

### Sessions
- `POST /session/new` - Create new session
  - URL: `{BACKEND_URL}/session/new`
- `POST /session/{id}/clear` - Clear conversation
  - URL: `{BACKEND_URL}/session/{id}/clear`
- `GET /session/{id}/history` - Get conversation history
  - URL: `{BACKEND_URL}/session/{id}/history`

### Admin
- `GET /admin/mcp-tools` - List available MCP tools
  - URL: `{BACKEND_URL}/admin/mcp-tools`
- `GET /health` - Health check with MCP status
  - URL: `{BACKEND_URL}/health`
- `GET /docs` - Interactive API documentation (Swagger UI)
  - URL: `{BACKEND_URL}/docs`

## 🐛 Troubleshooting

### Backend Can't Connect to MCP Server
- Check `MCP_SERVER_URL` is set correctly
- Verify MCP server is accessible
- Check Cloud Run logs: `gcloud run services logs read support-agent-api --region us-central1`

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS configuration in backend
- Check browser console for errors

### Answer Quality Issues
- Check regeneration count in response
- Review evaluation criteria
- Adjust `max_regenerations` if needed

## 📚 Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)

## 📄 License

This project is part of an AI bootcamp assessment showcase.

---

**Built with ❤️ for TechStore Pro Customer Support**
