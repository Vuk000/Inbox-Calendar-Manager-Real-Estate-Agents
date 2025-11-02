"""Application configuration management"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ValidationError
from typing import List
import os
import sys


class Settings(BaseSettings):
    """Application settings with environment variable support and strict validation"""
    
    # Application
    APP_NAME: str = "Project Apex - Real Estate CRM"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    SECRET_KEY: str = Field(..., min_length=32)
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis (Optional - required for caching and Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    REDIS_ENABLED: bool = True  # Set to False to disable Redis (app will work but caching/Celery disabled)
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Encryption
    ENCRYPTION_KEY: str
    ENCRYPTION_SALT: str
    
    # Anthropic Claude
    ANTHROPIC_API_KEY: str = Field(..., min_length=20)
    ANTHROPIC_MODEL: str = "claude-sonnet-4.5-20250514"
    ANTHROPIC_MAX_TOKENS: int = 4096
    
    @field_validator('ANTHROPIC_API_KEY')
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        if not v.startswith('sk-ant-'):
            raise ValueError('ANTHROPIC_API_KEY must start with sk-ant-')
        return v
    
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str = "realinbox-emails"
    
    # Google
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    # Microsoft
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_CLIENT_SECRET: str
    MICROSOFT_TENANT_ID: str = "common"
    MICROSOFT_REDIRECT_URI: str
    
    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    TWILIO_WHATSAPP_NUMBER: str
    
    # Twitter/X
    TWITTER_CLIENT_ID: str = ""
    TWITTER_CLIENT_SECRET: str = ""
    TWITTER_REDIRECT_URI: str = ""
    TWITTER_WEBHOOK_ENV: str = ""
    
    # Facebook / Messenger
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_REDIRECT_URI: str = ""
    FACEBOOK_PAGE_ID: str = ""
    FACEBOOK_VERIFY_TOKEN: str = ""
    
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET: str
    AWS_REGION: str = "us-east-1"
    
    # CRM
    HUBSPOT_API_KEY: str = ""
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    
    # Real Estate APIs
    ZILLOW_API_KEY: str = ""
    RAPIDAPI_KEY: str = ""
    YELP_API_KEY: str = ""
    
    # AI Services - OpenAI (for NLP in Neighborhood Whisper)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"  # Fast and cost-effective for NLP parsing
    
    # Google Cloud Vision (for VisionHome AI)
    GOOGLE_APPLICATION_CREDENTIALS: str = ""  # Path to service account JSON file
    
    # Marketing & Tours
    CANVA_API_KEY: str = ""
    MATTERPORT_API_KEY: str = ""
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    # Celery (Optional - requires Redis)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Localization
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: str = "en,es,fr"
    
    # Automation Defaults
    FOLLOW_UP_SCHEDULE_MINUTES: str = "1440,4320,10080,20160,43200"  # 1d,3d,7d,14d,30d
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,https://*.vercel.app"
    CORS_CREDENTIALS: bool = True
    
    # Stripe
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Subscription Tier Limits
    FREE_TIER_VISION_SCANS: int = 5  # Per month
    FREE_TIER_NEIGHBORHOOD_SEARCHES: int = 10  # Per month
    SOLO_TIER_VISION_SCANS: int = 50  # Per month
    SOLO_TIER_NEIGHBORHOOD_SEARCHES: int = 100  # Per month
    PRO_TIER_VISION_SCANS: int = 100  # Per month (or unlimited)
    PRO_TIER_NEIGHBORHOOD_SEARCHES: int = 500  # Per month (or unlimited)
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def supported_languages_list(self) -> List[str]:
        return [lang.strip() for lang in self.SUPPORTED_LANGUAGES.split(",") if lang.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance with validation
try:
    settings = Settings()
except ValidationError as e:
    print("❌ Configuration Error: Missing or invalid environment variables!")
    print("\nDetails:")
    for error in e.errors():
        field = error['loc'][0]
        msg = error['msg']
        print(f"  - {field}: {msg}")
    print("\n📝 Please check your .env file and ENV_TEMPLATE.md for required variables.")
    sys.exit(1)

