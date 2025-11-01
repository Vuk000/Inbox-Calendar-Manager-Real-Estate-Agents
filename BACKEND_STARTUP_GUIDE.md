# Backend Startup Guide

## Quick Start

To start the backend server, follow these steps:

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Activate Virtual Environment (if not already activated)

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. Start the Backend Server

```bash
python -m uvicorn app.main:app --reload
```

The server will start on **http://localhost:8000**

### 4. Verify Backend is Running

- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/api/v1/docs
- **Root Endpoint**: http://localhost:8000/

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, you can use a different port:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Then update `frontend_nextjs/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8001/ws
```

### Database Connection Issues

If you see database errors:

1. Check that the database file exists: `backend/reininbox_db.db`
2. If missing, run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

### Import Errors

If you see import errors:

1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables Missing

The backend requires a `.env` file in the `backend/` directory. If missing:

1. Check `backend/ENV_TEMPLATE.md` for required variables
2. Create `.env` file with at minimum:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///./realinbox_db.db
   JWT_SECRET_KEY=your-jwt-secret
   ```

## Expected Output

When the backend starts successfully, you should see:

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

## Next Steps

Once the backend is running:

1. Start the frontend: `cd frontend_nextjs && npm run dev`
2. Open http://localhost:3000 in your browser
3. You should see "API Online" status indicator in the bottom right
4. Try logging in with your account credentials

## Health Check Endpoints

The backend provides several health check endpoints:

- `/health` - Basic health check (always returns 200 if app is running)
- `/health/live` - Liveness probe
- `/health/ready` - Readiness probe (checks database and Redis)
- `/health/detailed` - Detailed health information

These can be used to verify the backend is running and healthy.

