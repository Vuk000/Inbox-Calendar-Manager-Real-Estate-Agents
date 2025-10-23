"""
Email management router - CRUD operations for email communications
Refactored to use CommunicationLog model
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..db import get_db
from ..models.user import User
from ..models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from ..models.email_account import EmailAccount
from ..dependencies import get_current_user
from ..security.audit import log_action
from ..tasks.email_sync_task import process_email_with_ai
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# Pydantic schemas
class EmailListResponse(BaseModel):
    id: int
    subject: Optional[str]
    from_address: str
    summary: Optional[str]
    urgency_score: Optional[float]
    sentiment_score: Optional[float]
    has_attachments: bool
    occurred_at: datetime
    contact_id: int
    
    class Config:
        from_attributes = True


class EmailDetailResponse(BaseModel):
    id: int
    subject: Optional[str]
    from_address: str
    to_address: Optional[str]
    body: Optional[str]
    summary: Optional[str]
    urgency_score: Optional[float]
    sentiment_score: Optional[float]
    key_topics: dict
    has_attachments: bool
    attachments: List[dict]
    occurred_at: datetime
    contact_id: int
    
    class Config:
        from_attributes = True


class EmailSearchRequest(BaseModel):
    query: str
    limit: int = 10


class AnalyzeEmailResponse(BaseModel):
    communication_log_id: int
    urgency_score: float
    sentiment_score: float
    key_topics: dict


@router.get("/emails", response_model=List[EmailListResponse])
async def list_emails(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    urgency_min: Optional[float] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List email communications with filtering and pagination.
    
    - **page**: Page number (starts at 1)
    - **limit**: Items per page (max 100)
    - **urgency_min**: Filter by minimum urgency score (0-100)
    - **search**: Search in subject and sender
    """
    # Build query for email communications
    query = db.query(CommunicationLog).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL
    )
    
    # Apply filters
    if urgency_min is not None:
        query = query.filter(CommunicationLog.urgency_score >= urgency_min)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                CommunicationLog.subject.ilike(search_pattern),
                CommunicationLog.from_address.ilike(search_pattern),
                CommunicationLog.summary.ilike(search_pattern)
            )
        )
    
    # Order by urgency score (desc) and occurred date (desc)
    query = query.order_by(
        desc(CommunicationLog.urgency_score),
        desc(CommunicationLog.occurred_at)
    )
    
    # Pagination
    offset = (page - 1) * limit
    emails = query.offset(offset).limit(limit).all()
    
    return emails


@router.get("/emails/{comm_log_id}", response_model=EmailDetailResponse)
async def get_email(
    comm_log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed email communication information.
    
    - **comm_log_id**: Communication log ID
    """
    # Get communication log
    comm_log = db.query(CommunicationLog).filter(
        CommunicationLog.id == comm_log_id,
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL
    ).first()
    
    if not comm_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Log access
    await log_action(
        db=db,
        action="read_email",
        user_id=current_user.id,
        resource_type="communication_log",
        resource_id=comm_log_id,
        description=f"Read email: {comm_log.subject}"
    )
    
    return comm_log


@router.post("/emails/search")
async def search_emails(
    request: EmailSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search across email communications.
    
    - **query**: Natural language search query
    - **limit**: Number of results to return
    """
    # Basic text search (semantic search with vector DB can be added later)
    search_pattern = f"%{request.query}%"
    communications = db.query(CommunicationLog).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL,
        or_(
            CommunicationLog.subject.ilike(search_pattern),
            CommunicationLog.summary.ilike(search_pattern),
            CommunicationLog.body.ilike(search_pattern),
            CommunicationLog.from_address.ilike(search_pattern)
        )
    ).order_by(desc(CommunicationLog.urgency_score)).limit(request.limit).all()
    
    return {
        "results": [EmailListResponse.from_orm(comm) for comm in communications],
        "count": len(communications),
        "query": request.query,
        "search_type": "text"
    }


@router.post("/emails/{comm_log_id}/analyze", response_model=AnalyzeEmailResponse)
async def analyze_email(
    comm_log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger AI analysis on an email communication.
    
    - **comm_log_id**: Communication log ID
    """
    # Get communication log
    comm_log = db.query(CommunicationLog).filter(
        CommunicationLog.id == comm_log_id,
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL
    ).first()
    
    if not comm_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Trigger AI processing
    result = process_email_with_ai.delay(comm_log_id)
    
    # Wait for result (with timeout)
    try:
        analysis_result = result.get(timeout=10)
        
        if analysis_result.get("status") == "success":
            # Refresh from DB
            db.refresh(comm_log)
            
            return AnalyzeEmailResponse(
                communication_log_id=comm_log.id,
                urgency_score=comm_log.urgency_score or 0.0,
                sentiment_score=comm_log.sentiment_score or 0.0,
                key_topics=comm_log.key_topics or {}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI analysis failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis error: {str(e)}"
        )


@router.get("/emails/stats/summary")
async def get_email_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email communication statistics summary"""
    total = db.query(CommunicationLog).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL
    ).count()
    
    urgent = db.query(CommunicationLog).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL,
        CommunicationLog.urgency_score >= 70
    ).count()
    
    today = db.query(CommunicationLog).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL,
        CommunicationLog.occurred_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()
    
    # Average sentiment
    avg_sentiment = db.query(func.avg(CommunicationLog.sentiment_score)).filter(
        CommunicationLog.user_id == current_user.id,
        CommunicationLog.communication_type == CommunicationType.EMAIL,
        CommunicationLog.sentiment_score.isnot(None)
    ).scalar()
    
    return {
        "total": total,
        "urgent": urgent,
        "today": today,
        "avg_sentiment": round(float(avg_sentiment), 2) if avg_sentiment else None
    }
