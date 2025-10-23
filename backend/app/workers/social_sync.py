"""Social channel synchronization workers"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from celery import Task
from sqlalchemy.orm import Session

from .celery_app import celery_app
from ..db import SessionLocal
from ..models.social_account import SocialAccount, SocialProvider
from ..models.communication_log import CommunicationLog, CommunicationType, CommunicationDirection
from ..models.contact import Contact
from ..services.contact_service import ContactService
from ..security.encryption import encrypt_data
from ..integrations.twitter_integration import TwitterIntegration
from ..integrations.facebook_messenger import FacebookMessengerIntegration
from ..tasks.email_sync_task import process_email_with_ai

logger = logging.getLogger(__name__)


class BaseSocialSyncTask(Task):
    """Base Celery task providing DB session."""

    def __call__(self, *args, **kwargs):
        db = SessionLocal()
        try:
            return self.run(*args, db=db, **kwargs)
        finally:
            db.close()


@celery_app.task(base=BaseSocialSyncTask, bind=True, max_retries=3)
def sync_twitter_account(self, account_id: int, db: Session = None):
    """Sync Twitter/X DMs for a connected account."""
    account: Optional[SocialAccount] = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.provider == SocialProvider.TWITTER,
        SocialAccount.is_active == True,
    ).first()
    if not account:
        logger.warning("Twitter account %s not found or inactive", account_id)
        return {"status": "skipped"}

    try:
        twitter = TwitterIntegration()
        messages = twitter.list_direct_messages(account.encrypted_access_token)
        events = messages.get("data", [])
        processed = 0
        user_id = account.user_id
        for event in events:
            normalized = TwitterIntegration.normalize_dm_event(event)
            external_id = normalized.get("external_id")
            if not external_id:
                continue

            existing = db.query(CommunicationLog).filter(
                CommunicationLog.external_id == external_id,
                CommunicationLog.user_id == user_id,
            ).first()
            if existing:
                continue

            # Get or create contact by Twitter ID (using from_address as identifier)
            sender_id = normalized.get("sender_id")
            contact = ContactService.get_or_create_contact_by_email(
                db=db,
                email=f"{sender_id}@twitter.com",  # Pseudo-email for Twitter DMs
                user_id=user_id,
                sender_name=sender_id
            )

            comm_log = CommunicationLog(
                user_id=user_id,
                contact_id=contact.id,
                communication_type=CommunicationType.TWITTER_DM,
                direction=CommunicationDirection.INBOUND,
                external_id=external_id,
                subject=f"Twitter DM from {sender_id}",
                body=normalized.get("text", ""),
                summary=normalized.get("text", "")[:500],
                from_address=sender_id,
                occurred_at=datetime.fromtimestamp(
                    int(normalized.get("sent_at", datetime.utcnow().timestamp())) / 1000
                ),
            )
            db.add(comm_log)
            db.commit()
            process_email_with_ai.delay(comm_log.id)
            processed += 1
        logger.info("Synced %s Twitter messages for account %s", processed, account_id)
        return {"status": "success", "processed": processed}
    except Exception as exc:
        logger.exception("Twitter sync failed for account %s", account_id)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(base=BaseSocialSyncTask, bind=True, max_retries=3)
def sync_facebook_account(self, account_id: int, db: Session = None):
    """Sync Facebook Messenger inbox."""
    account: Optional[SocialAccount] = db.query(SocialAccount).filter(
        SocialAccount.id == account_id,
        SocialAccount.provider == SocialProvider.FACEBOOK_MESSENGER,
        SocialAccount.is_active == True,
    ).first()
    if not account:
        logger.warning("Facebook account %s not found or inactive", account_id)
        return {"status": "skipped"}

    try:
        messenger = FacebookMessengerIntegration(page_id=account.page_id)
        conversations = messenger.get_conversations(account.encrypted_access_token)
        processed = 0
        user_id = account.user_id
        
        for convo in conversations.get("data", []):
            for message in convo.get("messages", {}).get("data", []):
                normalized = FacebookMessengerIntegration.normalize_message({"messaging": [
                    {
                        "sender": {"id": message.get("from", {}).get("id")},
                        "recipient": {"id": message.get("to", {}).get("data", [{}])[0].get("id")},
                        "message": {
                            "text": message.get("message"),
                            "mid": message.get("id"),
                            "attachments": message.get("attachments", []),
                        },
                        "timestamp": message.get("created_time"),
                    }
                ]})
                external_id = normalized.get("mid")
                if not external_id:
                    continue
                    
                existing = db.query(CommunicationLog).filter(
                    CommunicationLog.external_id == external_id,
                    CommunicationLog.user_id == user_id,
                ).first()
                if existing:
                    continue
                
                # Get or create contact by Facebook ID
                sender_id = normalized.get("sender_id")
                contact = ContactService.get_or_create_contact_by_email(
                    db=db,
                    email=f"{sender_id}@messenger.com",  # Pseudo-email for FB Messenger
                    user_id=user_id,
                    sender_name=sender_id
                )
                
                comm_log = CommunicationLog(
                    user_id=user_id,
                    contact_id=contact.id,
                    communication_type=CommunicationType.FACEBOOK_MESSENGER,
                    direction=CommunicationDirection.INBOUND,
                    external_id=external_id,
                    subject=f"Messenger from {sender_id}",
                    body=normalized.get("text", ""),
                    summary=normalized.get("text", "")[:500],
                    from_address=sender_id,
                    occurred_at=datetime.utcnow(),
                )
                db.add(comm_log)
                db.commit()
                process_email_with_ai.delay(comm_log.id)
                processed += 1
        logger.info("Synced %s Facebook messages for account %s", processed, account_id)
        return {"status": "success", "processed": processed}
    except Exception as exc:
        logger.exception("Facebook sync failed for account %s", account_id)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
