"""
WebSocket API Routes
Real-time chat and messaging endpoints
"""
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from app.websockets.chat_handler import chat_handler
from app.websockets.connection_manager import connection_manager
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    user_id: str = Query(..., description="User ID for the connection"),
    conversation_id: Optional[str] = Query(None, description="Optional conversation ID")
):
    """
    WebSocket endpoint for real-time chat
    
    Message Types:
    - ping: Health check
    - chat_request: Send a chat message
    - user_rating: Rate a response
    - cancel_request: Cancel active request
    - get_conversation_history: Get chat history
    """
    
    logger.info(
        "WebSocket chat connection requested",
        user_id=user_id,
        conversation_id=conversation_id
    )
    
    await chat_handler.handle_connection(
        websocket=websocket,
        user_id=user_id,
        conversation_id=conversation_id
    )


@router.websocket("/admin")
async def websocket_admin_endpoint(
    websocket: WebSocket,
    admin_token: str = Query(..., description="Admin authentication token")
):
    """
    Admin WebSocket endpoint for monitoring connections
    """
    
    # TODO: Add proper admin authentication
    if admin_token != "admin_debug_token":  # Temporary debug token
        await websocket.close(code=1008, reason="Invalid admin token")
        return
    
    connection_id = "admin_connection"
    
    try:
        await connection_manager.connect(
            websocket=websocket,
            connection_id=connection_id,
            user_id="admin"
        )
        
        logger.info("Admin WebSocket connected")
        
        while True:
            try:
                data = await websocket.receive_text()
                
                if data == "get_stats":
                    # Send connection statistics
                    stats = connection_manager.get_connection_info()
                    await connection_manager.send_personal_message({
                        "type": "stats",
                        "data": stats
                    }, connection_id)
                
                elif data == "broadcast_test":
                    # Send test broadcast message
                    sent_count = await connection_manager.broadcast({
                        "type": "system_message",
                        "message": "Test broadcast from admin",
                        "timestamp": "2024-01-01T00:00:00Z"
                    })
                    
                    await connection_manager.send_personal_message({
                        "type": "broadcast_result",
                        "sent_to": sent_count
                    }, connection_id)
                
                else:
                    await connection_manager.send_personal_message({
                        "type": "error",
                        "message": f"Unknown admin command: {data}"
                    }, connection_id)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error("Admin WebSocket error", error=str(e))
                break
    
    finally:
        await connection_manager.disconnect(connection_id)
        logger.info("Admin WebSocket disconnected")


# Health check endpoint for WebSocket monitoring
@router.get("/health")
async def websocket_health():
    """Get WebSocket service health and statistics"""
    
    stats = connection_manager.get_connection_info()
    
    return {
        "status": "healthy",
        "websocket_stats": stats,
        "features": [
            "real_time_chat",
            "processing_updates", 
            "user_ratings",
            "conversation_history",
            "request_cancellation"
        ]
    }