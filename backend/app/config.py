"""
Configuration for Customer Support Agent
========================================
UPDATE THIS FILE when swapping in actual company data.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# DATA CONFIGURATION - UPDATE THIS SECTION TO SWAP DATA
# =============================================================================

# Base directories (Windows/Linux compatible)
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
PROJECT_ROOT = BASE_DIR.parent  # showcase-prep/
DATA_DIR = PROJECT_ROOT / "data"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Unstructured documents for RAG (markdown, txt, pdf)
# UPDATE THESE PATHS when you receive actual data
UNSTRUCTURED_DOCS = [
    DATA_DIR / "company_overview.md",
    DATA_DIR / "faqs.md",
    DATA_DIR / "policies.md",
    # Add more documents here:
    # DATA_DIR / "actual_guide.pdf",
]

# Structured data files (CSV) for tool-based lookups
# UPDATE THESE PATHS when you receive actual data
STRUCTURED_DATA = {
    "pricing": DATA_DIR / "pricing.csv",
    "features": DATA_DIR / "features.csv",
    "support_issues": DATA_DIR / "support_issues.csv",
    # Add more structured data:
    # "products": DATA_DIR / "products.csv",
}

# =============================================================================
# COMPANY CONFIGURATION - UPDATE FOR ACTUAL COMPANY
# =============================================================================

COMPANY_NAME = "NimbusFlow"  # <-- CHANGE THIS

SYSTEM_PROMPT = f"""You are a helpful, friendly customer support agent for {COMPANY_NAME}.

Your role is to:
1. Answer customer questions accurately using the company knowledge base
2. Look up specific pricing, features, and product information when needed
3. Be empathetic and professional in all interactions
4. Admit when you don't know something rather than making up information
5. Suggest contacting human support for complex issues you cannot resolve

Guidelines:
- Keep responses concise but complete
- Use bullet points for lists of features or steps
- Always be polite and helpful
- If a question is outside your knowledge, say so clearly
- For billing or account-specific issues, direct to support@{COMPANY_NAME.lower()}.io

Remember: You have access to tools to look up pricing and feature information. Use them when customers ask about specific plans, prices, or feature availability.
"""

# =============================================================================
# LLM CONFIGURATION
# =============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# =============================================================================
# RAG CONFIGURATION
# =============================================================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"

# =============================================================================
# API CONFIGURATION
# =============================================================================

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

# =============================================================================
# OBSERVABILITY (Optional)
# =============================================================================

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "customer-support-agent")
