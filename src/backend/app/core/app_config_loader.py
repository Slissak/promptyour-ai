
from shared_python.config.config_loader import ConfigLoader
from typing import Dict, List, Any

class AppConfigLoader(ConfigLoader):

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

# Global config loader instance
_config_loader = None

def get_config_loader() -> AppConfigLoader:
    """Get global config loader instance (singleton)"""
    global _config_loader
    if _config_loader is None:
        _config_loader = AppConfigLoader()
    return _config_loader
