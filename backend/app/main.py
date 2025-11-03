"""
RealInbox AI - Main FastAPI Application
Enterprise-grade AI inbox manager for real estate agents
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sentry_sdk
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import settings
from .db import init_db
import time


# Initialize Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.APP_ENV,
        traces_sample_rate=0.1 if settings.APP_ENV == "production" else 1.0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Project Apex...")
    init_db()
    print("✅ Database initialized")
    
    # Setup audit logging event listeners
    from .security.audit import setup_audit_listeners
    setup_audit_listeners()
    print("✅ Audit listeners registered")
    
    # Verify password hashing is available
    try:
        from .security.encryption import hash_password
        hash_password("test")
        print("✅ Password hashing initialized")
    except Exception as e:
        print(f"⚠️ Password hashing warning: {e}")
    
    # Check Redis/Celery status
    from .workers.celery_app import celery_app
    if celery_app is None:
        print("ℹ️ Celery disabled (Redis optional)")
    else:
        print("✅ Celery available (background tasks enabled)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Project Apex...")


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app with comprehensive documentation
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    **RealInbox AI Pro** - Enterprise-grade AI inbox manager for real estate agents.
    
    ## Features
    
    ### Core Inbox Management
    - **Unified Inbox**: Manage multiple email accounts (Gmail, Outlook) in one place
    - **AI Email Triage**: Automatic categorization and prioritization using Claude Sonnet 4.5
    - **AI Draft Generation**: Generate personalized email responses with voice matching
    - **Smart Calendar**: AI-powered scheduling and calendar management
    
    ### VisionHome AI
    - **Computer Vision**: Property image analysis using Google Cloud Vision
    - **Virtual Renovations**: AI-powered renovation suggestions
    - **Property Matching**: Match properties using ML algorithms
    
    ### Neighborhood Whisper
    - **Fit Scores**: ML-powered neighborhood compatibility scoring
    - **Market Forecasts**: Predictive analytics for neighborhoods
    - **Eco-Values**: Environmental impact analysis
    
    ### CRM & Pipeline
    - **Contact Management**: Unified CRM with timeline tracking
    - **Transaction Pipeline**: Deal tracking from offer to closing
    - **Team Collaboration**: Shared inboxes and team workflows
    
    ### Security & Compliance
    - **JWT Authentication**: Secure token-based authentication
    - **RBAC**: Role-based access control
    - **AES-256 Encryption**: Bank-level security for sensitive data
    - **GDPR Compliant**: Full data privacy controls
    
    ## API Versioning
    
    All endpoints are versioned under `/api/v1/`. Use the version header for future compatibility.
    
    ## Authentication
    
    Most endpoints require JWT authentication. Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_access_token>
    ```
    
    ## Rate Limiting
    
    API requests are rate-limited:
    - 60 requests per minute
    - 1000 requests per hour
    
    ## WebSocket Support
    
    Real-time updates are available via WebSocket connections for:
    - New email notifications
    - AI draft completion
    - Task updates
    - Transaction status changes
    
    ## Support
    
    For API support, contact: support@realinbox.ai
    """,
    version="3.0.0",
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "RealInbox AI Pro Support",
        "email": "support@realinbox.ai",
    },
    license_info={
        "name": "Proprietary",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        },
        {
            "url": "https://api.realinbox.ai",
            "description": "Production server"
        }
    ] if settings.APP_ENV == "production" else [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Enhanced exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """Handle 404 Not Found errors"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": "Endpoint not found",
            "path": str(request.url.path),
            "method": request.method
        }
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: Exception):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "error": str(exc) if settings.DEBUG else "Invalid request format"
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle uncaught exceptions with proper error reporting.
    
    In production, detailed error messages are hidden for security.
    Errors are logged to Sentry if configured.
    """
    # Log error to Sentry if configured
    if settings.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.capture_exception(exc)
    
    # Log error details
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred",
            "path": str(request.url.path),
            "method": request.method
        }
    )


# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check API health status and dependencies",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "app": "RealInbox AI Pro",
                        "version": "3.0.0",
                        "environment": "production",
                        "database": "connected",
                        "redis": "connected",
                        "celery": "available"
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns the current health status of the API and its dependencies.
    Use this endpoint for monitoring, health checks, and status pages.
    """
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "3.0.0",
        "environment": settings.APP_ENV
    }
    
    # Check database connection
    try:
        from .db import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["database_error"] = str(e) if settings.DEBUG else "Connection failed"
    
    # Check Redis connection
    try:
        import redis
        if settings.REDIS_ENABLED:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "disabled"
    except Exception as e:
        health_status["redis"] = "disconnected"
        health_status["redis_error"] = str(e) if settings.DEBUG else "Connection failed"
    
    # Check Celery
    try:
        from .workers.celery_app import celery_app
        if celery_app is not None:
            health_status["celery"] = "available"
        else:
            health_status["celery"] = "disabled"
    except Exception:
        health_status["celery"] = "unavailable"
    
    return health_status


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Information",
    description="Get basic API information and available endpoints",
    responses={
        200: {
            "description": "API information",
            "content": {
                "application/json": {
                    "example": {
                        "app": "RealInbox AI Pro",
                        "version": "3.0.0",
                        "docs": "/api/v1/docs",
                        "status": "operational",
                        "endpoints": {
                            "auth": "/api/v1/auth",
                            "emails": "/api/v1/emails",
                            "vision": "/api/v1/vision",
                            "neighborhood": "/api/v1/neighborhood",
                            "calendar": "/api/v1/calendar"
                        }
                    }
                }
            }
        }
    }
)
async def root():
    """
    Root endpoint with API information.
    
    Returns basic information about the API including:
    - Application name and version
    - Documentation URLs
    - Service status
    - Available endpoint categories
    """
    return {
        "app": settings.APP_NAME,
        "version": "3.0.0",
        "docs": f"/api/{settings.API_VERSION}/docs",
        "redoc": f"/api/{settings.API_VERSION}/redoc",
        "openapi": f"/api/{settings.API_VERSION}/openapi.json",
        "status": "operational",
        "environment": settings.APP_ENV,
        "endpoints": {
            "auth": f"/api/{settings.API_VERSION}/auth",
            "emails": f"/api/{settings.API_VERSION}/emails",
            "drafts": f"/api/{settings.API_VERSION}/drafts",
            "tasks": f"/api/{settings.API_VERSION}/tasks",
            "calendar": f"/api/{settings.API_VERSION}/calendar",
            "vision": f"/api/{settings.API_VERSION}/vision",
            "neighborhood": f"/api/{settings.API_VERSION}/neighborhood",
            "contacts": f"/api/{settings.API_VERSION}/contacts",
            "transactions": f"/api/{settings.API_VERSION}/transactions",
            "teams": f"/api/{settings.API_VERSION}/teams",
            "analytics": f"/api/{settings.API_VERSION}/analytics",
            "subscription": f"/api/{settings.API_VERSION}/subscription",
            "websocket": f"/api/{settings.API_VERSION}/ws"
        }
    }


# Import and include routers
from .routers import (
    auth, emails, drafts, tasks, analytics, properties, integrations,
    webhooks, payments, privacy, metrics, health, websocket as ws_router,
    # New Project Apex routers
    contacts, teams, ai_actions, communications, transactions,
    # VisionHome AI & Neighborhood Whisper routers
    vision, neighborhood, subscription, calendar
)

app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(emails.router, prefix=f"/api/{settings.API_VERSION}", tags=["Emails"])
app.include_router(drafts.router, prefix=f"/api/{settings.API_VERSION}", tags=["Drafts"])
app.include_router(tasks.router, prefix=f"/api/{settings.API_VERSION}", tags=["Tasks"])
app.include_router(analytics.router, prefix=f"/api/{settings.API_VERSION}", tags=["Analytics"])
app.include_router(properties.router, prefix=f"/api/{settings.API_VERSION}", tags=["Properties"])
app.include_router(integrations.router, prefix=f"/api/{settings.API_VERSION}", tags=["Integrations"])
app.include_router(webhooks.router, prefix=f"/api/{settings.API_VERSION}", tags=["Webhooks"])
app.include_router(payments.router, prefix=f"/api/{settings.API_VERSION}", tags=["Payments"])
app.include_router(privacy.router, prefix=f"/api/{settings.API_VERSION}", tags=["Privacy & GDPR"])
app.include_router(metrics.router, tags=["Metrics"])
app.include_router(health.router)
app.include_router(ws_router.router, tags=["WebSocket"])

# Project Apex CRM routers
app.include_router(contacts.router, prefix=f"/api/{settings.API_VERSION}", tags=["CRM - Contacts"])
app.include_router(teams.router, prefix=f"/api/{settings.API_VERSION}", tags=["CRM - Teams"])
app.include_router(ai_actions.router, prefix=f"/api/{settings.API_VERSION}", tags=["CRM - AI Actions"])
app.include_router(communications.router, prefix=f"/api/{settings.API_VERSION}", tags=["CRM - Communications"])
app.include_router(transactions.router, prefix=f"/api/{settings.API_VERSION}", tags=["CRM - Transactions"])

# VisionHome AI & Neighborhood Whisper routers
app.include_router(vision.router, prefix=f"/api/{settings.API_VERSION}")
app.include_router(neighborhood.router, prefix=f"/api/{settings.API_VERSION}", tags=["Neighborhood Whisper"])
app.include_router(subscription.router, prefix=f"/api/{settings.API_VERSION}", tags=["Subscription"])
app.include_router(calendar.router, prefix=f"/api/{settings.API_VERSION}", tags=["Calendar"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

