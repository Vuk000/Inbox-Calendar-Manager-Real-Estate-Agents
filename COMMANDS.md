# Command Reference - Phase 1 Completion

Quick copy-paste commands to complete Phase 1.

## ⚡ Quick Start (After Adding API Credentials)

```powershell
# 1. Test configuration
cd backend
python -c "from app.config import settings; print('✅ Config loaded!')"

# 2. Run migrations
alembic upgrade head

# 3. Start backend
python -m app.main
# Keep this terminal open, backend running on port 8000

# 4. New terminal: Start frontend
cd frontend
npm install
npm run dev
# Frontend running on port 5173

# 5. Open browser
start http://localhost:5173
```

## 🧪 Testing Commands

```powershell
cd backend

# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html

# Individual test files
pytest tests/test_auth.py -v
pytest tests/test_email_sync_integration.py -v
pytest tests/test_contact_timeline_api.py -v
pytest tests/test_contact_import.py -v

# Run specific test
pytest tests/test_contact_timeline_api.py::TestContactTimelineAPI::test_contact_timeline_performance -v

# View coverage report
start htmlcov/index.html
```

## 🗄️ Database Commands

```powershell
# PostgreSQL (if using)
psql -U username -d realinbox_db

# View tables
\dt

# View contacts
SELECT id, first_name, last_name, email, relationship_score FROM contacts;

# View communications
SELECT id, contact_id, communication_type, subject, occurred_at FROM communication_logs ORDER BY occurred_at DESC LIMIT 10;

# SQLite (if using)
sqlite3 realinbox_test.db

# View tables
.tables

# Same queries work
```

## 📝 Create Test Communication (SQL)

```sql
-- For PostgreSQL
INSERT INTO communication_logs (
    user_id, contact_id, communication_type, direction,
    subject, body, summary, from_address, occurred_at, created_at
) VALUES (
    1, 1, 'email', 'inbound',
    'Interested in property',
    'Hi, I am very interested in the listing...',
    'Client expressing interest',
    'john.buyer@example.com',
    NOW() - INTERVAL '2 hours',
    NOW()
);

-- For SQLite
INSERT INTO communication_logs (
    user_id, contact_id, communication_type, direction,
    subject, body, summary, from_address, occurred_at, created_at
) VALUES (
    1, 1, 'email', 'inbound',
    'Interested in property',
    'Hi, I am very interested in the listing...',
    'Client expressing interest',
    'john.buyer@example.com',
    datetime('now', '-2 hours'),
    datetime('now')
);
```

## 🔑 Generate New Keys (If Needed)

```powershell
# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_hex(16))"

# ENCRYPTION_SALT
python -c "import secrets; print(secrets.token_hex(8))"
```

## 📊 Check Server Health

```powershell
# Health check
curl http://localhost:8000/health

# API docs (in browser)
start http://localhost:8000/api/v1/docs

# Test auth endpoint
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"password123\",\"full_name\":\"Test User\"}'
```

## 🔄 Reset Database (If Needed)

```powershell
cd backend

# Downgrade all migrations
alembic downgrade base

# Reapply all migrations
alembic upgrade head

# OR for SQLite, just delete and recreate:
Remove-Item realinbox_test.db
alembic upgrade head
```

## 📦 Frontend Commands

```powershell
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run frontend tests
npm test
```

## 🔍 Debugging Commands

```powershell
# Check Python version
python --version

# Check if packages installed
pip list | Select-String "fastapi|sqlalchemy|alembic|pytest"

# Check environment variables loaded
cd backend
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('ANTHROPIC_API_KEY:', os.getenv('ANTHROPIC_API_KEY')[:20])"

# Test database connection (PostgreSQL)
python -c "from app.db import SessionLocal; db = SessionLocal(); print('✅ DB connected'); db.close()"

# View alembic current revision
alembic current

# View alembic history
alembic history

# Check for pending migrations
alembic heads
```

## 🧹 Cleanup Commands (If Starting Fresh)

```powershell
# Backend: Remove virtual environment and reinstall
cd backend
deactivate  # if in venv
Remove-Item -Recurse -Force venv
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Frontend: Clean install
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install

# Database: Fresh start (SQLite)
cd backend
Remove-Item realinbox_test.db
alembic upgrade head
```

## 📝 Git Commands (Save Your Progress)

```powershell
# Check status
git status

# Add new files
git add .

# Commit
git commit -m "Phase 1: Environment setup, tests, and documentation"

# Push to remote
git push origin main

# Create a Phase 1 tag
git tag -a v1.0-phase1 -m "Phase 1 complete: Validated MVP with Unified Timeline"
git push origin v1.0-phase1
```

## 🎯 Most Common Workflow

```powershell
# Morning startup
cd backend
python -m app.main  # Terminal 1

cd frontend
npm run dev  # Terminal 2

# Open browser
start http://localhost:5173

# Work on backend
# Edit code -> Ctrl+C -> python -m app.main

# Work on frontend
# Edit code -> Save (auto-reload with Vite)

# Run tests
cd backend
pytest tests/test_contact_timeline_api.py -v

# Commit changes
git add .
git commit -m "Your commit message"
git push
```

## 💡 Tips

**PowerShell Aliases** (add to `$PROFILE`):
```powershell
function Start-Backend { cd C:\Business\AI inbox manager for real estate agents\backend; python -m app.main }
function Start-Frontend { cd C:\Business\AI inbox manager for real estate agents\frontend; npm run dev }
function Run-Tests { cd C:\Business\AI inbox manager for real estate agents\backend; pytest tests/ -v }

Set-Alias sb Start-Backend
Set-Alias sf Start-Frontend
Set-Alias rt Run-Tests
```

Then just type: `sb`, `sf`, or `rt`

**VS Code Tasks** (`.vscode/tasks.json`):
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "cd backend && python -m app.main",
      "problemMatcher": []
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "cd frontend && npm run dev",
      "problemMatcher": []
    },
    {
      "label": "Run All Tests",
      "type": "shell",
      "command": "cd backend && pytest tests/ -v",
      "problemMatcher": []
    }
  ]
}
```

Use: Ctrl+Shift+P → "Tasks: Run Task"

