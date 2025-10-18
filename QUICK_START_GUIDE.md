# 🚀 Quick Start Guide - Phase 1 CRM

## Prerequisites
- PostgreSQL database running
- Redis running (for Celery)
- Node.js installed
- Python 3.9+ installed

## Step 1: Environment Setup

Create `backend/.env` file with these required variables:

```bash
# Core Settings
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/realinbox
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-jwt-secret

# Encryption
ENCRYPTION_KEY=your-32-byte-encryption-key
ENCRYPTION_SALT=your-salt

# AI Services
ANTHROPIC_API_KEY=your-anthropic-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-environment

# Email OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-secret
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/auth/microsoft/callback

# SMS (Optional for Phase 1)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
TWILIO_WHATSAPP_NUMBER=your-whatsapp-number

# Storage (Optional for Phase 1)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-bucket-name

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

See `backend/ENV_TEMPLATE.md` for full details.

## Step 2: Database Migration

```bash
cd backend
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 001_initial_schema -> 002_project_apex
```

Creates tables: `contacts`, `communication_logs`, `transactions`, `teams`, etc.

## Step 3: Start Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Verify at: http://localhost:8000/health

## Step 4: Start Celery Worker

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

## Step 5: Start Celery Beat (Periodic Tasks)

```bash
cd backend
celery -A app.workers.celery_app beat --loglevel=info
```

## Step 6: Start Frontend

```bash
cd frontend
npm install  # First time only
npm run dev
```

Access at: http://localhost:5173

## Step 7: Initial Testing

### 7.1 Register/Login
1. Go to http://localhost:5173/register
2. Create account: email, password, full name
3. Login

### 7.2 Connect Email (Optional but recommended)
1. Settings → Integrations
2. Click "Connect Gmail" or "Connect Outlook"
3. Complete OAuth flow
4. Wait 5 minutes for first sync (or trigger manually)

### 7.3 Test Contacts Page
1. Navigate to "Contacts" in sidebar
2. Should see contacts page (empty initially)

### 7.4 Test CSV Import
1. Click "Import CSV" button
2. Create test CSV:
   ```csv
   First Name,Last Name,Email,Phone,Company
   John,Doe,john@example.com,555-1234,Acme Corp
   Jane,Smith,jane@example.com,555-5678,Tech Inc
   ```
3. Upload and map fields
4. Verify import success
5. See contacts in table

### 7.5 Test Contact Detail
1. Click on any contact in table
2. View contact detail page with:
   - Contact header
   - Stats (should be zeros initially)
   - Timeline (empty initially)

### 7.6 Verify Auto-Contact Creation (If email connected)
1. Send test email to your connected account
2. Wait for sync (or trigger via backend)
3. Go to Contacts page
4. Find contact created from sender email
5. Click contact
6. See email in timeline!

## Step 8: Monitor Celery Tasks

### View Celery Logs
```bash
# Worker logs (in worker terminal)
# Should see: "Processed message X", "Auto-linked to contact Y"

# Beat logs (in beat terminal)
# Should see periodic tasks scheduling
```

### Manual Trigger (Testing)
```python
# In Python shell with backend context
from app.workers.relationship_scoring import bulk_update_relationship_scores
bulk_update_relationship_scores.delay(user_id=1, limit=50)
```

## Common Issues & Solutions

### Issue: Alembic migration fails
**Solution**: Check DATABASE_URL in .env, ensure PostgreSQL is running

### Issue: Celery worker won't start
**Solution**: Check REDIS_URL, ensure Redis is running: `redis-server`

### Issue: Frontend API calls fail
**Solution**: Check backend is running on port 8000, check CORS settings

### Issue: Email sync not working
**Solution**: 
1. Check OAuth credentials in .env
2. Verify email account connected in Settings
3. Check Celery worker logs for errors

### Issue: Contacts not auto-created
**Solution**:
1. Verify Celery worker is running
2. Check worker logs for errors
3. Ensure email sync task completed successfully

### Issue: Relationship scores are 0
**Solution**:
1. Wait for daily Celery Beat task (2 AM)
2. OR manually trigger scoring task
3. Scores need communications to calculate from

## Verify Everything Works

✅ Backend health check: http://localhost:8000/health  
✅ API docs: http://localhost:8000/api/v1/docs  
✅ Frontend loads: http://localhost:5173  
✅ Can login  
✅ Contacts page accessible  
✅ Can import CSV  
✅ Can view contact details  
✅ Timeline displays  

If all checked, **Phase 1 is fully operational!** 🎉

## Next Steps

1. **Connect real email accounts** and let auto-contact creation work
2. **Import your existing contact database** via CSV
3. **Monitor relationship scores** as they update daily
4. **Create test transactions** via API (frontend UI in Phase 2)
5. **Start planning Phase 2** features (Glass Pipeline, SMS, Landing Pages)

## API Endpoints Available

### Contacts
- `GET /api/v1/contacts` - List all contacts
- `GET /api/v1/contacts/{id}` - Get single contact
- `POST /api/v1/contacts` - Create contact
- `PUT /api/v1/contacts/{id}` - Update contact
- `DELETE /api/v1/contacts/{id}` - Delete contact
- `GET /api/v1/contacts/{id}/timeline` - Get timeline
- `POST /api/v1/contacts/import` - Import CSV

### Communications
- `GET /api/v1/communications` - List communications
- `GET /api/v1/communications/stats?contact_id=X` - Get stats

### Transactions
- `GET /api/v1/transactions` - List transactions
- `GET /api/v1/transactions/{id}` - Get transaction
- `POST /api/v1/transactions` - Create transaction
- `PUT /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `GET /api/v1/transactions/{id}/timeline` - Get timeline
- `GET /api/v1/transactions/stats` - Get pipeline stats

## Support

- Check `IMPLEMENTATION_COMPLETE.md` for full technical details
- Check `PHASE_1_IMPLEMENTATION_SUMMARY.md` for architecture overview
- Backend API docs: http://localhost:8000/api/v1/docs (interactive!)

---

**You're ready to build an empire!** 🚀

