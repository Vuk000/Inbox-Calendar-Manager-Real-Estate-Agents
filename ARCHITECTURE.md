# 🏗️ RealInbox AI - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                   React + TypeScript                         │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Login/  │  │Dashboard │  │  Inbox   │  │  Drafts  │  │
│  │ Register │  │   Page   │  │   Page   │  │   Page   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Tasks   │  │Properties│  │Analytics │  │ Settings │  │
│  │   Page   │  │   Page   │  │   Page   │  │   Page   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                              │
│         Zustand State │ TanStack Query │ Axios               │
└─────────────────────────────────────────────────────────────┘
                              │
                         HTTP/REST API
                              │
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   API Routers                         │  │
│  │  /auth  │  /emails  │  /drafts  │  /tasks  │  /analytics│
│  └──────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              AI Agents Layer                          │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │  │
│  │  │ Triage  │ │  Draft  │ │  Lead   │ │  Nego-  │   │  │
│  │  │  Agent  │ │  Agent  │ │  Qual.  │ │ tiation │   │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             Integration Layer                         │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │  │
│  │  │ Gmail  │ │Outlook │ │ Twilio │ │Pinecone│       │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘       │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Security Layer                           │  │
│  │  Encryption │ JWT Auth │ RBAC │ Audit Logs           │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             Database Models (ORM)                     │  │
│  │  User │ EmailAccount │ Message │ Draft │ Property     │  │
│  │  Task │ Analytics │ AuditLog                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  PostgreSQL   │  │      Redis       │  │    Pinecone     │
│   Database    │  │    (Cache)       │  │  (Vector DB)    │
└───────────────┘  └──────────────────┘  └─────────────────┘
```

---

## Data Flow

### 1. Email Triage Flow

```
┌─────────────┐
│ Email Arrives│
│  (Gmail/    │
│   Outlook)  │
└──────┬──────┘
       │
       │ Webhook/Poll
       ▼
┌────────────────┐
│  Email Sync    │
│    Worker      │
│   (Celery)     │
└──────┬─────────┘
       │
       │ Store in DB (encrypted)
       ▼
┌────────────────┐
│  Message       │
│   Model        │
└──────┬─────────┘
       │
       │ Trigger AI
       ▼
┌────────────────┐
│ Triage Agent   │
│  (Claude API)  │
└──────┬─────────┘
       │
       │ Extract:
       │ - Priority (high/medium/low)
       │ - Category (offer, lead, etc.)
       │ - Entities (address, amounts)
       │ - Actions (reply, schedule)
       ▼
┌────────────────┐
│  Update DB     │
│  + Store in    │
│   Pinecone     │
└──────┬─────────┘
       │
       │ Real-time update
       ▼
┌────────────────┐
│  Frontend      │
│   Displays     │
│  Triaged Email │
└────────────────┘
```

### 2. Draft Generation Flow

```
┌─────────────┐
│ User clicks │
│ "Generate   │
│  Draft"     │
└──────┬──────┘
       │
       │ API Request
       ▼
┌────────────────┐
│ Draft Router   │
│  /drafts/      │
│   generate     │
└──────┬─────────┘
       │
       │ Fetch context:
       │ - Original email
       │ - Thread history
       │ - User style examples
       │ - CRM data (if any)
       ▼
┌────────────────┐
│  Draft Agent   │
│  (Claude API)  │
└──────┬─────────┘
       │
       │ Generate 1-3 variants
       │ with personalization
       ▼
┌────────────────┐
│  Store Drafts  │
│  in Database   │
└──────┬─────────┘
       │
       │ Return to frontend
       ▼
┌────────────────┐
│  Draft Editor  │
│  UI Component  │
│  (User reviews,│
│   edits, sends)│
└────────────────┘
```

### 3. Lead Qualification Flow

```
┌─────────────┐
│ Lead Email  │
│  Arrives    │
└──────┬──────┘
       │
       │ Detected as "lead" category
       ▼
┌────────────────┐
│ Lead Qual      │
│   Agent        │
│ (Claude API)   │
└──────┬─────────┘
       │
       │ Extract & Score:
       │ - Budget: $300K-400K
       │ - Timeline: 3 months
       │ - Location: Downtown
       │ - Score: 85 (HOT)
       ▼
┌────────────────┐
│  Create CRM    │
│    Entry       │
│  (HubSpot)     │
└──────┬─────────┘
       │
       │ Auto-generate
       │ qualification questions
       ▼
