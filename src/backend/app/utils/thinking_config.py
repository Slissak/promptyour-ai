"""
Configuration for extended thinking/reasoning capabilities across different LLM providers.

This module provides utilities to:
1. Detect which models support extended thinking/reasoning
2. Configure appropriate reasoning parameters based on model and provider
3. Apply correct parameter formats for OpenRouter API
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# Models that support extended thinking/reasoning
THINKING_CAPABLE_MODELS = {
    # Anthropic models (via OpenRouter use 'reasoning' parameter)
    "claude-sonnet-4": {"type": "anthropic", "default_tokens": 8000},
    "claude-opus-4": {"type": "anthropic", "default_tokens": 10000},
    "claude-3.7-sonnet": {"type": "anthropic", "default_tokens": 8000},
    "claude-3-7-sonnet": {"type": "anthropic", "default_tokens": 8000},

    # OpenAI reasoning models (via OpenRouter use 'reasoning' parameter)
    "o3-mini": {"type": "openai", "default_effort": "high"},
    "o1": {"type": "openai", "default_effort": "high"},
    "o1-mini": {"type": "openai", "default_effort": "medium"},

    # DeepSeek reasoning models (via OpenRouter use 'reasoning' parameter)
    "deepseek-r1": {"type": "deepseek", "default_effort": "high"},
    "deepseek-r1-distill": {"type": "deepseek", "default_effort": "medium"},
}


def supports_thinking(model: str) -> bool:
    """
    Check if a model supports extended thinking/reasoning.

    Args:
        model: Model name (e.g., "claude-sonnet-4", "openai/gpt-4o")

    Returns:
        True if model supports thinking, False otherwise
    """
    # Extract model name without provider prefix
    model_name = model.split("/")[-1] if "/" in model else model

    # Check if model name or any part of it matches thinking-capable models
    for capable_model in THINKING_CAPABLE_MODELS:
        if capable_model in model_name.lower():
            return True

    return False


def get_thinking_config(
    model: str,
    enable_reasoning: bool = False,
    reasoning_effort: Optional[str] = None,
    reasoning_budget_tokens: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Get the appropriate reasoning configuration for a model.

    For OpenRouter API, all models use the unified 'reasoning' parameter with either:
    - max_tokens: for Anthropic models
    - effort: for OpenAI/DeepSeek models

    Args:
        model: Model name
        enable_reasoning: Whether to enable reasoning
        reasoning_effort: Override effort level ("high", "medium", "low")
        reasoning_budget_tokens: Override token budget

    Returns:
        Dictionary with reasoning configuration, or None if reasoning is disabled
    """
    if not enable_reasoning:
        return None

    # Extract model name without provider prefix
    model_name = model.split("/")[-1] if "/" in model else model

    # Find matching thinking-capable model
    model_config = None
    for capable_model, config in THINKING_CAPABLE_MODELS.items():
        if capable_model in model_name.lower():
            model_config = config
            break

    if not model_config:
        logger.warning(f"Model {model} does not support extended thinking/reasoning")
        return None

    # Build reasoning configuration based on model type
    reasoning_config = {}

    if model_config["type"] == "anthropic":
        # Anthropic models use max_tokens
        tokens = reasoning_budget_tokens or model_config.get("default_tokens", 8000)
        reasoning_config["max_tokens"] = tokens
        logger.info(f"Enabling reasoning for Anthropic model {model} with {tokens} tokens")

    elif model_config["type"] in ["openai", "deepseek"]:
        # OpenAI and DeepSeek use effort levels
        effort = reasoning_effort or model_config.get("default_effort", "high")
        reasoning_config["effort"] = effort
        logger.info(f"Enabling reasoning for {model_config['type']} model {model} with effort={effort}")

    return reasoning_config


def get_recommended_reasoning_params(model: str, mode: str = "enhanced") -> Dict[str, Any]:
    """
    Get recommended reasoning parameters for a model based on the chat mode.

    Args:
        model: Model name
        mode: Chat mode ("quick" or "enhanced")

    Returns:
        Dictionary with recommended enable_reasoning, effort, and budget_tokens
    """
    if mode == "quick":
        # Quick mode: NO reasoning for fast responses
        return {
            "enable_reasoning": False,
            "reasoning_effort": None,
            "reasoning_budget_tokens": None
        }

    elif mode == "enhanced":
        # Enhanced mode: Enable reasoning if model supports it
        if not supports_thinking(model):
            return {
                "enable_reasoning": False,
                "reasoning_effort": None,
                "reasoning_budget_tokens": None
            }

        # Extract model name
        model_name = model.split("/")[-1] if "/" in model else model

        # Find model configuration
        for capable_model, config in THINKING_CAPABLE_MODELS.items():
            if capable_model in model_name.lower():
                if config["type"] == "anthropic":
                    return {
                        "enable_reasoning": True,
                        "reasoning_effort": None,
                        "reasoning_budget_tokens": config.get("default_tokens", 8000)
                    }
                else:  # OpenAI or DeepSeek
                    return {
                        "enable_reasoning": True,
                        "reasoning_effort": config.get("default_effort", "high"),
                        "reasoning_budget_tokens": None
                    }

        # Default if not found
        return {
            "enable_reasoning": False,
            "reasoning_effort": None,
            "reasoning_budget_tokens": None
        }

    # Default: no reasoning
    return {
        "enable_reasoning": False,
        "reasoning_effort": None,
        "reasoning_budget_tokens": None
    }
