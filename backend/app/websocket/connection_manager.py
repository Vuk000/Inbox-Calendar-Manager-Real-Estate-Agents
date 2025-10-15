"""
WebSocket connection manager for real-time notifications
"""
from typing import Dict, List, Set
from fastapi import WebSocket
import json


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
                "message": message
            },
            user_id
        )