┌────────────────┐
│  Draft Agent   │
│  creates reply │
└──────┬─────────┘
       │
       │ Present to user
       ▼
┌────────────────┐
│  Dashboard     │
│  shows lead in │
│ "Recent Leads" │
└────────────────┘
```

---

## Database Schema

### Core Tables

```
┌──────────────────────────────────────────────────────────┐
│                         USERS                            │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ email (unique)                                           │
│ hashed_password                                          │
│ full_name                                                │
│ role (admin/agent/team_member)                           │
│ subscription_tier (free_trial/solo/pro/team/enterprise) │
│ subscription_status                                      │
│ ai_actions_this_month                                    │
│ settings (JSON)                                          │
│ created_at, updated_at                                   │
└──────────────────────────────────────────────────────────┘
                        │
                        │ 1:N
                        ▼
┌──────────────────────────────────────────────────────────┐
│                    EMAIL_ACCOUNTS                        │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ user_id (FK)                                             │
│ provider (gmail/outlook)                                 │
│ email_address                                            │
│ encrypted_access_token                                   │
│ encrypted_refresh_token                                  │
│ sync_status (idle/syncing/error)                         │
│ last_sync_at                                             │
│ created_at, updated_at                                   │
└──────────────────────────────────────────────────────────┘
                        │
                        │ 1:N
                        ▼
┌──────────────────────────────────────────────────────────┐
│                       MESSAGES                           │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ email_account_id (FK)                                    │
│ external_id (Gmail/Outlook ID)                           │
│ thread_id                                                │
│ source (email/sms/whatsapp)                              │
│ sender_email, sender_name                                │
│ subject                                                  │
│ encrypted_body                                           │
│ body_preview                                             │
│ priority (high/medium/low) ← AI                          │
│ category (offer/lead/inspection) ← AI                    │
│ urgency_score (0-100) ← AI                               │
│ sentiment_score (-1 to 1) ← AI                           │
│ entities (JSON) ← AI extracted                           │
│ suggested_actions (JSON) ← AI                            │
│ vector_id (Pinecone reference)                           │
│ property_id (FK, optional)                               │
│ received_at, processed_at                                │
└──────────────────────────────────────────────────────────┘
                        │
                        │ 1:N
                        ▼
┌──────────────────────────────────────────────────────────┐
│                        DRAFTS                            │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ user_id (FK)                                             │
│ message_id (FK)                                          │
│ subject                                                  │
│ generated_content ← AI generated                         │
│ final_content (after human edits)                        │
│ confidence_score (0-1)                                   │
│ variant_number (1, 2, 3)                                 │
│ approval_status (pending/approved/edited/rejected/sent)  │
│ human_edits (JSON for learning)                          │
│ context_data (JSON)                                      │
│ generated_at, reviewed_at, sent_at                       │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                     PROPERTIES                           │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ address                                                  │
│ city, state, zip_code                                    │
│ mls_id (unique)                                          │
│ property_type (house/condo/land)                         │
│ bedrooms, bathrooms, square_feet                         │
│ list_price, sale_price                                   │
│ transaction_type (buying/selling)                        │
│ transaction_status (active/pending/closed)               │
│ listing_date, offer_date, closing_date                   │
│ document_urls (JSON)                                     │
│ metadata (JSON)                                          │
│ created_at, updated_at                                   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                        TASKS                             │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ user_id (FK)                                             │
│ message_id (FK, optional)                                │
│ property_id (FK, optional)                               │
│ task_type (showing/inspection/deadline/call)             │
│ title, description                                       │
│ due_date, due_time                                       │
│ status (todo/in_progress/done/cancelled)                 │
│ priority (low/medium/high)                               │
│ calendar_event_id (Google Calendar)                      │
│ is_completed, completed_at                               │
│ created_at, updated_at                                   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                      ANALYTICS                           │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ user_id (FK)                                             │
│ metric_type (emails_processed, time_saved, leads...)     │
│ metric_value                                             │
│ metric_unit (hours, count, percentage)                   │
│ metadata (JSON)                                          │
│ date, week_start, month_start                            │
│ created_at                                               │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                     AUDIT_LOGS                           │
├──────────────────────────────────────────────────────────┤
│ id (PK)                                                  │
│ user_id (FK)                                             │
│ action (login, read_email, send_email, delete_data...)  │
│ resource_type (email, draft, task)                       │
│ resource_id                                              │
│ description                                              │
│ metadata (JSON)                                          │
│ ip_address, user_agent                                   │
│ status (success/failure)                                 │
│ timestamp                                                │
└──────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Encryption Flow

