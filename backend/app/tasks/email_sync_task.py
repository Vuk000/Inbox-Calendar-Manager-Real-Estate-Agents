"""
Email synchronization tasks using Celery
Handles periodic sync of Gmail and Outlook accounts
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import asyncio

from ..workers.celery_app import celery_app
from ..db import SessionLocal
from ..models.email_account import EmailAccount, EmailProvider, SyncStatus
from ..models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from ..models.user import User
from ..models.contact import Contact
from ..services.contact_service import ContactService
from ..integrations.gmail_integration import GmailIntegration
from ..integrations.outlook_integration import OutlookIntegration
from ..integrations.vector_store import VectorStore
from ..agents.triage_agent import TriageAgent
from ..security.encryption import encrypt_data, decrypt_data
from ..security.audit import log_action
from ..websocket.connection_manager import connection_manager
from ..shared.exceptions import (
    GmailIntegrationException,
    OutlookIntegrationException,
    TaskRetryException
)

logger = logging.getLogger(__name__)

# Only import Task if celery_app is available
if celery_app is not None:
    from celery import Task
else:
    # Mock Task class if Celery unavailable
    class Task:
        pass


class BaseEmailSyncTask(Task):
    """Base task with database session management"""
    
    def __call__(self, *args, **kwargs):
        db = SessionLocal()
        try:
            return self.run(*args, db=db, **kwargs)
        finally:
            db.close()


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


@celery_task(base=BaseEmailSyncTask, bind=True, max_retries=3)
def sync_gmail_account(self, user_id: int, account_id: int, db: Session = None) -> dict:
    """
    Sync emails from a Gmail account.
    
    Args:
        user_id: User ID
        account_id: EmailAccount ID
        db: Database session
        
    Returns:
        Dictionary with sync status and processed count
        
    Raises:
        GmailIntegrationException: If Gmail API fails
        TaskRetryException: If task needs to be retried
    """
    try:
        # Get email account
        account = db.query(EmailAccount).filter(
            EmailAccount.id == account_id,
            EmailAccount.user_id == user_id,
            EmailAccount.provider == EmailProvider.GMAIL
        ).first()
        
        if not account or not account.is_active:
            logger.warning(f"Gmail account {account_id} not found or inactive")
            return {"status": "skipped", "reason": "account_inactive"}
        
        # Update sync status
        account.sync_status = SyncStatus.SYNCING
        db.commit()
        
        # Initialize Gmail integration
        gmail = GmailIntegration()
        
        # List recent emails (last 100)
        result = asyncio.run(gmail.list_messages(
            encrypted_access_token=account.encrypted_access_token,
            encrypted_refresh_token=account.encrypted_refresh_token,
            max_results=100,
            query="is:unread OR newer_than:1d"  # Unread or last 24h
        ))
        
        if "error" in result:
            raise GmailIntegrationException(
                f"Gmail API error: {result['error']}",
                error_code="GMAIL_API_ERROR"
            )
        
        messages = result.get("messages", [])
        processed_count = 0
        
        # Get user for contact creation
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "reason": "user_not_found"}
        
        for msg in messages:
            # Check if communication already exists by external_id
            existing = db.query(CommunicationLog).filter(
                CommunicationLog.external_id == msg["id"],
                CommunicationLog.user_id == user_id
            ).first()
            
            if existing:
                continue  # Skip already processed
            
            # Get full message details
            msg_details = asyncio.run(gmail.get_message(
                encrypted_access_token=account.encrypted_access_token,
                message_id=msg["id"],
                encrypted_refresh_token=account.encrypted_refresh_token
            ))
            
            if "error" in msg_details:
                logger.error(f"Failed to fetch message {msg['id']}: {msg_details['error']}")
                continue
            
            # Parse sender email
            sender_email = msg_details.get("from", "")
            sender_name = msg_details.get("from_name", "")
            
            if not sender_email:
                logger.warning(f"No sender email for message {msg['id']}, skipping")
                continue
            
            # Get or create contact for sender
            contact = ContactService.get_or_create_contact_by_email(
                db=db,
                email=sender_email,
                user_id=user_id,
                sender_name=sender_name
            )
            
            # Create communication log entry
            new_comm_log = CommunicationLog(
                user_id=user_id,
                contact_id=contact.id,
                communication_type=CommunicationType.EMAIL,
                direction=CommunicationDirection.INBOUND,
                subject=msg_details.get("subject", ""),
                body=msg_details.get("body", ""),
                summary=msg_details.get("snippet", "")[:500],
                from_address=sender_email,
                to_address=account.email_address,
                external_id=msg_details["id"],
                has_attachments=msg_details.get("has_attachments", False),
                attachments=[{"filename": att.get("filename"), "size": att.get("size")} 
                           for att in msg_details.get("attachments", [])],
                occurred_at=datetime.fromisoformat(msg_details.get("date", datetime.utcnow().isoformat()))
            )
            
            db.add(new_comm_log)
            db.commit()
            db.refresh(new_comm_log)
            
            # Trigger AI processing
            process_email_with_ai.delay(new_comm_log.id)
            
            processed_count += 1
        
        # Update sync status
        account.sync_status = SyncStatus.IDLE
        account.last_sync_at = datetime.utcnow()
        account.sync_error_message = None
        db.commit()
        
        # Log audit
        asyncio.run(log_action(
            db=db,
            action="gmail_sync",
            user_id=user_id,
            description=f"Synced {processed_count} emails from Gmail",
            metadata={"account_id": account_id, "processed": processed_count}
        ))
        
        # Notify sync complete
        asyncio.run(connection_manager.notify_sync_status(
            user_id=user_id,
            status="complete",
            message=f"Synced {processed_count} new emails"
        ))
        
        logger.info(f"Successfully synced {processed_count} emails from Gmail account {account_id}")
        
        return {
            "status": "success",
            "account_id": account_id,
            "processed": processed_count
        }
        
    except GmailIntegrationException as e:
        logger.exception(f"Gmail integration error for account {account_id}")
        
        # Update account with error
        if account:
            account.sync_status = SyncStatus.ERROR
            account.sync_error_message = str(e)
            db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
    except Exception as e:
        logger.exception(f"Unexpected error syncing Gmail account {account_id}")
        
        # Update account with error
        if account:
            account.sync_status = SyncStatus.ERROR
            account.sync_error_message = str(e)
            db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_task(base=BaseEmailSyncTask, bind=True, max_retries=3)
def sync_outlook_account(self, user_id: int, account_id: int, db: Session = None) -> dict:
    """
    Sync emails from an Outlook account.
    
    Args:
        user_id: User ID
        account_id: EmailAccount ID
        db: Database session
        
    Returns:
        Dictionary with sync status and processed count
        
    Raises:
        OutlookIntegrationException: If Outlook API fails
        TaskRetryException: If task needs to be retried
    """
    try:
        # Get email account
        account = db.query(EmailAccount).filter(
            EmailAccount.id == account_id,
            EmailAccount.user_id == user_id,
            EmailAccount.provider == EmailProvider.OUTLOOK
        ).first()
        
        if not account or not account.is_active:
            logger.warning(f"Outlook account {account_id} not found or inactive")
            return {"status": "skipped", "reason": "account_inactive"}
        
        # Update sync status
        account.sync_status = SyncStatus.SYNCING
        db.commit()
        
        # Initialize Outlook integration
        outlook = OutlookIntegration()
        
        # List recent emails
        result = asyncio.run(outlook.list_messages(
            encrypted_access_token=account.encrypted_access_token,
            max_results=100,
            filter_query="isRead eq false or receivedDateTime ge " + 
                        datetime.utcnow().replace(hour=0, minute=0).isoformat() + "Z"
        ))
        
        if "error" in result:
            raise OutlookIntegrationException(
                f"Outlook API error: {result['error']}",
                error_code="OUTLOOK_API_ERROR"
            )
        
        messages = result.get("messages", [])
        processed_count = 0
        
        # Get user for contact creation
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "reason": "user_not_found"}
        
        for msg_data in messages:
            # Check if communication already exists by external_id
            existing = db.query(CommunicationLog).filter(
                CommunicationLog.external_id == msg_data["id"],
                CommunicationLog.user_id == user_id
            ).first()
            
            if existing:
                continue
            
            # Parse message
            msg_details = outlook._parse_message(msg_data)
            
            # Parse sender email
            sender_email = msg_details.get("from", "")
            sender_name = msg_details.get("from_name", "")
            
            if not sender_email:
                logger.warning(f"No sender email for message {msg_data['id']}, skipping")
                continue
            
            # Get or create contact for sender
            contact = ContactService.get_or_create_contact_by_email(
                db=db,
                email=sender_email,
                user_id=user_id,
                sender_name=sender_name
            )
            
            # Create communication log entry
            new_comm_log = CommunicationLog(
                user_id=user_id,
                contact_id=contact.id,
                communication_type=CommunicationType.EMAIL,
                direction=CommunicationDirection.INBOUND,
                subject=msg_details.get("subject", ""),
                body=msg_details.get("body", ""),
                summary=msg_details.get("body_preview", "")[:500],
                from_address=sender_email,
                to_address=account.email_address,
                external_id=msg_details["id"],
                has_attachments=msg_details.get("has_attachments", False),
                occurred_at=datetime.fromisoformat(msg_details.get("date", datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            )
            
            db.add(new_comm_log)
            db.commit()
            db.refresh(new_comm_log)
            
            # Trigger AI processing
            process_email_with_ai.delay(new_comm_log.id)
            
            processed_count += 1
        
        # Update sync status
        account.sync_status = SyncStatus.IDLE
        account.last_sync_at = datetime.utcnow()
        account.sync_error_message = None
        db.commit()
        
        # Log audit
        asyncio.run(log_action(
            db=db,
            action="outlook_sync",
            user_id=user_id,
            description=f"Synced {processed_count} emails from Outlook",
            metadata={"account_id": account_id, "processed": processed_count}
        ))
        
        logger.info(f"Successfully synced {processed_count} emails from Outlook account {account_id}")
        
        return {
            "status": "success",
            "account_id": account_id,
            "processed": processed_count
        }
        
    except OutlookIntegrationException as e:
        logger.exception(f"Outlook integration error for account {account_id}")
        
        # Update account with error
        if account:
            account.sync_status = SyncStatus.ERROR
            account.sync_error_message = str(e)
            db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        
    except Exception as e:
        logger.exception(f"Unexpected error syncing Outlook account {account_id}")
        
        # Update account with error
        if account:
            account.sync_status = SyncStatus.ERROR
            account.sync_error_message = str(e)
            db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_task(base=BaseEmailSyncTask, bind=True)
def process_email_with_ai(self, comm_log_id: int, db: Session = None) -> dict:
    """
    Process an email with AI triage agent.
    
    Args:
        comm_log_id: CommunicationLog ID
        db: Database session
        
    Returns:
        Dictionary with processing status and AI results
    """
    try:
        # Get communication log entry
        comm_log = db.query(CommunicationLog).filter(CommunicationLog.id == comm_log_id).first()
        
        if not comm_log:
            logger.warning(f"CommunicationLog {comm_log_id} not found")
            return {"status": "error", "reason": "comm_log_not_found"}
        
        # Skip if already processed (has sentiment and urgency scores)
        if comm_log.sentiment_score is not None and comm_log.urgency_score is not None:
            return {"status": "skipped", "reason": "already_processed"}
        
        # Initialize triage agent
        agent = TriageAgent()
        
        # Prepare email data for AI
        email_data = {
            "subject": comm_log.subject or "",
            "body": comm_log.body or comm_log.summary or "",
            "sender_email": comm_log.from_address or "",
            "sender_name": "",  # Not stored separately in CommunicationLog
            "received_at": comm_log.occurred_at.isoformat()
        }
        
        # Run AI analysis
        analysis = asyncio.run(agent.analyze_email(email_data))
        
        # Update communication log with AI results
        comm_log.urgency_score = analysis.get("urgency_score", 20.0)
        comm_log.sentiment_score = analysis.get("sentiment_score", 0.0)
        comm_log.key_topics = analysis.get("entities", {})
        
        # Generate AI summary if not already present
        if not comm_log.summary and comm_log.body:
            comm_log.summary = comm_log.body[:500]  # Simple truncation for now
        
        db.commit()
        
        # TODO: Store in vector database for semantic search
        # Generate embedding and store in Pinecone
        
        logger.info(f"Processed communication {comm_log_id}: urgency={comm_log.urgency_score}, sentiment={comm_log.sentiment_score}")
        
        return {
            "status": "success",
            "comm_log_id": comm_log_id,
            "urgency_score": comm_log.urgency_score,
            "sentiment_score": comm_log.sentiment_score
        }
        
    except Exception as e:
        logger.exception(f"Error processing communication {comm_log_id} with AI")
        return {"status": "error", "error": str(e)}


@celery_task(base=BaseEmailSyncTask)
def sync_all_gmail_accounts(db: Session = None) -> dict:
    """
    Sync all active Gmail accounts (periodic task).
    
    Returns:
        Dictionary with queue status and count
    """
    accounts = db.query(EmailAccount).filter(
        EmailAccount.provider == EmailProvider.GMAIL,
        EmailAccount.is_active == True,
        EmailAccount.auto_sync_enabled == True
    ).all()
    
    for account in accounts:
        sync_gmail_account.delay(account.user_id, account.id)
    
    logger.info(f"Queued Gmail sync for {len(accounts)} accounts")
    return {"status": "queued", "count": len(accounts)}


@celery_task(base=BaseEmailSyncTask)
def sync_all_outlook_accounts(db: Session = None) -> dict:
    """
    Sync all active Outlook accounts (periodic task).
    
    Returns:
        Dictionary with queue status and count
    """
    accounts = db.query(EmailAccount).filter(
        EmailAccount.provider == EmailProvider.OUTLOOK,
        EmailAccount.is_active == True,
        EmailAccount.auto_sync_enabled == True
    ).all()
    
    for account in accounts:
        sync_outlook_account.delay(account.user_id, account.id)
    
    logger.info(f"Queued Outlook sync for {len(accounts)} accounts")
    return {"status": "queued", "count": len(accounts)}


# TODO: Add webhook support for instant email notifications
# TODO: Implement optimistic UI updates for real-time email arrival
# TODO: Add retry logic for failed AI processing
# TODO: Implement email deduplication across accounts

