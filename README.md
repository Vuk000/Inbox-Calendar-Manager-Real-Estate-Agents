# RealInbox AI - Complete SaaS Platform

🚀 **AI-Powered Inbox Manager for Real Estate Agents**

**Status**: ✅ **READY FOR LOCAL DEVELOPMENT**  
**Last Updated**: October 25, 2025  
**Version**: 2.0.0 (Project Apex - CRM Focus)

An enterprise-grade SaaS platform that uses AI (Claude Sonnet 4.5) to automate email management, lead qualification, response drafting, and workflow automation specifically for real estate professionals.

> **✅ All critical fixes applied! Backend starts successfully. Environment configured. Database migrations complete. Ready for development!**  
> **📚 New Documentation**: See [`PROJECT_STATUS.md`](PROJECT_STATUS.md) for current state and [`DEVELOPER_SETUP.md`](DEVELOPER_SETUP.md) for setup instructions.

## 🎯 Overview

RealInbox AI solves the email overwhelm problem for real estate agents by providing:

- **Intelligent Email Triage**: AI categorizes and prioritizes emails (offers, leads, inspections, etc.)
- **Auto-Draft Responses**: Generate personalized replies in the agent's voice
- **Lead Qualification**: Automatically score and enrich leads from inquiries
- **Multi-Channel Inbox**: Unify email, SMS, and WhatsApp in one place
- **Task Automation**: Convert emails to calendar events and actionable tasks
- **Analytics & Insights**: Track productivity, ROI, and lead conversion

### Market Opportunity

- 1.5M+ real estate agents in the US
- Agents spend 2-3 hours daily on email chaos
- 73% of leads go cold without timely follow-ups
- Target: $100K+ ARR in 12 months at $29-149/month

## 📁 Project Structure

```
RealInbox AI/
├── backend/                # Python FastAPI backend
│   ├── app/
│   │   ├── agents/        # AI agents (triage, draft, negotiation, lead qualification)
│   │   ├── integrations/  # Gmail, Outlook, Twilio, Pinecone, etc.
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── routers/       # API endpoints
│   │   ├── security/      # Auth, encryption, RBAC, audit logging
│   │   ├── config.py      # Configuration management
│   │   ├── db.py          # Database connection
│   │   └── main.py        # FastAPI app entry point
│   ├── requirements.txt   # Python dependencies
│   ├── docker-compose.yml # Local dev services (PostgreSQL, Redis)
│   └── README.md
│
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API integration
│   │   ├── stores/       # State management (Zustand)
│   │   └── App.tsx
│   ├── package.json
│   └── README.md
│
├── docs/                  # Documentation (to be created)
├── .gitignore
└── README.md             # This file
```

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 15+ (primary), Redis (cache), Pinecone (vector DB)
- **AI**: Anthropic Claude Sonnet 4.5, LangChain for agents
- **Auth**: OAuth 2.0, JWT tokens, AES-256 encryption
- **Integrations**: Gmail API, Microsoft Graph, Twilio, AWS S3
- **Background Jobs**: Celery + Redis
- **Monitoring**: Sentry

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Notifications**: React Hot Toast

## 🚀 Quick Start

### Prerequisites

- **Python 3.11 - 3.13** (3.13.3 currently in use)
- **Node.js 18+** and npm
- **Git**

Optional but recommended:
- **PostgreSQL 15+** (SQLite used by default for dev)
- **Redis 7+** (optional for caching)

### 1. Clone Repository

```bash
git clone <repository-url>
cd "AI inbox manager for real estate agents"
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Environment is pre-configured (.env file exists)
# Database migrations are already applied
# Just verify everything loads:
python -c "from app.config import settings; print('✅ Config OK')"

# Start backend server
python -m uvicorn app.main:app --reload
```

**Backend runs at**: http://localhost:8000  
**API docs at**: http://localhost:8000/api/v1/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file (if not exists)
echo VITE_API_URL=http://localhost:8000/api/v1 > .env

