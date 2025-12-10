@echo off
REM =============================================================================
REM Quick Start Backend for Windows
REM Double-click this file to start the backend server
REM =============================================================================

echo.
echo ========================================
echo   Customer Support Agent - Backend
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Make sure Python 3.11+ is installed and in PATH.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt -q

REM Check for .env file
if not exist ".env" (
    echo.
    echo No .env file found. Creating from template...
    copy .env.example .env >nul 2>&1
    if not exist ".env" (
        echo OPENAI_API_KEY=your-key-here> .env
    )
    echo.
    echo IMPORTANT: Edit backend\.env and add your OPENAI_API_KEY
    echo.
    notepad .env
    echo.
    echo Press any key after saving your API key...
    pause >nul
)

REM Load environment variables from .env
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if not "%%a"=="" if not "%%b"=="" set "%%a=%%b"
)

echo.
echo Starting backend server...
echo.
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
