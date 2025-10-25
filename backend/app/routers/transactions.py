"""Transaction management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..dependencies import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.transaction import Transaction, TransactionStage, TransactionType
from ..services.transaction_service import TransactionService
from ..shared.exceptions import ValidationException

router = APIRouter(prefix="/transactions", tags=["Transactions"])


# Pydantic schemas
class TransactionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    transaction_type: TransactionType
    contact_id: int
    property_id: Optional[int] = None
    estimated_value: Optional[float] = None
    commission_percentage: Optional[float] = None
    estimated_commission: Optional[float] = None
    checklist_template: str = "buyer"
    lead_date: Optional[datetime] = None
    contract_date: Optional[datetime] = None
    closing_date: Optional[datetime] = None
    probability: float = 50.0
    notes: Optional[str] = None
    tags: List[str] = []
    is_shared: bool = False


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    transaction_type: Optional[TransactionType] = None
    stage: Optional[TransactionStage] = None
    property_id: Optional[int] = None
    estimated_value: Optional[float] = None
    commission_percentage: Optional[float] = None
    estimated_commission: Optional[float] = None
    actual_sale_price: Optional[float] = None
    actual_commission: Optional[float] = None
    contract_date: Optional[datetime] = None
    inspection_date: Optional[datetime] = None
    appraisal_date: Optional[datetime] = None
    closing_date: Optional[datetime] = None
    probability: Optional[float] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_shared: Optional[bool] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    team_id: Optional[int]
    title: str
    description: Optional[str]
    transaction_type: str
    stage: str
    pipeline_position: int
    contact_id: int
    property_id: Optional[int]
    estimated_value: Optional[float]
    commission_percentage: Optional[float]
    estimated_commission: Optional[float]
    actual_sale_price: Optional[float]
    actual_commission: Optional[float]
    lead_date: Optional[datetime]
    contract_date: Optional[datetime]
    closing_date: Optional[datetime]
    closed_at: Optional[datetime]
    probability: float
    is_shared: bool
    public_timeline_uuid: Optional[str]
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    skip: int
    limit: int


class UpdateStageRequest(BaseModel):
    stage: TransactionStage
    outcome_reason: Optional[str] = None


class UpdateChecklistRequest(BaseModel):
    checklist_items: List[dict]


# Endpoints
@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    try:
        transaction = TransactionService.create_transaction(
            db=db,
            user_id=current_user.id,
            transaction_data=transaction_data.model_dump(exclude_unset=True)
        )
        return transaction
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    stage: Optional[TransactionStage] = Query(None),
    transaction_type: Optional[TransactionType] = Query(None),
    contact_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List transactions with filters and pagination"""
    transactions = TransactionService.list_transactions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        stage=stage,
        transaction_type=transaction_type,
        contact_id=contact_id,
        search=search
    )
    
    # Simplified total count
    total = len(transactions) if len(transactions) < limit else skip + len(transactions)
    
    return {
        "transactions": transactions,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/stats")
async def get_pipeline_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get pipeline statistics"""
    stats = TransactionService.get_pipeline_stats(db, current_user.id)
    return stats


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single transaction by ID"""
    transaction = TransactionService.get_transaction(db, transaction_id, current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    try:
        transaction = TransactionService.update_transaction(
            db=db,
            transaction_id=transaction_id,
            user_id=current_user.id,
            update_data=transaction_data.model_dump(exclude_unset=True)
        )
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    try:
        success = TransactionService.delete_transaction(db, transaction_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{transaction_id}/stage", response_model=TransactionResponse)
async def update_transaction_stage(
    transaction_id: int,
    request: UpdateStageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update transaction stage (move through pipeline)"""
    try:
        transaction = TransactionService.update_stage(
            db=db,
            transaction_id=transaction_id,
            user_id=current_user.id,
            new_stage=request.stage,
            outcome_reason=request.outcome_reason
        )
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transaction_id}/timeline")
async def get_transaction_timeline(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get timeline for a transaction"""
    timeline = TransactionService.get_transaction_timeline(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id
    )
    
    if not timeline.get("timeline_events") and not timeline.get("communications"):
        # Check if transaction exists
        transaction = TransactionService.get_transaction(db, transaction_id, current_user.id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "transaction_id": transaction_id,
        **timeline
    }


@router.put("/{transaction_id}/checklist", response_model=TransactionResponse)
async def update_transaction_checklist(
    transaction_id: int,
    request: UpdateChecklistRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update transaction checklist"""
    try:
        transaction = TransactionService.update_checklist(
            db=db,
            transaction_id=transaction_id,
            user_id=current_user.id,
            checklist_items=request.checklist_items
        )
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))

