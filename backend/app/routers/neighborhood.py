"""Neighborhood router - Neighborhood Whisper endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..models.neighborhood_report import NeighborhoodReport
from ..agents.whisper_agent import WhisperAgent
from ..utils.subscription_utils import check_tier_limit
from ..shared.exceptions import SubscriptionLimitException, NeighborhoodSearchException

router = APIRouter(
    prefix="/neighborhood",
    tags=["Neighborhood Whisper"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Subscription tier or usage limit"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"}
    }
)
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


class NeighborhoodSearchRequest(BaseModel):
    """Request model for neighborhood search"""
    query: str = Field(..., min_length=5, max_length=500, description="Neighborhood search query")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences for matching")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "family-friendly neighborhood in Seattle with good schools",
                "preferences": {
                    "schools": "important",
                    "parks": "important",
                    "commute": "prefer_short"
                }
            }
        }


class NeighborhoodSearchResponse(BaseModel):
    """Response model for neighborhood search"""
    id: int
    query: str
    location: str
    fit_score: Optional[float] = Field(None, ge=0, le=100, description="Fit score 0-100")
    status: str
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "query": "family-friendly neighborhood in Seattle",
                "location": "Seattle, WA",
                "fit_score": 87.5,
                "status": "completed",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class NeighborhoodReportDetail(BaseModel):
    """Detailed neighborhood report model"""
    id: int
    query: str
    location: str
    zip_code: Optional[str]
    fit_score: Optional[float]
    amenities_score: Optional[float]
    sentiment_score: Optional[float]
    eco_score: Optional[float]
    forecast: Dict[str, Any]
    eco_roi: Optional[float]
    review_insights: List[Dict[str, Any]]
    similar_neighborhoods: List[Dict[str, Any]]
    market_data: Dict[str, Any]
    status: str
    created_at: str
    completed_at: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "query": "family-friendly neighborhood in Seattle",
                "location": "Seattle, WA",
                "zip_code": "98101",
                "fit_score": 87.5,
                "amenities_score": 85.0,
                "sentiment_score": 0.75,
                "eco_score": 82.0,
                "forecast": {"price_trend": "up", "growth_rate": 5.2},
                "eco_roi": 15.5,
                "review_insights": [],
                "similar_neighborhoods": [],
                "market_data": {},
                "status": "completed",
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:30:45Z"
            }
        }


class NeighborhoodReportListResponse(BaseModel):
    """Response model for listing neighborhood reports"""
    reports: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int

    class Config:
        json_schema_extra = {
            "example": {
                "reports": [
                    {
                        "id": 123,
                        "query": "family-friendly neighborhood",
                        "location": "Seattle, WA",
                        "fit_score": 87.5,
                        "status": "completed",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 20
            }
        }


@router.post(
    "/search",
    response_model=NeighborhoodSearchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Search Neighborhood",
    description="""
    Analyze a neighborhood using Neighborhood Whisper ML/NLP technology.
    
    **Features:**
    - Natural language query parsing using OpenAI GPT-4o-mini
    - Sentiment analysis from Yelp reviews
    - ML-powered fit score calculation
    - Market forecast generation
    - Similar neighborhood discovery using Pinecone vector search
    
    **Requirements:**
    - Valid subscription tier
    - Usage limit: Free tier (10/month), Solo (50/month), Pro (100/month)
    
    **Processing:**
    - Analysis runs synchronously (can take 10-30 seconds)
    - Results include fit score, amenities score, sentiment, eco score, and forecast
    """,
    responses={
        201: {
            "description": "Analysis started successfully"
        },
        400: {
            "description": "Invalid request"
        },
        403: {
            "description": "Subscription tier limit exceeded"
        },
        500: {
            "description": "Neighborhood analysis failed"
        }
    }
)
@limiter.limit("10/minute")
async def search_neighborhood(
    request: Request,
    search_request: NeighborhoodSearchRequest,
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
        query=search_request.query,
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
            query=search_request.query,
            user_preferences=search_request.preferences
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


@router.get(
    "/report/{report_id}",
    response_model=NeighborhoodReportDetail,
    summary="Get Neighborhood Report",
    description="Retrieve detailed neighborhood analysis report by ID",
    responses={
        200: {"description": "Report retrieved successfully"},
        404: {"description": "Report not found"}
    }
)
@limiter.limit("30/minute")
async def get_neighborhood_report(
    request: Request,
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(NeighborhoodReport).filter(
        NeighborhoodReport.id == report_id,
        NeighborhoodReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Neighborhood report not found or access denied"
        )
    
    return NeighborhoodReportDetail(
        id=report.id,
        query=report.query,
        location=report.location,
        zip_code=report.zip_code,
        fit_score=float(report.fit_score) if report.fit_score else None,
        amenities_score=float(report.amenities_score) if report.amenities_score else None,
        sentiment_score=float(report.sentiment_score) if report.sentiment_score else None,
        eco_score=float(report.eco_score) if report.eco_score else None,
        forecast=report.forecast or {},
        eco_roi=float(report.eco_roi) if report.eco_roi else None,
        review_insights=report.review_insights or [],
        similar_neighborhoods=report.similar_neighborhoods or [],
        market_data=report.market_data or {},
        status=report.status,
        created_at=report.created_at.isoformat() if report.created_at else "",
        completed_at=report.completed_at.isoformat() if report.completed_at else None
    )


@router.get(
    "/reports",
    response_model=NeighborhoodReportListResponse,
    summary="List Neighborhood Reports",
    description="List all neighborhood reports for the authenticated user with pagination",
    responses={
        200: {"description": "Reports retrieved successfully"}
    }
)
@limiter.limit("30/minute")
async def list_neighborhood_reports(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reports = db.query(NeighborhoodReport).filter(
        NeighborhoodReport.user_id == current_user.id
    ).order_by(NeighborhoodReport.created_at.desc()).offset(skip).limit(limit).all()
    
    total = db.query(NeighborhoodReport).filter(NeighborhoodReport.user_id == current_user.id).count()
    
    return NeighborhoodReportListResponse(
        reports=[
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
        total=total,
        skip=skip,
        limit=limit
    )

