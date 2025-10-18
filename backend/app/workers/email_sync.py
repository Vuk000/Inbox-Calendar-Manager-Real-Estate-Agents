"""
Email synchronization workers using Celery
Handles periodic sync of Gmail and Outlook accounts
"""
from typing import List
from celery import Task
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from .celery_app import celery_app
from ..db import SessionLocal
from ..models.email_account import EmailAccount, EmailProvider, SyncStatus
from ..models.message import Message, MessagePriority, MessageCategory, MessageSource
from ..models.user import User
from ..integrations.gmail_integration import GmailIntegration
from ..integrations.outlook_integration import OutlookIntegration
from ..integrations.vector_store import VectorStore
from ..agents.triage_agent import TriageAgent
from ..security.encryption import encrypt_data
from ..security.audit import log_action

logger = logging.getLogger(__name__)


class BaseEmailSyncTask(Task):
    """Base task with database session management"""
    
    def __call__(self, *args, **kwargs):
        db = SessionLocal()
        try:
            return self.run(*args, db=db, **kwargs)
        finally:
            db.close()


@celery_app.task(base=BaseEmailSyncTask, bind=True, max_retries=3)
def sync_gmail_account(self, user_id: int, account_id: int, db: Session = None):
    """
    Sync emails from a Gmail account.
    
    Args:
        user_id: User ID
        account_id: EmailAccount ID
        db: Database session
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
        import asyncio
        result = asyncio.run(gmail.list_messages(
            encrypted_access_token=account.encrypted_access_token,
            encrypted_refresh_token=account.encrypted_refresh_token,
            max_results=100,
            query="is:unread OR newer_than:1d"  # Unread or last 24h
        ))
        
        if "error" in result:
            raise Exception(f"Gmail API error: {result['error']}")
        
        messages = result.get("messages", [])
        processed_count = 0
        
        for msg in messages:
            # Check if message already exists
            existing = db.query(Message).filter(
                Message.external_id == msg["id"],
                Message.email_account_id == account_id
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
            
            # Create message in database
            new_message = Message(
                email_account_id=account_id,
                external_id=msg_details["id"],
                thread_id=msg_details["thread_id"],
                source=MessageSource.EMAIL,
                sender_email=msg_details["from"],
                sender_name=msg_details.get("from_name", ""),
                subject=msg_details.get("subject", ""),
                encrypted_body=encrypt_data(msg_details.get("body", "")),
                body_preview=msg_details.get("snippet", "")[:200],
                has_attachments=msg_details.get("has_attachments", False),
                attachment_count=len(msg_details.get("attachments", [])),
                received_at=datetime.fromisoformat(msg_details.get("date", datetime.utcnow().isoformat()))
            )
            
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            
            # Trigger AI processing
            process_email_with_ai.delay(new_message.id)
            
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
        
        return {
            "status": "success",
            "account_id": account_id,
            "processed": processed_count
        }
        
    except Exception as e:
        logger.exception(f"Error syncing Gmail account {account_id}")
        
        # Update account with error
        if account:
            account.sync_status = SyncStatus.ERROR
            account.sync_error_message = str(e)
            db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(base=BaseEmailSyncTask, bind=True, max_retries=3)
def sync_outlook_account(self, user_id: int, account_id: int, db: Session = None):
    """
    Sync emails from an Outlook account.
    
    Args:
        user_id: User ID
        account_id: EmailAccount ID
        db: Database session
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
        import asyncio
        result = asyncio.run(outlook.list_messages(
            encrypted_access_token=account.encrypted_access_token,
            max_results=100,
            filter_query="isRead eq false or receivedDateTime ge " + 
                        datetime.utcnow().replace(hour=0, minute=0).isoformat() + "Z"
        ))
        
        if "error" in result:
            raise Exception(f"Outlook API error: {result['error']}")
        
        messages = result.get("messages", [])
        processed_count = 0
        
        for msg_data in messages:
            # Check if message already exists
            existing = db.query(Message).filter(
                Message.external_id == msg_data["id"],
                Message.email_account_id == account_id
            ).first()
            
            if existing:
                continue
            
            # Parse message
            msg_details = outlook._parse_message(msg_data)
            
            # Create message in database
            new_message = Message(
                email_account_id=account_id,
                external_id=msg_details["id"],
                thread_id=msg_details["thread_id"],
                source=MessageSource.EMAIL,
                sender_email=msg_details["from"],
                sender_name=msg_details.get("from_name", ""),
                subject=msg_details.get("subject", ""),
                encrypted_body=encrypt_data(msg_details.get("body", "")),
                body_preview=msg_details.get("body_preview", "")[:200],
                has_attachments=msg_details.get("has_attachments", False),
                received_at=datetime.fromisoformat(msg_details.get("date", datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            )
            
            db.add(new_message)
            db.commit()
            db.refresh(new_message)
            
            # Trigger AI processing
            process_email_with_ai.delay(new_message.id)
            
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
        
        return {
            "status": "success",
            "account_id": account_id,
            "processed": processed_count
        }
        
    except Exception as e:
        logger.exception(f"Error syncing Outlook account {account_id}")
        
        # Update account with error
        if account:
            account.sync_status = SyncStatus.ERROR
            account.sync_error_message = str(e)
            db.commit()
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(base=BaseEmailSyncTask, bind=True)
def process_email_with_ai(self, message_id: int, db: Session = None):
    """
    Process an email with AI triage agent.
    
    Args:
        message_id: Message ID
        db: Database session
    """
    try:
        # Get message
        message = db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            logger.warning(f"Message {message_id} not found")
            return {"status": "error", "reason": "message_not_found"}
        
        # Skip if already processed
        if message.processed_at:
            return {"status": "skipped", "reason": "already_processed"}
        
        # Initialize triage agent
        agent = TriageAgent()
        
        # Prepare email data for AI
        from ..security.encryption import decrypt_data
        email_data = {
            "subject": message.subject,
            "body": decrypt_data(message.encrypted_body),
            "sender_email": message.sender_email,
            "sender_name": message.sender_name,
            "received_at": message.received_at.isoformat()
        }
        
        # Run AI analysis
        import asyncio
        analysis = asyncio.run(agent.analyze_email(email_data))
        
        # Update message with AI results
        message.priority = MessagePriority(analysis.get("priority", "low"))
        message.category = MessageCategory(analysis.get("category", "general"))
        message.urgency_score = analysis.get("urgency_score", 20.0)
        message.sentiment_score = analysis.get("sentiment_score", 0.0)
        message.entities = analysis.get("entities", {})
        message.suggested_actions = analysis.get("suggested_actions", [])
        message.processed_at = datetime.utcnow()
        
        db.commit()
        
        # Auto-create contact and communication log
        from ..services.contact_service import ContactService
        from ..services.communication_service import CommunicationService
        from ..models.communication_log import CommunicationType, CommunicationDirection
        
        try:
            # Get the user_id from the email account
            user_id = message.email_account.user_id
            
            # Get or create contact by sender email
            contact = ContactService.get_or_create_contact_by_email(
                db=db,
                email=message.sender_email,
                user_id=user_id,
                sender_name=message.sender_name
            )
            
            # Create communication log
            comm_log = asyncio.run(CommunicationService.log_communication(
                db=db,
                user_id=user_id,
                contact_id=contact.id,
                communication_type=CommunicationType.EMAIL,
                direction=CommunicationDirection.INBOUND,
                occurred_at=message.received_at,
                subject=message.subject,
                body=message.body_preview,
                from_address=message.sender_email,
                to_address=None,  # Could extract from message headers
                message_id=message.id,
                external_id=message.external_id,
                sentiment_score=message.sentiment_score,
                urgency_score=message.urgency_score,
                has_attachments=message.has_attachments
            ))
            
            logger.info(f"Auto-linked message {message_id} to contact {contact.id}, comm_log {comm_log.id}")
            
        except Exception as e:
            logger.error(f"Error creating contact/comm_log for message {message_id}: {str(e)}")
            # Don't fail the whole task, just log the error
        
        # Store in vector database for semantic search
        # TODO: Generate embedding and store in Pinecone
        # For now, we'll skip this step
        
        logger.info(f"Processed message {message_id}: {message.priority} priority, {message.category} category")
        
        return {
            "status": "success",
            "message_id": message_id,
            "priority": message.priority.value,
            "category": message.category.value,
            "urgency_score": message.urgency_score
        }
        
    except Exception as e:
        logger.exception(f"Error processing message {message_id} with AI")
        return {"status": "error", "error": str(e)}


@celery_app.task(base=BaseEmailSyncTask)
def sync_all_gmail_accounts(db: Session = None):
    """Sync all active Gmail accounts (periodic task)"""
    accounts = db.query(EmailAccount).filter(
        EmailAccount.provider == EmailProvider.GMAIL,
        EmailAccount.is_active == True,
        EmailAccount.auto_sync_enabled == True
    ).all()
    
    for account in accounts:
        sync_gmail_account.delay(account.user_id, account.id)
    
    return {"status": "queued", "count": len(accounts)}


@celery_app.task(base=BaseEmailSyncTask)
def sync_all_outlook_accounts(db: Session = None):
    """Sync all active Outlook accounts (periodic task)"""
    accounts = db.query(EmailAccount).filter(
        EmailAccount.provider == EmailProvider.OUTLOOK,
        EmailAccount.is_active == True,
        EmailAccount.auto_sync_enabled == True
    ).all()
    
    for account in accounts:
        sync_outlook_account.delay(account.user_id, account.id)
    
    return {"status": "queued", "count": len(accounts)}

