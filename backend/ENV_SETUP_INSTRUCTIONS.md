# Environment Setup Instructions

## ✅ Step 1: .env File Created

The `.env` file has been created at `backend/.env` with secure generated keys for:
- ✅ SECRET_KEY (generated)
- ✅ JWT_SECRET_KEY (generated)
- ✅ ENCRYPTION_KEY (generated)
- ✅ ENCRYPTION_SALT (generated)

## ⚠️ Step 2: Required API Credentials

Please update the following placeholders in `backend/.env` with your actual credentials:

### Critical for Server to Start:
1. **ANTHROPIC_API_KEY** (Required - must start with `sk-ant-`)
   - Get from: https://console.anthropic.com/
   - Current: `your-anthropic-api-key-here`

2. **PINECONE_API_KEY** (Required)
   - Get from: https://www.pinecone.io/
   - Current: `your-pinecone-api-key-here`

3. **PINECONE_ENVIRONMENT** (Required)
   - From Pinecone console
   - Current: `your-pinecone-environment-here`

4. **GOOGLE_CLIENT_ID** (Required for Gmail integration)
   - Get from: https://console.cloud.google.com/
   - Current: `your-google-client-id.apps.googleusercontent.com`

5. **GOOGLE_CLIENT_SECRET** (Required for Gmail integration)
   - From Google Cloud Console
   - Current: `your-google-client-secret`

6. **DATABASE_URL** (Required)
   - PostgreSQL connection string
   - Current: `postgresql://username:password@localhost:5432/realinbox_db`
   - **For testing**: Can use SQLite: `sqlite:///./realinbox_test.db`

7. **REDIS_URL** (Required for Celery)
   - Redis connection string
   - Current: `redis://localhost:6379/0`
   - **Note**: Redis must be running, or tests will use mock

### Optional (can be left as placeholders for Phase 1):
- MICROSOFT_CLIENT_ID / MICROSOFT_CLIENT_SECRET (Outlook integration)
- TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN (SMS integration)
- AWS credentials (File uploads)
- STRIPE_API_KEY (Payments)
- SENTRY_DSN (Error tracking)

## 🚀 Step 3: After Updating .env

Once you've added the real credentials:

```bash
# Test configuration loads
python -c "from app.config import settings; print('✅ Config loaded!')"

# Run database migrations
alembic upgrade head

# Start the server
python -m app.main
```

## 🧪 Alternative: Testing Without Full Services

For initial testing without external services, you can:

1. **Use SQLite instead of PostgreSQL**:
   ```
   DATABASE_URL=sqlite:///./realinbox_test.db
   ```

2. **Mock Celery** (tests will work without Redis running)

3. **Skip AI validation temporarily** by modifying `app/config.py` (not recommended for production)

The test suite uses in-memory SQLite and mocked services, so tests can run without real API credentials.

