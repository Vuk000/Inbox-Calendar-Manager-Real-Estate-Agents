"""
Property management router - Real estate properties
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

from ..dependencies import get_db
from ..models.user import User
from ..models.property import Property
from ..dependencies import get_current_user

router = APIRouter()


# Pydantic schemas
class PropertyCreate(BaseModel):
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    mls_id: Optional[str] = None
    property_type: Optional[str] = None
    list_price: Optional[float] = None
    transaction_type: Optional[str] = None


class PropertyUpdate(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    list_price: Optional[float] = None
    sale_price: Optional[float] = None
    transaction_status: Optional[str] = None
    closing_date: Optional[date] = None


class PropertyResponse(BaseModel):
    id: int
    address: str
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    mls_id: Optional[str]
    property_type: Optional[str]
    list_price: Optional[float]
    sale_price: Optional[float]
    transaction_type: Optional[str]
    transaction_status: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/properties", response_model=List[PropertyResponse])
async def list_properties(
    transaction_status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List properties.
    
    Note: Properties are shared across user's messages, not user-specific.
    This is a simplified implementation.
    """
    query = db.query(Property)
    
    if transaction_status:
        query = query.filter(Property.transaction_status == transaction_status)
    
    properties = query.order_by(Property.created_at.desc()).all()
    
    return properties


@router.post("/properties", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new property"""
    new_property = Property(
        address=property_data.address,
        city=property_data.city,
        state=property_data.state,
        zip_code=property_data.zip_code,
        mls_id=property_data.mls_id,
        property_type=property_data.property_type,
        list_price=property_data.list_price,
        transaction_type=property_data.transaction_type,
        transaction_status="active"
    )
    
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    
    return new_property


@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get property details"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return property_obj


@router.patch("/properties/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_update: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update property"""
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Update fields
    for field, value in property_update.dict(exclude_unset=True).items():
        setattr(property_obj, field, value)
    
    db.commit()
    db.refresh(property_obj)
    
    return property_obj


@router.get("/properties/{property_id}/related")
async def get_property_related(
    property_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all related items for a property (emails, tasks, documents).
    """
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return {
        "property": PropertyResponse.from_orm(property_obj),
        "messages": [{"id": m.id, "subject": m.subject} for m in property_obj.messages],
        "tasks": [{"id": t.id, "title": t.title} for t in property_obj.tasks],
        "documents": property_obj.document_urls or []
    }

