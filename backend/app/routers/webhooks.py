"""
Webhook router - Handle incoming webhooks from external services
"""
from fastapi import APIRouter, Request, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
import hmac
import hashlib
import logging

from ..db import SessionLocal
from ..workers.email_sync import process_email_with_ai, sync_gmail_account, sync_outlook_account
from ..models.email_account import EmailAccount, EmailProvider

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    """
    Handle Gmail push notifications.
    
    Gmail sends notifications when mailbox changes.
    This triggers email sync for the affected account.
    """
    try:
        body = await request.body()
        data = await request.json()
        
        # Gmail sends historyId in notification
        history_id = data.get("historyId")
        email_address = data.get("emailAddress")
        
        logger.info(f"Gmail webhook received for {email_address}, history: {history_id}")
        
        # Find account and trigger sync
        db = SessionLocal()
        try:
            account = db.query(EmailAccount).filter(
                EmailAccount.email_address == email_address,
                EmailAccount.provider == EmailProvider.GMAIL,
                EmailAccount.is_active == True
            ).first()
            
            if account:
                # Trigger sync in background
                sync_gmail_account.delay(account.user_id, account.id)
                logger.info(f"Triggered sync for Gmail account {account.id}")
        finally:
            db.close()
        
        return {"status": "received", "history_id": history_id}
        
    except Exception as e:
        logger.error(f"Gmail webhook error: {e}")
        return {"status": "error", "error": str(e)}


@router.post("/webhooks/outlook")
async def outlook_webhook(
    request: Request,
    validation_token: Optional[str] = Header(None, alias="validationtoken")
):
    """
    Handle Outlook subscription notifications.
    
    Microsoft requires validation token response on setup.
    Sends notifications for mailbox changes.
    """
    try:
        # Validation request (during subscription setup)
        if validation_token:
            return validation_token
        
        # Actual notification
        body = await request.body()
        data = await request.json()
        
        # Outlook sends array of notifications
        notifications = data.get("value", [])
        
        for notification in notifications:
            resource = notification.get("resource")
            change_type = notification.get("changeType")
            
            logger.info(f"Outlook webhook: {change_type} on {resource}")
            
            # Trigger sync for affected account
            # Extract email from resource (format: /users/{email}/messages/{id})
            if '/messages' in resource:
                db = SessionLocal()
                try:
                    # Trigger sync for all active Outlook accounts (simplified)
                    accounts = db.query(EmailAccount).filter(
                        EmailAccount.provider == EmailProvider.OUTLOOK,
                        EmailAccount.is_active == True
                    ).all()
                    
                    for account in accounts:
                        sync_outlook_account.delay(account.user_id, account.id)
                finally:
                    db.close()
        
        return {"status": "received", "count": len(notifications)}
        
    except Exception as e:
        logger.error(f"Outlook webhook error: {e}")
        return {"status": "error", "error": str(e)}


@router.post("/webhooks/twilio")
async def twilio_webhook(
    request: Request,
    x_twilio_signature: Optional[str] = Header(None)
):
    """
    Handle Twilio incoming SMS/WhatsApp messages.
    
    Twilio sends webhook when message is received.
    We process it and add to unified inbox.
    """
    try:
        form_data = await request.form()
        
        # Extract message details
        message_sid = form_data.get("MessageSid")
        from_number = form_data.get("From")
        to_number = form_data.get("To")
        body = form_data.get("Body")
        
        logger.info(f"Twilio webhook: Message from {from_number}")
        
        # Verify Twilio signature
        from app.config import settings
        from twilio.request_validator import RequestValidator
        
        validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        url = str(request.url)
        
        # Convert form data to dict for validation
        post_vars = dict(form_data)
        
        if x_twilio_signature and not validator.validate(url, post_vars, x_twilio_signature):
            logger.warning("Twilio signature validation failed")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Store message in database
        db = SessionLocal()
        try:
            from app.models.message import Message, MessageSource, MessagePriority
            from app.security.encryption import encrypt_data
            from datetime import datetime
            
            # Determine source
            source = MessageSource.WHATSAPP if from_number.startswith('whatsapp:') else MessageSource.SMS
            
            # Find user by phone number or create as system message
            # For now, store without user association (would need phone number mapping)
            
            new_message = Message(
                email_account_id=None,  # SMS/WhatsApp not tied to email account
                external_id=message_sid,
                thread_id=from_number,  # Use phone as thread
                source=source,
                sender_email=from_number,  # Store phone as "email"
                sender_name="",
                subject=f"SMS from {from_number}",
                encrypted_body=encrypt_data(body or ""),
                body_preview=(body or "")[:200],
                received_at=datetime.utcnow(),
                priority=MessagePriority.MEDIUM  # Default priority for SMS
            )
            
            db.add(new_message)
            db.commit()
            
            # Run AI triage
            process_email_with_ai.delay(new_message.id)
            
        finally:
            db.close()
        
        # Respond to Twilio (must be TwiML or empty)
        return {
            "status": "received",
            "message_sid": message_sid
        }
        
    except Exception as e:
        logger.error(f"Twilio webhook error: {e}")
        return {"status": "error", "error": str(e)}


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe payment webhooks.
    
    Stripe sends events for subscriptions, payments, etc.
    """
    try:
        body = await request.body()
        
        # Verify Stripe signature
        from app.config import settings
        import stripe
        
        stripe.api_key = settings.STRIPE_API_KEY
        
        try:
            event = stripe.Webhook.construct_event(
                payload=body,
                sig_header=stripe_signature,
                secret=settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            logger.error(f"Stripe signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle different event types
        event_type = event['type']
        data = event['data']['object']
        
        db = SessionLocal()
        try:
            if event_type == 'checkout.session.completed':
                # Handle successful checkout
                user_id = data.get('metadata', {}).get('user_id')
                tier = data.get('metadata', {}).get('tier')
                subscription_id = data.get('subscription')
                
                if user_id:
                    from app.models.user import User, SubscriptionTier
                    user = db.query(User).filter(User.id == int(user_id)).first()
                    if user:
                        user.stripe_subscription_id = subscription_id
                        user.subscription_tier = SubscriptionTier(tier)
                        user.subscription_status = "active"
                        db.commit()
            
            elif event_type == 'customer.subscription.updated':
                # Handle subscription updates
                subscription_id = data.get('id')
                status = data.get('status')
                
                from app.models.user import User
                user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
                if user:
                    user.subscription_status = status
                    db.commit()
            
            elif event_type == 'customer.subscription.deleted':
                # Handle subscription cancellation
                subscription_id = data.get('id')
                
                from app.models.user import User, SubscriptionTier
                user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
                if user:
                    user.subscription_status = "cancelled"
                    user.subscription_tier = SubscriptionTier.FREE_TRIAL
                    db.commit()
            
            elif event_type == 'invoice.payment_failed':
                # Handle failed payment
                subscription_id = data.get('subscription')
                
                from app.models.user import User
                user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
                if user:
                    user.subscription_status = "past_due"
                    db.commit()
        
        finally:
            db.close()
        
        logger.info(f"Stripe webhook processed: {event_type}")
        
        return {"status": "received", "event_type": event_type}
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {"status": "error", "error": str(e)}

