"""
Email management router - CRUD operations for emails
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..db import get_db
from ..models.user import User
from ..models.message import Message, MessagePriority, MessageCategory
from ..models.email_account import EmailAccount
from ..dependencies import get_current_user, get_triage_agent
from ..security.encryption import decrypt_data
from ..security.audit import log_action
from ..agents.triage_agent import TriageAgent
from ..tasks.email_sync_task import process_email_with_ai
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# Pydantic schemas
class EmailListResponse(BaseModel):
    id: int
    subject: str
    sender_email: str
    sender_name: Optional[str]
    body_preview: str
    priority: str
    category: str
    urgency_score: Optional[float]
    has_attachments: bool
    is_read: bool
    is_starred: bool
    received_at: datetime
    
    class Config:
        from_attributes = True


class EmailDetailResponse(BaseModel):
    id: int
    subject: str
    sender_email: str
    sender_name: Optional[str]
    body: str  # Decrypted
    priority: str
    category: str
    urgency_score: Optional[float]
    sentiment_score: Optional[float]
    entities: dict
    suggested_actions: List[str]
    has_attachments: bool
    attachment_count: int
    is_read: bool
    is_starred: bool
    received_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EmailSearchRequest(BaseModel):
    query: str
    limit: int = 10


class AnalyzeEmailResponse(BaseModel):
    message_id: int
    priority: str
    category: str
    urgency_score: float
    entities: dict
    suggested_actions: List[str]


@router.get("/emails", response_model=List[EmailListResponse])
async def list_emails(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List emails with filtering and pagination.
    
    - **page**: Page number (starts at 1)
    - **limit**: Items per page (max 100)
    - **priority**: Filter by priority (high, medium, low)
    - **category**: Filter by category (offer, lead, inspection, etc.)
    - **search**: Search in subject and sender
    """
    # Get user's email accounts
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    if not account_ids:
        return []
    
    # Build query
    query = db.query(Message).filter(Message.email_account_id.in_(account_ids))
    
    # Apply filters
    if priority:
        try:
            query = query.filter(Message.priority == MessagePriority(priority))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority: {priority}"
            )
    
    if category:
        try:
            query = query.filter(Message.category == MessageCategory(category))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}"
            )
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Message.subject.ilike(search_pattern),
                Message.sender_email.ilike(search_pattern),
                Message.sender_name.ilike(search_pattern)
            )
        )
    
    # Order by urgency score (desc) and received date (desc)
    query = query.order_by(
        desc(Message.urgency_score),
        desc(Message.received_at)
    )
    
    # Pagination
    offset = (page - 1) * limit
    emails = query.offset(offset).limit(limit).all()
    
    return emails


