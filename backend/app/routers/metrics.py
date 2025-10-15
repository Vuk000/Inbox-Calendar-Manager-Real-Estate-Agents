"""
Prometheus Metrics Router
Phase 5.4: Monitoring & Observability
"""
from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Metrics definitions
emails_triaged_counter = Counter(
    'realinbox_emails_triaged_total',
    'Total number of emails triaged by AI'
)

drafts_generated_counter = Counter(
    'realinbox_drafts_generated_total',
    'Total number of AI-generated drafts'
)

tasks_created_counter = Counter(
    'realinbox_tasks_created_total',
    'Total number of tasks created'
)

api_request_duration = Histogram(
    'realinbox_api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint', 'status']
)

ai_api_calls_counter = Counter(
    'realinbox_ai_api_calls_total',
    'Total Claude API calls',
    ['agent_type', 'status']
)

active_users_gauge = Gauge(
    'realinbox_active_users',
    'Number of currently active users'
)

websocket_connections_gauge = Gauge(
    'realinbox_websocket_connections',
    'Number of active WebSocket connections'
)

email_sync_duration = Histogram(
    'realinbox_email_sync_duration_seconds',
    'Email sync task duration in seconds',
    ['provider']
)


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.
    
    Exposes application metrics in Prometheus format.
    Access at: http://localhost:8000/metrics
    
    Metrics include:
    - Email triage counts
    - Draft generation counts
    - Task creation counts
    - API request durations
    - AI API call counts
    - Active users
    - WebSocket connections
    - Email sync durations
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# Helper functions to increment metrics
def record_email_triaged():
    """Record email triage event"""
    emails_triaged_counter.inc()


def record_draft_generated():
    """Record draft generation event"""
    drafts_generated_counter.inc()


def record_task_created():
    """Record task creation event"""
    tasks_created_counter.inc()


def record_ai_api_call(agent_type: str, success: bool = True):
    """
    Record AI API call.
    
    Args:
        agent_type: Type of agent (triage, draft, lead_qual)
        success: Whether call was successful
    """
    status = "success" if success else "error"
    ai_api_calls_counter.labels(agent_type=agent_type, status=status).inc()


def record_api_request(method: str, endpoint: str, duration: float, status_code: int):
    """
    Record API request metrics.
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        duration: Request duration in seconds
        status_code: HTTP status code
    """
    api_request_duration.labels(
        method=method,
        endpoint=endpoint,
        status=str(status_code)
    ).observe(duration)


def set_active_users(count: int):
    """Set active users gauge"""
    active_users_gauge.set(count)


def set_websocket_connections(count: int):
    """Set WebSocket connections gauge"""
    websocket_connections_gauge.set(count)


def record_email_sync(provider: str, duration: float):
    """
    Record email sync duration.
    
    Args:
        provider: Email provider (gmail, outlook)
        duration: Sync duration in seconds
    """
    email_sync_duration.labels(provider=provider).observe(duration)