```
┌────────────────┐
│  Sensitive     │
│  Data Input    │
│ (OAuth token,  │
│  email body)   │
└───────┬────────┘
        │
        │ Python app
        ▼
┌────────────────┐
│ encrypt_data() │
│  (AES-256)     │
│ + PBKDF2 KDF   │
└───────┬────────┘
        │
        │ Base64 encoded
        ▼
┌────────────────┐
│  PostgreSQL    │
│  (encrypted    │
│   at rest)     │
└───────┬────────┘
        │
        │ On read
        ▼
┌────────────────┐
│ decrypt_data() │
│  (AES-256)     │
└───────┬────────┘
        │
        │ Plaintext (in memory only)
        ▼
┌────────────────┐
│  Use in app    │
│  (never logged)│
└────────────────┘
```

### Authentication Flow

```
┌──────────────┐
│ User enters  │
│ email/pwd    │
└──────┬───────┘
       │
       │ POST /auth/login
       ▼
┌──────────────────┐
│  FastAPI         │
│  Auth Router     │
└──────┬───────────┘
       │
       │ 1. Hash check (bcrypt)
       ▼
┌──────────────────┐
│  verify_password │
└──────┬───────────┘
       │
       │ 2. Generate tokens
       ▼
┌──────────────────┐
│  JWT Handler     │
│  - Access token  │
│    (30 min)      │
│  - Refresh token │
│    (7 days)      │
└──────┬───────────┘
       │
       │ 3. Return to client
       ▼
┌──────────────────┐
│  Frontend stores │
│  in localStorage │
│  (via Zustand)   │
└──────┬───────────┘
       │
       │ 4. Every API request
       ▼
┌──────────────────┐
│  Axios adds      │
│  Authorization:  │
│  Bearer <token>  │
└──────┬───────────┘
       │
       │ 5. Backend verifies
       ▼
┌──────────────────┐
│  get_current_user│
│  dependency      │
└──────┬───────────┘
       │
       │ If expired (401)
       ▼
┌──────────────────┐
│  Auto refresh    │
│  using refresh   │
│  token           │
└──────────────────┘
```

---

## AI Agent Architecture

### Agent Structure

