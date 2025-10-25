"""
Enhanced Analytics Router - Productivity and ROI Metrics
Phase 4.4: Analytics Dashboard Implementation
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..dependencies import get_db
from ..models.user import User
from ..models.communication_log import CommunicationLog, CommunicationType
from ..models.task import Task, TaskStatus
from ..models.draft import Draft
from ..dependencies import get_current_active_user
from ..shared.types import ProductivityMetrics, ROIMetrics

router = APIRouter()


@router.get("/metrics/productivity", response_model=ProductivityMetrics)
async def get_productivity_metrics(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get productivity metrics for the user.
    
    Args:
        timeframe: Time period (7d, 30d, 90d, 1y)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ProductivityMetrics with emails triaged, time saved, etc.
    """
    # Calculate date range
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map.get(timeframe, 30)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get user's email accounts
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    # Emails triaged
    emails_triaged = 0
    if account_ids:
        emails_triaged = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.processed_at >= start_date,
            Message.processed_at.isnot(None)
        ).count()
    
    # Time saved calculation (est. 2 minutes per email for triage)
    time_saved_hours = round((emails_triaged * 2) / 60, 2)
    
    # Lead conversion rate
    leads_count = 0
    leads_converted = 0
    if account_ids:
        leads_count = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.category == MessageCategory.LEAD,
            Message.processed_at >= start_date
        ).count()
        
        # Count leads that resulted in tasks (proxy for conversion)
        leads_converted = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.category == MessageCategory.LEAD,
            Message.processed_at >= start_date,
            Message.tasks.any()
        ).count()
    
    lead_conversion_rate = round(leads_converted / leads_count, 3) if leads_count > 0 else 0.0
    
    # Average response time
    drafts_with_approval = db.query(Draft).filter(
        Draft.user_id == current_user.id,
        Draft.approved_at.isnot(None),
        Draft.generated_at >= start_date
    ).all()
    
    total_response_time = 0
    for draft in drafts_with_approval:
        if draft.approved_at and draft.generated_at:
            delta = draft.approved_at - draft.generated_at
            total_response_time += delta.total_seconds() / 3600  # Convert to hours
    
    response_time_avg_hours = round(
        total_response_time / len(drafts_with_approval), 2
    ) if drafts_with_approval else 0.0
    
    return ProductivityMetrics(
        emails_triaged=emails_triaged,
        time_saved_hours=time_saved_hours,
        lead_conversion_rate=lead_conversion_rate,
        response_time_avg_hours=response_time_avg_hours,
        period=timeframe
    )


