"""Calendar router - Calendar management with AI-powered suggestions"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..models.neighborhood_report import NeighborhoodReport
from ..agents.whisper_agent import WhisperAgent
from ..services.calendar_service import CalendarService

router = APIRouter()
logger = logging.getLogger(__name__)


class CalendarSuggestRequest(BaseModel):
    """Request model for calendar suggestions"""
    location: Optional[str] = Field(None, description="Property location or neighborhood")
    date_range_start: Optional[datetime] = Field(None, description="Start of date range for suggestions")
    date_range_end: Optional[datetime] = Field(None, description="End of date range for suggestions")
    event_type: Optional[str] = Field("property_showing", description="Type of event (property_showing, open_house, etc.)")
    max_suggestions: int = Field(5, ge=1, le=20, description="Maximum number of suggestions")


class CalendarSuggestion(BaseModel):
    """Individual calendar suggestion"""
    suggested_date: datetime
    suggested_time: str
    confidence_score: float
    reasoning: str
    neighborhood_fit_score: Optional[float] = None
    market_forecast: Optional[Dict[str, Any]] = None
    recommended_duration_minutes: int = 60


class CalendarSuggestResponse(BaseModel):
    """Response model for calendar suggestions"""
    suggestions: List[CalendarSuggestion]
    location: Optional[str] = None
    forecast_used: bool = False


@router.post("/calendar/suggest", response_model=CalendarSuggestResponse)
async def suggest_calendar_events(
    request: CalendarSuggestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Suggest optimal calendar events based on neighborhood forecasts.
    
    Uses Neighborhood Whisper forecasts to suggest the best times for:
    - Property showings
    - Open houses
    - Neighborhood tours
    
    - **location**: Property location or neighborhood
    - **date_range_start**: Start of date range for suggestions
    - **date_range_end**: End of date range for suggestions
    - **event_type**: Type of event (property_showing, open_house, etc.)
    - **max_suggestions**: Maximum number of suggestions to return
    """
    try:
        # Set default date range if not provided (next 7 days)
        if not request.date_range_start:
            request.date_range_start = datetime.utcnow()
        if not request.date_range_end:
            request.date_range_end = datetime.utcnow() + timedelta(days=7)
        
        suggestions = []
        forecast_used = False
        
        # If location provided, try to get neighborhood forecast
        if request.location:
            try:
                # Get most recent neighborhood report for this location
                recent_report = db.query(NeighborhoodReport).filter(
                    NeighborhoodReport.user_id == current_user.id,
                    NeighborhoodReport.location.ilike(f"%{request.location}%"),
                    NeighborhoodReport.status == "completed"
                ).order_by(NeighborhoodReport.created_at.desc()).first()
                
                if recent_report and recent_report.forecast:
                    forecast_used = True
                    forecast = recent_report.forecast
                    fit_score = float(recent_report.fit_score) if recent_report.fit_score else None
                    
                    # Use forecast to suggest optimal times
                    # Example: If forecast shows high demand, suggest more showings
                    demand_index = forecast.get('demand_index', 5.0)
                    
                    # Generate suggestions based on forecast
                    # Higher demand = more frequent suggestions
                    num_suggestions = min(
                        request.max_suggestions,
                        max(3, int(demand_index / 2))  # Scale with demand
                    )
                    
                    # Suggest times spread across the date range
                    date_range = (request.date_range_end - request.date_range_start).days
                    interval_days = max(1, date_range // num_suggestions)
                    
                    for i in range(num_suggestions):
                        suggested_date = request.date_range_start + timedelta(days=i * interval_days)
                        
                        # Best times for property showings (weekends preferred, mornings)
                        if suggested_date.weekday() >= 5:  # Weekend
                            suggested_time = "10:00"
                            confidence = 0.8
                            reasoning = "Weekend morning showing - optimal for buyers"
                        elif suggested_date.weekday() < 5:  # Weekday
                            suggested_time = "17:00"
                            confidence = 0.6
                            reasoning = "Weekday evening showing - after work hours"
                        else:
                            suggested_time = "14:00"
                            confidence = 0.5
                            reasoning = "Midday showing"
                        
                        # Adjust confidence based on fit score
                        if fit_score:
                            if fit_score > 70:
                                confidence += 0.1
                                reasoning += f" (High neighborhood fit: {fit_score:.1f}%)"
                            elif fit_score < 50:
                                confidence -= 0.1
                                reasoning += f" (Lower neighborhood fit: {fit_score:.1f}%)"
                        
                        suggestions.append(CalendarSuggestion(
                            suggested_date=suggested_date.replace(hour=int(suggested_time.split(':')[0]), minute=0),
                            suggested_time=suggested_time,
                            confidence_score=min(1.0, max(0.0, confidence)),
                            reasoning=reasoning,
                            neighborhood_fit_score=fit_score,
                            market_forecast=forecast,
                            recommended_duration_minutes=60 if request.event_type == "property_showing" else 120
                        ))
                
            except Exception as e:
                logger.warning(f"Could not use neighborhood forecast for suggestions: {e}")
        
        # If no forecast-based suggestions, generate generic suggestions
        if not suggestions:
            date_range = (request.date_range_end - request.date_range_start).days
            num_suggestions = min(request.max_suggestions, max(3, date_range // 2))
            interval_days = max(1, date_range // num_suggestions)
            
            for i in range(num_suggestions):
                suggested_date = request.date_range_start + timedelta(days=i * interval_days)
                
                # Default to weekend mornings if possible
                if suggested_date.weekday() >= 5:  # Weekend
                    suggested_time = "10:00"
                    confidence = 0.7
                    reasoning = "Weekend morning - optimal for property showings"
                else:
                    suggested_time = "17:00"
                    confidence = 0.5
                    reasoning = "Weekday evening - after work hours"
                
                suggestions.append(CalendarSuggestion(
                    suggested_date=suggested_date.replace(hour=int(suggested_time.split(':')[0]), minute=0),
                    suggested_time=suggested_time,
                    confidence_score=confidence,
                    reasoning=reasoning,
                    recommended_duration_minutes=60 if request.event_type == "property_showing" else 120
                ))
        
        return CalendarSuggestResponse(
            suggestions=suggestions[:request.max_suggestions],
            location=request.location,
            forecast_used=forecast_used
        )
        
    except Exception as e:
        logger.error(f"Error generating calendar suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate calendar suggestions: {str(e)}"
        )


@router.get("/calendar/suggestions")
async def get_calendar_suggestions(
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get calendar suggestions (legacy endpoint, redirects to POST /calendar/suggest).
    """
    request = CalendarSuggestRequest(
        location=location,
        date_range_start=start_date,
        date_range_end=end_date
    )
    return await suggest_calendar_events(request, current_user, db)

