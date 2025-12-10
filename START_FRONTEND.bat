@echo off
REM =============================================================================
REM Quick Start Frontend for Windows
REM Double-click this file to start the frontend server
REM =============================================================================

echo.
echo ========================================
echo   Customer Support Agent - Frontend
echo ========================================
echo.

cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies.
        echo Make sure Node.js 18+ is installed.
        pause
        exit /b 1
    )
)

echo.
echo Starting frontend server...
echo.
echo UI: http://localhost:3000
echo.
echo Press Ctrl+C to stop
echo.

call npm run dev

pause
