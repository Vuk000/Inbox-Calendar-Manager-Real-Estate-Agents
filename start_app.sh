#!/bin/bash
# Start Both Servers Script for Mac/Linux
# This script starts both the backend and frontend servers

echo "========================================"
echo "Starting AgentFlow - Backend + Frontend"
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

# Check if frontend node_modules exists
if [ ! -d "frontend_nextjs/node_modules" ]; then
    echo "Frontend dependencies not found!"
    echo "Installing frontend dependencies..."
    cd frontend_nextjs
    npm install
    cd ..
    echo ""
fi

echo "Starting both servers..."
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press CTRL+C to stop both servers"
echo "========================================"
echo ""

# Start backend in background
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in foreground
cd frontend_nextjs
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