@router.get("/emails/{message_id}", response_model=EmailDetailResponse)
async def get_email(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed email information.
    
    - **message_id**: Email message ID
    """
    # Get user's email accounts
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    # Get message
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.email_account_id.in_(account_ids)
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Mark as read
    if not message.is_read:
        message.is_read = True
        db.commit()
    
    # Decrypt body
    decrypted_body = decrypt_data(message.encrypted_body)
    
    # Log access
    await log_action(
        db=db,
        action="read_email",
        user_id=current_user.id,
        resource_type="message",
        resource_id=message_id,
        description=f"Read email: {message.subject}"
    )
    
    # Convert to response model
    response = EmailDetailResponse(
        id=message.id,
        subject=message.subject,
        sender_email=message.sender_email,
        sender_name=message.sender_name,
        body=decrypted_body,
        priority=message.priority.value if message.priority else "low",
        category=message.category.value if message.category else "general",
        urgency_score=message.urgency_score,
        sentiment_score=message.sentiment_score,
        entities=message.entities or {},
        suggested_actions=message.suggested_actions or [],
        has_attachments=message.has_attachments,
        attachment_count=message.attachment_count,
        is_read=message.is_read,
        is_starred=message.is_starred,
        received_at=message.received_at,
        processed_at=message.processed_at
    )
    
    return response


@router.post("/emails/search")
async def search_emails(
    request: EmailSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Semantic search across emails using AI.
    
    - **query**: Natural language search query
    - **limit**: Number of results to return
    """
    # Try semantic search with Pinecone if available, fallback to text search
    # Note: sentence-transformers disabled for Python 3.13 compatibility
    # To enable semantic search, install sentence-transformers in Python 3.10/3.11 environment
    try:
        # Attempt import - will gracefully fail if not installed
        from sentence_transformers import SentenceTransformer
        from ..integrations.vector_store import VectorStore
        
        # Generate query embedding
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(request.query).tolist()
        
        # Search Pinecone
        vector_store = VectorStore()
        import asyncio
        search_results = asyncio.run(vector_store.search_similar_emails(
            query_embedding=query_embedding,
            user_id=current_user.id,
            top_k=request.limit
        ))
        
        if search_results.get("success") and search_results.get("matches"):
            # Get message IDs from vector search
            message_ids = [int(m["message_id"]) for m in search_results["matches"]]
            
            # Fetch actual messages
            messages = db.query(Message).filter(
                Message.id.in_(message_ids)
            ).all()
            
            # Sort by original similarity scores
            message_map = {msg.id: msg for msg in messages}
            sorted_messages = [message_map[mid] for mid in message_ids if mid in message_map]
            
            return {
                "results": [EmailListResponse.from_orm(msg) for msg in sorted_messages],
                "count": len(sorted_messages),
                "query": request.query,
                "search_type": "semantic"
            }
    except (ImportError, Exception) as e:
        logger.warning(f"Semantic search unavailable, using text search: {e}")
    
    # Fallback to basic text search
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    if not account_ids:
        return {"results": [], "count": 0}
    
    search_pattern = f"%{request.query}%"
    messages = db.query(Message).filter(
        Message.email_account_id.in_(account_ids),
        or_(
            Message.subject.ilike(search_pattern),
            Message.body_preview.ilike(search_pattern),
            Message.sender_email.ilike(search_pattern)
        )
    ).order_by(desc(Message.urgency_score)).limit(request.limit).all()
    
    return {
        "results": [EmailListResponse.from_orm(msg) for msg in messages],
        "count": len(messages),
        "query": request.query,
        "search_type": "text"
    }


@router.post("/emails/{message_id}/analyze", response_model=AnalyzeEmailResponse)
async def analyze_email(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger AI analysis on an email.
    
    - **message_id**: Email message ID
    """
    # Get user's email accounts
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    # Get message
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.email_account_id.in_(account_ids)
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Trigger AI processing
    result = process_email_with_ai.delay(message_id)
    
    # Wait for result (with timeout)
    try:
        analysis_result = result.get(timeout=10)
        
        if analysis_result.get("status") == "success":
            # Refresh message from DB
            db.refresh(message)
            
            return AnalyzeEmailResponse(
                message_id=message.id,
                priority=message.priority.value,
                category=message.category.value,
                urgency_score=message.urgency_score or 0.0,
                entities=message.entities or {},
                suggested_actions=message.suggested_actions or []
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


@router.patch("/emails/{message_id}/star")
async def toggle_star(
    message_id: int,
    starred: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Star or unstar an email.
    
    - **message_id**: Email message ID
    - **starred**: True to star, False to unstar
    """
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.email_account_id.in_(account_ids)
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    message.is_starred = starred
    db.commit()
    
    return {"success": True, "starred": starred}


@router.get("/emails/stats/summary")
async def get_email_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email statistics summary"""
    account_ids = [acc.id for acc in current_user.email_accounts if acc.is_active]
    
    if not account_ids:
        return {
            "total": 0,
            "unread": 0,
            "urgent": 0,
            "today": 0
        }
    
    total = db.query(Message).filter(Message.email_account_id.in_(account_ids)).count()
    unread = db.query(Message).filter(
        Message.email_account_id.in_(account_ids),
        Message.is_read == False
    ).count()
    urgent = db.query(Message).filter(
        Message.email_account_id.in_(account_ids),
        Message.priority == MessagePriority.HIGH
    ).count()
    
    today = db.query(Message).filter(
        Message.email_account_id.in_(account_ids),
        Message.received_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
    ).count()
    
    return {
        "total": total,
        "unread": unread,
        "urgent": urgent,
        "today": today
    }

