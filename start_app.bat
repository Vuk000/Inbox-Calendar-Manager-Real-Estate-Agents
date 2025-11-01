@echo off
REM Start Both Servers Script for Windows
REM This script starts both the backend and frontend servers

echo ========================================
echo Starting AgentFlow - Backend + Frontend
echo ========================================
echo.

REM Check if we're in the project root
if not exist "backend\app\main.py" (
    echo Error: This script must be run from the project root directory
    echo Current directory: %CD%
    echo.
    echo Please navigate to the project root first
    pause
    exit /b 1
)

REM Check if backend virtual environment exists
if not exist "backend\venv\Scripts\activate.bat" (
    echo Backend virtual environment not found!
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    echo.
    echo Installing backend dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
    echo.
)

REM Check if frontend node_modules exists
if not exist "frontend_nextjs\node_modules" (
    echo Frontend dependencies not found!
    echo Installing frontend dependencies...
    cd frontend_nextjs
    call npm install
    cd ..
    echo.
)

echo Starting both servers...
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
echo Press CTRL+C to stop both servers
echo ========================================
echo.

REM Start backend in a new window
start "AgentFlow Backend" cmd /k "cd /d %~dp0backend && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload) else (python -m venv venv && call venv\Scripts\activate.bat && pip install -r requirements.txt && python -m uvicorn app.main:app --reload)"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in current window
cd frontend_nextjs
echo.
echo Frontend starting on http://localhost:3000
echo Backend is running in a separate window
echo.
call npm run dev

