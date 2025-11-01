# ✅ Setup Complete!

Your backend dependencies are now installed and ready to use. Here's how to start the servers:

## 🚀 Quick Start (Easiest Way!)

### Option 1: One-Click Startup Scripts (Recommended)

**Windows PowerShell:**
```powershell
.\start_app.ps1
```

**Windows Command Prompt:**
```cmd
start_app.bat
```

**Note for PowerShell users:** If you try to run `start_app.bat` in PowerShell, you'll get an error. PowerShell requires the `.\` prefix for security. Use:
- `.\start_app.ps1` (PowerShell script - recommended)
- `.\start_app.bat` (if you prefer the batch file)

**Mac/Linux:**
```bash
./start_app.sh
```

These scripts will:
- ✅ Check and create virtual environments if needed
- ✅ Install dependencies automatically
- ✅ Start backend in a separate window
- ✅ Start frontend in current window

### Option 2: VS Code Tasks

1. Open VS Code in the project root
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Tasks: Run Task"
4. Select "Start Both Servers"

Or use the debugger:
- Press `F5` → Select "Full Stack: Backend + Frontend"

### Option 3: npm Script (from frontend_nextjs folder)

```powershell
cd frontend_nextjs
npm run dev:all
```

This uses `concurrently` to start both servers in the same terminal.

## 📝 Two Terminal Approach (Manual)

If you prefer to control each server separately:

### Terminal 1 - Backend:
```powershell
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

### Terminal 2 - Frontend:
```powershell
cd frontend_nextjs
npm run dev
```

## What to Expect

**Backend Terminal:**
- You'll see: "🚀 Starting Project Apex..."
- Then: "Uvicorn running on http://0.0.0.0:8000"
- Backend is ready when you see: "Application startup complete."
- **Note**: Redis warnings are normal - Redis is optional for basic functionality

**Frontend Terminal:**
- You'll see: "Ready on http://localhost:3000"
- Frontend is ready when you see this message

**In Browser:**
- Open http://localhost:3000
- You should see "API Online" indicator in bottom right
- Login with your credentials

## 🔧 VS Code Setup

### Virtual Environment Configuration

VS Code is configured to:
- ✅ **Ignore root `.venv`** - Won't auto-activate it
- ✅ **Use `backend/venv`** - Automatically for backend files
- ✅ **Set correct Python interpreter** - `backend/venv/Scripts/python.exe`

**If VS Code still activates wrong venv:**
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose: `.\backend\venv\Scripts\python.exe`

### Recommended Extensions

VS Code will suggest these extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- ESLint
- Prettier
- Tailwind CSS IntelliSense

## 🐛 Troubleshooting

### Backend Issues

**"No module named uvicorn" error:**
- ❌ **Problem**: VS Code is using root `.venv` instead of `backend/venv`
- ✅ **Solution**: 
  1. Press `Ctrl+Shift+P` → "Python: Select Interpreter"
  2. Choose `.\backend\venv\Scripts\python.exe`
  3. Or use startup scripts: `.\start_app.ps1` (they use correct venv)

**"bcrypt" or "passlib" errors:**
- ✅ Fixed! bcrypt 4.1.2 is now installed (compatible with passlib 1.7.4)
- If you see bcrypt errors, run: `cd backend && venv\Scripts\activate && pip install bcrypt==4.1.2 --force-reinstall`

**Redis connection errors:**
- ✅ Normal! Redis is optional - the app works without it
- Redis is only needed for:
  - Caching (performance optimization)
  - Background tasks (Celery)
- To disable Redis completely, set `REDIS_ENABLED=false` in your `.env` file

**"Cannot connect to server" on login:**
- Make sure backend is running (check separate window or terminal)
- Check backend shows "Application startup complete"
- Verify backend is accessible at http://localhost:8000/health
- Ensure you're using `backend/venv`, not root `.venv`

### Frontend Issues

**"API Online" indicator shows offline:**
- Check backend is running
- Verify backend health endpoint: http://localhost:8000/health
- Check browser console for errors

### Virtual Environment Confusion

**Root `.venv` vs `backend/venv`:**
- ⚠️ **Root `.venv`**: Exists but **should NOT be used** (no backend dependencies)
- ✅ **`backend/venv`**: **MUST be used** (has all backend dependencies)
- VS Code settings prevent root `.venv` auto-activation
- Always use `backend/venv` for backend work

**Verify correct venv:**
```powershell
# Check which Python is being used
cd backend
venv\Scripts\activate
python -c "import sys; print(sys.executable)"
# Should show: ...\backend\venv\Scripts\python.exe
```

**Verify uvicorn is installed:**
```powershell
cd backend
venv\Scripts\activate
python -c "import uvicorn; print('✅ uvicorn found')"
```

## 🔍 Environment Verification

Run the verification script to check everything:
```powershell
.\setup_dev_env.ps1
```

This will check:
- Python installation
- Backend venv existence
- uvicorn installation
- Node.js installation
- Frontend dependencies
- Configuration files

## Redis Optional

Redis is now **optional** for basic functionality:
- ✅ App works without Redis
- ✅ Login/authentication works
- ✅ Database operations work
- ⚠️ Caching disabled (slower performance)
- ⚠️ Background tasks disabled (email sync won't run automatically)

To enable Redis:
1. Install Redis: https://redis.io/download
2. Start Redis: `redis-server`
3. Set `REDIS_ENABLED=true` in `.env` (default)

## Quick Commands Summary

**Start everything:**
- `.\start_app.ps1` (PowerShell)
- `start_app.bat` (Command Prompt)
- `npm run dev:all` (from frontend_nextjs folder)

**Start individually:**
- Backend: `cd backend && venv\Scripts\activate && python -m uvicorn app.main:app --reload`
- Frontend: `cd frontend_nextjs && npm run dev`

**Verify environment:**
- `.\setup_dev_env.ps1`

The backend venv now has all required dependencies installed!

