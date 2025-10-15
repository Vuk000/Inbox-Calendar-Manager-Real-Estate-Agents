# RealInbox AI - Backend

AI-powered inbox manager for real estate agents built with FastAPI, Claude Sonnet 4.5, and PostgreSQL.

## Features

- 🔐 Enterprise-grade security (AES-256, OAuth 2.0, RBAC)
- 🤖 AI-powered email triage and prioritization
- ✍️ Auto-draft personalized responses
- 📧 Gmail & Outlook integration
- 💬 SMS/WhatsApp support via Twilio
- 🔍 Semantic email search with Pinecone
- 📊 Analytics and insights
- 🏠 Real estate-specific workflows

## Tech Stack

- **Backend:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL 15+
- **Cache:** Redis 7+
- **AI:** Anthropic Claude Sonnet 4.5
- **Vector DB:** Pinecone
- **Email APIs:** Google (Gmail), Microsoft Graph (Outlook)
- **SMS/WhatsApp:** Twilio

## Setup

### 1. Prerequisites

- Python 3.10 or higher
- PostgreSQL 15+
- Redis 7+
- Anthropic API key
- Google Cloud Console project (for Gmail)
- Microsoft Azure app (for Outlook)
- Twilio account (for SMS/WhatsApp)
- Pinecone account

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Start PostgreSQL and Redis with Docker Compose
docker-compose up -d postgres redis

# Or install locally and start services
```

### 4. Environment Configuration

```bash
# Copy example environment file
copy .env.example .env

# Edit .env and add your API keys and credentials
```

**Required Environment Variables:**

```env
# Core
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://realinbox_user:realinbox_password@localhost:5432/realinbox_db
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Encryption
ENCRYPTION_KEY=your-32-byte-key
ENCRYPTION_SALT=your-salt

# Anthropic Claude
ANTHROPIC_API_KEY=your-anthropic-api-key

# Google OAuth (Gmail)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Microsoft OAuth (Outlook)
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/auth/microsoft/callback

# Twilio
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1-aws

# AWS S3 (for documents)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-bucket-name
```

### 5. Database Migration

```bash
# Initialize database (creates tables)
python -c "from app.db import init_db; init_db()"

# Or use Alembic for migrations (optional)
alembic upgrade head
```

### 6. Run Development Server

```bash
# Start FastAPI server
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

API Documentation: http://localhost:8000/api/v1/docs

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/google/authorize` - Start Google OAuth
- `GET /api/v1/auth/microsoft/authorize` - Start Microsoft OAuth

### Emails (Coming Soon)
- `GET /api/v1/emails` - List emails with AI triage
- `GET /api/v1/emails/{id}` - Get email details
- `POST /api/v1/emails/{id}/analyze` - Run AI analysis
- `POST /api/v1/emails/search` - Semantic search

### Drafts (Coming Soon)
- `POST /api/v1/drafts/generate` - Generate AI draft
- `GET /api/v1/drafts` - List drafts
- `PATCH /api/v1/drafts/{id}` - Edit draft
- `POST /api/v1/drafts/{id}/send` - Send draft

### Tasks (Coming Soon)
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `PATCH /api/v1/tasks/{id}` - Update task

### Analytics (Coming Soon)
- `GET /api/v1/analytics/dashboard` - Get dashboard metrics
- `GET /api/v1/analytics/reports` - Generate reports

## Project Structure

```
backend/
├── app/
│   ├── agents/              # AI agents (triage, draft, etc.)
│   │   ├── triage_agent.py
│   │   ├── draft_agent.py
│   │   ├── lead_qualification_agent.py
│   │   └── negotiation_agent.py
│   ├── integrations/        # External API integrations
│   │   ├── gmail_integration.py
│   │   ├── outlook_integration.py
│   │   ├── twilio_integration.py
│   │   └── vector_store.py
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── email_account.py
│   │   ├── message.py
│   │   ├── draft.py
│   │   ├── property.py
│   │   ├── task.py
│   │   ├── analytics.py
│   │   └── audit_log.py
│   ├── routers/             # FastAPI route handlers
│   │   ├── auth.py
│   │   ├── emails.py
│   │   ├── drafts.py
│   │   ├── tasks.py
│   │   └── analytics.py
│   ├── security/            # Security utilities
│   │   ├── encryption.py
│   │   ├── jwt_handler.py
│   │   ├── rbac.py
│   │   └── audit.py
│   ├── config.py            # Configuration management
│   ├── db.py                # Database connection
│   ├── dependencies.py      # FastAPI dependencies
│   └── main.py              # FastAPI app entry point
├── tests/                   # Test suite
├── docker-compose.yml       # Docker services
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```

## Development

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

### Code Style

```bash
# Format with black
black app/

# Lint with flake8
flake8 app/
```

## Deployment

### Production Setup

1. Use production-grade database (AWS RDS PostgreSQL)
2. Use Redis cluster or AWS ElastiCache
3. Set up HTTPS with SSL certificates
4. Configure environment variables securely
5. Use Gunicorn + Uvicorn workers
6. Set up monitoring (Sentry, CloudWatch)
7. Configure auto-scaling

### Deploy to AWS

```bash
# Build Docker image
docker build -t realinbox-api .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag realinbox-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/realinbox-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/realinbox-api:latest

# Deploy to ECS or EKS
```

## Security Best Practices

1. **Never commit `.env` files** - Use environment variable management
2. **Rotate API keys regularly** - Set up key rotation policies
3. **Use HTTPS in production** - Enforce TLS 1.3
4. **Enable rate limiting** - Protect against abuse
5. **Monitor audit logs** - Track suspicious activity
6. **Regular security audits** - Use OWASP ZAP, etc.

## Support

For issues or questions:
- Create an issue on GitHub
- Email: support@realinbox.ai
- Documentation: https://docs.realinbox.ai

## License

Proprietary - All rights reserved

