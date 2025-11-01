"""
Celery application configuration for background tasks
Optional - only initialized if Redis is available
"""
import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)

# Initialize Celery only if Redis is enabled
celery_app: Optional['Celery'] = None

try:
    if settings.REDIS_ENABLED:
        import redis
        from celery import Celery
        from celery.schedules import crontab
        
        # Test Redis connection
        try:
            redis_client = redis.from_url(settings.CELERY_BROKER_URL, socket_connect_timeout=2)
            redis_client.ping()
            logger.info("✅ Redis available - initializing Celery")
            
            # Initialize Celery
            celery_app = Celery(
                "realinbox",
                broker=settings.CELERY_BROKER_URL,
                backend=settings.CELERY_RESULT_BACKEND,
                include=[
                    "app.tasks.email_sync_task",
                ]
            )
            
            # Celery configuration
            celery_app.conf.update(
                task_serializer="json",
                accept_content=["json"],
                result_serializer="json",
                timezone="UTC",
                enable_utc=True,
                task_track_started=True,
                task_time_limit=300,  # 5 minutes max per task
                task_soft_time_limit=240,  # 4 minutes soft limit
                worker_prefetch_multiplier=4,
                worker_max_tasks_per_child=1000,
            )
            
            # Periodic tasks schedule
            celery_app.conf.beat_schedule = {
                "sync-all-gmail-accounts": {
                    "task": "app.workers.email_sync.sync_all_gmail_accounts",
                    "schedule": crontab(minute="*/5"),  # Every 5 minutes
                },
                "sync-all-outlook-accounts": {
                    "task": "app.workers.email_sync.sync_all_outlook_accounts",
                    "schedule": crontab(minute="*/5"),  # Every 5 minutes
                },
                # Relationship scoring tasks
                "update-all-relationship-scores": {
                    "task": "app.workers.relationship_scoring.update_all_active_contacts",
                    "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
                },
                "update-scores-recent-activity": {
                    "task": "app.workers.relationship_scoring.update_scores_for_recent_communications",
                    "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
                },
            }
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable - Celery disabled: {e}")
            logger.warning("Background tasks will not run. App will work without Celery.")
            celery_app = None
    else:
        logger.info("ℹ️ Redis disabled in config - Celery not initialized")
        celery_app = None
except ImportError:
    logger.warning("⚠️ Celery not installed - background tasks disabled")
    celery_app = None

if __name__ == "__main__":
    if celery_app:
        celery_app.start()
    else:
        print("❌ Celery not available. Redis must be running and enabled.")

