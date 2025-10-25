"""
WebSocket router for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..dependencies import get_db
from ..websocket.connection_manager import ConnectionManager
from ..models.user import User
from ..security.jwt_handler import verify_token

router = APIRouter()

# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time updates.
    
    Query params:
    - token: JWT access token for authentication
    
    Messages from server:
    - {"type": "connected", "message": "Connected"}
    - {"type": "new_email", "data": {...}}
    - {"type": "draft_ready", "data": {...}}
    - {"type": "sync_status", "status": "...", "message": "..."}
    - {"type": "task_update", "data": {...}}
    """
    # Authenticate user from token
    payload = verify_token(token, token_type="access")
    
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id = payload.get("user_id")
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        await websocket.close(code=1008, reason="User not found or inactive")
        return
    
    # Connect
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            # Parse client message
            import json
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        {"type": "pong"},
                        websocket
                    )
                elif message.get("type") == "subscribe":
                    # Subscribe to specific events
                    await manager.send_personal_message(
                        {"type": "subscribed", "events": message.get("events", [])},
                        websocket
                    )
                
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON"},
                    websocket
                )
        
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

