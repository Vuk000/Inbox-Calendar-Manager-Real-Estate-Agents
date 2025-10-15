# 🚀 Getting Started with RealInbox AI

This comprehensive guide will help you set up and run the RealInbox AI platform from scratch.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Testing](#testing)
6. [Next Steps](#next-steps)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.10 or higher
- **Node.js**: 18 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 10GB free space
- **Internet**: Broadband connection for API calls

### Software Prerequisites

Before starting, install these:

1. **Python 3.10+**
   - Download from: https://www.python.org/downloads/
   - Verify: `python --version`

2. **Node.js 18+ and npm**
   - Download from: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

3. **PostgreSQL 15+**
   - Download from: https://www.postgresql.org/download/
   - OR use Docker (see below)

4. **Redis 7+**
   - Download from: https://redis.io/download
   - OR use Docker (see below)

5. **Git**
   - Download from: https://git-scm.com/downloads

6. **Docker Desktop** (Recommended)
   - Download from: https://www.docker.com/products/docker-desktop
   - Simplifies PostgreSQL and Redis setup

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd "AI inbox manager for real estate agents"
```

### Step 2: Backend Setup

#### 2.1 Create Python Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

#### 2.2 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install ~40 packages including FastAPI, SQLAlchemy, Anthropic, etc.

#### 2.3 Start Database Services

**Option A: Using Docker (Recommended)**

```bash
# Make sure Docker Desktop is running
docker-compose up -d postgres redis
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379

Verify with: `docker-compose ps`

**Option B: Local Installation**

If you installed PostgreSQL and Redis locally:

```bash
# Start PostgreSQL (varies by OS)
# Windows: Start from Services or pgAdmin
# macOS: brew services start postgresql@15
# Linux: sudo systemctl start postgresql

# Start Redis
# Windows: Download from GitHub releases and run redis-server.exe
# macOS: brew services start redis
# Linux: sudo systemctl start redis
```

### Step 3: Frontend Setup

Open a **new terminal** (keep backend terminal open).

```bash
# Navigate to frontend directory from project root
cd frontend

# Install Node dependencies
npm install
```

This will install React, Vite, Tailwind, and other packages (~200 packages).

---

## Configuration

### Backend Configuration

#### 1. Create Environment File

```bash
# In backend directory
cd backend
copy .env.example .env   # Windows
# OR
cp .env.example .env     # macOS/Linux
```

#### 2. Edit .env File

Open `backend/.env` in your favorite text editor and configure:

**Essential Settings (Required to Start)**

```env
# Core Settings
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-also-change-this

# Database (if using Docker defaults, these work as-is)
DATABASE_URL=postgresql://realinbox_user:realinbox_password@localhost:5432/realinbox_db
REDIS_URL=redis://localhost:6379/0

# Encryption (generate secure keys)
ENCRYPTION_KEY=your-32-character-encryption-key-here
ENCRYPTION_SALT=your-encryption-salt-here

# Anthropic Claude (REQUIRED - Get from https://console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

**How to Generate Secure Keys:**

```python
# Run this in Python to generate secure keys
import secrets
print("SECRET_KEY:", secrets.token_urlsafe(32))
print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))
print("ENCRYPTION_KEY:", secrets.token_urlsafe(32))
print("ENCRYPTION_SALT:", secrets.token_urlsafe(16))
```

**Optional Settings (For Full Features)**

Add these as you obtain API keys:

```env
# Google OAuth (for Gmail integration)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Microsoft OAuth (for Outlook)
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/auth/microsoft/callback

# Pinecone (for semantic search)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1-aws

# Twilio (for SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# AWS S3 (for document storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=realinbox-documents
```

#### 3. Initialize Database

```bash
# Make sure you're in backend directory with venv activated
python -c "from app.db import init_db; init_db()"
```

You should see: "Database initialized" or similar message.

### Frontend Configuration

```bash
# In frontend directory
cd frontend

# Create .env file
echo VITE_API_URL=http://localhost:8000/api/v1 > .env
```

---

## Running the Application

### 1. Start Backend Server

```bash
# In backend directory with venv activated
cd backend
python -m app.main
```

Expected output:
```
🚀 Starting RealInbox AI...
✅ Database initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify backend is running:**
- Open: http://localhost:8000/health
- Should see: `{"status": "healthy", ...}`
- API docs: http://localhost:8000/api/v1/docs

### 2. Start Frontend Dev Server

In a **new terminal**:

```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**Verify frontend is running:**
- Open: http://localhost:3000
- Should see login page

### 3. Create Your First Account

1. Go to http://localhost:3000
2. Click "Sign up for free"
3. Fill in:
   - **Full Name**: Your Name
   - **Email**: your@email.com
   - **Password**: At least 8 characters
   - **Confirm Password**: Same password
4. Click "Create Account"
5. You'll be logged in automatically and see the dashboard!

---

## Testing

### Test Authentication

1. **Register a new user** (as above)
2. **Logout**: Click "Logout" in sidebar
3. **Login**: Use the credentials you just created
4. **Verify dashboard loads**: Should see welcome message and stats

### Test API Endpoints

Using the interactive API docs:

1. Go to http://localhost:8000/api/v1/docs
2. Try the `/health` endpoint: Should return healthy status
3. Try `/api/v1/auth/register`: Create a test user
4. Try `/api/v1/auth/login`: Get access token
5. Click "Authorize" button, paste your access token
6. Try `/api/v1/auth/me`: Should return your user info

### Test AI Agents (Backend Only)

```python
# In a Python shell with venv activated
from app.agents.triage_agent import TriageAgent
import asyncio

