"""
WebSocket Chat Handler
Handles real-time chat messages and streaming responses
"""
import json
import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from app.models.schemas import UserInput, ThemeType, AudienceType, UserRating
from app.services.chat_service import ChatService
from app.websockets.connection_manager import connection_manager
from app.core.logging import get_logger

logger = get_logger(__name__)


class WebSocketChatHandler:
    """Handles WebSocket chat interactions"""
    
    def __init__(self):
        self.chat_service = ChatService()
        self.active_requests: Dict[str, Dict[str, Any]] = {}  # connection_id -> request_info

    async def handle_connection(
        self, 
        websocket: WebSocket, 
        user_id: str, 
        conversation_id: Optional[str] = None
    ):
        """Handle a WebSocket connection for chat"""
        
        connection_id = str(uuid.uuid4())
        
        try:
            await connection_manager.connect(
                websocket=websocket,
                connection_id=connection_id,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            # Handle messages in a loop
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    await self._handle_message(connection_id, user_id, message)
                    
                except WebSocketDisconnect:
                    logger.info("WebSocket disconnected normally", connection_id=connection_id)
                    break
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON received", connection_id=connection_id)
                    await self._send_error(connection_id, "Invalid JSON format")
                except Exception as e:
                    logger.error("Error handling WebSocket message", connection_id=connection_id, error=str(e))
                    await self._send_error(connection_id, f"Message handling error: {e}")
        
        except Exception as e:
            logger.error("WebSocket connection error", connection_id=connection_id, error=str(e))
        
        finally:
            await connection_manager.disconnect(connection_id)
            # Clean up any active requests
            if connection_id in self.active_requests:
                del self.active_requests[connection_id]

    async def _handle_message(self, connection_id: str, user_id: str, message: dict):
        """Handle incoming WebSocket message"""
        
        message_type = message.get("type", "unknown")
        
        logger.info(
            "WebSocket message received", 
            connection_id=connection_id, 
            user_id=user_id, 
            message_type=message_type
        )
        
        if message_type == "ping":
            await connection_manager.handle_ping(connection_id)
            
        elif message_type == "chat_request":
            await self._handle_chat_request(connection_id, user_id, message)
            
        elif message_type == "user_rating":
            await self._handle_user_rating(connection_id, user_id, message)
            
        elif message_type == "cancel_request":
            await self._handle_cancel_request(connection_id, user_id, message)
            
        elif message_type == "get_conversation_history":
            await self._handle_get_history(connection_id, user_id, message)
            
        else:
            logger.warning("Unknown message type", connection_id=connection_id, message_type=message_type)
            await self._send_error(connection_id, f"Unknown message type: {message_type}")

    async def _handle_chat_request(self, connection_id: str, user_id: str, message: dict):
        """Handle a chat request with real-time streaming"""
        
        try:
            # Parse user input
            data = message.get("data", {})
            debug_mode = message.get("debug", False)
            
            # Parse message history if provided
            message_history = []
            if "message_history" in data and data["message_history"]:
                from app.models.schemas import ChatMessage, MessageRole
                for msg_data in data["message_history"]:
                    try:
                        message_history.append(ChatMessage(
                            role=MessageRole(msg_data.get("role", "user")),
                            content=msg_data.get("content", ""),
                            timestamp=msg_data.get("timestamp"),
                            model=msg_data.get("model"),
                            provider=msg_data.get("provider")
                        ))
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Skipping invalid message in history: {e}")
                        continue
            
            user_input = UserInput(
                question=data.get("question", ""),
                theme=ThemeType(data.get("theme", "general_questions")),
                audience=AudienceType(data.get("audience", "adults")),
                context=data.get("context"),
                conversation_id=data.get("conversation_id"),
                message_history=message_history,
                force_model=data.get("force_model"),
                force_provider=data.get("force_provider")
            )
            
            # Store active request info
            request_id = str(uuid.uuid4())
            self.active_requests[connection_id] = {
                "request_id": request_id,
                "user_input": user_input,
                "debug_mode": debug_mode,
                "started_at": datetime.utcnow()
            }
            
            # Send processing started message
            await connection_manager.send_personal_message({
                "type": "processing_started",
                "request_id": request_id,
                "message": "Processing your request...",
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
            
            # Send step-by-step updates
            await self._send_step_update(connection_id, request_id, "input_processing", "Analyzing your input...")
            
            # Process the request (this will take some time)
            response = await self.chat_service.process_user_request(
                user_input=user_input,
                user_id=user_id,
                debug_mode=debug_mode,
                debug_callback=self._send_debug_comparison if debug_mode else None,
                connection_id=connection_id if debug_mode else None,
                request_id=request_id if debug_mode else None
            )
            
            # Send completion message
            await connection_manager.send_personal_message({
                "type": "chat_response",
                "request_id": request_id,
                "data": {
                    "content": response.content,
                    "model_used": response.model_used,
                    "provider": response.provider,
                    "message_id": response.message_id,
                    "cost": response.cost,
                    "response_time_ms": response.response_time_ms,
                    "reasoning": response.reasoning
                },
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
            
            logger.info(
                "WebSocket chat request completed",
                connection_id=connection_id,
                request_id=request_id,
                model_used=response.model_used,
                cost=response.cost
            )
            
        except Exception as e:
            logger.error("Chat request failed", connection_id=connection_id, error=str(e))
            await self._send_error(connection_id, f"Chat request failed: {e}")
        
        finally:
            # Clean up request
            if connection_id in self.active_requests:
                del self.active_requests[connection_id]

    async def _send_step_update(self, connection_id: str, request_id: str, step: str, message: str):
        """Send a processing step update"""
        
        await connection_manager.send_personal_message({
            "type": "processing_step",
            "request_id": request_id,
            "step": step,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        
        # Add small delay to make updates visible
        await asyncio.sleep(0.1)

    # _send_debug_prompt method removed - now using _send_debug_comparison for better evaluation

    async def _send_debug_comparison(self, connection_id: str, request_id: str, comparison_data: dict):
        """Send debug comparison data (enhanced vs basic response) to client"""

        await connection_manager.send_personal_message({
            "type": "debug_comparison",
            "request_id": request_id,
            "data": comparison_data,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)

        logger.info(
            "Debug comparison sent",
            connection_id=connection_id,
            request_id=request_id,
            model=comparison_data.get("model", "unknown"),
            enhanced_tokens=comparison_data.get("enhanced_response", {}).get("tokens_used", 0),
            basic_tokens=comparison_data.get("basic_response", {}).get("tokens_used", 0)
        )

    async def _handle_user_rating(self, connection_id: str, user_id: str, message: dict):
        """Handle user rating submission"""
        
        try:
            data = message.get("data", {})
            rating = UserRating(
                message_id=data.get("message_id", ""),
                rating=data.get("rating", 3),
                feedback=data.get("feedback")
            )
            
            success = await self.chat_service.collect_user_rating(rating, user_id)
            
            await connection_manager.send_personal_message({
                "type": "rating_submitted",
                "success": success,
                "message_id": rating.message_id,
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
            
        except Exception as e:
            logger.error("Rating submission failed", connection_id=connection_id, error=str(e))
            await self._send_error(connection_id, f"Rating submission failed: {e}")

    async def _handle_cancel_request(self, connection_id: str, user_id: str, message: dict):
        """Handle request cancellation"""
        
        if connection_id in self.active_requests:
            request_info = self.active_requests[connection_id]
            request_id = request_info["request_id"]
            
            # TODO: Implement request cancellation logic
            # For now, just remove from active requests
            del self.active_requests[connection_id]
            
            await connection_manager.send_personal_message({
                "type": "request_cancelled",
                "request_id": request_id,
                "message": "Request cancelled successfully",
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
            
            logger.info("Request cancelled", connection_id=connection_id, request_id=request_id)
        else:
            await self._send_error(connection_id, "No active request to cancel")

    async def _handle_get_history(self, connection_id: str, user_id: str, message: dict):
        """Handle conversation history request"""
        
        try:
            data = message.get("data", {})
            conversation_id = data.get("conversation_id", "")
            limit = data.get("limit", 10)
            
            # Get conversation history
            history = await self.chat_service.get_conversation_history(
                conversation_id=conversation_id,
                user_id=user_id,
                limit=limit
            )
            
            await connection_manager.send_personal_message({
                "type": "conversation_history",
                "conversation_id": conversation_id,
                "history": history,
                "timestamp": datetime.utcnow().isoformat()
            }, connection_id)
            
        except Exception as e:
            logger.error("Failed to get conversation history", connection_id=connection_id, error=str(e))
            await self._send_error(connection_id, f"Failed to get conversation history: {e}")

    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message to client"""
        
        await connection_manager.send_personal_message({
            "type": "error",
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)


# Global chat handler instance
chat_handler = WebSocketChatHandler()