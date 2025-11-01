# Quick Start Guide - Backend Connection Issues

## Problem
You're seeing errors like:
- "Cannot connect to server"
- "Network error. Please check if the backend server is running."
- "Backend Unreachable"

## Solution

The backend server needs to be started before you can login. Follow these steps:

### Option 1: Use the Startup Script (Windows)

1. Navigate to the `backend` folder
2. Double-click `start_backend.bat`
3. Wait for the server to start (you'll see "Uvicorn running on http://0.0.0.0:8000")
4. Keep this terminal window open while using the app

### Option 2: Manual Start (Windows)

1. Open PowerShell or Command Prompt
2. Navigate to the backend folder:
   ```powershell
   cd "C:\Business\AI inbox manager for real estate agents\backend"
   ```
3. Activate virtual environment:
   ```powershell
   venv\Scripts\activate
   ```
4. Start the server:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```

### Option 3: Manual Start (Mac/Linux)

1. Open Terminal
2. Navigate to the backend folder:
   ```bash
   cd "path/to/AI inbox manager for real estate agents/backend"
   ```
3. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Start the server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Verify Backend is Running

Once started, you should see:
```
🚀 Starting Project Apex...
✅ Database initialized
✅ Audit listeners registered
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

You can verify by:
- Opening http://localhost:8000/health in your browser
- Looking for "API Online" indicator in the bottom right of the frontend

## Troubleshooting

### Virtual Environment Not Found

If you see "No module named 'venv'", create the virtual environment:

**Windows:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 is already in use, use a different port:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Then update `frontend_nextjs/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8001/ws
```

### Import Errors

If you see import errors when starting:
1. Make sure you're in the `backend` directory
2. Make sure virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`

## Important Notes

- **Keep the backend terminal open** - Closing it will stop the server
- **Both servers needed** - Backend (port 8000) and Frontend (port 3000) must both be running
- **Redis warnings are normal** - Redis is optional, you can ignore those warnings

## Next Steps

Once the backend is running:
1. Start the frontend: `cd frontend_nextjs && npm run dev`
2. Open http://localhost:3000
3. You should see "API Online" indicator
4. Login with your credentials

