"""
Configuration Manager for Model Evaluation System
Handles loading, validation, and hot-reloading of evaluation configuration
"""
import yaml
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.core.logging import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manages configuration for the model evaluation system"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = {}
        self.last_loaded = None
        self.observers = []  # For file watching
        self.change_callbacks = []  # Callbacks for config changes
        
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Look for config file in multiple locations
        possible_paths = [
            "config/evaluation_config.yaml",
            "../../../config/evaluation_config.yaml",
            "/app/config/evaluation_config.yaml",
            os.path.join(os.path.dirname(__file__), "../../../config/evaluation_config.yaml")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no file found, use the first path as default
        return possible_paths[0]

    async def load_config(self, validate: bool = True) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        
        try:
            if not os.path.exists(self.config_file):
                logger.warning(f"Config file not found: {self.config_file}, using defaults")
                return self._get_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if validate:
                await self._validate_config(config)
            
            self.config = config
            self.last_loaded = datetime.now()
            
            logger.info(f"Configuration loaded successfully from {self.config_file}")
            
            # Notify callbacks
            await self._notify_change_callbacks()
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            if not self.config:
                logger.warning("Using default configuration")
                self.config = self._get_default_config()
            return self.config

    async def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to YAML file"""
        
        try:
            config_to_save = config or self.config
            
            # Validate before saving
            await self._validate_config(config_to_save)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Save with backup
            backup_file = f"{self.config_file}.backup.{int(datetime.now().timestamp())}"
            if os.path.exists(self.config_file):
                os.rename(self.config_file, backup_file)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_to_save, f, default_flow_style=False, sort_keys=False)
            
            self.config = config_to_save
            self.last_loaded = datetime.now()
            
            logger.info(f"Configuration saved successfully to {self.config_file}")
            
            # Clean up old backups (keep last 5)
            self._cleanup_backups()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get_evaluation_sources(self, active_only: bool = True) -> Dict[str, Any]:
        """Get evaluation sources configuration"""
        sources = self.config.get('evaluation_sources', {})
        
        if active_only:
            return {k: v for k, v in sources.items() if v.get('active', True)}
        
        return sources

    def get_themes(self, active_only: bool = True) -> Dict[str, Any]:
        """Get themes configuration"""
        themes = self.config.get('themes', {})
        
        if active_only:
            return {k: v for k, v in themes.items() if v.get('active', True)}
        
        return themes

    def get_theme_source_weights(self) -> Dict[str, Dict[str, float]]:
        """Get theme to source weight mappings"""
        return self.config.get('theme_source_weights', {})

    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return self.config.get('model_config', {})

    def get_scoring_config(self) -> Dict[str, Any]:
        """Get scoring configuration"""
        return self.config.get('scoring', {})

    def get_scheduler_config(self) -> Dict[str, Any]:
        """Get scheduler configuration"""
        return self.config.get('scheduler', {})

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags"""
        return self.config.get('features', {})

    async def add_evaluation_source(self, source_name: str, source_config: Dict[str, Any]) -> bool:
        """Add a new evaluation source"""
        
        try:
            if 'evaluation_sources' not in self.config:
                self.config['evaluation_sources'] = {}
            
            # Validate source configuration
            required_fields = ['name', 'url', 'type', 'themes', 'scraping_config']
            for field in required_fields:
                if field not in source_config:
                    raise ValueError(f"Missing required field: {field}")
            
            self.config['evaluation_sources'][source_name] = source_config
            
            # Save to file
            await self.save_config()
            
            logger.info(f"Added new evaluation source: {source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add evaluation source {source_name}: {e}")
            return False

    async def update_theme_weights(self, theme: str, weights: Dict[str, float]) -> bool:
        """Update theme source weights"""
        
        try:
            if 'theme_source_weights' not in self.config:
                self.config['theme_source_weights'] = {}
            
            # Validate weights sum to approximately 1.0
            total_weight = sum(weights.values())
            if abs(total_weight - 1.0) > 0.1:
                logger.warning(f"Theme weights for {theme} sum to {total_weight}, not 1.0")
            
            self.config['theme_source_weights'][theme] = weights
            
            # Save to file
            await self.save_config()
            
            logger.info(f"Updated theme weights for {theme}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update theme weights for {theme}: {e}")
            return False

    async def add_theme(self, theme_name: str, theme_config: Dict[str, Any]) -> bool:
        """Add a new theme"""
        
        try:
            if 'themes' not in self.config:
                self.config['themes'] = {}
            
            # Validate theme configuration
            required_fields = ['display_name', 'description', 'keywords']
            for field in required_fields:
                if field not in theme_config:
                    raise ValueError(f"Missing required field: {field}")
            
            self.config['themes'][theme_name] = theme_config
            
            # Save to file
            await self.save_config()
            
            logger.info(f"Added new theme: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add theme {theme_name}: {e}")
            return False

    async def toggle_source(self, source_name: str, active: bool) -> bool:
        """Enable or disable an evaluation source"""
        
        try:
            sources = self.config.get('evaluation_sources', {})
            if source_name not in sources:
                raise ValueError(f"Source not found: {source_name}")
            
            sources[source_name]['active'] = active
            
            # Save to file
            await self.save_config()
            
            logger.info(f"{'Enabled' if active else 'Disabled'} source: {source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to toggle source {source_name}: {e}")
            return False

    async def update_feature_flag(self, feature: str, enabled: bool) -> bool:
        """Update a feature flag"""
        
        try:
            if 'features' not in self.config:
                self.config['features'] = {}
            
            self.config['features'][feature] = enabled
            
            # Save to file
            await self.save_config()
            
            logger.info(f"{'Enabled' if enabled else 'Disabled'} feature: {feature}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update feature flag {feature}: {e}")
            return False

    def start_file_watcher(self):
        """Start watching configuration file for changes"""
        
        class ConfigFileHandler(FileSystemEventHandler):
            def __init__(self, config_manager):
                self.config_manager = config_manager
                
            def on_modified(self, event):
                if event.src_path == self.config_manager.config_file:
                    logger.info("Configuration file changed, reloading...")
                    asyncio.create_task(self.config_manager.load_config())
        
        if os.path.exists(self.config_file):
            observer = Observer()
            observer.schedule(
                ConfigFileHandler(self), 
                os.path.dirname(self.config_file), 
                recursive=False
            )
            observer.start()
            self.observers.append(observer)
            
            logger.info(f"Started watching config file: {self.config_file}")

    def stop_file_watcher(self):
        """Stop watching configuration file"""
        
        for observer in self.observers:
            observer.stop()
            observer.join()
        
        self.observers.clear()
        logger.info("Stopped watching config file")

    def add_change_callback(self, callback):
        """Add callback to be notified of config changes"""
        self.change_callbacks.append(callback)

    def remove_change_callback(self, callback):
        """Remove change callback"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)

    async def _notify_change_callbacks(self):
        """Notify all callbacks of configuration change"""
        for callback in self.change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.config)
                else:
                    callback(self.config)
            except Exception as e:
                logger.error(f"Error in config change callback: {e}")

    async def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration structure"""
        
        validation_rules = config.get('validation', {})
        
        # Validate evaluation sources
        sources = config.get('evaluation_sources', {})
        if len(sources) < validation_rules.get('min_sources_required', 2):
            raise ValueError("Insufficient evaluation sources configured")
        
        # Validate themes
        themes = config.get('themes', {})
        if not themes:
            raise ValueError("No themes configured")
        
        # Validate theme weights
        theme_weights = config.get('theme_source_weights', {})
        for theme, weights in theme_weights.items():
            if theme not in themes:
                logger.warning(f"Theme weights configured for unknown theme: {theme}")
            
            # Check that all weighted sources exist
            for source in weights.keys():
                if source not in sources:
                    logger.warning(f"Unknown source in theme weights: {source}")
        
        logger.debug("Configuration validation passed")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get minimal default configuration"""
        return {
            'evaluation_sources': {},
            'themes': {
                'general_questions': {
                    'display_name': 'General Questions',
                    'description': 'General knowledge and everyday questions',
                    'keywords': ['general', 'question'],
                    'active': True,
                    'priority': 1.0
                }
            },
            'theme_source_weights': {},
            'model_config': {
                'cost_tiers': {
                    'budget': 0.01,
                    'balanced': 0.05,
                    'premium': 1.0
                }
            },
            'scoring': {
                'score_combination': {
                    'static_weight': 0.4,
                    'dynamic_weight': 0.6
                }
            },
            'features': {
                'enable_web_scraping': True,
                'enable_scheduler': True,
                'debug_mode': False
            }
        }

    def _cleanup_backups(self, keep_count: int = 5):
        """Clean up old backup files"""
        try:
            backup_pattern = f"{self.config_file}.backup.*"
            backup_dir = os.path.dirname(self.config_file)
            
            import glob
            backup_files = glob.glob(os.path.join(backup_dir, f"{os.path.basename(self.config_file)}.backup.*"))
            backup_files.sort(reverse=True)  # Newest first
            
            # Remove old backups
            for backup_file in backup_files[keep_count:]:
                os.remove(backup_file)
                logger.debug(f"Removed old backup: {backup_file}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup backups: {e}")

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for monitoring/debugging"""
        return {
            'config_file': self.config_file,
            'last_loaded': self.last_loaded.isoformat() if self.last_loaded else None,
            'sources_count': len(self.get_evaluation_sources()),
            'active_sources_count': len(self.get_evaluation_sources(active_only=True)),
            'themes_count': len(self.get_themes()),
            'active_themes_count': len(self.get_themes(active_only=True)),
            'feature_flags': self.get_feature_flags(),
            'file_exists': os.path.exists(self.config_file),
            'file_size': os.path.getsize(self.config_file) if os.path.exists(self.config_file) else 0
        }


# Global config manager instance
config_manager = ConfigManager()