```
┌──────────────────────────────────────────────────────────┐
│                    AI Agent Pattern                      │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  1. Input Processing                               │ │
│  │     - Receive email/data                           │ │
│  │     - Clean and format                             │ │
│  │     - Extract context                              │ │
│  └────────────────────────────────────────────────────┘ │
│                         │                                │
│                         ▼                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  2. Prompt Construction                            │ │
│  │     - System prompt (role definition)              │ │
│  │     - User prompt (task + context)                 │ │
│  │     - Few-shot examples (if needed)                │ │
│  └────────────────────────────────────────────────────┘ │
│                         │                                │
│                         ▼                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  3. Claude API Call                                │ │
│  │     - anthropic.messages.create()                  │ │
│  │     - Model: claude-sonnet-4.5                     │ │
│  │     - Max tokens: 4096                             │ │
│  │     - Temperature: 0.5-0.7                         │ │
│  └────────────────────────────────────────────────────┘ │
│                         │                                │
│                         ▼                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  4. Response Parsing                               │ │
│  │     - Extract JSON from response                   │ │
│  │     - Validate structure                           │ │
│  │     - Handle errors                                │ │
│  └────────────────────────────────────────────────────┘ │
│                         │                                │
│                         ▼                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  5. Fallback Logic (if AI fails)                   │ │
│  │     - Rule-based classification                    │ │
│  │     - Keyword matching                             │ │
│  │     - Return best-effort result                    │ │
│  └────────────────────────────────────────────────────┘ │
│                         │                                │
│                         ▼                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │  6. Output Formatting                              │ │
│  │     - Add metadata (timestamp, model version)      │ │
│  │     - Return structured data                       │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────────────────┐
│                        FRONTEND                          │
│                    (Vercel/Netlify)                      │
│                                                          │
│  - React app built with Vite                            │
│  - CDN for static assets                                │
│  - Automatic SSL/TLS                                    │
│  - Global edge network                                  │
└──────────────┬──────────────────────────────────────────┘
               │
               │ HTTPS
               ▼
┌─────────────────────────────────────────────────────────┐
│                      LOAD BALANCER                       │
│                    (AWS ELB / Nginx)                     │
│                                                          │
│  - SSL termination                                      │
│  - Health checks                                        │
│  - Auto-scaling trigger                                 │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│                    BACKEND SERVERS                       │
│                   (AWS EC2 / Render)                     │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   FastAPI    │  │   FastAPI    │  │   FastAPI    │ │
│  │  Instance 1  │  │  Instance 2  │  │  Instance N  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  - Auto-scaling based on CPU/memory                     │
│  - Docker containers                                    │
│  - Environment variables from secrets manager           │
└─────────────┬────────────────────┬────────────────┬─────┘
              │                    │                │
              ▼                    ▼                ▼
┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐
│   PostgreSQL     │  │      Redis       │  │  Pinecone   │
│   (AWS RDS)      │  │ (AWS ElastiCache)│  │   (Cloud)   │
│                  │  │                  │  │             │
│ - Multi-AZ       │  │ - Cluster mode   │  │ - Serverless│
│ - Auto backup    │  │ - Persistence    │  │             │
│ - Encryption     │  │ - Pub/Sub        │  │             │
└──────────────────┘  └──────────────────┘  └─────────────┘

┌─────────────────────────────────────────────────────────┐
│                   BACKGROUND WORKERS                     │
│                      (Celery)                            │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Email Sync   │  │ AI Process   │  │ Scheduled    │ │
│  │   Worker     │  │   Worker     │  │   Tasks      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  - Separate from web servers                            │
│  - Auto-scaling based on queue length                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Anthropic  │  │   Google     │  │   Twilio     │ │
│  │  Claude API  │  │  Gmail API   │  │     API      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │    AWS S3    │  │    Stripe    │  │    Sentry    │ │
│  │  (Storage)   │  │  (Payments)  │  │ (Monitoring) │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Performance Considerations

### Optimization Strategies

1. **Database Queries**
   - Indexes on frequently queried fields (user_id, priority, category)
   - Connection pooling (20 connections)
   - Query optimization with SQLAlchemy

2. **Caching**
   - Redis for:
     - User sessions (JWT)
     - API rate limits
     - Frequently accessed data (user settings)
     - AI agent responses (deduplicate similar queries)

3. **AI API Costs**
   - Cache similar email analyses
   - Batch processing where possible
   - Fallback to rule-based for simple cases
   - Monitor usage per user (stay within budget)

4. **Vector Search**
   - Index optimization in Pinecone
   - Namespacing by user for faster queries
   - Pre-compute embeddings during email ingestion

5. **Frontend**
   - Code splitting by route
   - Lazy loading images
   - Virtualized lists for long email threads
   - Debounced search input
   - Optimistic UI updates

---

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────┐
│                      MONITORING                          │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Sentry (Error Tracking)                           │ │
│  │  - Capture exceptions                              │ │
│  │  - Stack traces                                    │ │
│  │  - User context                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Application Metrics                               │ │
│  │  - API response times                              │ │
│  │  - AI agent performance                            │ │
│  │  - Database query times                            │ │
│  │  - Queue lengths                                   │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Business Metrics                                  │ │
│  │  - User signups                                    │ │
│  │  - Email processing volume                         │ │
│  │  - AI actions per user                             │ │
│  │  - Conversion rates                                │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Audit Logs                                        │ │
│  │  - All user actions                                │ │
│  │  - Data access                                     │ │
│  │  - Security events                                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Scaling Plan

### Stage 1: 0-100 Users
- Single backend server
- Single PostgreSQL instance
- Redis instance
- Pinecone free tier

### Stage 2: 100-500 Users
- 2-3 backend servers with load balancer
- PostgreSQL with read replicas
- Redis cluster
- Pinecone paid tier
- Separate worker servers

### Stage 3: 500-2000 Users
- Auto-scaling backend (5-10 servers)
- Multi-AZ PostgreSQL
- Redis Cluster with persistence
- CDN for static assets
- Multiple worker pools
- Database sharding considerations

### Stage 4: 2000+ Users
- Microservices architecture
- Database sharding by user_id
- Separate services for:
  - Auth
  - Email processing
  - AI agents
  - Analytics
- Message queue (RabbitMQ/Kafka)
- Multi-region deployment

---

**This architecture is designed for:**
- ✅ Scalability (handle 10K+ users)
- ✅ Security (enterprise-grade)
- ✅ Performance (<2s API response time)
- ✅ Reliability (99.9% uptime)
- ✅ Maintainability (clean separation of concerns)
- ✅ Cost-efficiency (start small, scale as needed)

