#!/usr/bin/env python3
"""
Script to fetch and analyze OpenRouter models with pricing information.
Creates a table of cheapest and most reliable models for quick responses.
"""
import asyncio
import httpx
import json
from typing import List, Dict
from datetime import datetime


async def fetch_openrouter_models() -> List[Dict]:
    """
    Fetch all available models from OpenRouter API.

    Returns:
        List of model dictionaries with pricing and metadata
    """
    url = "https://openrouter.ai/api/v1/models"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []


def calculate_cost_per_1k_tokens(model: Dict) -> float:
    """
    Calculate average cost per 1K tokens (prompt + completion).
    For quick mode, we care about total cost for short responses.

    Args:
        model: Model dictionary from OpenRouter API

    Returns:
        Average cost per 1K tokens
    """
    pricing = model.get("pricing", {})

    # Get costs (in USD per token, need to multiply by 1000 for per-1k-tokens)
    prompt_cost = float(pricing.get("prompt", "0")) * 1000
    completion_cost = float(pricing.get("completion", "0")) * 1000

    # For quick mode (100 tokens max output, ~50 token prompt avg)
    # Estimate: 50 prompt tokens + 100 completion tokens
    estimated_cost = (prompt_cost * 50 + completion_cost * 100) / 1000

    return estimated_cost


def is_suitable_for_quick_mode(model: Dict) -> bool:
    """
    Check if model is suitable for quick one-liner responses.

    Criteria:
    - Has pricing information
    - Not explicitly marked as moderated (slower)
    - Context length >= 4096 (reasonable for quick responses)
    - Not a vision-only or specialized model

    Args:
        model: Model dictionary from OpenRouter API

    Returns:
        True if suitable, False otherwise
    """
    model_id = model.get("id", "")
    name = model.get("name", "")
    pricing = model.get("pricing", {})
    context_length = model.get("context_length", 0)

    # Must have pricing
    if not pricing or not pricing.get("prompt") or not pricing.get("completion"):
        return False

    # Must have reasonable context length
    if context_length < 4096:
        return False

    # Skip vision-only or specialized models
    if "vision" in name.lower() and "text" not in name.lower():
        return False

    # Skip embedding models
    if "embed" in model_id.lower() or "embed" in name.lower():
        return False

    # Skip audio/image generation models
    if any(x in model_id.lower() for x in ["whisper", "dall-e", "stable-diffusion", "flux"]):
        return False

    return True


