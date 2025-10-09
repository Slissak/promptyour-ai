"""
LM Studio Integration
Local LLM provider through LM Studio's OpenAI-compatible API
"""
import asyncio
import time
import re
from typing import Optional, Dict, Any, List, Tuple
import httpx
import json

from app.models.schemas import LLMRequest, LLMResponse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LMStudioProvider:
    """LM Studio local LLM provider with OpenAI-compatible API"""
    
    def __init__(self):
        # LM Studio default settings - can be configured via environment
        self.base_url = getattr(settings, 'LM_STUDIO_URL', "http://localhost:1234/v1")
        self.api_key = getattr(settings, 'LM_STUDIO_API_KEY', "lm-studio")  # LM Studio default
        
        # Local model cost tracking (minimal since it's local)
        self.local_cost_per_token = 0.0  # Free local inference
        
        # Common local model names and their display names
        self.model_display_names = {
            "llama-3.2-3b": "Llama 3.2 3B",
            "llama-3.2-1b": "Llama 3.2 1B", 
            "llama-3.1-8b": "Llama 3.1 8B",
            "llama-3.1-70b": "Llama 3.1 70B",
            "mistral-7b": "Mistral 7B",
            "codellama-7b": "Code Llama 7B",
            "phi-3-mini": "Phi-3 Mini",
            "gemma-2b": "Gemma 2B",
            "qwen-2.5": "Qwen 2.5"
        }

    async def call_model(self, request: LLMRequest) -> LLMResponse:
        """Call local model through LM Studio API"""
        
        logger.info(
            "Calling LM Studio local API",
            model=request.model,
            max_tokens=request.max_tokens,
            base_url=self.base_url
        )
        
        start_time = time.time()

        try:
            # Build messages array - only include system message if not empty
            messages = []
            if request.system_prompt and request.system_prompt.strip():
                messages.append({
                    "role": "system",
                    "content": request.system_prompt
                })
            messages.append({
                "role": "user",
                "content": request.user_message
            })

            async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for local inference
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": request.model,  # LM Studio uses the loaded model
                        "messages": messages,
                        "max_tokens": request.max_tokens,
                        "temperature": request.temperature,
                        "stream": False
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                
        except httpx.ConnectError as e:
            logger.error("LM Studio connection failed - is LM Studio running?", error=str(e))
            raise LMStudioError(f"LM Studio connection failed: {e}. Make sure LM Studio is running on {self.base_url}")
        except httpx.RequestError as e:
            logger.error("LM Studio API request failed", error=str(e))
            raise LMStudioError(f"LM Studio API request failed: {e}")
        except httpx.HTTPStatusError as e:
            logger.error("LM Studio API HTTP error", status_code=e.response.status_code, error=str(e))
            raise LMStudioError(f"LM Studio API error {e.response.status_code}: {e}")
        
        # Parse response
        response_time_ms = int((time.time() - start_time) * 1000)

        try:
            raw_content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            # Extract thinking from content if present
            content, thinking_content = self._extract_thinking(raw_content)

            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

            # Local inference is free
            cost = self.local_cost_per_token * total_tokens

            # Generate message ID
            message_id = self._generate_message_id()

            llm_response = LLMResponse(
                content=content,  # Only the final answer (no thinking shown to user)
                model=request.model,
                provider="lm_studio",
                tokens_used=total_tokens,
                cost=cost,
                response_time_ms=response_time_ms,
                message_id=message_id,
                thinking=thinking_content  # Stored internally for session/debug
            )

            logger.info(
                "LM Studio API success",
                model=request.model,
                tokens_used=total_tokens,
                response_time_ms=response_time_ms,
                has_thinking=bool(thinking_content),
                thinking_length=len(thinking_content) if thinking_content else 0
            )

            return llm_response
            
        except KeyError as e:
            logger.error("Failed to parse LM Studio response", error=str(e), response=data)
            raise LMStudioError(f"Invalid LM Studio response format: missing {e}")

    def _extract_thinking(self, content: str) -> Tuple[str, Optional[str]]:
        """
        Extract thinking/reasoning from model response.

        Handles common thinking patterns from models like Qwen, DeepSeek, etc.
        Returns (final_answer, thinking_content)
        """
        if not content:
            return content, None

        thinking_content = None
        final_answer = content

        # Pattern 1: <think>...</think> tags (common in Qwen models)
        think_pattern = r'<think>(.*?)</think>'
        think_matches = re.findall(think_pattern, content, re.DOTALL | re.IGNORECASE)
        if think_matches:
            thinking_content = "\n\n".join(think_matches)
            # Remove thinking tags from final answer
            final_answer = re.sub(think_pattern, '', content, flags=re.DOTALL | re.IGNORECASE).strip()
            logger.info(
                "Extracted thinking from <think> tags",
                thinking_length=len(thinking_content),
                answer_length=len(final_answer)
            )
            return final_answer, thinking_content

        # Pattern 2: <thinking>...</thinking> tags
        thinking_pattern = r'<thinking>(.*?)</thinking>'
        thinking_matches = re.findall(thinking_pattern, content, re.DOTALL | re.IGNORECASE)
        if thinking_matches:
            thinking_content = "\n\n".join(thinking_matches)
            final_answer = re.sub(thinking_pattern, '', content, flags=re.DOTALL | re.IGNORECASE).strip()
            logger.info(
                "Extracted thinking from <thinking> tags",
                thinking_length=len(thinking_content),
                answer_length=len(final_answer)
            )
            return final_answer, thinking_content

        # Pattern 3: <reasoning>...</reasoning> tags
        reasoning_pattern = r'<reasoning>(.*?)</reasoning>'
        reasoning_matches = re.findall(reasoning_pattern, content, re.DOTALL | re.IGNORECASE)
        if reasoning_matches:
            thinking_content = "\n\n".join(reasoning_matches)
            final_answer = re.sub(reasoning_pattern, '', content, flags=re.DOTALL | re.IGNORECASE).strip()
            logger.info(
                "Extracted thinking from <reasoning> tags",
                thinking_length=len(thinking_content),
                answer_length=len(final_answer)
            )
            return final_answer, thinking_content

        # Pattern 4: Markdown-style thinking blocks (```thinking ... ```)
        md_thinking_pattern = r'```thinking\n(.*?)```'
        md_thinking_matches = re.findall(md_thinking_pattern, content, re.DOTALL)
        if md_thinking_matches:
            thinking_content = "\n\n".join(md_thinking_matches)
            final_answer = re.sub(md_thinking_pattern, '', content, flags=re.DOTALL).strip()
            logger.info(
                "Extracted thinking from markdown blocks",
                thinking_length=len(thinking_content),
                answer_length=len(final_answer)
            )
            return final_answer, thinking_content

        # No thinking markers found - return original content
        return final_answer, None

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        import uuid
        return str(uuid.uuid4())

    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models from LM Studio"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                models_data = response.json()
                
                # Enhance with display names
                if "data" in models_data:
                    for model in models_data["data"]:
                        model_id = model.get("id", "")
                        for key, display_name in self.model_display_names.items():
                            if key in model_id.lower():
                                model["display_name"] = display_name
                                break
                        else:
                            model["display_name"] = model_id
                
                return models_data
                
        except Exception as e:
            logger.error("Failed to fetch LM Studio models", error=str(e))
            return {"data": []}

    async def get_loaded_model(self) -> Optional[Dict[str, Any]]:
        """Get currently loaded model in LM Studio"""
        try:
            models = await self.get_available_models()
            loaded_models = [m for m in models.get("data", []) if m.get("id")]
            
            if loaded_models:
                model = loaded_models[0]  # LM Studio typically loads one model at a time
                logger.info("Found loaded model", model_id=model.get("id"), display_name=model.get("display_name"))
                return model
            else:
                logger.warning("No model loaded in LM Studio")
                return None
                
        except Exception as e:
            logger.error("Failed to get loaded model", error=str(e))
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Check if LM Studio API is accessible and get status"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Check API availability
                response = await client.get(f"{self.base_url}/models")
                is_healthy = response.status_code == 200
                
                if is_healthy:
                    loaded_model = await self.get_loaded_model()
                    return {
                        "status": "healthy",
                        "url": self.base_url,
                        "loaded_model": loaded_model.get("id") if loaded_model else None,
                        "model_display_name": loaded_model.get("display_name") if loaded_model else None
                    }
                else:
                    return {
                        "status": "unhealthy", 
                        "url": self.base_url,
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except httpx.ConnectError:
            return {
                "status": "unavailable",
                "url": self.base_url,
                "error": "Connection failed - LM Studio not running?"
            }
        except Exception as e:
            return {
                "status": "error",
                "url": self.base_url, 
                "error": str(e)
            }

    async def get_model_info(self) -> Dict[str, Any]:
        """Get detailed information about the local setup"""
        health = await self.health_check()
        models = await self.get_available_models()
        
        return {
            "provider": "lm_studio",
            "status": health["status"],
            "base_url": self.base_url,
            "loaded_model": health.get("loaded_model"),
            "model_display_name": health.get("model_display_name"),
            "available_models": len(models.get("data", [])),
            "cost_per_token": self.local_cost_per_token,
            "advantages": [
                "Free local inference",
                "No API rate limits", 
                "Privacy - data stays local",
                "Offline capability",
                "Fast inference (GPU acceleration)"
            ]
        }


class LMStudioError(Exception):
    """Exception raised by LM Studio provider"""
    pass