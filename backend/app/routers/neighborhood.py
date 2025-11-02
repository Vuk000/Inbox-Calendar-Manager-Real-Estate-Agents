"""Neighborhood router - Neighborhood Whisper endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..models.neighborhood_report import NeighborhoodReport
from ..agents.whisper_agent import WhisperAgent
from ..utils.subscription_utils import check_tier_limit
from ..shared.exceptions import SubscriptionLimitException, NeighborhoodSearchException

router = APIRouter()
logger = logging.getLogger(__name__)


class NeighborhoodSearchRequest(BaseModel):
    """Request model for neighborhood search"""
    query: str = Field(..., min_length=5, description="Neighborhood search query")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class NeighborhoodSearchResponse(BaseModel):
    """Response model for neighborhood search"""
    id: int
    query: str
    location: str
    fit_score: Optional[float]
    status: str
    created_at: str


@router.post("/neighborhood/search", response_model=NeighborhoodSearchResponse, status_code=status.HTTP_201_CREATED)
async def search_neighborhood(
    request: NeighborhoodSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search neighborhood and generate fit score using Neighborhood Whisper.
    
    - **query**: Search query (e.g., "family-friendly neighborhood in Seattle")
    - **preferences**: Optional user preferences dict
    
    Requires subscription tier: free tier gets 10 searches/month
    """
    # Check tier limit
    try:
        check_tier_limit(db, current_user, 'neighborhood_searches', raise_exception=True)
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
    
    # Create report record
    report = NeighborhoodReport(
        user_id=current_user.id,
        query=request.query,
        location="",  # Will be set after parsing
        status="processing"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Analyze neighborhood
    try:
        whisper_agent = WhisperAgent()
        analysis_result = await whisper_agent.analyze_neighborhood(
            query=request.query,
            user_preferences=request.preferences
        )
        
        # Update report with results
        report.location = analysis_result.get('location', '')
        report.zip_code = analysis_result.get('zip_code')
        report.fit_score = analysis_result.get('fit_score')
        report.amenities_score = analysis_result.get('amenities_score')
        report.sentiment_score = analysis_result.get('sentiment_score')
        report.eco_score = analysis_result.get('eco_score')
        report.forecast = analysis_result.get('forecast', {})
        report.eco_roi = analysis_result.get('eco_roi')
        report.review_insights = analysis_result.get('review_insights', [])
        report.similar_neighborhoods = analysis_result.get('similar_neighborhoods', [])
        report.market_data = analysis_result.get('market_data', {})
        report.status = "completed"
        report.completed_at = datetime.utcnow()
        
        db.commit()
        
        return NeighborhoodSearchResponse(
            id=report.id,
            query=report.query,
            location=report.location,
            fit_score=float(report.fit_score) if report.fit_score else None,
            status=report.status,
            created_at=report.created_at.isoformat() if report.created_at else ""
        )
        
    except NeighborhoodSearchException as e:
        report.status = "failed"
        report.processing_error = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Neighborhood analysis failed: {str(e)}"
        )
    except Exception as e:
        report.status = "failed"
        report.processing_error = str(e)
        db.commit()
        logger.error(f"Unexpected error in neighborhood analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze neighborhood"
        )


@router.get("/neighborhood/report/{report_id}")
async def get_neighborhood_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get neighborhood report details by ID"""
    report = db.query(NeighborhoodReport).filter(
        NeighborhoodReport.id == report_id,
        NeighborhoodReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Neighborhood report not found"
        )
    
    return {
        "id": report.id,
        "query": report.query,
        "location": report.location,
        "zip_code": report.zip_code,
        "fit_score": float(report.fit_score) if report.fit_score else None,
        "amenities_score": float(report.amenities_score) if report.amenities_score else None,
        "sentiment_score": float(report.sentiment_score) if report.sentiment_score else None,
        "eco_score": float(report.eco_score) if report.eco_score else None,
        "forecast": report.forecast,
        "eco_roi": float(report.eco_roi) if report.eco_roi else None,
        "review_insights": report.review_insights,
        "similar_neighborhoods": report.similar_neighborhoods,
        "market_data": report.market_data,
        "status": report.status,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "completed_at": report.completed_at.isoformat() if report.completed_at else None
    }


@router.get("/neighborhood/reports")
async def list_neighborhood_reports(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's neighborhood reports"""
    reports = db.query(NeighborhoodReport).filter(
        NeighborhoodReport.user_id == current_user.id
    ).order_by(NeighborhoodReport.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "reports": [
            {
                "id": report.id,
                "query": report.query,
                "location": report.location,
                "fit_score": float(report.fit_score) if report.fit_score else None,
                "status": report.status,
                "created_at": report.created_at.isoformat() if report.created_at else None
            }
            for report in reports
        ],
        "total": db.query(NeighborhoodReport).filter(NeighborhoodReport.user_id == current_user.id).count()
    }

