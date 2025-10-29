# Gmail Integration Testing Guide

This guide explains how to test the Gmail integration with a real Google account. This is **not required for Phase 1** - the integration tests use mocked Gmail API responses.

## Prerequisites

- Google Cloud Platform account
- Gmail account for testing
- Backend server running locally

## Step 1: Google Cloud Console Setup

### 1.1 Create a New Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name: "RealInbox AI Development"
4. Click "Create"

### 1.2 Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Gmail API" → "Enable"

### 1.3 Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" (for testing)
3. Fill in required fields:
   - **App name**: RealInbox AI (Development)
   - **User support email**: your-email@gmail.com
   - **Developer contact**: your-email@gmail.com
4. Click "Save and Continue"
5. **Scopes**: Click "Add or Remove Scopes"
   - Add these Gmail scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.modify`
     - `https://www.googleapis.com/auth/gmail.labels`
6. Click "Save and Continue"
7. **Test users**: Add your Gmail address for testing
8. Click "Save and Continue"

### 1.4 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Web application"
4. Name: "RealInbox Development Client"
5. **Authorized redirect URIs**: Add:
   ```
   http://localhost:8000/api/v1/integrations/gmail/callback
   ```
6. Click "Create"
7. **Save the credentials**:
   - Copy the Client ID
   - Copy the Client Secret

## Step 2: Update Backend Configuration

Update your `backend/.env` file:

```env
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/integrations/gmail/callback
```

Restart your backend server for changes to take effect.

## Step 3: Test OAuth Flow

### 3.1 Start Authorization

1. Make sure your backend is running (`python -m app.main`)
2. Navigate to: `http://localhost:8000/api/v1/docs`
3. Find the `/integrations/gmail/auth` endpoint
4. Click "Try it out" → "Execute"
5. Copy the `authorization_url` from the response
6. Paste it in your browser

### 3.2 Grant Permissions

1. Sign in with your test Gmail account
2. Review the permissions requested
3. Click "Continue" / "Allow"
4. You'll be redirected to the callback URL
5. The page should show a success message with your email account connected

### 3.3 Verify Email Account Created

Check that an `EmailAccount` record was created in your database:

```sql
SELECT * FROM email_accounts WHERE provider = 'gmail';
```

You should see:
- `email_address`: Your Gmail address
- `is_active`: true
- `encrypted_access_token`: Encrypted OAuth token
- `encrypted_refresh_token`: Encrypted refresh token

## Step 4: Test Email Sync

### 4.1 Trigger Manual Sync

Using the API docs (`/api/v1/docs`):

1. Find `/integrations/gmail/sync` endpoint
2. Click "Try it out"
3. Enter your `email_account_id` (from database)
4. Click "Execute"

OR using curl:

```bash
curl -X POST "http://localhost:8000/api/v1/integrations/gmail/sync?account_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4.2 Verify Sync Results

The sync should:
1. Fetch recent emails from Gmail
2. Create a `Contact` for each unique sender
3. Create a `CommunicationLog` entry for each email

Check the database:

```sql
-- View created contacts
SELECT id, first_name, last_name, email, lead_source 
FROM contacts 
WHERE lead_source = 'email'
ORDER BY created_at DESC;

-- View communication logs
SELECT id, contact_id, subject, from_address, occurred_at
FROM communication_logs
WHERE communication_type = 'email'
ORDER BY occurred_at DESC;
```

### 4.3 Test Timeline Display

1. Note a `contact_id` from the query above
2. Go to frontend: `http://localhost:5173/contacts/{contact_id}`
3. You should see the email(s) displayed in the timeline

## Step 5: Test Celery Background Sync (Optional)

### 5.1 Start Celery Worker

In a new terminal:

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

Note: Use `--pool=solo` on Windows

### 5.2 Trigger Background Sync

The system can automatically sync all active Gmail accounts:

```python
from app.tasks.email_sync_task import sync_gmail_account

# Queue a sync task
sync_gmail_account.delay(user_id=1, account_id=1)
```

Or via the scheduler (configured in `app/workers/celery_beat_schedule.py`):

```bash
# Start Celery Beat for scheduled tasks
celery -A app.workers.celery_app beat --loglevel=info
```

### 5.3 Monitor Sync Status

Watch the Celery worker logs to see:
- Email fetching progress
- Contact creation
- CommunicationLog entries
- AI processing tasks

## Troubleshooting

### "Invalid grant" Error

- **Cause**: Refresh token expired or revoked
- **Solution**: Re-authorize the account (Step 3)

### "Access token expired"

- **Cause**: Access token expired (expected after 1 hour)
- **Solution**: The system should auto-refresh using the refresh token
- **Manual fix**: Re-run the OAuth flow

### No Emails Synced

- **Check**: Does your test Gmail account have recent emails?
- **Query filter**: By default, sync fetches `is:unread OR newer_than:1d`
- **Modify query**: Edit `email_sync_task.py` line 87 to fetch all emails:
  ```python
  query="in:inbox"
  ```

### Contacts Not Created

- **Check logs**: Look for errors in contact creation
- **Verify**: Emails have valid sender addresses
- **Database**: Check `contacts` table for created records

### Rate Limiting

Gmail API has quotas:
- **Free tier**: 250 quota units per user per second
- **Read operations**: 5 units each
- **For heavy testing**: Consider upgrading your Google Cloud project

## Security Notes

⚠️ **IMPORTANT**:

- Never commit OAuth credentials to version control
- Use separate Google Cloud projects for dev/staging/production
- Rotate credentials regularly
- Revoke test account access after testing
- In production, use service accounts or domain-wide delegation for enterprise

## Next Steps After Testing

Once you've verified the Gmail integration works:

1. **Add error handling**: Test what happens when access is revoked
2. **Test refresh flow**: Wait for token to expire and verify auto-refresh
3. **Test large syncs**: Try syncing an account with 1000+ emails
4. **Performance testing**: Measure sync speed and optimize if needed
5. **Webhook setup**: Consider using Gmail push notifications instead of polling

## Production Considerations

Before deploying to production:

- [ ] Update OAuth consent screen from "Testing" to "In production"
- [ ] Add proper error tracking (Sentry)
- [ ] Implement rate limit handling with exponential backoff
- [ ] Add webhook support for real-time email notifications
- [ ] Set up monitoring for sync failures
- [ ] Implement user notification for connection issues
- [ ] Add "Reconnect Gmail" flow in UI
- [ ] Store OAuth state parameter to prevent CSRF attacks
- [ ] Implement proper token encryption at rest

## Support Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 for Web Apps](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Gmail API Quotas](https://developers.google.com/gmail/api/reference/quota)
- [Google Cloud Support](https://cloud.google.com/support)