# Start development server
npm run dev
```

**Frontend runs at**: http://localhost:5173

### 4. Create Test User & Login

**Option 1 - Via Frontend**:
1. Open http://localhost:5173
2. Click "Sign up for free"
3. Create account and login

**Option 2 - Via API Docs**:
1. Go to http://localhost:8000/api/v1/docs
2. Use `POST /api/v1/auth/register` endpoint
3. Login with created credentials

---

## 📖 Documentation

**Start Here**:
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Current status, what works, known issues
- **[DEVELOPER_SETUP.md](DEVELOPER_SETUP.md)** - Detailed setup instructions

**Additional Guides**:
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Database migration management
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and design
- **[ENV_TEMPLATE.md](ENV_TEMPLATE.md)** - Environment variable reference

**Archived Docs**: `docs/archive/` - Historical status reports

## 🔑 Configuration

### Required API Keys

You'll need to obtain API keys for the following services:

#### 1. Anthropic Claude (Required)
- Sign up at: https://console.anthropic.com
- Get API key from Settings
- Add to `.env`: `ANTHROPIC_API_KEY=your-key`
- Cost: ~$20/month for development

#### 2. Google OAuth & Gmail API (For Gmail integration)
- Create project at: https://console.cloud.google.com
- Enable Gmail API
- Create OAuth 2.0 credentials
- Add to `.env`:
  ```
  GOOGLE_CLIENT_ID=your-client-id
  GOOGLE_CLIENT_SECRET=your-client-secret
  GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
  ```

#### 3. Microsoft Azure (For Outlook integration)
- Register app at: https://portal.azure.com
- Configure Microsoft Graph API permissions
- Add to `.env`:
  ```
  MICROSOFT_CLIENT_ID=your-client-id
  MICROSOFT_CLIENT_SECRET=your-client-secret
  ```

#### 4. Pinecone (For semantic search)
- Sign up at: https://www.pinecone.io
- Create index
- Add to `.env`:
  ```
  PINECONE_API_KEY=your-api-key
  PINECONE_ENVIRONMENT=us-east-1-aws
  ```

#### 5. Twilio (For SMS/WhatsApp)
- Sign up at: https://www.twilio.com
- Get phone number
- Add to `.env`:
  ```
  TWILIO_ACCOUNT_SID=your-sid
  TWILIO_AUTH_TOKEN=your-token
  TWILIO_PHONE_NUMBER=your-number
  ```

#### 6. AWS S3 (For document storage)
- Create S3 bucket
- Create IAM user with S3 access
- Add to `.env`:
  ```
  AWS_ACCESS_KEY_ID=your-key
  AWS_SECRET_ACCESS_KEY=your-secret
  AWS_S3_BUCKET=your-bucket-name
  ```

### Optional Integrations

- **Zillow API**: Real estate property data
- **HubSpot**: CRM integration
- **Stripe**: Payment processing
- **Canva API**: Marketing material generation
- **Matterport**: Virtual tour integration

See `backend/.env.example` for complete configuration options.

## 📖 Core Features Implementation Status

### ✅ Phase 1: Foundation (Completed)
- [x] Project structure setup
- [x] PostgreSQL database with enterprise security
- [x] User authentication (JWT, OAuth ready)
- [x] RBAC and audit logging
- [x] AES-256 encryption for sensitive data
- [x] FastAPI backend with health checks
- [x] React frontend with Tailwind UI
- [x] State management and routing

### ✅ Phase 2: AI Agents (Completed)
- [x] Triage Agent (email classification and prioritization)
- [x] Draft Agent (personalized response generation)
- [x] Lead Qualification Agent (scoring and enrichment)
- [x] Negotiation Agent (offer analysis and suggestions)

### ✅ Phase 3: Integrations (Completed)
- [x] Gmail Integration (OAuth, read, send)
- [x] Outlook Integration (Microsoft Graph)
- [x] Twilio Integration (SMS/WhatsApp)
- [x] Vector Store (Pinecone for semantic search)

### 🚧 Phase 4: Email Management (In Progress)
- [ ] Email sync workers
- [ ] Real-time triage pipeline
- [ ] Inbox UI with filters
- [ ] Semantic search interface
- [ ] Thread grouping

### 🚧 Phase 5: Drafts & Automation (In Progress)
- [ ] Draft generation UI
- [ ] Voice style training
- [ ] Multi-variant drafts
- [ ] Approval workflow
- [ ] Automated follow-up sequences

### 🚧 Phase 6: Additional Features (Planned)
- [ ] Task and calendar automation
- [ ] Property dashboard
- [ ] Document intelligence (PDF processing)
- [ ] Analytics and insights
- [ ] Team collaboration
- [ ] Mobile app (PWA)
- [ ] Voice interface

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## 🚢 Deployment

### Backend (AWS/Heroku/Render)

```bash
# Build Docker image
docker build -t realinbox-api ./backend

