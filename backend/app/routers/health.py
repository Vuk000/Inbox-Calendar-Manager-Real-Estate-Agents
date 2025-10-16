"""
Comprehensive health check endpoints for monitoring
"""
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import redis
import logging

from ..db import get_db
from ..config import settings
from ..websocket.connection_manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_basic():
    """
    Basic health check - always returns 200 if app is running.
    Used by load balancers for liveness probe.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
async def health_liveness():
    """
    Liveness probe - checks if application is responsive.
    Returns 200 if app is alive, 503 if not.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/health/ready")
async def health_readiness(db: Session = Depends(get_db)):
    """
    Readiness probe - checks if app can serve traffic.
    Verifies database and Redis connectivity.
    Returns 200 if ready, 503 if not ready.
    """
    checks = {
        "database": False,
        "redis": False,
        "overall": False
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
    
    # Check Redis
    try:
        redis_client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        redis_client.ping()
        checks["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
    
    # Overall status
    checks["overall"] = checks["database"] and checks["redis"]
    
    status_code = status.HTTP_200_OK if checks["overall"] else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if checks["overall"] else "not_ready",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/health/detailed")
async def health_detailed(db: Session = Depends(get_db)):
    """
    Detailed health check - returns status of all services.
    Use for debugging and monitoring dashboards.
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.APP_ENV,
        "services": {}
    }
    
    # Database check
    try:
        result = db.execute(text("SELECT version()"))
        db_version = result.scalar()
        health_data["services"]["database"] = {
            "status": "up",
            "type": "postgresql",
            "version": str(db_version).split()[1] if db_version else "unknown"
        }
    except Exception as e:
        health_data["services"]["database"] = {
            "status": "down",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Redis check
    try:
        redis_client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        redis_info = redis_client.info()
        health_data["services"]["redis"] = {
            "status": "up",
            "version": redis_info.get("redis_version", "unknown"),
            "used_memory": redis_info.get("used_memory_human", "unknown"),
            "connected_clients": redis_info.get("connected_clients", 0)
        }
    except Exception as e:
        health_data["services"]["redis"] = {
            "status": "down",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # WebSocket connections
    try:
        ws_count = connection_manager.get_connection_count()
        health_data["services"]["websocket"] = {
            "status": "up",
            "active_connections": ws_count
        }
    except Exception as e:
        health_data["services"]["websocket"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    # Anthropic API check (don't call API, just check config)
    health_data["services"]["anthropic_claude"] = {
        "status": "configured" if settings.ANTHROPIC_API_KEY else "not_configured",
        "model": settings.ANTHROPIC_MODEL
    }
    
    # Pinecone check (don't call API, just check config)
    health_data["services"]["pinecone"] = {
        "status": "configured" if settings.PINECONE_API_KEY else "not_configured",
        "index": settings.PINECONE_INDEX_NAME
    }
    
    # Gmail integration check
    health_data["services"]["gmail"] = {
        "status": "configured" if settings.GOOGLE_CLIENT_ID else "not_configured"
    }
    
    # Outlook integration check
    health_data["services"]["outlook"] = {
        "status": "configured" if settings.MICROSOFT_CLIENT_ID else "not_configured"
    }
    
    # Overall status determination
    critical_services = ["database", "redis"]
    all_critical_up = all(
        health_data["services"].get(svc, {}).get("status") == "up" 
        for svc in critical_services
    )
    
    if not all_critical_up:
        health_data["status"] = "unhealthy"
    
    return health_data

