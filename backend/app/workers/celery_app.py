"""
Celery application configuration for background tasks
"""
from celery import Celery
from celery.schedules import crontab
from ..config import settings

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
        "task": "app.tasks.email_sync_task.sync_all_gmail_accounts",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "sync-all-outlook-accounts": {
        "task": "app.tasks.email_sync_task.sync_all_outlook_accounts",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
}

if __name__ == "__main__":
    celery_app.start()

