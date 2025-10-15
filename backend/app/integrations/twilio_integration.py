"""
Twilio Integration - SMS and WhatsApp messaging
"""
from typing import Dict, Any, Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from ..config import settings


class TwilioIntegration:
    """
    Twilio integration for SMS and WhatsApp messaging.
    Enables multi-channel communication.
    """
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        self.client = Client(self.account_sid, self.auth_token)
    
    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message.
        
        Args:
            to: Recipient phone number (E.164 format: +1234567890)
            body: Message content
            from_number: Optional sender number (defaults to Twilio number)
            
        Returns:
            Send result with message SID
        """
        try:
            message = self.client.messages.create(
                body=body,
                from_=from_number or self.phone_number,
                to=to
            )
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_
            }
            
        except TwilioRestException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code
            }
    
    async def send_whatsapp(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message.
        
        Args:
            to: Recipient WhatsApp number (format: whatsapp:+1234567890)
            body: Message content
            from_number: Optional sender WhatsApp number
            
        Returns:
            Send result
        """
        try:
            # Ensure WhatsApp prefix
            if not to.startswith("whatsapp:"):
                to = f"whatsapp:{to}"
            
            message = self.client.messages.create(
                body=body,
                from_=from_number or self.whatsapp_number,
                to=to
            )
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_
            }
            
        except TwilioRestException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.code
            }
    
    async def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get status of a sent message.
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Message status and details
        """
        try:
            message = self.client.messages(message_sid).fetch()
            
            return {
                "success": True,
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": message.date_sent.isoformat() if message.date_sent else None,
                "error_code": message.error_code,
                "error_message": message.error_message
            }
            
        except TwilioRestException as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def setup_webhook(self, url: str) -> str:
        """
        Generate webhook URL for incoming messages.
        
        Args:
            url: Your server's webhook endpoint URL
            
        Returns:
            Instructions for webhook setup
        """
        return f"""
To receive incoming SMS/WhatsApp messages:
1. Go to Twilio Console > Phone Numbers
2. Select your number
3. Set Messaging webhook to: {url}
4. Method: POST
5. Save changes

Your webhook will receive POST requests with:
- MessageSid: Unique message ID
- From: Sender number
- To: Your Twilio number
- Body: Message content
"""

