#!/bin/bash
# Start Backend Server Script for Mac/Linux
# This script starts the backend server

echo "========================================"
echo "Starting AgentFlow - Backend"
echo "========================================"
echo ""

# Check if we're in the project root
if [ ! -f "backend/app/main.py" ]; then
    echo "Error: This script must be run from the project root directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if backend virtual environment exists
if [ ! -f "backend/venv/bin/activate" ]; then
    echo "Backend virtual environment not found!"
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    echo ""
    echo "Installing backend dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo ""
fi

echo "Starting backend server..."
echo ""
echo "Backend will run on: http://localhost:8000"
echo ""
echo "Press CTRL+C to stop the server"
echo "========================================"
echo ""

# Start backend
cd backend
if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python -m uvicorn app.main:app --reload
cd ..

