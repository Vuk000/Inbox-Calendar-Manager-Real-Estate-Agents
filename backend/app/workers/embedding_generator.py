"""
Generate embeddings for semantic email search
"""
from typing import List
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from .celery_app import celery_app
from ..db import SessionLocal
from ..models.communication_log import CommunicationLog, CommunicationType
from ..integrations.vector_store import VectorStore
from ..security.encryption import decrypt_data
import logging

logger = logging.getLogger(__name__)

# Import BaseEmailSyncTask from tasks module
from ..tasks.email_sync_task import BaseEmailSyncTask

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

# Load embedding model (cached globally)
embedding_model = None

def get_embedding_model():
    """Lazy load embedding model"""
    global embedding_model
    if embedding_model is None:
        # Using smaller, faster model for production
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return embedding_model


@celery_task(base=BaseEmailSyncTask, bind=True)
def generate_email_embedding(self, comm_log_id: int, db: Session = None):
    """
    Generate and store embedding for an email communication.
    
    Args:
        comm_log_id: CommunicationLog ID to process
        db: Database session
    """
    try:
        # Get communication log
        comm_log = db.query(CommunicationLog).filter(
            CommunicationLog.id == comm_log_id,
            CommunicationLog.communication_type == CommunicationType.EMAIL
        ).first()
        
        if not comm_log:
            logger.warning(f"CommunicationLog {comm_log_id} not found for embedding")
            return {"status": "error", "reason": "comm_log_not_found"}
        
        # Prepare text for embedding (subject + body or summary)
        email_text = f"{comm_log.subject or ''} {comm_log.body or comm_log.summary or ''}"[:1000]  # Limit to 1000 chars
        
        # Generate embedding
        model = get_embedding_model()
        embedding = model.encode(email_text).tolist()
        
        # Store in Pinecone
        vector_store = VectorStore()
        
        user_id = comm_log.user_id
        
        metadata = {
            "subject": comm_log.subject or "",
            "sender": comm_log.from_address or "",
            "urgency": str(comm_log.urgency_score) if comm_log.urgency_score else "0",
            "sentiment": str(comm_log.sentiment_score) if comm_log.sentiment_score else "0",
            "date": comm_log.occurred_at.isoformat() if comm_log.occurred_at else "",
            "contact_id": str(comm_log.contact_id)
        }
        
        import asyncio
        result = asyncio.run(vector_store.upsert_email(
            message_id=str(comm_log.id),
            user_id=user_id,
            embedding=embedding,
            metadata=metadata
        ))
        
        if result.get("success"):
            logger.info(f"Generated embedding for communication {comm_log_id}")
            
            return {
                "status": "success",
                "comm_log_id": comm_log_id,
                "vector_id": result.get("vector_id")
            }
        else:
            logger.error(f"Failed to store embedding: {result.get('error')}")
            return {"status": "error", "error": result.get("error")}
        
    except Exception as e:
        logger.exception(f"Error generating embedding for communication {comm_log_id}")
        return {"status": "error", "error": str(e)}

