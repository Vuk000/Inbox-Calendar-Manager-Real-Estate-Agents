"""
Privacy and GDPR Compliance Router
Handles data export, deletion, and consent management
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

from ..db import get_db
from ..models.user import User
from ..models.communication_log import CommunicationLog, CommunicationType
from ..models.draft import Draft
from ..models.task import Task
from ..models.audit_log import AuditLog
from ..dependencies import get_current_active_user
from ..security.audit import log_action
from ..security.encryption import decrypt_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/privacy", tags=["Privacy & GDPR"])


class ConsentRequest(BaseModel):
    """User consent request"""
    cookies: bool
    analytics: bool
    marketing: bool


class DataExportResponse(BaseModel):
    """Data export response"""
    export_id: str
    status: str
    download_url: Optional[str] = None
    created_at: str
    expires_at: str


class DataDeletionRequest(BaseModel):
    """Request to delete user data"""
    confirm_email: str
    reason: Optional[str] = None


@router.post("/consent", status_code=status.HTTP_200_OK)
async def update_consent(
    consent: ConsentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user's privacy consent preferences.
    
    Args:
        consent: Consent preferences
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Updated consent settings
    """
    # Update user consent settings
    if not hasattr(current_user, 'consent_settings'):
        current_user.consent_settings = {}
    
    current_user.consent_settings = {
        "cookies": consent.cookies,
        "analytics": consent.analytics,
        "marketing": consent.marketing,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    db.commit()
    
    # Log audit trail
    await log_action(
        db=db,
        action="update_consent",
        user_id=current_user.id,
        description=f"User updated privacy consent settings",
        metadata=current_user.consent_settings,
        status="success"
    )
    
    logger.info(f"User {current_user.id} updated consent settings")
    
    return {
        "message": "Consent preferences updated",
        "settings": current_user.consent_settings
    }


@router.get("/consent", response_model=Dict[str, Any])
async def get_consent(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's current consent preferences.
    
    Returns:
        Current consent settings
    """
    consent_settings = getattr(current_user, 'consent_settings', {
        "cookies": False,
        "analytics": False,
        "marketing": False
    })
    
    return {
        "consent": consent_settings,
        "user_id": current_user.id
    }


@router.post("/export-data", response_model=DataExportResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_data_export(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Request export of all user data (GDPR Article 20 - Data Portability).
    
    Export includes:
    - User profile
    - All emails (decrypted)
    - All drafts
    - All tasks
    - Analytics data
    - Audit logs
    
    Args:
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Export request confirmation with download info
    """
    export_id = f"export_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Schedule background task for data compilation
    background_tasks.add_task(
        compile_user_data_export,
        user_id=current_user.id,
        export_id=export_id,
        db_url=str(db.bind.url)
    )
    
    # Log audit trail
    await log_action(
        db=db,
        action="request_data_export",
        user_id=current_user.id,
        description="User requested data export (GDPR)",
        metadata={"export_id": export_id},
        status="success"
    )
    
    logger.info(f"User {current_user.id} requested data export: {export_id}")
    
    return DataExportResponse(
        export_id=export_id,
        status="processing",
        download_url=None,
        created_at=datetime.utcnow().isoformat(),
        expires_at=(datetime.utcnow() + timedelta(days=7)).isoformat()
    )


@router.post("/delete-account", status_code=status.HTTP_202_ACCEPTED)
async def request_account_deletion(
    deletion_request: DataDeletionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Request account and data deletion (GDPR Article 17 - Right to Erasure).
    
    This will:
    - Mark account for deletion (30-day grace period)
    - Schedule background task to anonymize/delete data
    - Send confirmation email
    
    Args:
        deletion_request: Deletion confirmation
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Deletion request confirmation
    """
    # Verify email confirmation
    if deletion_request.confirm_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email confirmation does not match"
        )
    
    # Mark user for deletion (grace period)
    current_user.deletion_requested_at = datetime.utcnow()
    current_user.deletion_reason = deletion_request.reason
    current_user.is_active = False
    db.commit()
    
    # Schedule background deletion (after 30 days)
    background_tasks.add_task(
        schedule_account_deletion,
        user_id=current_user.id,
        deletion_date=datetime.utcnow() + timedelta(days=30)
    )
    
    # Log audit trail
    await log_action(
        db=db,
        action="request_account_deletion",
        user_id=current_user.id,
        description=f"User requested account deletion (30-day grace period)",
        metadata={"reason": deletion_request.reason},
        status="success"
    )
    
    logger.warning(f"User {current_user.id} requested account deletion")
    
    return {
        "message": "Account deletion requested",
        "grace_period_days": 30,
        "deletion_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "note": "You can cancel this request within 30 days by logging in"
    }


@router.get("/my-data", response_model=Dict[str, Any])
async def get_my_data_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get summary of user's stored data (GDPR transparency).
    
    Returns:
        Summary of data stored for the user
    """
    # Count user's data
    email_count = db.query(Message).join(Message.email_account).filter(
        Message.email_account.has(user_id=current_user.id)
    ).count()
    
    draft_count = db.query(Draft).filter(Draft.user_id == current_user.id).count()
    task_count = db.query(Task).filter(Task.created_by == current_user.id).count()
    audit_count = db.query(AuditLog).filter(AuditLog.user_id == current_user.id).count()
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "data_summary": {
            "emails": email_count,
            "drafts": draft_count,
            "tasks": task_count,
            "audit_logs": audit_count
        },
        "account_created": current_user.created_at.isoformat() if current_user.created_at else None,
        "data_retention_policy": "Data is retained while account is active. You can request deletion at any time.",
        "rights": [
            "Right to access your data",
            "Right to export your data",
            "Right to delete your data",
            "Right to rectify inaccurate data",
            "Right to restrict processing",
            "Right to data portability"
        ]
    }


# Background task functions
async def compile_user_data_export(user_id: int, export_id: str, db_url: str):
    """
    Background task to compile user data export.
    
    TODO: Implement full data export functionality
    - Query all user data
    - Decrypt sensitive fields
    - Generate JSON/CSV files
    - Upload to S3 with expiring link
    - Send email notification
    """
    logger.info(f"TODO: Compile data export for user {user_id}: {export_id}")
    # Placeholder for implementation
    pass


async def schedule_account_deletion(user_id: int, deletion_date: datetime):
    """
    Schedule account deletion after grace period.
    
    TODO: Implement account deletion
    - Wait until deletion_date
    - Anonymize user data
    - Delete emails, drafts, tasks
    - Keep audit logs (anonymized)
    - Send final confirmation email
    """
    logger.info(f"TODO: Schedule deletion for user {user_id} on {deletion_date}")
    # Placeholder for implementation
    pass

