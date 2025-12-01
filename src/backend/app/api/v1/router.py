"""
Main API router for v1 endpoints
"""
from fastapi import APIRouter

# Import route modules
from backend.app.api.v1.routes import chat, config, llm_providers, evaluations, websocket, analytics

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(config.router, prefix="/config", tags=["Configuration"])
api_router.include_router(
    llm_providers.router, prefix="/llm-providers", tags=["LLM Providers"]
)
api_router.include_router(
    evaluations.router, prefix="/evaluations", tags=["Evaluations"]
)
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
