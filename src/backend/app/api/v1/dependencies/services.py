
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.database import get_db_session
from backend.app.services.chat_service import ChatService
from backend.app.websockets.chat_handler import WebSocketChatHandler


def get_chat_service(db: AsyncSession = Depends(get_db_session)) -> ChatService:
    return ChatService(db)

def get_websocket_chat_handler(db: AsyncSession = Depends(get_db_session)) -> WebSocketChatHandler:
    return WebSocketChatHandler(db)
