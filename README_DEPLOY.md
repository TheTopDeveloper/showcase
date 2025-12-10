# Customer Support Agent - Assessment Scaffold

A production-ready customer support chatbot with RAG (Retrieval-Augmented Generation) and tool-based lookups, built for rapid deployment.

## 📁 Project Structure

```
showcase-prep/
├── backend/                    # FastAPI + RAG + Agent
│   ├── app/
│   │   ├── agents/            # Agent implementation
│   │   ├── tools/             # Tool functions for CSV lookups
│   │   └── rag/               # ChromaDB RAG implementation
│   ├── main.py                # FastAPI endpoints
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Next.js Chatbot UI
│   ├── src/
│   │   ├── app/               # Next.js app router
│   │   ├── components/        # React components
│   │   └── lib/               # API client
│   ├── package.json
│   └── Dockerfile
├── data/                       # Company data (SWAP THESE)
│   ├── company_overview.md    # Unstructured → RAG
│   ├── faqs.md                # Unstructured → RAG
│   ├── policies.md            # Unstructured → RAG
│   ├── pricing.csv            # Structured → Tools
│   ├── features.csv           # Structured → Tools
│   └── support_issues.csv     # Structured → Tools
├── deployment/
│   ├── gcp/                   # GCP Cloud Run scripts
│   └── github-actions/        # CI/CD workflows
├── docs/                       # Documentation
│   └── WINDOWS_SETUP.md       # Windows 11 guide
├── docker-compose.yml          # Local development
├── START_BACKEND.bat           # Windows quick start
├── START_FRONTEND.bat          # Windows quick start
└── README.md                   # This file
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                         │
│                  (Chat Interface)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────────────────────┐
│                   FastAPI Backend                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Customer Support Agent                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │    RAG      │  │   Tools     │  │   OpenAI    │  │   │
│  │  │  (ChromaDB) │  │ (CSV/JSON)  │  │   GPT-4o    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

> **🪟 Windows Users**: See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for detailed instructions, or use the batch files below.

### Option 1: Windows Batch Files (Easiest)

1. Double-click `START_BACKEND.bat`
2. Edit `.env` when prompted, add your OpenAI key
3. Double-click `START_FRONTEND.bat` (new terminal)
4. Open http://localhost:3000

### Option 2: Manual Setup

**Backend (Terminal 1):**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows
# source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
$env:OPENAI_API_KEY = "sk-your-key"   # Windows
# export OPENAI_API_KEY="sk-your-key" # Linux/Mac
python main.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm install
npm run dev
```

### Option 3: Docker

```powershell
# Create .env file with your API key
echo "OPENAI_API_KEY=sk-your-key" > .env

# Run with Docker Compose
docker-compose up --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📁 HOW TO SWAP IN ACTUAL COMPANY DATA

When you receive the actual company data at assessment time:

### Step 1: Replace Data Files

```powershell
cd data

# Delete synthetic files
Remove-Item company_overview.md, faqs.md, policies.md, pricing.csv, features.csv, support_issues.csv

# Copy actual files (example)
Copy-Item C:\path\to\actual\*.md .
Copy-Item C:\path\to\actual\*.csv .
```

### Step 2: Update Configuration

Edit `backend/app/config.py`:

```python
# Line ~25: Update company name
COMPANY_NAME = "ActualCompanyName"

# Line ~30: Update document list
UNSTRUCTURED_DOCS = [
    DATA_DIR / "actual_company_info.md",
    DATA_DIR / "actual_faqs.pdf",      # PDF supported!
    DATA_DIR / "actual_policies.md",
]

# Line ~40: Update structured data
STRUCTURED_DATA = {
    "pricing": DATA_DIR / "actual_pricing.csv",
    "products": DATA_DIR / "actual_products.csv",  # Add new if needed
}
```

### Step 3: Update Frontend Branding

Edit `frontend/src/components/ChatBot.tsx`:

```typescript
// Line ~10
const COMPANY_NAME = 'ActualCompanyName';
```

### Step 4: Restart Backend

The vector store auto-rebuilds when files change. Or force rebuild:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/admin/rebuild-index" -Method Post
```

---

## 🚢 Deployment to GCP

### Using PowerShell (Windows)

```powershell
cd deployment\gcp
.\deploy-gcp.ps1 -ProjectId "your-gcp-project-id"
```

### Using Bash (Linux/Mac)

```bash
cd deployment/gcp
chmod +x deploy-gcp.sh
./deploy-gcp.sh your-gcp-project-id
```

### GitHub Actions (Automatic)

1. Copy `.github/workflows/deploy.yml` from `deployment/github-actions/`
2. Add GitHub Secrets:
   - `GCP_PROJECT_ID`
   - `GCP_SA_KEY` (Service Account JSON)
   - `OPENAI_API_KEY`
3. Push to `main` branch

---

## 🧪 Testing Checklist

Before deployment:
- [ ] Backend starts: `python main.py`
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] Chat works: Test in frontend or API docs
- [ ] Pricing tool works: "What plans do you offer?"
- [ ] RAG search works: "What is your refund policy?"

---

## 🔧 Key Files to Modify

| File | Purpose | When to Modify |
|------|---------|----------------|
| `data/*` | Company data | Replace with actual data |
| `backend/app/config.py` | Configuration | Update paths, company name |
| `backend/app/tools/data_tools.py` | Tool functions | If CSV columns differ |
| `frontend/src/components/ChatBot.tsx` | UI branding | Update company name |

---

## 🆘 Troubleshooting

See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for common issues.

**Quick fixes:**
```powershell
# Port in use
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Reset vector store
Remove-Item -Recurse backend\chroma_db

# Rebuild Docker
docker-compose down
docker-compose build --no-cache
docker-compose up
```
