#!/bin/bash
# Backend Startup Script for Mac/Linux
# This script starts the FastAPI backend server

echo "========================================"
echo "Starting AgentFlow Backend Server"
echo "========================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "app/main.py" ]; then
    echo "Error: This script must be run from the backend directory"
    echo "Current directory: $(pwd)"
    echo ""
    echo "Please navigate to the backend directory first:"
    echo "  cd backend"
    echo "  ./start_backend.sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
    echo "Virtual environment created. Please run this script again."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo ""
echo "Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Dependencies not installed. Installing..."
    pip install -r requirements.txt
    echo ""
    echo "Dependencies installed. Starting server..."
    echo ""
fi

# Start the server
echo ""
echo "========================================"
echo "Starting FastAPI server on http://localhost:8000"
echo "========================================"
echo ""
echo "Press CTRL+C to stop the server"
echo ""
echo "You can test the backend at:"
echo "  - Health Check: http://localhost:8000/health"
echo "  - API Docs: http://localhost:8000/api/v1/docs"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

