# Developer Setup Guide

Complete guide to get RealInbox AI running on your local machine for development.

---

## Prerequisites

Before you begin, ensure you have these installed:

- **Python 3.11 - 3.13** (3.13.3 currently in use)
- **Node.js 18+** and npm
- **Git**
- **Code Editor** (VS Code recommended)

Optional but recommended:
- **PostgreSQL 15+** (for production-like development)
- **Redis 7+** (for caching and background jobs)

---

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "AI inbox manager for real estate agents"
```

---

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Some packages are commented out in `requirements.txt` due to Python 3.13 compatibility:
- `langchain` - Requires numpy compilation
- `tiktoken` - Requires Rust compiler
- `sentence-transformers` - Requires numpy

These are optional. Core functionality works without them.

### 2.3 Environment Configuration

The `.env` file should already exist in the `backend/` directory with secure keys generated.

If you need to regenerate or customize:

```bash
# Copy template
cp ../.env.example .env

# Generate secure keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_hex(16))"
python -c "import secrets; print('ENCRYPTION_SALT=' + secrets.token_hex(8))"

# Edit .env and paste generated values
```

**Key variables to update for full functionality**:
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com (required for AI features)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - For Gmail OAuth
- `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET` - For Outlook OAuth

See `ENV_TEMPLATE.md` for complete configuration guide.

### 2.4 Database Setup

Migrations are already applied. To verify:

```bash
# Check migration status
alembic current

# Should show: 004_drop_messages_clean_slate (head)
```

If you need to reset the database:

```bash
# Backup existing database
cp inbox_manager_dev.db inbox_manager_dev.db.backup

# Delete database
rm inbox_manager_dev.db

# Run migrations from scratch
alembic upgrade head
```

### 2.5 Verify Backend Setup

```bash
# Test configuration loads
python -c "from app.config import settings; print('✅ Config OK')"

# Test database connection
python -c "from app.db import engine; print('✅ Database OK')"

# Test app imports
python -c "from app.main import app; print('✅ App OK')"
```

All should print success messages.

### 2.6 Start Backend Server

```bash
# Development mode with auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the provided script
python -m app.main
```

**Backend should now be running at**:
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/api/v1/docs
- Health Check: http://localhost:8000/health

---

## Step 3: Frontend Setup

Open a new terminal (keep backend running).

### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

### 3.2 Environment Configuration

Create frontend `.env` file:

```bash
# Windows
echo VITE_API_URL=http://localhost:8000/api/v1 > .env

# Mac/Linux
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
```

### 3.3 Start Development Server

```bash
npm run dev
```

**Frontend should now be running at**: http://localhost:5173

### 3.4 Verify Frontend

Open http://localhost:5173 in your browser. You should see the login page.

---

## Step 4: Create Test User

### Via API Docs (Swagger UI)

1. Go to http://localhost:8000/api/v1/docs
2. Find `POST /api/v1/auth/register`
3. Click "Try it out"
4. Enter test data:
```json
{
  "email": "test@example.com",
  "password": "TestPassword123!",
  "full_name": "Test User"
}
```
5. Click "Execute"
6. You should get a 200 response with access token

### Via Frontend

1. Go to http://localhost:5173
2. Click "Sign up for free"
3. Fill in registration form
4. Submit

### Via Python

```bash
cd backend
python -c "
from app.db import SessionLocal
from app.models.user import User, UserRole, SubscriptionTier
from app.security.encryption import hash_password

db = SessionLocal()
user = User(
    email='dev@example.com',
    hashed_password=hash_password('DevPassword123!'),
    full_name='Developer User',
    role=UserRole.ADMIN,
    subscription_tier=SubscriptionTier.PRO
)
db.add(user)
db.commit()
print(f'Created user: {user.email}')
"
```

---

## Step 5: Explore the Application

### Test the Full Stack

1. **Login**: Use the credentials you just created
2. **Dashboard**: Should load with empty state
3. **Contacts**: Navigate to contacts page
4. **Add Contact**: Create a test contact manually
5. **Timeline**: View contact timeline

### Test API Endpoints

Using the Swagger UI at http://localhost:8000/api/v1/docs:

1. **Authenticate**: Use `/api/v1/auth/login` to get token
2. **Contacts**: Test `/api/v1/contacts` CRUD operations
3. **Timeline**: Test `/api/v1/contacts/{id}/timeline`

---

## Optional: Advanced Setup

### Install Redis (for caching)

**Windows** (using Memurai - Redis alternative):
```bash
# Download from https://www.memurai.com/get-memurai
# Or use Docker:
docker run -d -p 6379:6379 redis:latest
```

**Mac** (using Homebrew):
```bash
brew install redis
brew services start redis
```

**Linux**:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### Switch to PostgreSQL

For production-like development:

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE realinbox_dev;
CREATE USER realinbox WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE realinbox_dev TO realinbox;
```

