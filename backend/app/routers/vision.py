"""Vision router - VisionHome AI endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import Optional
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

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


@router.post("/vision/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_property_image(
    request: Request,
    file: UploadFile = File(...),
    property_address: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze property image using VisionHome AI.
    
    - **file**: Image file (jpg, png, etc.)
    - **property_address**: Optional property address for matching
    
    Requires subscription tier: free tier gets 5 scans/month
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
        
        return {
            "id": scan.id,
            "status": scan.status,
            "analysis": analysis_result,
            "matches_count": len(analysis_result.get('matches', [])),
            "created_at": scan.created_at.isoformat()
        }
        
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


@router.get("/vision/preview/{scan_id}")
async def get_vision_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get vision scan details by ID"""
    scan = db.query(VisionScan).filter(
        VisionScan.id == scan_id,
        VisionScan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vision scan not found"
        )
    
    return {
        "id": scan.id,
        "property_address": scan.property_address,
        "property_type": scan.property_type,
        "status": scan.status,
        "matches": scan.matches,
        "renovations": scan.renovations,
        "vision_labels": scan.vision_labels,
        "rooms_detected": scan.rooms_detected,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None
    }


@router.get("/vision/scans")
async def list_vision_scans(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's vision scans"""
    scans = db.query(VisionScan).filter(
        VisionScan.user_id == current_user.id
    ).order_by(VisionScan.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "scans": [
            {
                "id": scan.id,
                "property_address": scan.property_address,
                "status": scan.status,
                "matches_count": len(scan.matches or []),
                "created_at": scan.created_at.isoformat() if scan.created_at else None
            }
            for scan in scans
        ],
        "total": db.query(VisionScan).filter(VisionScan.user_id == current_user.id).count()
    }

