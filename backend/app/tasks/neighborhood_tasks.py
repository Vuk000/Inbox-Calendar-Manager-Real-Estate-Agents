"""Celery tasks for Neighborhood Whisper - Async ML forecasting"""
from celery import Task
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..workers.celery_app import celery_app
from ..agents.whisper_agent import WhisperAgent
from ..models.neighborhood_report import NeighborhoodReport
from ..db import SessionLocal
from ..shared.exceptions import NeighborhoodSearchException

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="neighborhood.generate_report", max_retries=3)
def generate_neighborhood_report(
    self: Task,
    report_id: int,
    query: str,
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate neighborhood report asynchronously.
    
    Args:
        report_id: NeighborhoodReport ID
        query: Search query
        user_preferences: Optional user preferences
        
    Returns:
        Processing result
    """
    db = SessionLocal()
    try:
        report = db.query(NeighborhoodReport).filter(NeighborhoodReport.id == report_id).first()
        if not report:
            raise ValueError(f"Neighborhood report {report_id} not found")
        
        # Process with Whisper agent
        whisper_agent = WhisperAgent()
        
        # Run async function
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        analysis_result = loop.run_until_complete(
            whisper_agent.analyze_neighborhood(
                query=query,
                user_preferences=user_preferences
            )
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
        report.market_data = analysis_result.get('forecast', {})
        report.status = "completed"
        report.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "report_id": report_id,
            "fit_score": analysis_result.get('fit_score')
        }
        
    except Exception as e:
        logger.error(f"Neighborhood report generation error: {e}")
        
        # Update report status
        if 'report' in locals() and report:
            report.status = "failed"
            report.processing_error = str(e)
            db.commit()
        
        # Retry if transient error
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        
        raise NeighborhoodSearchException(f"Failed to generate neighborhood report: {str(e)}")
    
    finally:
        db.close()

