"""Vision router - VisionHome AI endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..models.vision_scan import VisionScan
from ..agents.vision_agent import VisionAgent
from ..utils.subscription_utils import check_tier_limit
from ..shared.exceptions import SubscriptionLimitException, VisionProcessingException
from ..config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(
    prefix="/vision",
    tags=["VisionHome AI"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Subscription tier or usage limit"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


# Pydantic Response Models
class VisionMatch(BaseModel):
    """Property match from Zillow"""
    property_id: str
    address: str
    price: Optional[float] = None
    similarity_score: float = Field(..., ge=0, le=100, description="Similarity score 0-100")
    url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "property_id": "zpid123456",
                "address": "123 Main St, Seattle, WA 98101",
                "price": 450000,
                "similarity_score": 87.5,
                "url": "https://www.zillow.com/homedetails/123-Main-St-Seattle-WA-98101/zpid123456/"
            }
        }


class RenovationSuggestion(BaseModel):
    """Renovation suggestion with overlay coordinates"""
    room: str
    suggestion: str
    estimated_cost: Optional[float] = None
    roi: Optional[float] = None
    overlay_coordinates: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "room": "kitchen",
                "suggestion": "Update cabinets and countertops",
                "estimated_cost": 15000,
                "roi": 85.0,
                "overlay_coordinates": {"x": 100, "y": 200, "width": 300, "height": 400}
            }
        }


class VisionAnalysisResponse(BaseModel):
    """Response model for vision analysis"""
    id: int
    status: str
    property_address: Optional[str] = None
    property_type: Optional[str] = None
    matches: List[Dict[str, Any]] = Field(default_factory=list, description="Matched properties")
    matches_count: int = 0
    renovations: Dict[str, Any] = Field(default_factory=dict, description="Renovation suggestions")
    vision_labels: List[str] = Field(default_factory=list, description="Detected labels")
    rooms_detected: List[str] = Field(default_factory=list, description="Detected rooms")
    created_at: str
    completed_at: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "status": "completed",
                "property_address": "123 Main St, Seattle, WA",
                "property_type": "house",
                "matches_count": 5,
                "matches": [],
                "renovations": {},
                "vision_labels": ["kitchen", "living room", "bedroom"],
                "rooms_detected": ["kitchen", "living room", "bedroom", "bathroom"],
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:30:45Z"
            }
        }


class VisionScanPreview(BaseModel):
    """Vision scan preview model"""
    id: int
    property_address: Optional[str] = None
    property_type: Optional[str] = None
    status: str
    matches: List[Dict[str, Any]]
    renovations: Dict[str, Any]
    vision_labels: List[str]
    rooms_detected: List[str]
    created_at: str
    completed_at: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "property_address": "123 Main St, Seattle, WA",
                "property_type": "house",
                "status": "completed",
                "matches": [],
                "renovations": {},
                "vision_labels": ["kitchen", "living room"],
                "rooms_detected": ["kitchen", "living room"],
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:30:45Z"
            }
        }


class VisionScanListResponse(BaseModel):
    """Response model for listing vision scans"""
    scans: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int

    class Config:
        json_schema_extra = {
            "example": {
                "scans": [
                    {
                        "id": 123,
                        "property_address": "123 Main St, Seattle, WA",
                        "status": "completed",
                        "matches_count": 5,
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 20
            }
        }


@router.post(
    "/analyze",
    response_model=VisionAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze Property Image",
    description="""
    Analyze a property image using VisionHome AI computer vision technology.
    
    **Features:**
    - Object detection and labeling using Google Cloud Vision
    - Property matching with Zillow database
    - Virtual renovation suggestions with ROI estimates
    - Room detection and classification
    
    **Requirements:**
    - Image file (jpg, png, gif, webp)
    - Valid subscription tier
    - Usage limit: Free tier (5/month), Solo (50/month), Pro (100/month)
    
    **Processing:**
    - Analysis runs asynchronously via Celery
    - Results include property matches, renovation suggestions, and detected features
    """,
    responses={
        201: {
            "description": "Analysis started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 123,
                        "status": "processing",
                        "matches_count": 0,
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid file type or file read error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid file type. Supported: jpg, png, gif, webp"
                    }
                }
            }
        },
        403: {
            "description": "Subscription tier limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Usage limit reached for vision_scans",
                        "feature": "vision_scans",
                        "limit": 5,
                        "current_usage": 5
                    }
                }
            }
        },
        500: {
            "description": "Vision processing failed",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Vision processing failed: Unable to connect to Google Vision API"
                    }
                }
            }
        }
    }
)
@limiter.limit("10/minute")
async def analyze_property_image(
    request: Request,
    file: UploadFile = File(..., description="Property image file (jpg, png, gif, webp)"),
    property_address: Optional[str] = Form(None, description="Optional property address for better matching"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze property image using VisionHome AI computer vision.
    
    Upload a property image to get:
    - Property matches from Zillow database
    - Virtual renovation suggestions with ROI estimates
    - Room detection and classification
    - Object detection and labeling
    
    **Example usage:**
    ```python
    import requests
    
    with open('property.jpg', 'rb') as f:
        response = requests.post(
            'https://api.realinbox.ai/api/v1/vision/analyze',
            files={'file': f},
            data={'property_address': '123 Main St, Seattle, WA'},
            headers={'Authorization': 'Bearer YOUR_TOKEN'}
        )
    ```
    """
    # Check tier limit
    try:
        check_tier_limit(db, current_user, 'vision_scans', raise_exception=True)
    except SubscriptionLimitException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": str(e),
                "feature": e.feature,
                "limit": e.limit,
                "current_usage": e.current_usage
            }
        )
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Supported: jpg, png, gif, webp"
        )
    
    # Read file content
    try:
        image_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )
    
    # Create scan record
    scan = VisionScan(
        user_id=current_user.id,
        image_url="",  # Will be set after upload to S3
        image_filename=file.filename,
        property_address=property_address,
        status="processing"
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    # Process image (async via Celery task would be better)
    try:
        vision_agent = VisionAgent()
        analysis_result = await vision_agent.analyze_property_image(
            image_content=image_content,
            property_address=property_address
        )
        
        # Update scan with results
        scan.matches = analysis_result.get('matches', [])
        scan.renovations = analysis_result.get('renovations', {})
        scan.vision_labels = analysis_result.get('vision_labels', [])
        scan.rooms_detected = analysis_result.get('rooms_detected', [])
        scan.property_type = analysis_result.get('analysis', {}).get('property_type')
        scan.status = "completed"
        scan.completed_at = datetime.utcnow()
        
        db.commit()
        
        return VisionAnalysisResponse(
            id=scan.id,
            status=scan.status,
            property_address=scan.property_address,
            property_type=scan.property_type,
            matches=analysis_result.get('matches', []),
            matches_count=len(analysis_result.get('matches', [])),
            renovations=analysis_result.get('renovations', {}),
            vision_labels=analysis_result.get('vision_labels', []),
            rooms_detected=analysis_result.get('rooms_detected', []),
            created_at=scan.created_at.isoformat() if scan.created_at else datetime.utcnow().isoformat(),
            completed_at=scan.completed_at.isoformat() if scan.completed_at else None
        )
        
    except VisionProcessingException as e:
        scan.status = "failed"
        scan.processing_error = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vision processing failed: {str(e)}"
        )
    except Exception as e:
        scan.status = "failed"
        scan.processing_error = str(e)
        db.commit()
        logger.error(f"Unexpected error in vision analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process image"
        )


