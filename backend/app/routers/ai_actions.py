"""AI Actions API - Human-in-the-loop confirmation system"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from ..db import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.ai_action import AIAction, AIActionType, AIActionStatus
from ..models.contact import Contact
from ..models.transaction import Transaction

router = APIRouter(prefix="/ai", tags=["AI Actions"])


# Pydantic schemas
class AIActionResponse(BaseModel):
    id: int
    action_type: str
    status: str
    proposed_data: dict
    reason: str
    confidence_score: Optional[float]
    result_data: Optional[dict]
    error_message: Optional[str]
    expires_at: datetime
    created_at: datetime
    confirmed_at: Optional[datetime]
    executed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AIActionListResponse(BaseModel):
    actions: List[AIActionResponse]
    total: int


class ConfirmActionRequest(BaseModel):
    notes: Optional[str] = Field(None, description="User notes about confirmation")


class RejectActionRequest(BaseModel):
    reason: str = Field(..., min_length=1, description="Reason for rejection")


# Endpoints
@router.get("/actions", response_model=AIActionListResponse)
async def list_ai_actions(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List pending AI actions for the current user"""
    query = db.query(AIAction).filter(AIAction.user_id == current_user.id)
    
    # Apply filters
    if status_filter:
        try:
            query = query.filter(AIAction.status == AIActionStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status filter")
    
    if action_type:
        try:
            query = query.filter(AIAction.action_type == AIActionType(action_type))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid action type")
    
    # Order by creation date (newest first)
    query = query.order_by(AIAction.created_at.desc())
    
    total = query.count()
    actions = query.offset(skip).limit(limit).all()
    
    return {
        "actions": actions,
        "total": total
    }


@router.get("/actions/{action_id}", response_model=AIActionResponse)
async def get_ai_action(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific AI action"""
    action = db.query(AIAction).filter(
        AIAction.id == action_id,
        AIAction.user_id == current_user.id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="AI action not found")
    
    return action


@router.post("/confirm-action/{action_id}", response_model=AIActionResponse)
async def confirm_ai_action(
    action_id: int,
    request: ConfirmActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm and execute an AI-proposed action"""
    # Get action
    action = db.query(AIAction).filter(
        AIAction.id == action_id,
        AIAction.user_id == current_user.id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="AI action not found")
    
    if action.status != AIActionStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Action is {action.status}, cannot confirm")
    
    if action.expires_at < datetime.utcnow():
        action.status = AIActionStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=400, detail="Action has expired")
    
    try:
        # Execute the action based on type
        result = _execute_ai_action(action, db)
        
        # Update action status
        action.status = AIActionStatus.EXECUTED
        action.confirmed_at = datetime.utcnow()
        action.executed_at = datetime.utcnow()
        action.result_data = result
        
        db.commit()
        db.refresh(action)
        
        return action
        
    except Exception as e:
        action.status = AIActionStatus.CONFIRMED
        action.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to execute action: {str(e)}")


@router.post("/reject-action/{action_id}", response_model=AIActionResponse)
async def reject_ai_action(
    action_id: int,
    request: RejectActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject an AI-proposed action"""
    action = db.query(AIAction).filter(
        AIAction.id == action_id,
        AIAction.user_id == current_user.id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="AI action not found")
    
    if action.status != AIActionStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Action is {action.status}, cannot reject")
    
    action.status = AIActionStatus.REJECTED
    action.result_data = {"rejection_reason": request.reason}
    action.confirmed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(action)
    
    return action


def _execute_ai_action(action: AIAction, db: Session) -> dict:
    """Execute an AI action based on its type"""
    action_type = action.action_type
    proposed_data = action.proposed_data
    
    if action_type == AIActionType.MERGE_CONTACTS:
        return _merge_contacts(proposed_data, db)
    
    elif action_type == AIActionType.UPDATE_CONTACT:
        return _update_contact(proposed_data, db)
    
    elif action_type == AIActionType.CREATE_TRANSACTION:
        return _create_transaction(proposed_data, db)
    
    elif action_type == AIActionType.UPDATE_TRANSACTION:
        return _update_transaction(proposed_data, db)
    
    elif action_type == AIActionType.LINK_CONTACT_PROPERTY:
        return _link_contact_property(proposed_data, db)
    
    elif action_type == AIActionType.SUGGEST_FOLLOW_UP:
        return _create_follow_up_task(proposed_data, db)
    
    else:
        raise ValueError(f"Unknown action type: {action_type}")


def _merge_contacts(data: dict, db: Session) -> dict:
    """Merge two contacts"""
    source_id = data.get("source_contact_id")
    target_id = data.get("target_contact_id")
    
    source = db.query(Contact).filter(Contact.id == source_id).first()
    target = db.query(Contact).filter(Contact.id == target_id).first()
    
    if not source or not target:
        raise ValueError("Source or target contact not found")
    
    # Merge logic: transfer communications, transactions, etc. to target
    # Update all foreign keys pointing to source to point to target
    from ..models.communication_log import CommunicationLog
    
    db.query(CommunicationLog).filter(
        CommunicationLog.contact_id == source_id
    ).update({"contact_id": target_id})
    
    db.query(Transaction).filter(
        Transaction.contact_id == source_id
    ).update({"contact_id": target_id})
    
    # Merge tags and custom fields
    if source.tags:
        target.tags = list(set((target.tags or []) + source.tags))
    
    if source.custom_fields:
        target.custom_fields = {**(target.custom_fields or {}), **source.custom_fields}
    
    # Delete source contact
    db.delete(source)
    db.commit()
    
    return {
        "merged_contact_id": target_id,
        "deleted_contact_id": source_id,
        "message": "Contacts merged successfully"
    }


def _update_contact(data: dict, db: Session) -> dict:
    """Update contact with AI-proposed changes"""
    contact_id = data.get("contact_id")
    updates = data.get("updates", {})
    
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise ValueError("Contact not found")
    
    for key, value in updates.items():
        if hasattr(contact, key):
            setattr(contact, key, value)
    
    contact.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "contact_id": contact_id,
        "updated_fields": list(updates.keys()),
        "message": "Contact updated successfully"
    }


def _create_transaction(data: dict, db: Session) -> dict:
    """Create a new transaction from AI suggestion"""
    from ..models.transaction import TransactionType, TransactionStage
    
    transaction = Transaction(
        user_id=data.get("user_id"),
        contact_id=data.get("contact_id"),
        property_id=data.get("property_id"),
        title=data.get("title"),
        description=data.get("description"),
        transaction_type=TransactionType(data.get("transaction_type", "buyer")),
        stage=TransactionStage(data.get("stage", "lead")),
        estimated_value=data.get("estimated_value")
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return {
        "transaction_id": transaction.id,
        "message": "Transaction created successfully"
    }


def _update_transaction(data: dict, db: Session) -> dict:
    """Update transaction with AI suggestions"""
    transaction_id = data.get("transaction_id")
    updates = data.get("updates", {})
    
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise ValueError("Transaction not found")
    
    for key, value in updates.items():
        if hasattr(transaction, key):
            setattr(transaction, key, value)
    
    transaction.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "transaction_id": transaction_id,
        "updated_fields": list(updates.keys()),
        "message": "Transaction updated successfully"
    }


def _link_contact_property(data: dict, db: Session) -> dict:
    """Link a contact to a property"""
    contact_id = data.get("contact_id")
    property_id = data.get("property_id")
    
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise ValueError("Contact not found")
    
    # Create a transaction linking them
    from ..models.transaction import Transaction, TransactionType, TransactionStage
    
    transaction = Transaction(
        user_id=contact.user_id,
        contact_id=contact_id,
        property_id=property_id,
        title=f"Property inquiry - {contact.first_name} {contact.last_name or ''}",
        transaction_type=TransactionType.BUYER,
        stage=TransactionStage.LEAD
    )
    
    db.add(transaction)
    db.commit()
    
    return {
        "contact_id": contact_id,
        "property_id": property_id,
        "transaction_id": transaction.id,
        "message": "Contact linked to property via transaction"
    }


def _create_follow_up_task(data: dict, db: Session) -> dict:
    """Create a follow-up task from AI suggestion"""
    from ..models.task import Task, TaskType, TaskStatus
    
    task = Task(
        user_id=data.get("user_id"),
        contact_id=data.get("contact_id"),
        task_type=TaskType.FOLLOW_UP,
        title=data.get("title", "Follow up"),
        description=data.get("description"),
        due_date=datetime.utcnow() + timedelta(days=data.get("days_until_due", 3)),
        status=TaskStatus.TODO,
        priority=data.get("priority", "medium")
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return {
        "task_id": task.id,
        "message": "Follow-up task created successfully"
    }

