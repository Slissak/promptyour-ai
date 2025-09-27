"""
Unified LLM Provider
Manages multiple LLM providers (OpenRouter, LM Studio) with automatic fallback
"""
from typing import Optional, Dict, Any, List
from enum import Enum

from app.models.schemas import LLMRequest, LLMResponse
from app.integrations.openrouter_provider import OpenRouterProvider, LLMProviderError
from app.integrations.lm_studio_provider import LMStudioProvider, LMStudioError
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ProviderType(str, Enum):
    """Available LLM provider types"""
    OPENROUTER = "openrouter"
    LM_STUDIO = "lm_studio"
    AUTO = "auto"


class UnifiedLLMProvider:
    """Unified interface for multiple LLM providers with intelligent routing"""
    
    def __init__(self):
        self.openrouter = OpenRouterProvider()
        self.lm_studio = LMStudioProvider()
        
        # Provider preference from settings (default: auto)
        self.preferred_provider = getattr(settings, 'PREFERRED_LLM_PROVIDER', ProviderType.AUTO)
        
        # Local model preference for automatic routing
        self.prefer_local_models = getattr(settings, 'PREFER_LOCAL_LLM', True)

    async def call_model(self, request: LLMRequest) -> LLMResponse:
        """Call LLM with automatic provider selection and fallback"""
        
        provider_type = await self._select_provider(request.model)
        
        logger.info(
            "Routing LLM request",
            model=request.model,
            selected_provider=provider_type,
            preferred_provider=self.preferred_provider
        )
        
        try:
            if provider_type == ProviderType.LM_STUDIO:
                return await self._call_lm_studio(request)
            else:
                return await self._call_openrouter(request)
                
        except (LMStudioError, LLMProviderError) as e:
            logger.warning(
                "Primary provider failed, attempting fallback",
                failed_provider=provider_type,
                error=str(e)
            )
            
            # Attempt fallback
            if provider_type == ProviderType.LM_STUDIO:
                return await self._call_openrouter(request)
            else:
                return await self._call_lm_studio(request)

    async def _call_lm_studio(self, request: LLMRequest) -> LLMResponse:
        """Call LM Studio with model adaptation"""
        
        # For LM Studio, we need to use the currently loaded model
        loaded_model = await self.lm_studio.get_loaded_model()
        if not loaded_model:
            raise LMStudioError("No model loaded in LM Studio")
        
        # Adapt the request for local model
        adapted_request = LLMRequest(
            model=loaded_model["id"],  # Use the actual loaded model ID
            system_prompt=request.system_prompt,
            user_message=request.user_message,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        response = await self.lm_studio.call_model(adapted_request)
        
        # Update response to reflect the original requested model
        response.model = f"{request.model} (via {loaded_model.get('display_name', loaded_model['id'])})"
        
        return response

    async def _call_openrouter(self, request: LLMRequest) -> LLMResponse:
        """Call OpenRouter"""
        return await self.openrouter.call_model(request)

    async def _select_provider(self, model: str) -> ProviderType:
        """Intelligently select provider based on model and availability"""
        
        # If explicitly set, use preferred provider
        if self.preferred_provider != ProviderType.AUTO:
            return self.preferred_provider
        
        # Check LM Studio availability first if local preference is enabled
        if self.prefer_local_models:
            lm_status = await self.lm_studio.health_check()
            if lm_status["status"] == "healthy":
                logger.debug("LM Studio available, using local inference")
                return ProviderType.LM_STUDIO
        
        # Check OpenRouter availability
        openrouter_healthy = await self.openrouter.health_check()
        if openrouter_healthy:
            logger.debug("Using OpenRouter for cloud inference")
            return ProviderType.OPENROUTER
        
        # Fallback to LM Studio even if not preferred
        lm_status = await self.lm_studio.health_check()
        if lm_status["status"] == "healthy":
            logger.debug("Falling back to LM Studio")
            return ProviderType.LM_STUDIO
        
        # If nothing is available, default to OpenRouter (will fail gracefully)
        logger.warning("No providers available, defaulting to OpenRouter")
        return ProviderType.OPENROUTER

    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        
        openrouter_status = await self.openrouter.health_check()
        lm_studio_status = await self.lm_studio.health_check()
        
        return {
            "preferred_provider": self.preferred_provider,
            "prefer_local_models": self.prefer_local_models,
            "providers": {
                "openrouter": {
                    "status": "healthy" if openrouter_status else "unhealthy",
                    "type": "cloud",
                    "api_key_configured": bool(self.openrouter.api_key and self.openrouter.api_key != "your_openrouter_key_here")
                },
                "lm_studio": {
                    **lm_studio_status,
                    "type": "local"
                }
            }
        }

    async def get_available_models(self) -> Dict[str, Any]:
        """Get available models from all providers"""
        
        result = {
            "openrouter": {"models": [], "status": "unavailable"},
            "lm_studio": {"models": [], "status": "unavailable"}
        }
        
        # Get OpenRouter models
        try:
            if await self.openrouter.health_check():
                or_models = await self.openrouter.get_available_models()
                result["openrouter"] = {
                    "models": or_models.get("data", []),
                    "status": "available",
                    "count": len(or_models.get("data", []))
                }
        except Exception as e:
            logger.debug("Failed to get OpenRouter models", error=str(e))
        
        # Get LM Studio models
        try:
            lm_status = await self.lm_studio.health_check()
            if lm_status["status"] == "healthy":
                lm_models = await self.lm_studio.get_available_models()
                result["lm_studio"] = {
                    "models": lm_models.get("data", []),
                    "status": "available",
                    "loaded_model": lm_status.get("loaded_model"),
                    "count": len(lm_models.get("data", []))
                }
        except Exception as e:
            logger.debug("Failed to get LM Studio models", error=str(e))
        
        return result

    async def health_check(self) -> Dict[str, Any]:
        """Overall health check of the unified provider"""
        
        status = await self.get_provider_status()
        
        # Determine overall health
        openrouter_ok = status["providers"]["openrouter"]["status"] == "healthy"
        lm_studio_ok = status["providers"]["lm_studio"]["status"] == "healthy"
        
        if lm_studio_ok or openrouter_ok:
            overall_status = "healthy"
        elif status["providers"]["lm_studio"]["status"] == "unavailable" and status["providers"]["openrouter"]["api_key_configured"]:
            overall_status = "degraded"  # OpenRouter available but not healthy
        else:
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "active_providers": [
                name for name, info in status["providers"].items() 
                if info["status"] == "healthy"
            ],
            **status
        }

    async def get_recommended_setup(self) -> Dict[str, Any]:
        """Get setup recommendations for optimal performance"""
        
        status = await self.get_provider_status()
        recommendations = []
        
        if not status["providers"]["lm_studio"]["status"] == "healthy":
            recommendations.append({
                "type": "lm_studio_setup",
                "priority": "high" if self.prefer_local_models else "medium",
                "title": "Set up LM Studio for local inference",
                "description": "Install LM Studio and load a model for free, private, and fast local inference",
                "steps": [
                    "Download and install LM Studio from https://lmstudio.ai/",
                    "Load a model (recommend Llama 3.2 3B for speed or Llama 3.1 8B for quality)",
                    "Start the local server (default: http://localhost:1234)",
                    "The backend will automatically detect and use the local model"
                ]
            })
        
        if not status["providers"]["openrouter"]["api_key_configured"]:
            recommendations.append({
                "type": "openrouter_setup", 
                "priority": "medium",
                "title": "Configure OpenRouter for cloud models",
                "description": "Add OpenRouter API key for access to multiple cloud LLM providers",
                "steps": [
                    "Sign up at https://openrouter.ai/",
                    "Get your API key from the dashboard",
                    "Add OPENROUTER_API_KEY to your .env file",
                    "Restart the backend to enable cloud model access"
                ]
            })
        
        if not recommendations:
            recommendations.append({
                "type": "optimization",
                "priority": "low",
                "title": "Everything looks good!",
                "description": "Your LLM setup is optimized and ready to go"
            })
        
        return {
            "current_setup": status,
            "recommendations": recommendations
        }