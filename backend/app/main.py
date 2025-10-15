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
    print("🚀 Starting RealInbox AI...")
    init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down RealInbox AI...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered inbox manager for real estate agents",
    version="1.0.0",
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    lifespan=lifespan
)


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


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info"""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": f"/api/{settings.API_VERSION}/docs",
        "status": "operational"
    }


# Import and include routers
from .routers import auth, emails, drafts, tasks, analytics, properties, integrations, webhooks, payments, websocket as ws_router

app.include_router(auth.router, prefix=f"/api/{settings.API_VERSION}/auth", tags=["Authentication"])
app.include_router(emails.router, prefix=f"/api/{settings.API_VERSION}", tags=["Emails"])
app.include_router(drafts.router, prefix=f"/api/{settings.API_VERSION}", tags=["Drafts"])
app.include_router(tasks.router, prefix=f"/api/{settings.API_VERSION}", tags=["Tasks"])
app.include_router(analytics.router, prefix=f"/api/{settings.API_VERSION}", tags=["Analytics"])
app.include_router(properties.router, prefix=f"/api/{settings.API_VERSION}", tags=["Properties"])
app.include_router(integrations.router, prefix=f"/api/{settings.API_VERSION}", tags=["Integrations"])
app.include_router(webhooks.router, prefix=f"/api/{settings.API_VERSION}", tags=["Webhooks"])
app.include_router(payments.router, prefix=f"/api/{settings.API_VERSION}", tags=["Payments"])
app.include_router(ws_router.router, tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

