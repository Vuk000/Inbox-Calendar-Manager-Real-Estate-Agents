"""
Draft management router - AI-generated email drafts
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ..dependencies import get_db
from ..models.user import User
from ..models.communication_log import CommunicationLog, CommunicationType
from ..models.draft import Draft, DraftStatus
from ..models.email_account import EmailAccount, EmailProvider
from ..dependencies import get_current_user
from ..security.encryption import decrypt_data
from ..agents.draft_agent import DraftAgent
from ..security.audit import log_action

router = APIRouter()


# Pydantic schemas
class GenerateDraftRequest(BaseModel):
    communication_log_id: int  # Changed from message_id
    num_variants: int = 1
    context: Optional[dict] = None


class DraftResponse(BaseModel):
    id: int
    communication_log_id: Optional[int]  # Changed from message_id
    subject: Optional[str]
    content: str
    variant_number: int
    confidence_score: Optional[float]
    approval_status: str
    generated_at: datetime
    
    class Config:
        from_attributes = True


class UpdateDraftRequest(BaseModel):
    content: str
    feedback: Optional[str] = None


@router.post("/drafts/generate", response_model=List[DraftResponse])
async def generate_draft(
    request: GenerateDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI draft responses for an email.
    
    - **communication_log_id**: Original communication to reply to
    - **num_variants**: Number of draft variations (1-3)
    - **context**: Optional additional context (CRM data, market data)
    """
    # Validate num_variants
    if request.num_variants < 1 or request.num_variants > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="num_variants must be between 1 and 3"
        )
    
    # Check AI actions limit
    if current_user.ai_actions_this_month >= current_user.ai_actions_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI actions limit exceeded for this month"
        )
    
    # Get communication log
    comm_log = db.query(CommunicationLog).filter(
        CommunicationLog.id == request.communication_log_id,
        CommunicationLog.user_id == current_user.id
    ).first()
    
    if not comm_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Communication not found"
        )
    
    # Prepare email data
    email_data = {
        "subject": comm_log.subject,
        "body": comm_log.body or comm_log.summary or "",
        "sender_email": comm_log.from_address or "",
        "sender_name": comm_log.from_address or "Unknown",
        "thread_context": ""  # TODO: Fetch thread history
    }
    
    # Prepare agent info
    agent_info = {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number
    }
    
    # Get style examples (TODO: fetch from user's sent emails)
    style_examples = []
    
    # Initialize draft agent
    draft_agent = DraftAgent()
    
    # Generate drafts
    generated_drafts = await draft_agent.generate_draft(
        original_email=email_data,
        agent_info=agent_info,
        style_examples=style_examples,
        context=request.context,
        num_variants=request.num_variants
    )
    
    # Save drafts to database
    draft_responses = []
    for draft_data in generated_drafts:
        if not draft_data.get("content"):
            continue
        
        new_draft = Draft(
            user_id=current_user.id,
            communication_log_id=comm_log.id,
            subject=f"Re: {comm_log.subject}" if comm_log.subject else "Re: (No subject)",
            generated_content=draft_data["content"],
            confidence_score=draft_data.get("confidence_score"),
            variant_number=draft_data.get("variant_number", 1),
            model_version=draft_data.get("model_version"),
            approval_status=DraftStatus.PENDING
        )
        
        db.add(new_draft)
        db.commit()
        db.refresh(new_draft)
        
        draft_responses.append(DraftResponse(
            id=new_draft.id,
            communication_log_id=new_draft.communication_log_id,
            subject=new_draft.subject,
            content=new_draft.generated_content,
            variant_number=new_draft.variant_number,
            confidence_score=new_draft.confidence_score,
            approval_status=new_draft.approval_status.value,
            generated_at=new_draft.generated_at
        ))
    
    # Increment AI actions count
    current_user.ai_actions_this_month += 1
    db.commit()
    
    # Log action
    await log_action(
        db=db,
        action="generate_draft",
        user_id=current_user.id,
        resource_type="communication_log",
        resource_id=comm_log.id,
        description=f"Generated {len(draft_responses)} draft(s) for email"
    )
    
    return draft_responses


