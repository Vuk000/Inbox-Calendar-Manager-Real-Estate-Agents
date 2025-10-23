"""Communications Hub API - Unified inbox and summarization"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from anthropic import Anthropic

from ..db import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.communication_log import CommunicationLog, CommunicationType
# Message model removed - using CommunicationLog
from ..services.communication_service import CommunicationService
from ..config import settings

router = APIRouter(prefix="/communications", tags=["Communications"])


# Pydantic schemas
class CommunicationResponse(BaseModel):
    id: int
    contact_id: int
    communication_type: str
    direction: str
    subject: Optional[str]
    summary: Optional[str]
    from_address: Optional[str]
    to_address: Optional[str]
    sentiment_score: Optional[float]
    urgency_score: Optional[float]
    occurred_at: datetime
    
    class Config:
        from_attributes = True


class SummarizeThreadRequest(BaseModel):
    message_ids: List[int] = Field(..., min_items=1, max_items=50)


class SummarizeThreadResponse(BaseModel):
    summary: str
    key_points: List[str]
    sentiment: str
    action_items: List[str]
    participant_count: int


class LinkMessageRequest(BaseModel):
    contact_id: int


# Endpoints
@router.get("", response_model=List[CommunicationResponse])
async def list_communications(
    contact_id: Optional[int] = Query(None),
    communication_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List communications with optional filters"""
    if not contact_id:
        # Get all communications for user
        query = db.query(CommunicationLog).filter(
            CommunicationLog.user_id == current_user.id
        )
        
        if communication_type:
            try:
                query = query.filter(
                    CommunicationLog.communication_type == CommunicationType(communication_type)
                )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid communication type")
        
        if start_date:
            query = query.filter(CommunicationLog.occurred_at >= start_date)
        
        if end_date:
            query = query.filter(CommunicationLog.occurred_at <= end_date)
        
        communications = query.order_by(
            CommunicationLog.occurred_at.desc()
        ).limit(limit).all()
    else:
        # Get communications for specific contact
        comm_type = CommunicationType(communication_type) if communication_type else None
        communications = CommunicationService.get_contact_communications(
            db=db,
            contact_id=contact_id,
            user_id=current_user.id,
            communication_type=comm_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    return communications


@router.get("/stats")
async def get_communication_stats(
    contact_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get communication statistics for a contact"""
    stats = CommunicationService.get_communication_stats(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id
    )
    return stats


# Endpoint removed - Message model deprecated
# Communications are now automatically linked to contacts during email sync


@router.post("/summarize", response_model=SummarizeThreadResponse)
async def summarize_email_thread(
    request: SummarizeThreadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Summarize an email thread using AI"""
    # Get messages
    messages = db.query(Message).filter(
        Message.id.in_(request.message_ids)
    ).order_by(Message.received_at.asc()).all()
    
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found")
    
    # Verify user has access to these messages
    for msg in messages:
        if msg.email_account.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to one or more messages")
    
    try:
        # Build thread summary request
        thread_text = _build_thread_text(messages)
        
        # Call Claude API
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2000,
            temperature=0.3,
            system="You are an expert email analyst. Summarize email threads concisely and extract actionable insights.",
            messages=[{
                "role": "user",
                "content": f"""Summarize this email thread and provide key insights.

EMAIL THREAD:
{thread_text}

Provide your analysis in this JSON format:
{{
    "summary": "<2-3 sentence summary>",
    "key_points": ["<point 1>", "<point 2>", "<point 3>"],
    "sentiment": "<Positive/Neutral/Negative>",
    "action_items": ["<action 1>", "<action 2>"],
    "participants": ["<email 1>", "<email 2>"]
}}
"""
            }]
        )
        
        # Parse response
        content = response.content[0].text
        result = _parse_summary_response(content, messages)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


def _build_thread_text(messages: List[CommunicationLog]) -> str:
    """Build readable thread text from messages"""
    thread_parts = []
    
    for msg in messages:
        thread_parts.append(f"""
---
From: {msg.sender_name} <{msg.sender_email}>
Date: {msg.received_at.strftime('%Y-%m-%d %H:%M')}
Subject: {msg.subject}

{msg.body_preview or '(No preview available)'}
---
""")
    
    return "\n".join(thread_parts)


def _parse_summary_response(content: str, messages: List[CommunicationLog]) -> dict:
    """Parse AI summary response"""
    import json
    
    try:
        # Extract JSON from response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Get unique participants
            participants = set()
            for msg in messages:
                participants.add(msg.sender_email)
                if msg.recipient_emails:
                    participants.update(msg.recipient_emails)
            
            return {
                "summary": result.get("summary", "Summary unavailable"),
                "key_points": result.get("key_points", []),
                "sentiment": result.get("sentiment", "Neutral"),
                "action_items": result.get("action_items", []),
                "participant_count": len(participants)
            }
        else:
            # Fallback if JSON not found
            return {
                "summary": content[:500],
                "key_points": [],
                "sentiment": "Neutral",
                "action_items": [],
                "participant_count": len(messages)
            }
            
    except json.JSONDecodeError:
        return {
            "summary": "Failed to parse summary",
            "key_points": [],
            "sentiment": "Neutral",
            "action_items": [],
            "participant_count": len(messages)
        }

