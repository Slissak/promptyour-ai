#!/usr/bin/env python3
"""
Script to update model pricing in config/models.yaml from OpenRouter API.
Fetches latest pricing and updates the configuration file automatically.
"""
import asyncio
import httpx
import yaml
from pathlib import Path
from datetime import datetime


async def fetch_openrouter_models():
    """Fetch all available models from OpenRouter API"""
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


def find_model_pricing(models, model_id):
    """Find pricing for a specific model"""
    for model in models:
        if model.get("id") == model_id:
            pricing = model.get("pricing", {})
            return {
                "prompt_cost_per_1k": float(pricing.get("prompt", "0")) * 1000,
                "completion_cost_per_1k": float(pricing.get("completion", "0")) * 1000,
                "context_length": model.get("context_length", 0)
            }
    return None


async def update_models_config():
    """Update models.yaml with latest pricing from OpenRouter"""
    print("Fetching latest pricing from OpenRouter...")

    # Fetch models
    openrouter_models = await fetch_openrouter_models()
    if not openrouter_models:
        print("Failed to fetch models from OpenRouter")
        return False

    print(f"✓ Fetched {len(openrouter_models)} models from OpenRouter")

    # Load current config
    config_path = Path(__file__).parent.parent / "config" / "models.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print("Updating pricing in config...")

    # Update quick mode default
    quick_model_id = config["quick_mode_default"]["model_id"]
    quick_pricing = find_model_pricing(openrouter_models, quick_model_id)
    if quick_pricing:
        config["quick_mode_default"].update(quick_pricing)
        print(f"✓ Updated quick mode: {quick_model_id}")

    # Update enhanced mode tiers
    for tier_name, tier_models in config["enhanced_mode_tiers"].items():
        for i, model_config in enumerate(tier_models):
            model_id = model_config["model_id"]
            pricing = find_model_pricing(openrouter_models, model_id)
            if pricing:
                config["enhanced_mode_tiers"][tier_name][i].update(pricing)
                print(f"✓ Updated {tier_name}: {model_id}")

    # Update free models
    for i, model_config in enumerate(config["free_models"]):
        model_id = model_config["model_id"]
        pricing = find_model_pricing(openrouter_models, model_id)
        if pricing:
            config["free_models"][i].update(pricing)
            print(f"✓ Updated free model: {model_id}")

    # Update thinking models
    for i, model_config in enumerate(config["thinking_models"]):
        model_id = model_config["model_id"]
        pricing = find_model_pricing(openrouter_models, model_id)
        if pricing:
            config["thinking_models"][i].update(pricing)
            print(f"✓ Updated thinking model: {model_id}")

    # Update last updated timestamp in comment
    # (Note: comments will be lost when using yaml.safe_load/dump, so we'll add it in a metadata field)
    if "metadata" not in config:
        config["metadata"] = {}
    config["metadata"]["last_updated"] = datetime.now().isoformat()
    config["metadata"]["total_models_available"] = len(openrouter_models)

    # Save updated config
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)

    print("\n" + "=" * 60)
    print(f"✓ Successfully updated {config_path}")
    print(f"  Last updated: {config['metadata']['last_updated']}")
    print(f"  Total models available: {config['metadata']['total_models_available']}")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = asyncio.run(update_models_config())
    exit(0 if success else 1)
