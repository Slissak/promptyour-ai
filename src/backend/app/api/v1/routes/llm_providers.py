"""
LLM Provider Management API Routes
Endpoints for managing OpenRouter, LM Studio, and unified provider settings
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.integrations.unified_llm_provider import UnifiedLLMProvider
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global unified provider instance
unified_provider = UnifiedLLMProvider()


@router.get("/status")
async def get_provider_status():
    """Get status of all LLM providers"""
    
    try:
        status = await unified_provider.get_provider_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error("Failed to get provider status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provider status: {e}"
        )


@router.get("/models")
async def get_available_models():
    """Get available models from all providers"""
    
    try:
        models = await unified_provider.get_available_models()
        return {
            "success": True,
            "data": models
        }
    except Exception as e:
        logger.error("Failed to get available models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available models: {e}"
        )


@router.get("/health")
async def get_provider_health():
    """Get overall health of the LLM provider system"""
    
    try:
        health = await unified_provider.health_check()
        return {
            "success": True,
            "data": health
        }
    except Exception as e:
        logger.error("Failed to get provider health", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provider health: {e}"
        )


@router.get("/lm-studio/status")
async def get_lm_studio_status():
    """Get detailed LM Studio status"""
    
    try:
        lm_status = await unified_provider.lm_studio.health_check()
        model_info = await unified_provider.lm_studio.get_model_info()
        
        return {
            "success": True,
            "data": {
                "status": lm_status,
                "info": model_info
            }
        }
    except Exception as e:
        logger.error("Failed to get LM Studio status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get LM Studio status: {e}"
        )


@router.get("/lm-studio/models")
async def get_lm_studio_models():
    """Get models available in LM Studio"""
    
    try:
        models = await unified_provider.lm_studio.get_available_models()
        loaded_model = await unified_provider.lm_studio.get_loaded_model()
        
        return {
            "success": True,
            "data": {
                "available_models": models.get("data", []),
                "loaded_model": loaded_model
            }
        }
    except Exception as e:
        logger.error("Failed to get LM Studio models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get LM Studio models: {e}"
        )


@router.get("/openrouter/status")
async def get_openrouter_status():
    """Get OpenRouter status"""
    
    try:
        health = await unified_provider.openrouter.health_check()
        
        return {
            "success": True,
            "data": {
                "healthy": health,
                "api_key_configured": bool(
                    unified_provider.openrouter.api_key and 
                    unified_provider.openrouter.api_key != "your_openrouter_key_here"
                ),
                "base_url": unified_provider.openrouter.base_url
            }
        }
    except Exception as e:
        logger.error("Failed to get OpenRouter status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OpenRouter status: {e}"
        )


@router.get("/openrouter/models")
async def get_openrouter_models():
    """Get models available through OpenRouter"""
    
    try:
        models = await unified_provider.openrouter.get_available_models()
        
        return {
            "success": True,
            "data": {
                "available_models": models.get("data", []),
                "total_count": len(models.get("data", []))
            }
        }
    except Exception as e:
        logger.error("Failed to get OpenRouter models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OpenRouter models: {e}"
        )


@router.get("/setup-guide")
async def get_setup_guide():
    """Get personalized setup recommendations"""
    
    try:
        recommendations = await unified_provider.get_recommended_setup()
        
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        logger.error("Failed to get setup recommendations", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get setup recommendations: {e}"
        )


@router.post("/test")
async def test_provider_integration():
    """Test the current provider setup with a simple query"""
    
    from app.models.schemas import LLMRequest
    
    test_request = LLMRequest(
        model="test-model",
        system_prompt="You are a helpful assistant. Respond with exactly: 'Provider test successful!'",
        user_message="Test message",
        max_tokens=50,
        temperature=0.1
    )
    
    try:
        response = await unified_provider.call_model(test_request)
        
        return {
            "success": True,
            "data": {
                "provider_used": response.provider,
                "model_used": response.model,
                "response_content": response.content,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "response_time_ms": response.response_time_ms
            }
        }
    except Exception as e:
        logger.error("Provider test failed", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "recommendations": [
                "Check that LM Studio is running with a model loaded, or",
                "Configure OpenRouter API key in your environment variables"
            ]
        }


@router.get("/troubleshoot")
async def troubleshoot_providers():
    """Diagnostic endpoint for troubleshooting provider issues"""
    
    diagnostics = {
        "timestamp": "2024-01-01T00:00:00Z",
        "checks": []
    }
    
    # Check LM Studio connectivity
    try:
        lm_status = await unified_provider.lm_studio.health_check()
        diagnostics["checks"].append({
            "name": "LM Studio Connection",
            "status": lm_status["status"],
            "details": lm_status,
            "suggestions": [
                "Ensure LM Studio is installed and running",
                "Check that the local server is started (usually http://localhost:1234)",
                "Load a model in LM Studio",
                "Verify firewall settings allow localhost connections"
            ] if lm_status["status"] != "healthy" else ["LM Studio is working correctly!"]
        })
    except Exception as e:
        diagnostics["checks"].append({
            "name": "LM Studio Connection",
            "status": "error",
            "error": str(e),
            "suggestions": [
                "Install LM Studio from https://lmstudio.ai/",
                "Start LM Studio and load a model",
                "Enable the local server in LM Studio settings"
            ]
        })
    
    # Check OpenRouter connectivity
    try:
        or_healthy = await unified_provider.openrouter.health_check()
        or_configured = bool(
            unified_provider.openrouter.api_key and 
            unified_provider.openrouter.api_key != "your_openrouter_key_here"
        )
        
        diagnostics["checks"].append({
            "name": "OpenRouter Connection",
            "status": "healthy" if (or_healthy and or_configured) else "issues",
            "api_key_configured": or_configured,
            "api_accessible": or_healthy,
            "suggestions": [
                "Sign up at https://openrouter.ai/ and get an API key",
                "Add OPENROUTER_API_KEY to your .env file",
                "Restart the backend server"
            ] if not (or_healthy and or_configured) else ["OpenRouter is working correctly!"]
        })
    except Exception as e:
        diagnostics["checks"].append({
            "name": "OpenRouter Connection", 
            "status": "error",
            "error": str(e),
            "suggestions": [
                "Check internet connectivity",
                "Verify OpenRouter service status",
                "Check API key format"
            ]
        })
    
    return {
        "success": True,
        "data": diagnostics
    }