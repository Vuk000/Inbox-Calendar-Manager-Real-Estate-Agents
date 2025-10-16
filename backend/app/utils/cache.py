"""
Redis caching utilities for performance optimization
"""
import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
import redis
from ..config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Redis client
try:
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Test connection
    redis_client.ping()
    logger.info("✅ Redis cache connected")
except Exception as e:
    logger.warning(f"Redis cache unavailable: {str(e)}")
    redis_client = None


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from function arguments.
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    # Create deterministic key from arguments
    key_data = f"{prefix}:{str(args)}:{sorted(kwargs.items())}"
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"realinbox:{prefix}:{key_hash}"


def cache_result(ttl: int = 3600, prefix: str = "default"):
    """
    Decorator to cache function results in Redis.
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
        prefix: Cache key prefix
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if redis_client is None:
                # No cache available, call function directly
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = get_cache_key(prefix, *args, **kwargs)
            
            try:
                # Try to get from cache
                cached = redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return json.loads(cached)
                
                # Cache miss - call function
                logger.debug(f"Cache MISS: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Store in cache
                if result is not None:
                    redis_client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result, default=str)  # Handle datetime etc
                    )
                
                return result
                
            except Exception as e:
                logger.error(f"Cache error: {str(e)}")
                # Fallback to direct call on cache error
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def invalidate_cache(prefix: str, *args, **kwargs):
    """
    Invalidate cached result.
    
    Args:
        prefix: Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
    """
    if redis_client is None:
        return
    
    cache_key = get_cache_key(prefix, *args, **kwargs)
    try:
        redis_client.delete(cache_key)
        logger.debug(f"Cache invalidated: {cache_key}")
    except Exception as e:
        logger.error(f"Cache invalidation error: {str(e)}")


def invalidate_pattern(pattern: str):
    """
    Invalidate all keys matching pattern.
    
    Args:
        pattern: Key pattern (e.g., "realinbox:triage:*")
    """
    if redis_client is None:
        return
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.debug(f"Cache invalidated {len(keys)} keys matching: {pattern}")
    except Exception as e:
        logger.error(f"Pattern invalidation error: {str(e)}")


def cache_email(email_id: int, email_data: dict, ttl: int = 3600):
    """
    Cache email data.
    
    Args:
        email_id: Email ID
        email_data: Email data dict
        ttl: Time to live in seconds
    """
    if redis_client is None:
        return
    
    try:
        cache_key = f"realinbox:email:{email_id}"
        redis_client.setex(cache_key, ttl, json.dumps(email_data, default=str))
    except Exception as e:
        logger.error(f"Email cache error: {str(e)}")


def get_cached_email(email_id: int) -> Optional[dict]:
    """
    Get cached email data.
    
    Args:
        email_id: Email ID
        
    Returns:
        Email data dict or None
    """
    if redis_client is None:
        return None
    
    try:
        cache_key = f"realinbox:email:{email_id}"
        cached = redis_client.get(cache_key)
        return json.loads(cached) if cached else None
    except Exception as e:
        logger.error(f"Email cache retrieval error: {str(e)}")
        return None


def cache_user_session(user_id: int, session_data: dict, ttl: int = 1800):
    """
    Cache user session data.
    
    Args:
        user_id: User ID
        session_data: Session data dict
        ttl: Time to live in seconds (30 min default)
    """
    if redis_client is None:
        return
    
    try:
        cache_key = f"realinbox:session:{user_id}"
        redis_client.setex(cache_key, ttl, json.dumps(session_data))
    except Exception as e:
        logger.error(f"Session cache error: {str(e)}")


def get_cached_session(user_id: int) -> Optional[dict]:
    """
    Get cached user session.
    
    Args:
        user_id: User ID
        
    Returns:
        Session data dict or None
    """
    if redis_client is None:
        return None
    
    try:
        cache_key = f"realinbox:session:{user_id}"
        cached = redis_client.get(cache_key)
        return json.loads(cached) if cached else None
    except Exception as e:
        logger.error(f"Session cache retrieval error: {str(e)}")
        return None