async def main():
    """Main function to fetch, analyze, and display OpenRouter models."""

    print("=" * 120)
    print("OPENROUTER MODELS ANALYSIS - FINDING BEST MODEL FOR QUICK MODE")
    print("=" * 120)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Fetch models
    print("Fetching models from OpenRouter API...")
    models = await fetch_openrouter_models()

    if not models:
        print("Failed to fetch models or no models available.")
        return

    print(f"✓ Fetched {len(models)} total models")
    print()

    # Filter suitable models
    suitable_models = []
    for model in models:
        if is_suitable_for_quick_mode(model):
            model["estimated_quick_cost"] = calculate_cost_per_1k_tokens(model)
            suitable_models.append(model)

    print(f"✓ Found {len(suitable_models)} models suitable for quick mode")
    print()

    # Sort by cost (cheapest first)
    suitable_models.sort(key=lambda m: m["estimated_quick_cost"])

    # Separate free and paid models
    free_models = [m for m in suitable_models if m["estimated_quick_cost"] == 0.0 and ":free" in m.get("id", "")]
    paid_models = [m for m in suitable_models if m["estimated_quick_cost"] > 0.0]

    # Display top 15 free models
    print("=" * 120)
    print("TOP 15 FREE MODELS FOR QUICK MODE")
    print("=" * 120)
    print()
    print(f"{'Rank':<5} {'Model ID':<50} {'Context':<15}")
    print("-" * 120)

    top_free = free_models[:15]
    for i, model in enumerate(top_free, 1):
        model_id = model.get("id", "")
        context = model.get("context_length", 0)
        print(f"{i:<5} {model_id:<50} {context:,}")

    print()

    # Display top 20 paid models
    print("=" * 120)
    print("TOP 20 CHEAPEST PAID MODELS FOR QUICK MODE")
    print("=" * 120)
    print()
    print(f"{'Rank':<5} {'Model ID':<50} {'Prompt/1K':<15} {'Compl/1K':<15} {'Est Cost':<15} {'Context':<15}")
    print("-" * 120)

    top_paid = paid_models[:20]
    for i, model in enumerate(top_paid, 1):
        model_id = model.get("id", "")
        pricing = model.get("pricing", {})
        context = model.get("context_length", 0)

        prompt_cost = float(pricing.get("prompt", "0")) * 1000
        completion_cost = float(pricing.get("completion", "0")) * 1000
        est_cost = model["estimated_quick_cost"]

        print(f"{i:<5} {model_id:<50} ${prompt_cost:.6f}     ${completion_cost:.6f}     ${est_cost:.6f}      {context:,}")

    # Combined top models for downstream processing
    top_models = suitable_models[:30]

    print()
    print("=" * 120)
    print("RECOMMENDED MODELS FOR QUICK MODE")
    print("=" * 120)
    print()

    # Recommend models from both free and paid tiers
    recommendations = []

    # Best FREE model (from reputable provider)
    reputable_providers = ["deepseek", "meta-llama", "google", "mistralai", "nvidia", "qwen"]
    for model in free_models[:10]:
        model_id = model.get("id", "").lower()
        if any(provider in model_id for provider in reputable_providers):
            recommendations.append({
                "rank": "🆓 BEST FREE (RELIABLE)",
                "model": model
            })
            break

    # Best PAID model from reputable provider
    paid_reputable = ["openai", "anthropic", "meta-llama", "google", "mistralai"]
    for model in paid_models[:20]:
        model_id = model.get("id", "").lower()
        if any(provider in model_id for provider in paid_reputable):
            recommendations.append({
                "rank": "💰 CHEAPEST PAID (RELIABLE)",
                "model": model
            })
            break

    # Find Anthropic model (high quality) in paid
    for model in paid_models[:30]:
        if "anthropic" in model.get("id", "").lower():
            recommendations.append({
                "rank": "🎯 ANTHROPIC (PREMIUM)",
                "model": model
            })
            break

    # Find OpenAI GPT model in paid
    for model in paid_models[:30]:
        model_id = model.get("id", "").lower()
        if "openai" in model_id and "gpt" in model_id:
            recommendations.append({
                "rank": "🤖 OPENAI GPT (PREMIUM)",
                "model": model
            })
            break

    # Display recommendations
    for rec in recommendations:
        model = rec["model"]
        model_id = model.get("id", "")
        name = model.get("name", "")
        pricing = model.get("pricing", {})
        context = model.get("context_length", 0)

        prompt_cost = float(pricing.get("prompt", "0")) * 1000
        completion_cost = float(pricing.get("completion", "0")) * 1000
        est_cost = model["estimated_quick_cost"]

        print(f"{rec['rank']}")
        print(f"  Model ID: {model_id}")
        print(f"  Name: {name}")
        print(f"  Pricing: ${prompt_cost:.6f}/1K prompt, ${completion_cost:.6f}/1K completion")
        print(f"  Estimated cost per quick response (50 prompt + 100 completion tokens): ${est_cost:.6f}")
        print(f"  Context length: {context:,} tokens")
        print()

    # Save to JSON for reference
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_models": len(models),
        "suitable_models": len(suitable_models),
        "top_30_cheapest": [
            {
                "rank": i + 1,
                "id": m.get("id"),
                "name": m.get("name"),
                "prompt_cost_per_1k": float(m.get("pricing", {}).get("prompt", "0")) * 1000,
                "completion_cost_per_1k": float(m.get("pricing", {}).get("completion", "0")) * 1000,
                "estimated_quick_cost": m["estimated_quick_cost"],
                "context_length": m.get("context_length")
            }
            for i, m in enumerate(top_models[:30])
        ],
        "recommendations": [
            {
                "category": rec["rank"],
                "id": rec["model"].get("id"),
                "name": rec["model"].get("name"),
                "estimated_quick_cost": rec["model"]["estimated_quick_cost"]
            }
            for rec in recommendations
        ]
    }

    output_file = "openrouter_models_analysis.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    print("=" * 120)
    print(f"✓ Full analysis saved to: {output_file}")
    print("=" * 120)
    print()

    # Final recommendation
    print("=" * 120)
    print("🎯 FINAL RECOMMENDATION FOR QUICK MODE")
    print("=" * 120)
    print()

    if recommendations:
        # Recommend the best free model for quick mode (speed + zero cost)
        free_rec = next((r for r in recommendations if "FREE" in r["rank"]), None)
        if free_rec:
            best = free_rec["model"]
            print("For QUICK MODE (Speed + Zero Cost):")
            print(f"   Model ID: {best.get('id')}")
            print(f"   Name: {best.get('name')}")
            print(f"   Cost: FREE (${best['estimated_quick_cost']:.6f} per response)")
            print(f"   Context: {best.get('context_length', 0):,} tokens")
            print()

        # Also show cheapest paid option
        paid_rec = next((r for r in recommendations if "PAID" in r["rank"]), None)
        if paid_rec:
            best_paid = paid_rec["model"]
            print("For QUICK MODE (Speed + Guaranteed Reliability):")
            print(f"   Model ID: {best_paid.get('id')}")
            print(f"   Name: {best_paid.get('name')}")
            print(f"   Cost: ${best_paid['estimated_quick_cost']:.6f} per response")
            print(f"   Context: {best_paid.get('context_length', 0):,} tokens")
            print()


if __name__ == "__main__":
    asyncio.run(main())