@router.get("/metrics/roi", response_model=ROIMetrics)
async def get_roi_metrics(
    hourly_rate: float = Query(50.0, description="Agent's hourly rate in USD"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Calculate ROI for the subscription.
    
    Args:
        hourly_rate: Agent's hourly rate (default $50/hour)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ROIMetrics with monthly ROI calculation
    """
    # Get productivity metrics for last 30 days
    metrics = await get_productivity_metrics("30d", current_user, db)
    
    # Subscription cost per month
    tier_costs = {
        "solo": 29.0,
        "professional": 49.0,
        "enterprise": 149.0
    }
    subscription_cost = tier_costs.get(current_user.subscription_tier, 29.0)
    
    # Calculate value (time saved * hourly rate)
    time_value = metrics.time_saved_hours * hourly_rate
    
    # Net ROI
    roi_monthly = round(time_value - subscription_cost, 2)
    net_value = round(time_value, 2)
    
    return ROIMetrics(
        roi_monthly=roi_monthly,
        time_saved_hours=metrics.time_saved_hours,
        hourly_rate=hourly_rate,
        subscription_cost=subscription_cost,
        net_value=net_value
    )


class EmailCategoryCount(BaseModel):
    """Email count by category"""
    category: str
    count: int
    percentage: float


@router.get("/metrics/email-distribution", response_model=List[EmailCategoryCount])
async def get_email_distribution(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get email distribution by category.
    
    Args:
        days: Number of days to analyze
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of category counts for chart visualization
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    if not account_ids:
        return []
    
    # Query category counts
    results = db.query(
        Message.category,
        func.count(Message.id).label('count')
    ).filter(
        Message.email_account_id.in_(account_ids),
        Message.processed_at >= start_date
    ).group_by(Message.category).all()
    
    # Calculate total
    total = sum(row.count for row in results)
    
    # Build response
    distribution = []
    for row in results:
        distribution.append(EmailCategoryCount(
            category=row.category.value if hasattr(row.category, 'value') else str(row.category),
            count=row.count,
            percentage=round((row.count / total) * 100, 1) if total > 0 else 0.0
        ))
    
    return distribution


class DailyEmailCount(BaseModel):
    """Daily email count"""
    date: str
    count: int
    high_priority: int
    leads: int


@router.get("/metrics/email-timeline", response_model=List[DailyEmailCount])
async def get_email_timeline(
    days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get daily email counts for timeline chart.
    
    Args:
        days: Number of days to include
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of daily counts for line chart
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    # Generate date range
    timeline = []
    for i in range(days):
        day_date = (datetime.utcnow() - timedelta(days=days - i - 1)).date()
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())
        
        # Count emails for this day
        day_count = 0
        high_priority_count = 0
        leads_count = 0
        
        if account_ids:
            day_count = db.query(Message).filter(
                Message.email_account_id.in_(account_ids),
                Message.processed_at >= day_start,
                Message.processed_at <= day_end
            ).count()
            
            high_priority_count = db.query(Message).filter(
                Message.email_account_id.in_(account_ids),
                Message.processed_at >= day_start,
                Message.processed_at <= day_end,
                Message.priority == MessagePriority.HIGH
            ).count()
            
            leads_count = db.query(Message).filter(
                Message.email_account_id.in_(account_ids),
                Message.processed_at >= day_start,
                Message.processed_at <= day_end,
                Message.category == MessageCategory.LEAD
            ).count()
        
        timeline.append(DailyEmailCount(
            date=day_date.isoformat(),
            count=day_count,
            high_priority=high_priority_count,
            leads=leads_count
        ))
    
    return timeline


class ChurnRiskScore(BaseModel):
    """Churn risk assessment"""
    risk_score: float  # 0-100, higher = more risk
    risk_level: str  # low, medium, high
    factors: List[str]
    recommendations: List[str]


@router.get("/metrics/churn-risk", response_model=ChurnRiskScore)
async def get_churn_risk(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Calculate churn risk based on usage patterns.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ChurnRiskScore with risk assessment
    """
    # Calculate usage metrics
    last_7_days = datetime.utcnow() - timedelta(days=7)
    last_30_days = datetime.utcnow() - timedelta(days=30)
    
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    # Recent activity
    emails_last_7_days = 0
    drafts_last_7_days = 0
    tasks_last_7_days = 0
    
    if account_ids:
        emails_last_7_days = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.processed_at >= last_7_days
        ).count()
    
    drafts_last_7_days = db.query(Draft).filter(
        Draft.user_id == current_user.id,
        Draft.generated_at >= last_7_days
    ).count()
    
    tasks_last_7_days = db.query(Task).filter(
        Task.created_by == current_user.id,
        Task.created_at >= last_7_days
    ).count()
    
    # Calculate risk score (0-100)
    risk_score = 0
    factors = []
    
    if emails_last_7_days == 0:
        risk_score += 40
        factors.append("No emails processed in 7 days")
    elif emails_last_7_days < 10:
        risk_score += 20
        factors.append("Low email processing activity")
    
    if drafts_last_7_days == 0:
        risk_score += 30
        factors.append("No drafts generated recently")
    
    if tasks_last_7_days == 0:
        risk_score += 15
        factors.append("No tasks created recently")
    
    # Last login check
    if hasattr(current_user, 'last_login_at') and current_user.last_login_at:
        days_since_login = (datetime.utcnow() - current_user.last_login_at).days
        if days_since_login > 7:
            risk_score += 15
            factors.append(f"Last login {days_since_login} days ago")
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Recommendations
    recommendations = []
    if risk_score >= 70:
        recommendations.append("Consider reaching out to check if user needs help")
        recommendations.append("Offer personalized onboarding session")
    elif risk_score >= 40:
        recommendations.append("Send engagement email with tips")
        recommendations.append("Highlight unused features")
    else:
        recommendations.append("User is engaged - maintain quality")
    
    return ChurnRiskScore(
        risk_score=min(risk_score, 100),
        risk_level=risk_level,
        factors=factors if factors else ["User is actively engaged"],
        recommendations=recommendations
    )


# TODO: Add predictive analytics (ML model for lead scoring)
# TODO: Implement anomaly detection (unusual email patterns)
# TODO: Add trend analysis (week-over-week, month-over-month)
# TODO: Implement cohort analysis for beta users
# TODO: Add export functionality for reports