@router.get(
    "/preview/{scan_id}",
    response_model=VisionScanPreview,
    summary="Get Vision Scan Details",
    description="Retrieve detailed results for a specific vision scan by ID",
    responses={
        200: {
            "description": "Vision scan details retrieved successfully"
        },
        404: {
            "description": "Vision scan not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Vision scan not found"
                    }
                }
            }
        }
    }
)
@limiter.limit("30/minute")
async def get_vision_scan(
    request: Request,
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed vision scan results by ID.
    
    Returns all analysis results including:
    - Property matches from Zillow
    - Renovation suggestions
    - Detected rooms and features
    - Vision labels
    """
    scan = db.query(VisionScan).filter(
        VisionScan.id == scan_id,
        VisionScan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vision scan not found or access denied"
        )
    
    return VisionScanPreview(
        id=scan.id,
        property_address=scan.property_address,
        property_type=scan.property_type,
        status=scan.status,
        matches=scan.matches or [],
        renovations=scan.renovations or {},
        vision_labels=scan.vision_labels or [],
        rooms_detected=scan.rooms_detected or [],
        created_at=scan.created_at.isoformat() if scan.created_at else "",
        completed_at=scan.completed_at.isoformat() if scan.completed_at else None
    )


@router.get(
    "/scans",
    response_model=VisionScanListResponse,
    summary="List Vision Scans",
    description="List all vision scans for the authenticated user with pagination",
    responses={
        200: {
            "description": "Vision scans retrieved successfully"
        }
    }
)
@limiter.limit("30/minute")
async def list_vision_scans(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all vision scans for the authenticated user.
    
    Supports pagination with skip and limit parameters.
    Results are ordered by creation date (newest first).
    """
    scans = db.query(VisionScan).filter(
        VisionScan.user_id == current_user.id
    ).order_by(VisionScan.created_at.desc()).offset(skip).limit(limit).all()
    
    total = db.query(VisionScan).filter(VisionScan.user_id == current_user.id).count()
    
    return VisionScanListResponse(
        scans=[
            {
                "id": scan.id,
                "property_address": scan.property_address,
                "status": scan.status,
                "matches_count": len(scan.matches or []),
                "created_at": scan.created_at.isoformat() if scan.created_at else None
            }
            for scan in scans
        ],
        total=total,
        skip=skip,
        limit=limit
    )

