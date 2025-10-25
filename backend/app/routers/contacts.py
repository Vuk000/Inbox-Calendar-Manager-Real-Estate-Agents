"""Contact management API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from ..dependencies import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.contact import Contact
from ..services.contact_service import ContactService
from ..shared.exceptions import ValidationException

router = APIRouter(prefix="/contacts", tags=["Contacts"])


# Pydantic schemas
class ContactBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    secondary_phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=500)
    address_line2: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: str = "USA"
    contact_type: Optional[str] = Field(None, max_length=50)
    lead_source: Optional[str] = Field(None, max_length=100)
    preferred_contact_method: Optional[str] = Field(None, max_length=50)
    tags: List[str] = []
    custom_fields: dict = {}
    linkedin_url: Optional[str] = Field(None, max_length=500)
    facebook_url: Optional[str] = Field(None, max_length=500)
    twitter_handle: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    secondary_phone: Optional[str] = Field(None, max_length=50)
    address_line1: Optional[str] = Field(None, max_length=500)
    address_line2: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = None
    contact_type: Optional[str] = Field(None, max_length=50)
    contact_status: Optional[str] = Field(None, max_length=50)
    lead_source: Optional[str] = Field(None, max_length=100)
    preferred_contact_method: Optional[str] = Field(None, max_length=50)
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None
    linkedin_url: Optional[str] = Field(None, max_length=500)
    facebook_url: Optional[str] = Field(None, max_length=500)
    twitter_handle: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class ContactResponse(ContactBase):
    id: int
    user_id: int
    team_id: Optional[int]
    contact_status: str
    relationship_score: float
    last_contact_date: Optional[datetime]
    contact_frequency: int
    ai_insights: dict
    is_shared_with_team: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    contacts: List[ContactResponse]
    total: int
    skip: int
    limit: int


class CSVImportRequest(BaseModel):
    field_mapping: dict = Field(
        ...,
        example={
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "phone": "Phone"
        }
    )


class ShareContactRequest(BaseModel):
    team_id: int


# Endpoints
@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new contact"""
    try:
        contact = ContactService.create_contact(
            db=db,
            user_id=current_user.id,
            contact_data=contact_data.model_dump(exclude_unset=True)
        )
        return contact
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=ContactListResponse)
async def list_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    contact_type: Optional[str] = Query(None),
    contact_status: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List contacts with filters and pagination"""
    tag_list = tags.split(",") if tags else None
    
    contacts = ContactService.list_contacts(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        contact_type=contact_type,
        contact_status=contact_status,
        tags=tag_list
    )
    
    # Get total count (simplified - in production use a separate count query)
    total = len(contacts) if len(contacts) < limit else skip + len(contacts)
    
    return {
        "contacts": contacts,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single contact by ID"""
    contact = ContactService.get_contact(db, contact_id, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a contact"""
    try:
        contact = ContactService.update_contact(
            db=db,
            contact_id=contact_id,
            user_id=current_user.id,
            update_data=contact_data.model_dump(exclude_unset=True)
        )
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a contact"""
    try:
        success = ContactService.delete_contact(db, contact_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Contact not found")
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import", status_code=status.HTTP_200_OK)
async def import_contacts_csv(
    file: UploadFile = File(...),
    field_mapping: str = Query(..., description="JSON string of field mapping"),
    duplicate_strategy: str = Query("skip", description="How to handle duplicates: skip, update, or create_duplicate"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import contacts from CSV file with field mapping and enhanced error handling.
    
    Args:
        file: CSV file upload
        field_mapping: JSON string mapping CSV columns to contact fields
        duplicate_strategy: How to handle duplicate emails (skip, update, create_duplicate)
    
    Returns:
        Import results with detailed row-level error reporting
    """
    import json
    
    # Validate file type
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file with .csv extension")
    
    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
    
    try:
        # Parse field mapping
        try:
            mapping = json.loads(field_mapping)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid field_mapping JSON: {str(e)}")
        
        # Validate duplicate strategy
        if duplicate_strategy not in ["skip", "update", "create_duplicate"]:
            raise HTTPException(status_code=400, detail="duplicate_strategy must be: skip, update, or create_duplicate")
        
        # Import contacts with enhanced error handling
        result = ContactService.import_from_csv(
            db=db,
            user_id=current_user.id,
            csv_file=contents,
            field_mapping=mapping,
            duplicate_strategy=duplicate_strategy
        )
        
        return {
            **result,
            "file_name": file.filename,
            "file_size_bytes": len(contents)
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CSV import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/{contact_id}/timeline")
async def get_contact_timeline(
    contact_id: int,
    cursor: Optional[str] = Query(None, description="Pagination cursor (timestamp:id)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get communication timeline for a contact with cursor-based pagination.
    
    Performance target: <500ms response time
    
    Args:
        contact_id: Contact ID
        cursor: Pagination cursor in format "timestamp:id" 
        limit: Items per page (default 20, max 100)
    
    Returns:
        Timeline with communications and pagination metadata
    """
    import time
    start_time = time.time()
    
    # Verify contact exists and user has access
    contact = ContactService.get_contact(db, contact_id, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Get timeline with cursor pagination
    result = ContactService.get_contact_timeline(
        db=db,
        contact_id=contact_id,
        user_id=current_user.id,
        cursor=cursor,
        limit=limit
    )
    
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
    
    return {
        "contact_id": contact_id,
        "communications": result["communications"],
        "pagination": {
            "next_cursor": result["next_cursor"],
            "has_more": result["has_more"],
            "limit": limit
        },
        "meta": {
            "response_time_ms": round(elapsed_time, 2),
            "count": len(result["communications"])
        }
    }


@router.post("/{contact_id}/share", response_model=ContactResponse)
async def share_contact(
    contact_id: int,
    share_request: ShareContactRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share contact with team"""
    try:
        contact = ContactService.share_contact_with_team(
            db=db,
            contact_id=contact_id,
            user_id=current_user.id,
            team_id=share_request.team_id
        )
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))