3. Update `backend/.env`:
```
DATABASE_URL=postgresql://realinbox:your_password@localhost:5432/realinbox_dev
```

4. Run migrations:
```bash
cd backend
alembic upgrade head
```

### Set Up Celery Workers

For background email syncing:

1. Ensure Redis is running

2. Start Celery worker:
```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

3. Start Celery beat (scheduler):
```bash
celery -A app.workers.celery_app beat --loglevel=info
```

---

## Development Workflow

### Making Changes

1. **Backend Code Changes**: Server auto-reloads (if using `--reload`)
2. **Frontend Code Changes**: Vite HMR updates instantly
3. **Model Changes**: Generate migration with `alembic revision --autogenerate`
4. **New Dependencies**: Update `requirements.txt` or `package.json`

### Running Tests

**Backend**:
```bash
cd backend
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --cov=app                # With coverage
pytest tests/test_contacts_api.py  # Specific file
```

**Frontend**:
```bash
cd frontend
npm test                        # Run all tests
npm run test:coverage           # With coverage
```

### Code Quality

**Backend**:
```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/

# Security scan
bandit -r app/
```

**Frontend**:
```bash
# Lint
npm run lint

# Format
npm run format
```

---

## Troubleshooting

### Backend Won't Start

**Issue**: `ImportError: cannot import name 'get_db'`

**Fix**: Ensure you've pulled latest changes. This was fixed in recent commit.

---

**Issue**: `ValidationError: Missing environment variables`

**Fix**: Check `backend/.env` file exists and has all required variables.

---

**Issue**: `Redis connection refused`

**Fix**: Redis is optional for basic development. Either:
- Install and start Redis
- Ignore the warning (app still works)

---

### Frontend Won't Start

**Issue**: `ENOENT: no such file or directory`

**Fix**: 
```bash
cd frontend
rm -rf node_modules
npm install
```

---

**Issue**: `Cannot connect to backend`

**Fix**: Ensure backend is running on port 8000. Check `VITE_API_URL` in `frontend/.env`.

---

### Database Issues

**Issue**: `no such table: contacts`

**Fix**: Run migrations:
```bash
cd backend
alembic upgrade head
```

---

**Issue**: `database is locked`

**Fix**: SQLite lock issue. Close all connections:
```bash
# Stop backend server
# Delete lock file if exists
rm inbox_manager_dev.db-shm
rm inbox_manager_dev.db-wal
# Restart server
```

---

### API Key Issues

**Issue**: AI features not working

**Fix**: Update `ANTHROPIC_API_KEY` in `backend/.env` with valid key from https://console.anthropic.com

---

**Issue**: Gmail/Outlook sync not working

**Fix**: Set up OAuth applications and update credentials in `.env`. See `ENV_TEMPLATE.md` for detailed instructions.

---

## Development Tips

1. **Use API Docs**: http://localhost:8000/api/v1/docs is your friend
2. **Check Logs**: Backend prints helpful errors in terminal
3. **Browser DevTools**: Network tab shows API requests/responses
4. **SQLite Browser**: Use DB Browser for SQLite to inspect database
5. **Git Commits**: Commit often with descriptive messages

---

## Next Steps

Now that you're set up:

1. **Read the Codebase**: Start with `app/main.py` and `src/App.tsx`
2. **Check Architecture**: Review `ARCHITECTURE.md`
3. **Review Status**: See `PROJECT_STATUS.md` for current state
4. **Pick a Task**: Check open issues or features to implement

---

## Getting Help

- **Documentation**: Check `*.md` files in root directory
- **API Reference**: http://localhost:8000/api/v1/docs
- **Migration Issues**: See `MIGRATION_GUIDE.md`
- **Environment Config**: See `ENV_TEMPLATE.md`

---

**Happy Coding! 🚀**

Last Updated: October 25, 2025

