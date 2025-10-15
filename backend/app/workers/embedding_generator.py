"""
Generate embeddings for semantic email search
"""
from typing import List
from sentence_transformers import SentenceTransformer
from .celery_app import celery_app, BaseEmailSyncTask
from ..db import SessionLocal
from ..models.message import Message
from ..integrations.vector_store import VectorStore
from ..security.encryption import decrypt_data
import logging

logger = logging.getLogger(__name__)

# Load embedding model (cached globally)
embedding_model = None

def get_embedding_model():
    """Lazy load embedding model"""
    global embedding_model
    if embedding_model is None:
        # Using smaller, faster model for production
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return embedding_model


@celery_app.task(base=BaseEmailSyncTask, bind=True)
def generate_email_embedding(self, message_id: int, db: Session = None):
    """
    Generate and store embedding for an email.
    
    Args:
        message_id: Message ID to process
        db: Database session
    """
    try:
        # Get message
        message = db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            logger.warning(f"Message {message_id} not found for embedding")
            return {"status": "error", "reason": "message_not_found"}
        
        # Skip if already has embedding
        if message.vector_id:
            return {"status": "skipped", "reason": "already_embedded"}
        
        # Prepare text for embedding
        decrypted_body = decrypt_data(message.encrypted_body)
        email_text = f"{message.subject} {decrypted_body}"[:1000]  # Limit to 1000 chars
        
        # Generate embedding
        model = get_embedding_model()
        embedding = model.encode(email_text).tolist()
        
        # Store in Pinecone
        vector_store = VectorStore()
        
        # Get email account for user_id
        if message.email_account_id:
            from ..models.email_account import EmailAccount
            account = db.query(EmailAccount).filter(EmailAccount.id == message.email_account_id).first()
            user_id = account.user_id if account else 0
        else:
            user_id = 0
        
        metadata = {
            "subject": message.subject or "",
            "sender": message.sender_email or "",
            "category": message.category.value if message.category else "general",
            "priority": message.priority.value if message.priority else "low",
            "date": message.received_at.isoformat() if message.received_at else ""
        }
        
        import asyncio
        result = asyncio.run(vector_store.upsert_email(
            message_id=str(message.id),
            user_id=user_id,
            embedding=embedding,
            metadata=metadata
        ))
        
        if result.get("success"):
            # Update message with vector ID
            message.vector_id = result.get("vector_id")
            db.commit()
            
            logger.info(f"Generated embedding for message {message_id}")
            
            return {
                "status": "success",
                "message_id": message_id,
                "vector_id": result.get("vector_id")
            }
        else:
            logger.error(f"Failed to store embedding: {result.get('error')}")
            return {"status": "error", "error": result.get("error")}
        
    except Exception as e:
        logger.exception(f"Error generating embedding for message {message_id}")
        return {"status": "error", "error": str(e)}

