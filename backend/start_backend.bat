@echo off
REM Backend Startup Script for Windows
REM This script starts the FastAPI backend server

echo ========================================
echo Starting AgentFlow Backend Server
echo ========================================
echo.

REM Check if we're in the backend directory
if not exist "app\main.py" (
    echo Error: This script must be run from the backend directory
    echo Current directory: %CD%
    echo.
    echo Please navigate to the backend directory first:
    echo   cd backend
    echo   start_backend.bat
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo.
    echo Virtual environment created. Please run this script again.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo.
echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Dependencies not installed. Installing...
    pip install -r requirements.txt
    echo.
    echo Dependencies installed. Starting server...
    echo.
)

REM Start the server
echo.
echo ========================================
echo Starting FastAPI server on http://localhost:8000
echo ========================================
echo.
echo Press CTRL+C to stop the server
echo.
echo You can test the backend at:
echo   - Health Check: http://localhost:8000/health
echo   - API Docs: http://localhost:8000/api/v1/docs
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

