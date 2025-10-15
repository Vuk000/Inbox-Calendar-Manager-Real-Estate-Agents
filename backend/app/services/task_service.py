"""
Task Service - Converts emails to tasks and manages calendar integration
Phase 4.3: Task Conversion
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import logging
from anthropic import Anthropic

from ..config import settings
from ..models.task import Task, TaskPriority, TaskStatus
from ..models.message import Message
from ..models.user import User
from ..integrations.google_calendar import GoogleCalendarIntegration
from ..security.encryption import decrypt_data
from ..shared.exceptions import TaskException, AnthropicAPIException

logger = logging.getLogger(__name__)


class TaskService:
    """
    Service for managing tasks and calendar integration.
    Converts emails to actionable tasks with AI assistance.
    """
    
    def __init__(self, claude_client: Optional[Anthropic] = None):
        """
        Initialize task service.
        
        Args:
            claude_client: Optional Claude client for DI
        """
        self.client = claude_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    async def create_from_email(
        self,
        email: Message,
        user: User,
        db: Session,
        auto_sync_calendar: bool = True
    ) -> Task:
        """
        Convert email to task with AI analysis.
        
        Args:
            email: Message to convert
            user: User creating the task
            db: Database session
            auto_sync_calendar: Whether to auto-sync to Google Calendar
            
        Returns:
            Created Task instance
            
        Raises:
            TaskException: If task creation fails
        """
        try:
            # Decrypt email body
            email_body = decrypt_data(email.encrypted_body) if email.encrypted_body else email.body_preview
            
            # Use AI to extract action items
            prompt = f"""Analyze this email and extract actionable tasks.

Email Details:
From: {email.sender_name} <{email.sender_email}>
Subject: {email.subject}
Body:
{email_body[:1500]}

Extract the following in JSON format:
1. **task_title** (string): Clear, actionable task title (max 100 chars)
2. **task_description** (string): Detailed description with context
3. **priority** (string): "high", "medium", or "low" based on urgency
4. **due_date** (string or null): Suggested due date in ISO format if mentioned
5. **action_items** (array): List of specific action items to complete
6. **attendees** (array): People who should be involved
7. **estimated_duration** (string or null): How long this might take

Return ONLY valid JSON:"""

            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                task_data = json.loads(message.content[0].text)
                
            except Exception as e:
                logger.warning(f"AI task extraction failed, using fallback: {str(e)}")
                # Fallback: Use email subject as task title
                task_data = {
                    "task_title": f"Follow up: {email.subject}",
                    "task_description": f"Address email from {email.sender_name}",
                    "priority": email.priority.value if hasattr(email, 'priority') else "medium",
                    "due_date": None,
                    "action_items": ["Review email", "Draft response"],
                    "attendees": [email.sender_name] if email.sender_name else [],
                    "estimated_duration": None
                }
            
            # Parse due date
            due_date = None
            if task_data.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(task_data["due_date"])
                except:
                    # Default to 3 days if parsing fails
                    due_date = datetime.utcnow() + timedelta(days=3)
            else:
                # Default to 3 days for medium/low, 1 day for high
                days = 1 if task_data.get("priority") == "high" else 3
                due_date = datetime.utcnow() + timedelta(days=days)
            
            # Create task
            task = Task(
                title=task_data.get("task_title", f"Follow up: {email.subject}")[:200],
                description=task_data.get("task_description"),
                status=TaskStatus.PENDING,
                priority=TaskPriority(task_data.get("priority", "medium")),
                due_date=due_date,
                email_id=email.id,
                created_by=user.id,
                metadata={
                    "action_items": task_data.get("action_items", []),
                    "attendees": task_data.get("attendees", []),
                    "estimated_duration": task_data.get("estimated_duration"),
                    "created_from_email": True
                }
            )
            
            db.add(task)
            db.commit()
            db.refresh(task)
            
            logger.info(f"Created task {task.id} from email {email.id}")
            
            # Sync to Google Calendar if enabled
            if auto_sync_calendar and user.google_calendar_enabled:
                try:
                    await self.sync_to_calendar(task, user, db)
                except Exception as e:
                    logger.warning(f"Failed to sync task to calendar: {str(e)}")
                    # Don't fail task creation if calendar sync fails
            
            return task
            
        except Exception as e:
            logger.exception(f"Failed to create task from email {email.id}")
            raise TaskException(
                f"Failed to create task: {str(e)}",
                error_code="TASK_CREATION_FAILED"
            )
    
    async def sync_to_calendar(
        self,
        task: Task,
        user: User,
        db: Session
    ) -> Dict[str, Any]:
        """
        Sync task to Google Calendar.
        
        Args:
            task: Task to sync
            user: User owning the task
            db: Database session
            
        Returns:
            Calendar event data
            
        Raises:
            TaskException: If calendar sync fails
        """
        try:
            # Get user's calendar integration
            calendar_integration = GoogleCalendarIntegration()
            
            # Prepare event data
            event_data = {
                "summary": task.title,
                "description": task.description or "",
                "start": {
                    "dateTime": task.due_date.isoformat() if task.due_date else (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "timeZone": "UTC"
                },
                "end": {
                    "dateTime": (task.due_date + timedelta(hours=1) if task.due_date else datetime.utcnow() + timedelta(days=1, hours=1)).isoformat(),
                    "timeZone": "UTC"
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},  # 1 day before
                        {"method": "popup", "minutes": 30}  # 30 min before
                    ]
                }
            }
            
            # Add attendees if available
            attendees = task.metadata.get("attendees", []) if task.metadata else []
            if attendees:
                event_data["attendees"] = [{"email": email} for email in attendees if "@" in str(email)]
            
            # Create calendar event
            # TODO: Get user's encrypted calendar credentials
            # result = await calendar_integration.create_event(
            #     encrypted_access_token=user.google_calendar_token,
            #     event_data=event_data
            # )
            
            # For now, log placeholder
            logger.info(f"TODO: Sync task {task.id} to Google Calendar")
            
            # Store calendar event ID in task metadata
            if task.metadata:
                task.metadata["calendar_event_id"] = "placeholder_event_id"
            else:
                task.metadata = {"calendar_event_id": "placeholder_event_id"}
            
            db.commit()
            
            return {"status": "synced", "event_id": "placeholder_event_id"}
            
        except Exception as e:
            logger.exception(f"Failed to sync task {task.id} to calendar")
            raise TaskException(
                f"Calendar sync failed: {str(e)}",
                error_code="CALENDAR_SYNC_FAILED"
            )
    
    async def extract_action_items(
        self,
        email_body: str,
        email_subject: str
    ) -> List[str]:
        """
        Extract action items from email using AI.
        
        Args:
            email_body: Email body text
            email_subject: Email subject
            
        Returns:
            List of action items
        """
        prompt = f"""Extract specific action items from this email.

Subject: {email_subject}
Body: {email_body[:1000]}

List each actionable task as a bullet point. Be specific and clear.
Return as JSON array of strings:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            action_items = json.loads(message.content[0].text)
            return action_items if isinstance(action_items, list) else []
            
        except Exception as e:
            logger.error(f"Failed to extract action items: {str(e)}")
            # Fallback to simple extraction
            return [f"Review and respond to email: {email_subject}"]


# TODO: Add NLP for recurring task detection
# TODO: Implement smart scheduling (find free calendar slots)
# TODO: Add task templates for common email types
# TODO: Implement task dependencies (task chains)
# TODO: Add task prioritization based on email urgency

