@echo off
REM Start Backend Server Script for Windows
REM This script starts the backend server

echo ========================================
echo Starting AgentFlow - Backend
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

echo Starting backend server...
echo.
echo Backend will run on: http://localhost:8000
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

REM Start backend
cd backend
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python -m uvicorn app.main:app --reload
) else (
    echo Virtual environment not found. Creating...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    python -m uvicorn app.main:app --reload
)
cd ..

