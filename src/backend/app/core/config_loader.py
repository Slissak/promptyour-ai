"""
Configuration Loader
Centralized loader for YAML configuration files (themes, audiences, response styles, models)
"""
from pathlib import Path
from typing import Dict, List, Any
from enum import Enum
import yaml

from app.core.logging import get_logger

logger = get_logger(__name__)


class ConfigLoader:
    """Centralized configuration loader for easy-to-modify YAML configs"""

    def __init__(self):
        # Path to config directory
        self.config_dir = Path(__file__).parent.parent.parent.parent / "config"
        self._cache = {}

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML file from config directory with caching"""
        if filename in self._cache:
            return self._cache[filename]

        file_path = self.config_dir / filename
        if not file_path.exists():
            logger.warning(f"Config file not found: {filename}")
            return {}

        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                self._cache[filename] = data
                logger.info(f"Loaded config: {filename}")
                return data
        except Exception as e:
            logger.error(f"Failed to load config {filename}: {e}")
            return {}

    def reload(self):
        """Clear cache to force reload of configs"""
        self._cache.clear()
        logger.info("Config cache cleared")

    # ===== THEMES =====
    def get_themes(self) -> List[Dict[str, str]]:
        """Get list of available themes"""
        data = self._load_yaml("themes.yaml")
        return data.get("themes", [])

    def get_theme_ids(self) -> List[str]:
        """Get list of theme IDs for enum creation"""
        return [theme["id"] for theme in self.get_themes()]

    def get_theme_by_id(self, theme_id: str) -> Dict[str, str]:
        """Get theme details by ID"""
        for theme in self.get_themes():
            if theme["id"] == theme_id:
                return theme
        return {}

    # ===== AUDIENCES =====
    def get_audiences(self) -> List[Dict[str, str]]:
        """Get list of available audiences"""
        data = self._load_yaml("audiences.yaml")
        return data.get("audiences", [])

    def get_audience_ids(self) -> List[str]:
        """Get list of audience IDs for enum creation"""
        return [audience["id"] for audience in self.get_audiences()]

    def get_audience_by_id(self, audience_id: str) -> Dict[str, str]:
        """Get audience details by ID"""
        for audience in self.get_audiences():
            if audience["id"] == audience_id:
                return audience
        return {}

    # ===== RESPONSE STYLES =====
    def get_response_styles(self) -> List[Dict[str, str]]:
        """Get list of available response styles"""
        data = self._load_yaml("response_styles.yaml")
        return data.get("response_styles", [])

    def get_response_style_ids(self) -> List[str]:
        """Get list of response style IDs for enum creation"""
        return [style["id"] for style in self.get_response_styles()]

    def get_response_style_by_id(self, style_id: str) -> Dict[str, str]:
        """Get response style details by ID"""
        for style in self.get_response_styles():
            if style["id"] == style_id:
                return style
        return {}

    # ===== MODELS =====
    def get_models_config(self) -> Dict[str, Any]:
        """Get full models configuration"""
        return self._load_yaml("models.yaml")

    def get_quick_mode_default(self) -> Dict[str, Any]:
        """Get default model for quick mode"""
        config = self.get_models_config()
        return config.get("quick_mode_default", {})

    def get_enhanced_mode_tiers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get model tiers for enhanced mode"""
        config = self.get_models_config()
        return config.get("enhanced_mode_tiers", {})

    def get_free_models(self) -> List[Dict[str, Any]]:
        """Get list of free models"""
        config = self.get_models_config()
        return config.get("free_models", [])

    def get_thinking_models(self) -> List[Dict[str, Any]]:
        """Get list of thinking-capable models"""
        config = self.get_models_config()
        return config.get("thinking_models", [])

    def get_model_aliases(self) -> Dict[str, str]:
        """Get model aliases mapping"""
        config = self.get_models_config()
        return config.get("model_aliases", {})

    def get_model_by_id(self, model_id: str) -> Dict[str, Any]:
        """Find model configuration by ID across all categories"""
        config = self.get_models_config()

        # Check quick mode default
        if config.get("quick_mode_default", {}).get("model_id") == model_id:
            return config["quick_mode_default"]

        # Check enhanced mode tiers
        for tier_models in config.get("enhanced_mode_tiers", {}).values():
            for model in tier_models:
                if model.get("model_id") == model_id:
                    return model

        # Check free models
        for model in config.get("free_models", []):
            if model.get("model_id") == model_id:
                return model

        # Check thinking models
        for model in config.get("thinking_models", []):
            if model.get("model_id") == model_id:
                return model

        return {}


# Global config loader instance
_config_loader = None


def get_config_loader() -> ConfigLoader:
    """Get global config loader instance (singleton)"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
