"""
Analytics router - Metrics and insights
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta, date

from ..dependencies import get_db
from ..models.user import User
from ..models.communication_log import CommunicationLog, CommunicationType
from ..models.task import Task, TaskStatus
from ..models.draft import Draft, DraftStatus
from ..models.analytics import Analytics
from ..models.contact import Contact
from ..dependencies import get_current_user

router = APIRouter()


@router.get("/analytics/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard metrics for the current user.
    
    Returns:
    - Emails processed today
    - Time saved this week
    - Drafts generated
    - Tasks completed
    - Urgent emails
    - Recent leads
    """
    # Today's start
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = datetime.utcnow() - timedelta(days=7)
    
    # Communications (emails) processed today
    emails_today = db.query(CommunicationLog).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL,
        CommunicationLog.created_at >= today_start
    ).count()
    
    # Time saved this week (estimate: 0.1h per communication)
    comms_this_week = db.query(CommunicationLog).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.created_at >= week_start
    ).count()
    time_saved_hours = round(comms_this_week * 0.1, 1)
    
    # Drafts generated
    drafts_generated = db.query(Draft).filter(
        Draft.user_id == current_user.id,
        Draft.generated_at >= week_start
    ).count()
    
    # Tasks completed
    tasks_completed = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.is_completed == True,
        Task.completed_at >= week_start
    ).count()
    
    # Urgent communications (high urgency score)
    urgent_comms = db.query(CommunicationLog).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL,
        CommunicationLog.urgency_score >= 70
    ).order_by(CommunicationLog.urgency_score.desc()).limit(5).all()
    
    urgent_emails = [
        {
            "id": comm.id,
            "subject": comm.subject or "No subject",
            "sender": comm.from_address,
            "category": "urgent",
            "urgency_score": comm.urgency_score
        }
        for comm in urgent_comms
    ]
    
    # Recent leads (contacts created from email in last week)
    recent_lead_contacts = db.query(Contact).filter(
        Contact.user_id == current_user.id,
        Contact.lead_source == "email",
        Contact.created_at >= week_start
    ).order_by(Contact.relationship_score.desc()).limit(5).all()
    
    recent_leads = [
        {
            "id": contact.id,
            "name": contact.full_name,
            "email": contact.email,
            "score": int(contact.relationship_score),
            "received_at": contact.created_at.isoformat()
        }
        for contact in recent_lead_contacts
    ]
    
    # Email activity chart data (last 14 days)
    email_activity = []
    for i in range(14):
        day = today_start - timedelta(days=13-i)
        day_end = day + timedelta(days=1)
        
        day_emails = db.query(CommunicationLog).filter(
            CommunicationLog.user_id == current_user.id,
            CommunicationLog.communication_type == CommunicationType.EMAIL,
            CommunicationLog.created_at >= day,
            CommunicationLog.created_at < day_end
        ).count()
        
        email_activity.append({
            "date": day.isoformat(),
            "emails": day_emails,
            "ai_actions": day_emails  # Simplified for now
        })
    
    # AI action breakdown
    ai_action_breakdown = [
        {"name": "Email Triage", "value": emails_today},
        {"name": "Drafts", "value": drafts_generated},
        {"name": "Tasks Created", "value": tasks_completed}
    ]
    
    # Lead funnel (simplified)
    total_contacts = db.query(Contact).filter(Contact.user_id == current_user.id).count()
    contacted = db.query(Contact).filter(Contact.user_id == current_user.id, Contact.last_contact_date.isnot(None)).count()
    qualified = db.query(Contact).filter(Contact.user_id == current_user.id, Contact.relationship_score >= 50).count()
    
    lead_funnel = [
        {"stage": "New", "count": total_contacts},
        {"stage": "Contacted", "count": contacted},
        {"stage": "Qualified", "count": qualified}
    ]
    
    # ROI over time (based on actual activity)
    roi_over_time = []
    for i in range(7, -1, -1):
        day = today_start - timedelta(days=i)
        day_end = day + timedelta(days=1)
        day_comms = db.query(CommunicationLog).filter(
            CommunicationLog.user_id == current_user.id,
            CommunicationLog.created_at >= day,
            CommunicationLog.created_at < day_end
        ).count()
        roi_over_time.append({
            "date": day.isoformat(),
            "hours_saved": round(day_comms * 0.1, 1),
            "value_generated": day_comms * 25
        })
    
    return {
        "emails_processed_today": emails_today,
        "time_saved_hours": time_saved_hours,
        "drafts_generated": drafts_generated,
        "tasks_completed": tasks_completed,
        "urgent_emails": urgent_emails,
        "recent_leads": recent_leads,
        "email_activity": email_activity,
        "ai_action_breakdown": ai_action_breakdown,
        "lead_funnel": lead_funnel,
        "roi_over_time": roi_over_time,
        "ai_actions_used": current_user.ai_actions_this_month,
        "ai_actions_limit": current_user.ai_actions_limit
    }


