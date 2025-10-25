# Quick Reference Guide

One-page reference for common development tasks.

---

## 🚀 Starting the Application

### Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```
**Runs at**: http://localhost:8000

### Frontend
```bash
cd frontend
npm run dev
```
**Runs at**: http://localhost:5173

---

## 📖 Key Documentation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - What works, what's in progress
- **[DEVELOPER_SETUP.md](DEVELOPER_SETUP.md)** - Detailed setup instructions
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Database management
- **[COMPLETION_REPORT.md](COMPLETION_REPORT.md)** - What was just fixed

---

## 🔧 Common Commands

### Database
```bash
# Check migration status
cd backend
alembic current

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing
```bash
# Backend tests
cd backend
pytest
pytest -v  # verbose
pytest --cov=app  # with coverage

# Frontend tests
cd frontend
npm test
```

### Code Quality
```bash
# Backend
black app/  # format
isort app/  # sort imports
mypy app/   # type check

# Frontend
npm run lint
```

---

## 🌐 Important URLs

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:5173

---

## 🔑 Environment Variables

Edit `backend/.env`:

**Required for AI features**:
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com

**Required for email sync**:
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET`

**Optional**:
- Redis, Twilio, AWS S3, etc.

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Verify config loads
python -c "from app.config import settings; print('OK')"

# Check database
alembic current
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Port already in use
```bash
# Find and kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend build fails
```bash
cd frontend
rm -rf node_modules
npm install
```

---

## 📊 Project Structure

```
RealInbox AI/
├── backend/
│   ├── app/
│   │   ├── agents/      # AI agents
│   │   ├── models/      # Database models
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   └── main.py      # Entry point
│   ├── alembic/         # Migrations
│   ├── tests/           # Tests
│   └── .env             # Config (DO NOT COMMIT)
│
├── frontend/
│   └── src/
│       ├── pages/       # Page components
│       ├── components/  # UI components
│       └── stores/      # State management
│
└── docs/
    └── archive/         # Old documentation
```

---

## ✅ Current Status

**Backend**: ✅ Running  
**Database**: ✅ Migrations applied (004)  
**Frontend**: Ready to start  
**Documentation**: ✅ Consolidated  
**Tests**: Need updates (non-blocking)

---

## 🎯 Next Steps

1. Start backend & frontend
2. Create test user
3. Explore the app
4. (Optional) Add Anthropic API key for AI features
5. (Optional) Set up Gmail OAuth for email sync

---

**Last Updated**: October 25, 2025

