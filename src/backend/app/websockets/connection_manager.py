"""
WebSocket Connection Manager
Handles WebSocket connections, user sessions, and message broadcasting
"""
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectedClient:
    """Represents a connected WebSocket client"""
    websocket: WebSocket
    user_id: str
    conversation_id: Optional[str] = None
    connected_at: datetime = None
    
    def __post_init__(self):
        if self.connected_at is None:
            self.connected_at = datetime.utcnow()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages"""
    
    def __init__(self):
        # Active connections: connection_id -> ConnectedClient
        self.connections: Dict[str, ConnectedClient] = {}
        
        # User mappings for quick lookup
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        self.conversation_connections: Dict[str, Set[str]] = {}  # conversation_id -> set of connection_ids
        
    async def connect(
        self, 
        websocket: WebSocket, 
        connection_id: str, 
        user_id: str, 
        conversation_id: Optional[str] = None
    ):
        """Accept a new WebSocket connection"""
        
        await websocket.accept()
        
        client = ConnectedClient(
            websocket=websocket,
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        # Store connection
        self.connections[connection_id] = client
        
        # Update user mapping
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Update conversation mapping
        if conversation_id:
            if conversation_id not in self.conversation_connections:
                self.conversation_connections[conversation_id] = set()
            self.conversation_connections[conversation_id].add(connection_id)
        
        logger.info(
            "WebSocket connected",
            connection_id=connection_id,
            user_id=user_id,
            conversation_id=conversation_id,
            total_connections=len(self.connections)
        )
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "message": "Successfully connected to real-time chat",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)

    async def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        
        if connection_id not in self.connections:
            return
        
        client = self.connections[connection_id]
        user_id = client.user_id
        conversation_id = client.conversation_id
        
        # Remove from connections
        del self.connections[connection_id]
        
        # Remove from user mapping
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from conversation mapping
        if conversation_id and conversation_id in self.conversation_connections:
            self.conversation_connections[conversation_id].discard(connection_id)
            if not self.conversation_connections[conversation_id]:
                del self.conversation_connections[conversation_id]
        
        logger.info(
            "WebSocket disconnected",
            connection_id=connection_id,
            user_id=user_id,
            conversation_id=conversation_id,
            total_connections=len(self.connections)
        )

    async def send_personal_message(self, message: dict, connection_id: str):
        """Send a message to a specific connection"""
        
        if connection_id not in self.connections:
            logger.warning("Attempted to send message to non-existent connection", connection_id=connection_id)
            return False
        
        try:
            websocket = self.connections[connection_id].websocket
            await websocket.send_text(json.dumps(message))
            
            logger.debug(
                "Message sent to connection",
                connection_id=connection_id,
                message_type=message.get("type", "unknown")
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send message to connection",
                connection_id=connection_id,
                error=str(e)
            )
            # Connection might be dead, remove it
            await self.disconnect(connection_id)
            return False

    async def send_to_user(self, message: dict, user_id: str) -> int:
        """Send a message to all connections of a specific user"""
        
        if user_id not in self.user_connections:
            logger.debug("No connections found for user", user_id=user_id)
            return 0
        
        connection_ids = self.user_connections[user_id].copy()
        sent_count = 0
        
        for connection_id in connection_ids:
            success = await self.send_personal_message(message, connection_id)
            if success:
                sent_count += 1
        
        logger.info(
            "Message sent to user connections",
            user_id=user_id,
            sent_count=sent_count,
            total_connections=len(connection_ids)
        )
        
        return sent_count

    async def send_to_conversation(self, message: dict, conversation_id: str) -> int:
        """Send a message to all participants in a conversation"""
        
        if conversation_id not in self.conversation_connections:
            logger.debug("No connections found for conversation", conversation_id=conversation_id)
            return 0
        
        connection_ids = self.conversation_connections[conversation_id].copy()
        sent_count = 0
        
        for connection_id in connection_ids:
            success = await self.send_personal_message(message, connection_id)
            if success:
                sent_count += 1
        
        logger.info(
            "Message sent to conversation participants",
            conversation_id=conversation_id,
            sent_count=sent_count,
            total_connections=len(connection_ids)
        )
        
        return sent_count

    async def broadcast(self, message: dict) -> int:
        """Broadcast a message to all connected clients"""
        
        if not self.connections:
            logger.debug("No connections to broadcast to")
            return 0
        
        connection_ids = list(self.connections.keys())
        sent_count = 0
        
        for connection_id in connection_ids:
            success = await self.send_personal_message(message, connection_id)
            if success:
                sent_count += 1
        
        logger.info(
            "Message broadcasted to all connections",
            sent_count=sent_count,
            total_connections=len(connection_ids)
        )
        
        return sent_count

    def get_connection_info(self) -> dict:
        """Get information about current connections"""
        
        return {
            "total_connections": len(self.connections),
            "unique_users": len(self.user_connections),
            "active_conversations": len(self.conversation_connections),
            "connections": [
                {
                    "connection_id": conn_id,
                    "user_id": client.user_id,
                    "conversation_id": client.conversation_id,
                    "connected_at": client.connected_at.isoformat()
                }
                for conn_id, client in self.connections.items()
            ]
        }

    async def handle_ping(self, connection_id: str) -> bool:
        """Handle ping message for connection health check"""
        
        return await self.send_personal_message({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)


# Global connection manager instance
connection_manager = ConnectionManager()