@router.get("/drafts", response_model=List[DraftResponse])
async def list_drafts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all drafts for current user"""
    drafts = db.query(Draft).filter(
        Draft.user_id == current_user.id
    ).order_by(Draft.generated_at.desc()).all()
    
    return [DraftResponse(
        id=d.id,
        communication_log_id=d.communication_log_id,
        subject=d.subject,
        content=d.final_content or d.generated_content,
        variant_number=d.variant_number,
        confidence_score=d.confidence_score,
        approval_status=d.approval_status.value,
        generated_at=d.generated_at
    ) for d in drafts]


@router.get("/drafts/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific draft"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    return DraftResponse(
        id=draft.id,
        communication_log_id=draft.communication_log_id,
        subject=draft.subject,
        content=draft.final_content or draft.generated_content,
        variant_number=draft.variant_number,
        confidence_score=draft.confidence_score,
        approval_status=draft.approval_status.value,
        generated_at=draft.generated_at
    )


@router.patch("/drafts/{draft_id}")
async def update_draft(
    draft_id: int,
    request: UpdateDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update/edit a draft.
    
    - **draft_id**: Draft ID
    - **content**: Updated content
    - **feedback**: Optional feedback on why edits were made
    """
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    # Track edits for learning
    if draft.generated_content != request.content:
        draft.human_edits = {
            "original": draft.generated_content,
            "edited": request.content,
            "feedback": request.feedback,
            "edited_at": datetime.utcnow().isoformat()
        }
    
    draft.final_content = request.content
    draft.approval_status = DraftStatus.EDITED
    draft.reviewed_at = datetime.utcnow()
    
    db.commit()
    
    return {"success": True, "draft_id": draft_id}


@router.post("/drafts/{draft_id}/send")
async def send_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a draft email.
    
    - **draft_id**: Draft ID to send
    """
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    # Get original communication log for threading
    comm_log = db.query(CommunicationLog).filter(
        CommunicationLog.id == draft.communication_log_id
    ).first()
    
    if not comm_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original communication not found"
        )
    
    # Get email account to send from (use first active account)
    email_account = None
    if current_user.email_accounts:
        email_account = next((acc for acc in current_user.email_accounts if acc.is_active), None)
    
    if not email_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active email account found"
        )
    
    try:
        # Get final content to send
        content_to_send = draft.final_content or draft.generated_content
        
        # Send via appropriate provider
        if email_account.provider == EmailProvider.GMAIL:
            from ..integrations.gmail_integration import GmailIntegration
            gmail = GmailIntegration()
            import asyncio
            send_result = asyncio.run(gmail.send_message(
                encrypted_access_token=email_account.encrypted_access_token,
                to=comm_log.from_address or "",
                subject=draft.subject or f"Re: {comm_log.subject or 'No subject'}",
                body=content_to_send,
                encrypted_refresh_token=email_account.encrypted_refresh_token,
                in_reply_to=comm_log.external_id,
                references=comm_log.external_id
            ))
            
            if not send_result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email: {send_result.get('error')}"
                )
        else:  # Outlook
            from ..integrations.outlook_integration import OutlookIntegration
            outlook = OutlookIntegration()
            import asyncio
            send_result = asyncio.run(outlook.send_message(
                encrypted_access_token=email_account.encrypted_access_token,
                to=[comm_log.from_address or ""],
                subject=draft.subject or f"Re: {comm_log.subject or 'No subject'}",
                body=content_to_send
            ))
            
            if not send_result.get("success"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email: {send_result.get('error')}"
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )
    
    draft.approval_status = DraftStatus.SENT
    draft.sent_at = datetime.utcnow()
    db.commit()
    
    # Log action
    await log_action(
        db=db,
        action="send_email",
        user_id=current_user.id,
        resource_type="draft",
        resource_id=draft_id,
        description=f"Sent draft email: {draft.subject}"
    )
    
    return {
        "success": True,
        "draft_id": draft_id,
        "sent_at": draft.sent_at
    }


@router.delete("/drafts/{draft_id}")
async def delete_draft(
    draft_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a draft"""
    draft = db.query(Draft).filter(
        Draft.id == draft_id,
        Draft.user_id == current_user.id
    ).first()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    
    db.delete(draft)
    db.commit()
    
    return {"success": True, "draft_id": draft_id}

