# Windows 11 Setup Guide

## Prerequisites

### 1. Install Python 3.11+
```powershell
winget install Python.Python.3.11
```
**IMPORTANT**: Check "Add Python to PATH" during installation.

### 2. Install Node.js 18+
```powershell
winget install OpenJS.NodeJS.LTS
```

### 3. Install Docker Desktop (Optional)
```powershell
winget install Docker.DockerDesktop
```

### 4. Install Google Cloud CLI
```powershell
winget install Google.CloudSDK
```
Then run: `gcloud init` and `gcloud auth login`

---

## Quick Start

### Option A: Double-Click Batch Files (Easiest)

1. Double-click `START_BACKEND.bat`
2. Edit `.env` when prompted, add your OpenAI key
3. Double-click `START_FRONTEND.bat` (new terminal)
4. Open http://localhost:3000

### Option B: PowerShell

**Terminal 1 - Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY = "sk-your-key"
python main.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

### Option C: Docker
```powershell
echo "OPENAI_API_KEY=sk-your-key" > .env
docker-compose up --build
```

---

## Deploying to GCP

```powershell
$env:OPENAI_API_KEY = "sk-your-key"
cd deployment\gcp
.\deploy-gcp.ps1 -ProjectId "your-project-id"
```

---

## Common Issues

### "python is not recognized"
Reinstall Python with "Add to PATH" checked.

### "cannot run scripts is disabled"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port already in use
```powershell
netstat -ano | findstr :8000
taskkill /PID <number> /F
```

### Reset vector store
```powershell
Remove-Item -Recurse backend\chroma_db
```

---

## VS Code Setup

Install extensions:
- Python
- ES7+ React snippets
- Tailwind CSS IntelliSense

Add to `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/Scripts/python.exe",
    "files.eol": "\n"
}
```