@router.get("/analytics/email-patterns")
async def get_email_patterns(
    days: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get email patterns and statistics.
    
    - **days**: Number of days to analyze (1-90)
    """
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    if not account_ids:
        return {
            "total_emails": 0,
            "by_priority": {},
            "by_category": {},
            "by_hour": {}
        }
    
    since_date = datetime.utcnow() - timedelta(days=days)
    
    # Total emails
    total = db.query(Message).filter(
        Message.email_account_id.in_(account_ids),
        Message.received_at >= since_date
    ).count()
    
    # By priority
    by_priority = {}
    for priority in MessagePriority:
        count = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.received_at >= since_date,
            Message.priority == priority
        ).count()
        by_priority[priority.value] = count
    
    # By category
    by_category = {}
    for category in MessageCategory:
        count = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.received_at >= since_date,
            Message.category == category
        ).count()
        by_category[category.value] = count
    
    # By hour of day (simplified - would need more complex query in production)
    by_hour = {str(i): 0 for i in range(24)}
    
    return {
        "total_emails": total,
        "by_priority": by_priority,
        "by_category": by_category,
        "by_hour": by_hour,
        "period_days": days
    }


@router.get("/analytics/reports")
async def get_reports(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate performance reports.
    
    - **start_date**: Report start date
    - **end_date**: Report end date
    """
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).date()
    if not end_date:
        end_date = datetime.utcnow().date()
    
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Email metrics
    emails_processed = 0
    if account_ids:
        emails_processed = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.processed_at >= start_datetime,
            Message.processed_at <= end_datetime
        ).count()
    
    # Time saved (0.1h per email)
    time_saved = round(emails_processed * 0.1, 1)
    
    # Drafts metrics
    drafts_generated = db.query(Draft).filter(
        Draft.user_id == current_user.id,
        Draft.generated_at >= start_datetime,
        Draft.generated_at <= end_datetime
    ).count()
    
    drafts_sent = db.query(Draft).filter(
        Draft.user_id == current_user.id,
        Draft.approval_status == DraftStatus.SENT,
        Draft.sent_at >= start_datetime,
        Draft.sent_at <= end_datetime
    ).count()
    
    # Task metrics
    tasks_created = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.created_at >= start_datetime,
        Task.created_at <= end_datetime
    ).count()
    
    tasks_completed = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.completed_at >= start_datetime,
        Task.completed_at <= end_datetime
    ).count()
    
    # Lead metrics
    leads_qualified = 0
    if account_ids:
        leads_qualified = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.category == MessageCategory.LEAD,
            Message.received_at >= start_datetime,
            Message.received_at <= end_datetime
        ).count()
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "email_metrics": {
            "processed": emails_processed,
            "time_saved_hours": time_saved
        },
        "draft_metrics": {
            "generated": drafts_generated,
            "sent": drafts_sent,
            "acceptance_rate": round(drafts_sent / drafts_generated * 100, 1) if drafts_generated > 0 else 0
        },
        "task_metrics": {
            "created": tasks_created,
            "completed": tasks_completed,
            "completion_rate": round(tasks_completed / tasks_created * 100, 1) if tasks_created > 0 else 0
        },
        "lead_metrics": {
            "qualified": leads_qualified
        }
    }


@router.get("/analytics/roi")
async def get_roi(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate ROI from using RealInbox AI.
    """
    # Last 30 days
    since_date = datetime.utcnow() - timedelta(days=30)
    
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    # Emails processed
    emails_processed = 0
    if account_ids:
        emails_processed = db.query(Message).filter(
            Message.email_account_id.in_(account_ids),
            Message.processed_at >= since_date
        ).count()
    
    # Time saved (0.1h per email)
    hours_saved = round(emails_processed * 0.1, 1)
    
    # Value (assuming $50/hour for agent time)
    value_saved = round(hours_saved * 50, 2)
    
    # Subscription cost (simplified)
    monthly_cost = 29.0  # Solo agent tier
    
    # ROI percentage
    roi_percentage = round(((value_saved - monthly_cost) / monthly_cost) * 100, 1) if monthly_cost > 0 else 0
    
    return {
        "period_days": 30,
        "emails_processed": emails_processed,
        "hours_saved": hours_saved,
        "value_saved_usd": value_saved,
        "monthly_cost_usd": monthly_cost,
        "roi_percentage": roi_percentage,
        "net_value": round(value_saved - monthly_cost, 2)
    }

