"""
Customer Support Agent API
==========================
FastAPI backend for the customer support chatbot.
"""

import uuid
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import API_HOST, API_PORT, CORS_ORIGINS, COMPANY_NAME
from app.agents.customer_agent import get_agent, clear_session
from app.rag.vector_store import get_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    print("🚀 Starting Customer Support Agent API...")
    print("📚 Initializing RAG vector store...")
    try:
        get_vector_store()
        print("✅ Vector store ready")
    except Exception as e:
        print(f"⚠️ Vector store initialization failed: {e}")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title=f"{COMPANY_NAME} Customer Support Agent",
    description="AI-powered customer support chatbot with RAG and tool capabilities",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources_used: list[str] = []
    tools_called: list[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    status: str
    company: str
    timestamp: datetime
    vector_store_ready: bool


class SessionResponse(BaseModel):
    session_id: str
    message: str


# Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    try:
        vs = get_vector_store()
        vs_ready = vs.vector_store is not None
    except:
        vs_ready = False

    return HealthResponse(
        status="healthy",
        company=COMPANY_NAME,
        timestamp=datetime.now(),
        vector_store_ready=vs_ready,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint."""
    try:
        vs = get_vector_store()
        vs_ready = vs.vector_store is not None
    except:
        vs_ready = False

    return HealthResponse(
        status="healthy",
        company=COMPANY_NAME,
        timestamp=datetime.now(),
        vector_store_ready=vs_ready,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint."""
    session_id = request.session_id or str(uuid.uuid4())

    try:
        agent = get_agent(session_id)
        result = agent.chat(request.message)

        return ChatResponse(
            response=result.message,
            session_id=session_id,
            sources_used=result.sources_used,
            tools_called=result.tools_called,
            timestamp=datetime.now(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/session/new", response_model=SessionResponse)
async def new_session():
    """Create a new conversation session."""
    session_id = str(uuid.uuid4())
    return SessionResponse(session_id=session_id, message="New session created")


@app.post("/session/{session_id}/clear", response_model=SessionResponse)
async def clear_conversation(session_id: str):
    """Clear conversation history for a session."""
    clear_session(session_id)
    return SessionResponse(session_id=session_id, message="Conversation cleared")


@app.get("/session/{session_id}/history")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    agent = get_agent(session_id)
    return {"session_id": session_id, "history": agent.get_conversation_history()}


@app.post("/admin/rebuild-index")
async def rebuild_index():
    """Force rebuild of the vector store index."""
    try:
        vs = get_vector_store()
        vs.initialize(force_rebuild=True)
        return {"status": "success", "message": "Vector store rebuilt"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/search-test")
async def search_test(query: str):
    """Test RAG search functionality."""
    try:
        vs = get_vector_store()
        results = vs.search_with_scores(query, k=3)
        return {
            "query": query,
            "results": [
                {
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source_file", "Unknown"),
                    "score": score
                }
                for doc, score in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=True)