agent = TriageAgent()

email = {
    "subject": "Offer for 123 Main St",
    "body": "I'm interested in making an offer of $450,000 for the property at 123 Main St. Can we discuss?",
    "sender_email": "buyer@example.com"
}

result = asyncio.run(agent.analyze_email(email))
print(result)
```

You should see JSON output with priority, category, entities extracted, etc.

---

## Next Steps

### 1. Obtain API Keys

To unlock full features, get these API keys:

**Priority 1 (Core Features):**
- [x] Anthropic Claude: https://console.anthropic.com (Already required)
- [ ] Pinecone: https://www.pinecone.io (For semantic search)

**Priority 2 (Email Integration):**
- [ ] Google Cloud Console: https://console.cloud.google.com (Gmail)
- [ ] Microsoft Azure: https://portal.azure.com (Outlook)

**Priority 3 (Multi-Channel):**
- [ ] Twilio: https://www.twilio.com (SMS/WhatsApp)
- [ ] AWS: https://aws.amazon.com (Document storage)

### 2. Connect Your Email Account

Once you have Google/Microsoft OAuth credentials:

1. Go to Settings page
2. Click "Connect Gmail" or "Connect Outlook"
3. Follow OAuth flow
4. Grant permissions
5. Your emails will start syncing!

### 3. Explore Features

- **Dashboard**: Overview of your productivity
- **Inbox**: AI-triaged emails (coming soon)
- **Drafts**: Generate AI responses (coming soon)
- **Tasks**: Auto-created from emails (coming soon)
- **Properties**: Property-centric views (coming soon)
- **Analytics**: Track your ROI (coming soon)

### 4. Customize AI Behavior

- Train the AI on your writing style
- Set up custom automation rules
- Configure notification preferences
- Adjust priority thresholds

---

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'app'`
- **Solution**: Make sure you're in the `backend` directory and venv is activated

**Issue**: `Connection refused` to PostgreSQL
- **Solution**: 
  1. Check if PostgreSQL is running: `docker-compose ps` or `psql --version`
  2. Verify DATABASE_URL in .env matches your setup
  3. If using Docker: `docker-compose restart postgres`

**Issue**: `Anthropic API key not found`
- **Solution**: Add your Anthropic API key to `backend/.env`

**Issue**: Database tables not created
- **Solution**: Run `python -c "from app.db import init_db; init_db()"`

**Issue**: Port 8000 already in use
- **Solution**: Kill the process using port 8000 or change port in `main.py`

### Frontend Issues

**Issue**: `Cannot GET /api/v1/...`
- **Solution**: Make sure backend is running on port 8000

**Issue**: CORS errors in browser console
- **Solution**: Verify CORS_ORIGINS in backend .env includes `http://localhost:3000`

**Issue**: `npm install` fails
- **Solution**: 
  1. Delete `node_modules` and `package-lock.json`
  2. Run `npm cache clean --force`
  3. Run `npm install` again

**Issue**: Blank page after build
- **Solution**: Check browser console for errors, verify VITE_API_URL in .env

### Database Issues

**Issue**: Docker containers won't start
- **Solution**: 
  1. Make sure Docker Desktop is running
  2. Check ports 5432 and 6379 aren't in use: `netstat -an | findstr 5432`
  3. Try: `docker-compose down && docker-compose up -d`

**Issue**: "Password authentication failed"
- **Solution**: 
  1. Check DATABASE_URL credentials match docker-compose.yml
  2. Try: `docker-compose down -v` (removes volumes) then `docker-compose up -d`

### Getting Help

If you're still stuck:

1. Check the error message carefully
2. Search for the error in:
   - Backend logs (terminal where backend is running)
   - Frontend browser console (F12 → Console tab)
   - Docker logs: `docker-compose logs postgres redis`
3. Review the README.md files in backend/ and frontend/
4. Check that all prerequisites are installed with correct versions

---

## Development Workflow

### Daily Development

1. **Start services** (once per day):
   ```bash
   # Terminal 1: Databases
   docker-compose up -d
   
   # Terminal 2: Backend
   cd backend
   venv\Scripts\activate  # or source venv/bin/activate
   python -m app.main
   
   # Terminal 3: Frontend
   cd frontend
   npm run dev
   ```

2. **Make changes** to code
   - Backend: Changes auto-reload (FastAPI reload)
   - Frontend: Changes auto-reload (Vite HMR)

3. **Test changes** in browser at http://localhost:3000

4. **Stop services** (end of day):
   ```bash
   # Ctrl+C in each terminal
   # Then:
   docker-compose down
   ```

### Adding New Features

1. **Backend**: Add to `app/routers/` or `app/agents/`
2. **Frontend**: Add to `src/pages/` or `src/components/`
3. **Test**: Write tests in `backend/tests/` or `frontend/src/__tests__/`
4. **Document**: Update README files

---

## Success Checklist

Before moving to production:

- [ ] All API keys configured
- [ ] Database migrations run successfully
- [ ] Backend health check passes
- [ ] Frontend builds without errors (`npm run build`)
- [ ] Can register and login
- [ ] Can connect email account
- [ ] AI agents return valid results
- [ ] No console errors in browser
- [ ] Responsive design works on mobile
- [ ] Security: Strong secret keys set
- [ ] Backup strategy in place

---

**🎉 Congratulations! You've successfully set up RealInbox AI!**

Start building the future of real estate email management! 🚀

For questions or issues, refer to the main README.md or backend/frontend specific READMEs.

