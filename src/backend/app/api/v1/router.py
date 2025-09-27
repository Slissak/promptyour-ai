"""
Main API router for v1 endpoints
"""
from fastapi import APIRouter

# Import route modules
from app.api.v1.routes import chat, evaluations, config, websocket, llm_providers

# Create main API router
api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """API health check"""
    return {"status": "healthy", "version": "1.0.0"}

# Include route modules
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(llm_providers.router, prefix="/providers", tags=["llm_providers"])