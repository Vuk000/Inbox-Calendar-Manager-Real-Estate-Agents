#!/usr/bin/env python3
"""
Setup script to create .env file with secure keys
Run this script to generate the initial .env file for development
"""
import secrets
import os

def generate_env_file():
    """Generate .env file with secure keys and placeholder values"""
    
    # Generate secure keys
    secret_key = secrets.token_urlsafe(32)
    jwt_secret_key = secrets.token_urlsafe(32)
    encryption_key = secrets.token_hex(16)  # 32 chars
    encryption_salt = secrets.token_hex(8)   # 16 chars
    
    env_content = f"""# Application Settings
APP_NAME=RealInbox AI
APP_ENV=development
DEBUG=True
API_VERSION=v1
SECRET_KEY={secret_key}

# Database Configuration
DATABASE_URL=postgresql://realinbox_user:realinbox_password@localhost:5432/realinbox_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# JWT Authentication
JWT_SECRET_KEY={jwt_secret_key}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
ENCRYPTION_KEY={encryption_key}
ENCRYPTION_SALT={encryption_salt}

# AI - Anthropic Claude (placeholder - replace with real key)
ANTHROPIC_API_KEY=sk-ant-api03-placeholder-key-12345678901234567890123456789012345678901234567890123456789012345678901234567890
ANTHROPIC_MODEL=claude-sonnet-4.5-20250514
ANTHROPIC_MAX_TOKENS=4096

# Vector Database - Pinecone (placeholder - replace with real key)
PINECONE_API_KEY=placeholder-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=realinbox-emails

# Google Services (placeholder - replace with real credentials)
GOOGLE_CLIENT_ID=placeholder-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=placeholder-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/integrations/gmail/callback

# Microsoft Services (placeholder - replace with real credentials)
MICROSOFT_CLIENT_ID=placeholder-microsoft-client-id
MICROSOFT_CLIENT_SECRET=placeholder-microsoft-client-secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/integrations/outlook/callback

# Twilio (SMS/WhatsApp) (placeholder - replace with real credentials)
TWILIO_ACCOUNT_SID=placeholder-twilio-account-sid
TWILIO_AUTH_TOKEN=placeholder-twilio-auth-token
TWILIO_PHONE_NUMBER=+15551234567
TWILIO_WHATSAPP_NUMBER=+15551234567

# AWS S3 (placeholder - replace with real credentials)
AWS_ACCESS_KEY_ID=placeholder-aws-access-key-id
AWS_SECRET_ACCESS_KEY=placeholder-aws-secret-access-key
AWS_S3_BUCKET=placeholder-s3-bucket-name
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
RAPIDAPI_KEY=
YELP_API_KEY=
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=
SENTRY_DSN=

# AI Services - OpenAI (for Neighborhood Whisper NLP)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

# Google Cloud Vision (for VisionHome AI)
GOOGLE_APPLICATION_CREDENTIALS=

# Subscription Tier Limits (defaults)
FREE_TIER_VISION_SCANS=5
FREE_TIER_NEIGHBORHOOD_SEARCHES=10
SOLO_TIER_VISION_SCANS=50
SOLO_TIER_NEIGHBORHOOD_SEARCHES=100
PRO_TIER_VISION_SCANS=100
PRO_TIER_NEIGHBORHOOD_SEARCHES=500
"""
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        print(f"⚠️  .env file already exists at {env_path}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_path}")
        print("\n📝 IMPORTANT: Replace placeholder values with real API keys:")
        print("   - ANTHROPIC_API_KEY (get from Anthropic)")
        print("   - PINECONE_API_KEY (get from Pinecone)")
        print("   - GOOGLE_CLIENT_ID/SECRET (for Gmail integration)")
        print("   - MICROSOFT_CLIENT_ID/SECRET (for Outlook integration)")
        print("   - Other service credentials as needed")
        print("\n🔐 Secure keys (SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY, ENCRYPTION_SALT) have been generated automatically.")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        raise

if __name__ == "__main__":
    generate_env_file()

