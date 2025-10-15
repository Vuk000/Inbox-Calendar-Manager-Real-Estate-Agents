# Environment Variables Template

Copy the configuration below to create your `.env` file in the `backend/` directory.

```env
# Application Settings
APP_NAME=RealInbox AI
APP_ENV=development
DEBUG=True
API_VERSION=v1
SECRET_KEY=your-secret-key-min-32-characters-long-change-this

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/realinbox_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# JWT Authentication
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
ENCRYPTION_KEY=your-encryption-key-32-characters
ENCRYPTION_SALT=your-salt-16chars

# AI - Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4.5-20250514
ANTHROPIC_MAX_TOKENS=4096

# Vector Database - Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=realinbox-emails

# Google Services
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/integrations/gmail/callback

# Microsoft Services
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/integrations/outlook/callback

# Twilio (SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+15551234567
TWILIO_WHATSAPP_NUMBER=+15551234567

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1

# Celery Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_CREDENTIALS=True

# Optional Services (leave empty if not using)
TWITTER_CLIENT_ID=
FACEBOOK_APP_ID=
HUBSPOT_API_KEY=
ZILLOW_API_KEY=
STRIPE_API_KEY=
SENTRY_DSN=
```

## Generating Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (exactly 32 characters)
python -c "import secrets; print(secrets.token_hex(16))"

# Generate ENCRYPTION_SALT (exactly 16 characters)
python -c "import secrets; print(secrets.token_hex(8))"
```

## Required vs Optional Variables

### Required (Application won't start without these):
- `SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `ENCRYPTION_KEY`
- `ENCRYPTION_SALT`
- `ANTHROPIC_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENVIRONMENT`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

### Required for Email Integration:
- `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` (for Gmail)
- `MICROSOFT_CLIENT_ID` + `MICROSOFT_CLIENT_SECRET` (for Outlook)

### Required for SMS/WhatsApp:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

### Optional (Features limited without):
- Twitter, Facebook, CRM, Zillow, Stripe, Sentry APIs

## Security Notes

⚠️ **IMPORTANT**:
- Never commit `.env` to version control
- Use strong, unique values for all keys
- Rotate keys regularly in production
- Use environment-specific values (dev/staging/prod)
- Store production secrets in secure vaults (AWS Secrets Manager, etc.)

