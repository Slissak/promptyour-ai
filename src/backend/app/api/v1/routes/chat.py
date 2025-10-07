"""
Chat API Routes
Main endpoints for the chat functionality
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from app.models.schemas import UserInput, QuickInput, RawInput, ChatResponse, QuickResponse, RawResponse, UserRating
from app.services.chat_service import ChatService, ChatServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global chat service instance (in production, use dependency injection)
chat_service = ChatService()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: UserInput,
    user_id: str = "demo_user"  # TODO: Get from authentication
) -> ChatResponse:
    """
    Main chat endpoint - Process user message through AI agentic system
    
    Flow:
    1. User inputs question + context (subject, grade level)
    2. Backend chooses optimal model  
    3. Generates model-specific system prompt
    4. Calls LLM via OpenRouter
    5. Returns enhanced response
    """
    
    logger.info(
        "Chat message received",
        user_id=user_id,
        theme=request.theme,
        audience=request.audience,
        question_length=len(request.question)
    )
    
    try:
        response = await chat_service.process_user_request(request, user_id)
        
        logger.info(
            "Chat message processed successfully",
            user_id=user_id,
            message_id=response.message_id,
            model_used=response.model_used,
            cost=response.cost
        )
        
        return response
        
    except ChatServiceError as e:
        logger.error("Chat service error", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat service error: {e}"
        )
    except Exception as e:
        logger.error("Unexpected error in chat endpoint", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/quick", response_model=QuickResponse)
async def send_quick_message(
    request: QuickInput,
    user_id: str = "demo_user"  # TODO: Get from authentication
) -> QuickResponse:
    """
    Quick chat endpoint - Provides one-liner answers without theme/audience selection

    Flow:
    1. User inputs question only
    2. Backend uses fast model (claude-3-haiku)
    3. Generates simple system prompt for concise answers
    4. Returns quick one-line response
    """

    logger.info(
        "Quick chat message received",
        user_id=user_id,
        question_length=len(request.question)
    )

    try:
        response = await chat_service.process_quick_request(request, user_id)

        logger.info(
            "Quick chat message processed successfully",
            user_id=user_id,
            message_id=response.message_id,
            model_used=response.model_used,
            cost=response.cost
        )

        return response

    except ChatServiceError as e:
        logger.error("Chat service error in quick mode", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick chat service error: {e}"
        )
    except Exception as e:
        logger.error("Unexpected error in quick chat endpoint", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/raw", response_model=RawResponse)
async def send_raw_message(
    request: RawInput,
    user_id: str = "demo_user"  # TODO: Get from authentication
) -> RawResponse:
    """
    RAW chat endpoint - NO prompt engineering, ONLY user question sent to model

    This endpoint demonstrates what happens when you send ONLY the user's question
    to the model without any system prompt, context, theme, or audience adaptation.

    Use this to compare against enhanced responses and see the value of prompt engineering.

    Flow:
    1. User inputs question only
    2. Backend sends EMPTY system prompt
    3. Model receives ONLY the question
    4. Returns RAW model output
    """

    logger.info(
        "RAW chat message received",
        user_id=user_id,
        question_length=len(request.question)
    )

    try:
        response = await chat_service.process_raw_request(request, user_id)

        logger.info(
            "RAW chat message processed successfully",
            user_id=user_id,
            message_id=response.message_id,
            model_used=response.model_used,
            cost=response.cost
        )

        return response

    except ChatServiceError as e:
        logger.error("Chat service error in RAW mode", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAW chat service error: {e}"
        )
    except Exception as e:
        logger.error("Unexpected error in RAW chat endpoint", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/rate/{message_id}")
async def rate_message(
    message_id: str,
    rating: UserRating,
    user_id: str = "demo_user"  # TODO: Get from authentication
) -> Dict[str, Any]:
    """
    Collect user rating for a message
    Critical for model selection improvement
    """
    
    # Validate message_id matches rating
    if rating.message_id != message_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message ID mismatch"
        )
    
    logger.info(
        "Rating received",
        message_id=message_id,
        user_id=user_id,
        rating=rating.rating
    )
    
    try:
        success = await chat_service.collect_user_rating(rating, user_id)
        
        if success:
            return {
                "message": "Rating collected successfully",
                "message_id": message_id,
                "rating": rating.rating
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store rating"
            )
            
    except Exception as e:
        logger.error("Error collecting rating", message_id=message_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect rating"
        )


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    user_id: str = "demo_user",  # TODO: Get from authentication
    limit: int = 10
) -> Dict[str, Any]:
    """Get conversation history for context"""
    
    logger.info(
        "Fetching conversation history",
        conversation_id=conversation_id,
        user_id=user_id,
        limit=limit
    )
    
    try:
        history = await chat_service.get_conversation_history(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit
        )
        
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error("Error fetching conversation history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversation history"
        )


@router.get("/health")
async def chat_health_check() -> Dict[str, Any]:
    """Health check for chat service components"""
    
    try:
        health_status = await chat_service.health_check()
        
        if health_status["service"] == "healthy":
            return health_status
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_status
            )
            
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "service": "unhealthy",
                "error": str(e)
            }
        )


@router.get("/models/available")
async def get_available_models() -> Dict[str, Any]:
    """Get list of available models and their capabilities"""
    
    try:
        models = chat_service.model_selector.get_available_models()
        
        return {
            "models": models,
            "count": len(models)
        }
        
    except Exception as e:
        logger.error("Error fetching available models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available models"
        )