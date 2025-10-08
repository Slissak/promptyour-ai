"""
OpenRouter Integration
Unified interface for multiple LLM providers through OpenRouter API
"""
import asyncio
import time
from typing import Optional, Dict, Any
import httpx
import json

from app.models.schemas import LLMRequest, LLMResponse
from app.core.config import settings
from app.core.logging import get_logger
from app.utils.thinking_config import get_thinking_config

logger = get_logger(__name__)


class OpenRouterProvider:
    """OpenRouter API client for unified LLM access"""
    
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = settings.OPENROUTER_API_KEY if hasattr(settings, 'OPENROUTER_API_KEY') else None
        
        # OpenRouter model mapping
        self.model_mapping = {
            "claude-3-opus": "anthropic/claude-3-opus",
            "claude-3-sonnet": "anthropic/claude-3-sonnet",
            "claude-3-haiku": "anthropic/claude-3-haiku", 
            "gpt-4": "openai/gpt-4",
            "gpt-3.5-turbo": "openai/gpt-3.5-turbo"
        }
        
        # Cost tracking (per 1K tokens)
        self.model_costs = {
            "anthropic/claude-3-opus": {"input": 0.015, "output": 0.075},
            "anthropic/claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "anthropic/claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "openai/gpt-4": {"input": 0.03, "output": 0.06},
            "openai/gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
        }

    async def call_model(self, request: LLMRequest) -> LLMResponse:
        """Call model through OpenRouter API"""
        
        # Map model name to OpenRouter format
        openrouter_model = self.model_mapping.get(request.model, request.model)
        
        logger.info(
            "Calling OpenRouter API",
            model=request.model,
            openrouter_model=openrouter_model,
            max_tokens=request.max_tokens
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

            # Get reasoning configuration if enabled
            reasoning_config = get_thinking_config(
                model=request.model,
                enable_reasoning=request.enable_reasoning,
                reasoning_effort=request.reasoning_effort,
                reasoning_budget_tokens=request.reasoning_budget_tokens
            )

            logger.info(
                "OpenRouter API request details",
                model=openrouter_model,
                message_count=len(messages),
                has_system_prompt=bool(request.system_prompt and request.system_prompt.strip()),
                user_message_length=len(request.user_message),
                reasoning_enabled=bool(reasoning_config)
            )

            # Build request payload
            payload = {
                "model": openrouter_model,
                "messages": messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": False
            }

            # Add reasoning configuration if enabled
            if reasoning_config:
                payload["reasoning"] = reasoning_config
                logger.info("Extended thinking/reasoning enabled", reasoning_config=reasoning_config)

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://promptyour.ai",  # Required by OpenRouter
                        "X-Title": "PromptYour.AI"  # Optional but recommended
                    },
                    json=payload
                )
                
                response.raise_for_status()
                data = response.json()
                
        except httpx.RequestError as e:
            logger.error("OpenRouter API request failed", error=str(e))
            raise LLMProviderError(f"OpenRouter API request failed: {e}")
        except httpx.HTTPStatusError as e:
            logger.error("OpenRouter API HTTP error", status_code=e.response.status_code, error=str(e))
            raise LLMProviderError(f"OpenRouter API error {e.response.status_code}: {e}")
        
        # Parse response
        response_time_ms = int((time.time() - start_time) * 1000)

        try:
            message = data["choices"][0]["message"]
            content = message.get("content", "")
            thinking_content = None

            # Extract thinking/reasoning from response (but don't show to user)
            # Case 1: Anthropic models return content as array with thinking blocks
            if isinstance(content, list):
                thinking_blocks = []
                text_blocks = []

                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "thinking":
                            thinking_blocks.append(block.get("thinking", ""))
                        elif block.get("type") == "text":
                            text_blocks.append(block.get("text", ""))

                # Combine thinking blocks (stored internally)
                if thinking_blocks:
                    thinking_content = "\n\n".join(thinking_blocks)

                # Combine text blocks (shown to user)
                content = "\n\n".join(text_blocks) if text_blocks else ""

                logger.info(
                    "Extracted thinking from Anthropic-style response",
                    thinking_length=len(thinking_content) if thinking_content else 0,
                    text_length=len(content)
                )

            # Case 2: OpenAI models return reasoning_details separately
            elif "reasoning_details" in message:
                reasoning_details = message.get("reasoning_details", [])
                if reasoning_details:
                    reasoning_texts = []
                    for detail in reasoning_details:
                        if isinstance(detail, dict):
                            # Extract text or summary from reasoning
                            if detail.get("type") == "reasoning.text":
                                reasoning_texts.append(detail.get("text", ""))
                            elif detail.get("type") == "reasoning.summary":
                                reasoning_texts.append(detail.get("summary", ""))

                    if reasoning_texts:
                        thinking_content = "\n\n".join(reasoning_texts)
                        logger.info(
                            "Extracted thinking from OpenAI-style reasoning_details",
                            thinking_length=len(thinking_content)
                        )

            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

            logger.info(
                "OpenRouter response parsed",
                model=openrouter_model,
                content_length=len(content) if content else 0,
                content_preview=content[:100] if content else "EMPTY",
                has_thinking=bool(thinking_content),
                tokens=total_tokens
            )

            # Calculate cost
            cost = self._calculate_cost(openrouter_model, prompt_tokens, completion_tokens)

            # Generate message ID
            message_id = self._generate_message_id()

            llm_response = LLMResponse(
                content=content,  # Only the text answer (no thinking shown to user)
                model=request.model,
                provider="openrouter",
                tokens_used=total_tokens,
                cost=cost,
                response_time_ms=response_time_ms,
                message_id=message_id,
                thinking=thinking_content  # Stored internally for session/debug
            )
            
            logger.info(
                "OpenRouter API success",
                model=request.model,
                tokens_used=total_tokens,
                cost=cost,
                response_time_ms=response_time_ms
            )
            
            return llm_response
            
        except KeyError as e:
            logger.error("Failed to parse OpenRouter response", error=str(e), response=data)
            raise LLMProviderError(f"Invalid OpenRouter response format: missing {e}")

    def _calculate_cost(self, openrouter_model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on token usage"""
        if openrouter_model not in self.model_costs:
            # Fallback cost estimation
            return (prompt_tokens + completion_tokens) * 0.001 / 1000
        
        costs = self.model_costs[openrouter_model]
        input_cost = (prompt_tokens / 1000) * costs["input"]
        output_cost = (completion_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        import uuid
        return str(uuid.uuid4())

    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models from OpenRouter"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("Failed to fetch OpenRouter models", error=str(e))
            return {}

    async def health_check(self) -> bool:
        """Check if OpenRouter API is accessible"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/models")
                return response.status_code == 200
        except Exception:
            return False


class LLMProviderError(Exception):
    """Exception raised by LLM providers"""
    pass


class ModelNotResponsiveError(LLMProviderError):
    """Exception raised when model is not responsive"""
    pass


class RateLimitError(LLMProviderError):
    """Exception raised when rate limit is exceeded"""
    pass