"""
WebSocket connection manager for real-time notifications
Enhanced for Phase 4: Real-time email sync and notifications
"""
from typing import Dict, List, Set, Any
from fastapi import WebSocket
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    Supports broadcasting to specific users or all users.
    """
    
    def __init__(self):
        # Map of user_id to list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        
        # Send welcome message
        await self.send_personal_message(
            {"type": "connected", "message": "Connected to RealInbox AI"},
            websocket
        )
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
            # Clean up empty user lists
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to a specific WebSocket connection.
        
        Args:
            message: Message data (will be JSON serialized)
            websocket: Target WebSocket
        """
        await websocket.send_text(json.dumps(message))
    
    async def broadcast_to_user(self, message: dict, user_id: int):
        """
        Broadcast message to all connections of a specific user.
        
        Args:
            message: Message data
            user_id: User ID
        """
        if user_id in self.active_connections:
            dead_connections = []
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    dead_connections.append(connection)
            
            # Remove dead connections
            for dead in dead_connections:
                self.active_connections[user_id].remove(dead)
    
    async def broadcast_to_all(self, message: dict):
        """
        Broadcast message to all connected users.
        
        Args:
            message: Message data
        """
        for user_id in list(self.active_connections.keys()):
            await self.broadcast_to_user(message, user_id)
    
    async def notify_new_email(
        self,
        user_id: int,
        email_data: Dict[str, Any]
    ):
        """
        Notify user about new email.
        
        Args:
            user_id: User ID
            email_data: Email metadata
        """
        await self.broadcast_to_user(
            {
                "type": "new_email",
                "data": email_data
            },
            user_id
        )
    
    async def notify_draft_ready(
        self,
        user_id: int,
        draft_data: Dict[str, Any]
    ):
        """
        Notify user that AI draft is ready.
        
        Args:
            user_id: User ID
            draft_data: Draft metadata
        """
        await self.broadcast_to_user(
            {
                "type": "draft_ready",
                "data": draft_data
            },
            user_id
        )
    
    async def notify_sync_status(
        self,
        user_id: int,
        status: str,
        message: str
    ):
        """
        Notify user about email sync status.
        
        Args:
            user_id: User ID
            status: Status (syncing, complete, error)
            message: Status message
        """
        await self.broadcast_to_user(
            {
                "type": "sync_status",
                "status": status,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id
        )
    
    async def notify_triage_complete(
        self,
        user_id: int,
        email_id: int,
        triage_result: Dict[str, Any]
    ):
        """
        Notify user that email triage is complete.
        
        Args:
            user_id: User ID
            email_id: Email ID
            triage_result: Triage analysis results
        """
        await self.broadcast_to_user(
            {
                "type": "triage_complete",
                "email_id": email_id,
                "triage": triage_result,
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id
        )
        
        logger.info(f"Notified user {user_id} about triage completion for email {email_id}")
    
    async def notify_task_update(
        self,
        user_id: int,
        task_data: Dict[str, Any]
    ):
        """
        Notify user about task updates.
        
        Args:
            user_id: User ID
            task_data: Task data
        """
        await self.broadcast_to_user(
            {
                "type": "task_update",
                "data": task_data,
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id
        )
    
    def get_connection_count(self, user_id: Optional[int] = None) -> int:
        """
        Get count of active connections.
        
        Args:
            user_id: Optional user ID to get count for specific user
            
        Returns:
            Number of active connections
        """
        if user_id:
            return len(self.active_connections.get(user_id, []))
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager instance for use across app
connection_manager = ConnectionManager()

