"""Celery tasks for VisionHome AI - Async CV processing"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..workers.celery_app import celery_app
from ..agents.vision_agent import VisionAgent
from ..models.vision_scan import VisionScan
from ..db import SessionLocal
from ..shared.exceptions import VisionProcessingException

logger = logging.getLogger(__name__)

# Only import Task if celery_app is available
if celery_app is not None:
    from celery import Task
else:
    # Mock Task class if Celery unavailable
    class Task:
        pass


# Decorator helper for conditional Celery task registration
def celery_task(*args, **kwargs):
    """Conditional Celery task decorator - only registers if celery_app is available"""
    if celery_app is not None:
        return celery_app.task(*args, **kwargs)
    else:
        # Return a no-op decorator if Celery unavailable
        def decorator(func):
            logger.warning(f"Celery unavailable - task {func.__name__} will not be registered")
            return func
        return decorator


@celery_task(bind=True, name="vision.process_image", max_retries=3)
def process_vision_scan(
    self,
    scan_id: int,
    image_content: bytes,
    property_address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process vision scan asynchronously.
    
    Args:
        scan_id: VisionScan ID
        image_content: Image bytes
        property_address: Optional property address
        
    Returns:
        Processing result
    """
    db = SessionLocal()
    try:
        scan = db.query(VisionScan).filter(VisionScan.id == scan_id).first()
        if not scan:
            raise ValueError(f"Vision scan {scan_id} not found")
        
        # Process with Vision agent
        vision_agent = VisionAgent()
        
        # Note: This is a sync function but vision_agent uses async
        # In production, use async celery tasks or run sync
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        analysis_result = loop.run_until_complete(
            vision_agent.analyze_property_image(
                image_content=image_content,
                property_address=property_address
            )
        )
        
        # Update scan with results
        scan.matches = analysis_result.get('similar_properties', [])
        scan.renovations = analysis_result.get('llm_interpretation', {}).get('renovation_suggestions', [])
        scan.vision_labels = analysis_result.get('vision_analysis', {}).get('labels', [])
        scan.rooms_detected = analysis_result.get('vision_analysis', {}).get('objects', [])
        scan.property_type = analysis_result.get('llm_interpretation', {}).get('property_type')
        scan.status = "completed"
        scan.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "scan_id": scan_id,
            "matches_count": len(analysis_result.get('similar_properties', []))
        }
        
    except Exception as e:
        logger.error(f"Vision scan processing error: {e}")
        
        # Update scan status
        if 'scan' in locals() and scan:
            scan.status = "failed"
            scan.processing_error = str(e)
            db.commit()
        
        # Retry if transient error
        if celery_app is not None and hasattr(self, 'request') and self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)
        
        raise VisionProcessingException(f"Failed to process vision scan: {str(e)}")
    
    finally:
        db.close()