# Deploy to your chosen platform
```

### Frontend (Vercel/Netlify)

```bash
cd frontend
npm run build

# Deploy dist/ folder to Vercel/Netlify
```

See individual README files in `backend/` and `frontend/` for detailed deployment instructions.

## 📊 Business Model

### Pricing Tiers

- **Solo Agent**: $29/month
  - 1 email account
  - 500 AI actions/month
  - Core features

- **Pro Agent**: $49/month
  - 3 email accounts
  - Unlimited AI actions
  - Advanced analytics
  - Voice mode

- **Team/Brokerage**: $149/month (up to 5 agents)
  - Shared inbox
  - Team collaboration
  - Admin dashboard

- **Enterprise**: Custom pricing
  - White-label
  - Dedicated support
  - SLA

### Target Metrics (12 months)

- 500 active users
- $100K ARR
- 70% DAU/MAU
- 90% AI accuracy
- <5% monthly churn

## 🔐 Security & Compliance

- ✅ AES-256 encryption for sensitive data
- ✅ OAuth 2.0 + JWT authentication
- ✅ Role-based access control (RBAC)
- ✅ Comprehensive audit logging
- ✅ Rate limiting and DDoS protection
- ✅ GDPR compliance (data export, right-to-delete)
- 🚧 SOC 2 compliance (planned)
- 🚧 HIPAA compliance (planned for healthcare clients)

## 🤝 Contributing

This is a proprietary project. For feature requests or bug reports, please contact the development team.

## 📝 Development Roadmap

### Month 1-2: MVP
- Complete email sync and triage
- Draft generation interface
- Beta testing with 50 agents

### Month 3-4: Full Feature Set
- Multi-channel (SMS, WhatsApp)
- Task automation
- Property dashboard
- Analytics

### Month 5-6: Scale & Monetize
- Stripe integration
- Marketing website
- Onboarding flow
- Beta → Paid conversion

### Month 7-12: Growth
- Mobile app
- Team features
- Advanced integrations (CRMs, MLS)
- Scale to 500+ users

## 📞 Support

- **Email**: support@realinbox.ai
- **Documentation**: https://docs.realinbox.ai (coming soon)
- **Status**: https://status.realinbox.ai (coming soon)

## 📄 License

Proprietary - All rights reserved. © 2025 RealInbox AI

---

## 🎓 Development Notes

### Using Cursor + Claude for Development

This project was built to be developed with Cursor IDE and Claude Sonnet 4.5. To continue development:

1. **Open project in Cursor**
2. **Use Claude for code generation**:
   - "Create a new email router with CRUD endpoints"
   - "Add pagination to the messages list endpoint"
   - "Build a React component for the email list view"

3. **Leverage AI agents**:
   - Test AI agents in isolation
   - Iterate on prompts for better results
   - Fine-tune based on real email data

### Next Immediate Tasks

1. **Email Sync Workers**: Implement Celery tasks for Gmail/Outlook sync
2. **Inbox UI**: Build the main inbox interface with filters
3. **Draft UI**: Create draft generation and editing interface
4. **Testing**: Write comprehensive test suites
5. **Documentation**: Create user guides and API docs

### Key Design Decisions

- **Monorepo**: Backend and frontend in same repo for easier development
- **API-First**: Backend exposes REST API, frontend is separate SPA
- **Multi-Tenancy**: User namespacing in vector DB and data isolation
- **Human-in-the-Loop**: AI suggests, humans approve (especially for sending emails)
- **Real Estate Focus**: Domain-specific prompts and workflows

---

**Built with ❤️ for real estate agents who deserve better inbox management**

