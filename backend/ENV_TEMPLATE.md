# Environment Variables Template

Copy this content into `backend/.env` and fill in your actual values:

```bash
# RealInbox AI - Environment Configuration
# Application
APP_NAME=RealInbox AI
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
API_VERSION=v1

# Database
DATABASE_URL=postgresql://realinbox:password@localhost:5432/realinbox_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# JWT Authentication
JWT_SECRET_KEY=your-jwt-secret-key-here-generate-with-openssl-rand-hex-32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption (AES-256)
ENCRYPTION_KEY=your-32-char-encryption-key-here
ENCRYPTION_SALT=your-16-char-salt-here

# Anthropic Claude AI (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
ANTHROPIC_MODEL=claude-sonnet-4.5-20250514
ANTHROPIC_MAX_TOKENS=4096

# Pinecone Vector Database (Optional - for semantic search)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=realinbox-emails

# Google OAuth (for Gmail integration)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/integrations/gmail/callback

# Microsoft OAuth (for Outlook integration)
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/integrations/outlook/callback

# Twilio (for SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=+1234567890

# Twitter/X (Optional)
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
TWITTER_REDIRECT_URI=http://localhost:8000/api/v1/integrations/twitter/callback
TWITTER_WEBHOOK_ENV=production

# Facebook Messenger (Optional)
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
FACEBOOK_REDIRECT_URI=http://localhost:8000/api/v1/integrations/facebook/callback
FACEBOOK_PAGE_ID=
FACEBOOK_VERIFY_TOKEN=

# AWS S3 (for document storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=realinbox-documents
AWS_REGION=us-east-1

# CRM Integrations (Optional)
HUBSPOT_API_KEY=
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=

# Real Estate APIs (Optional)
ZILLOW_API_KEY=
RAPIDAPI_KEY=

# Marketing & Tours (Optional)
CANVA_API_KEY=
MATTERPORT_API_KEY=

# Monitoring (Optional)
SENTRY_DSN=

# Celery (Background Jobs)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Localization
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,es,fr

# Automation
FOLLOW_UP_SCHEDULE_MINUTES=1440,4320,10080,20160,43200

# CORS (Frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_CREDENTIALS=True

# Stripe Payments (Optional)
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=
```

## Quick Start

Generate secure keys:
```bash
# SECRET_KEY and JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# ENCRYPTION_KEY (32 characters)
python -c "import secrets; print(secrets.token_urlsafe(32)[:32])"

# ENCRYPTION_SALT (16 characters)
python -c "import secrets; print(secrets.token_urlsafe(16)[:16])"
```

