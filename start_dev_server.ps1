# RealInbox AI - Development Server Startup Script
# Run this to start the backend server in development mode

Write-Host "🚀 Starting RealInbox AI Backend (Development Mode)" -ForegroundColor Green
Write-Host "Note: Using placeholder API keys - Replace with real keys tomorrow`n" -ForegroundColor Yellow

# Set all required environment variables
$env:SECRET_KEY = "dev-secret-key-minimum-32-characters-long-for-security"
$env:DATABASE_URL = "postgresql://realinbox:realinbox@localhost:5432/realinbox_db"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:JWT_SECRET_KEY = "dev-jwt-secret-key-change-in-production"
$env:ENCRYPTION_KEY = "dev-encryption-key-32-chars-long"
$env:ENCRYPTION_SALT = "dev-salt-16chars"
$env:ANTHROPIC_API_KEY = "sk-ant-placeholder-replace-with-real-key-tomorrow"
$env:ANTHROPIC_MODEL = "claude-sonnet-4.5-20250514"
$env:PINECONE_API_KEY = "placeholder-pinecone-key"
$env:PINECONE_ENVIRONMENT = "us-west1-gcp"
$env:PINECONE_INDEX_NAME = "realinbox-emails"
$env:GOOGLE_CLIENT_ID = "placeholder-google-client-id"
$env:GOOGLE_CLIENT_SECRET = "placeholder-google-secret"
$env:GOOGLE_REDIRECT_URI = "http://localhost:8000/api/v1/integrations/gmail/callback"
$env:MICROSOFT_CLIENT_ID = "placeholder-microsoft-id"
$env:MICROSOFT_CLIENT_SECRET = "placeholder-microsoft-secret"
$env:MICROSOFT_TENANT_ID = "common"
$env:MICROSOFT_REDIRECT_URI = "http://localhost:8000/api/v1/integrations/outlook/callback"
$env:TWILIO_ACCOUNT_SID = "placeholder-twilio-sid"
$env:TWILIO_AUTH_TOKEN = "placeholder-twilio-token"
$env:TWILIO_PHONE_NUMBER = "+15551234567"
$env:TWILIO_WHATSAPP_NUMBER = "+15551234567"
$env:AWS_ACCESS_KEY_ID = "placeholder-aws-key"
$env:AWS_SECRET_ACCESS_KEY = "placeholder-aws-secret"
$env:AWS_S3_BUCKET = "realinbox-dev-bucket"
$env:AWS_REGION = "us-east-1"
$env:CELERY_BROKER_URL = "redis://localhost:6379/0"
$env:CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:5173"

Write-Host "✅ Environment variables set" -ForegroundColor Green
Write-Host "📡 Starting server on http://localhost:8000`n" -ForegroundColor Cyan

# Navigate to backend directory
Set-Location backend

# Start the server
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

