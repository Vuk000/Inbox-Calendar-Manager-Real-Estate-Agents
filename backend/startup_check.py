"""
Startup validation script - checks that all dependencies and config are correct
Run this before starting the application
"""
import sys
import os

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required. Current:", sys.version)
        return False
    print("✅ Python version OK:", sys.version.split()[0])
    return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ .env file not found! Copy .env.example to .env and configure it.")
        return False
    print("✅ .env file found")
    return True

def check_imports():
    """Check critical imports"""
    try:
        import fastapi
        print("✅ FastAPI installed")
    except ImportError:
        print("❌ FastAPI not installed. Run: pip install -r requirements.txt")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy installed")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        return False
    
    try:
        import anthropic
        print("✅ Anthropic SDK installed")
    except ImportError:
        print("❌ Anthropic SDK not installed")
        return False
    
    return True

def check_config():
    """Check configuration"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from app.config import settings
        
        # Check critical settings
        if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "your-anthropic-api-key":
            print("⚠️  ANTHROPIC_API_KEY not configured in .env")
            print("   Get one at: https://console.anthropic.com")
        else:
            print("✅ Anthropic API key configured")
        
        if not settings.DATABASE_URL:
            print("❌ DATABASE_URL not set")
            return False
        print("✅ Database URL configured")
        
        if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
            print("⚠️  SECRET_KEY not changed from default! Generate a secure key.")
        else:
            print("✅ SECRET_KEY configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def check_database_connection():
    """Check database connection"""
    try:
        from app.db import engine
        with engine.connect() as conn:
            print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running: docker-compose up -d postgres")
        return False

def check_redis_connection():
    """Check Redis connection"""
    try:
        import redis
        from app.config import settings
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("   Make sure Redis is running: docker-compose up -d redis")
        return False

def main():
    """Run all checks"""
    print("\n🔍 RealInbox AI - Startup Validation\n")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        (".env File", check_env_file),
        ("Python Packages", check_imports),
        ("Configuration", check_config),
        ("Database Connection", check_database_connection),
        ("Redis Connection", check_redis_connection),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("\n✅ All checks passed! You can start the application.")
        print("\nRun: python -m app.main")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before starting.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

