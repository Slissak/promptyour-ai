"""
Configuration Management API Routes
Endpoints for viewing and updating evaluation system configuration
"""
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel

from app.core.config_manager import config_manager
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class SourceConfig(BaseModel):
    """Model for evaluation source configuration"""
    name: str
    url: str
    type: str
    themes: List[str]
    scraping_config: Dict[str, Any]
    active: bool = True
    update_frequency_hours: int = 24
    weight: float = 1.0
    reliability: float = 0.8


class ThemeConfig(BaseModel):
    """Model for theme configuration"""
    display_name: str
    description: str
    keywords: List[str]
    complexity_levels: List[str] = ["beginner", "intermediate", "advanced"]
    active: bool = True
    priority: float = 1.0


class ThemeWeights(BaseModel):
    """Model for theme source weights"""
    weights: Dict[str, float]


@router.get("/summary")
async def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary"""
    
    try:
        await config_manager.load_config()
        return config_manager.get_config_summary()
        
    except Exception as e:
        logger.error(f"Error getting config summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get configuration summary"
        )


@router.get("/sources")
async def get_evaluation_sources(active_only: bool = True) -> Dict[str, Any]:
    """Get evaluation sources configuration"""
    
    try:
        sources = config_manager.get_evaluation_sources(active_only=active_only)
        
        return {
            "sources": sources,
            "count": len(sources),
            "active_only": active_only
        }
        
    except Exception as e:
        logger.error(f"Error getting evaluation sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get evaluation sources"
        )


@router.post("/sources/{source_name}")
async def add_evaluation_source(source_name: str, source_config: SourceConfig) -> Dict[str, Any]:
    """Add a new evaluation source"""
    
    try:
        # Convert Pydantic model to dict
        source_dict = source_config.dict()
        
        success = await config_manager.add_evaluation_source(source_name, source_dict)
        
        if success:
            return {
                "message": f"Successfully added evaluation source: {source_name}",
                "source_name": source_name,
                "config": source_dict
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to add evaluation source: {source_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding evaluation source {source_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add evaluation source: {e}"
        )


@router.put("/sources/{source_name}/toggle")
async def toggle_evaluation_source(source_name: str, active: bool = Body(...)) -> Dict[str, Any]:
    """Enable or disable an evaluation source"""
    
    try:
        success = await config_manager.toggle_source(source_name, active)
        
        if success:
            return {
                "message": f"Successfully {'enabled' if active else 'disabled'} source: {source_name}",
                "source_name": source_name,
                "active": active
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to toggle source: {source_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling source {source_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle source: {e}"
        )


@router.get("/themes")
async def get_themes(active_only: bool = True) -> Dict[str, Any]:
    """Get themes configuration"""
    
    try:
        themes = config_manager.get_themes(active_only=active_only)
        
        return {
            "themes": themes,
            "count": len(themes),
            "active_only": active_only
        }
        
    except Exception as e:
        logger.error(f"Error getting themes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get themes"
        )


@router.post("/themes/{theme_name}")
async def add_theme(theme_name: str, theme_config: ThemeConfig) -> Dict[str, Any]:
    """Add a new theme"""
    
    try:
        # Convert Pydantic model to dict
        theme_dict = theme_config.dict()
        
        success = await config_manager.add_theme(theme_name, theme_dict)
        
        if success:
            return {
                "message": f"Successfully added theme: {theme_name}",
                "theme_name": theme_name,
                "config": theme_dict
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to add theme: {theme_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding theme {theme_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add theme: {e}"
        )


@router.get("/weights")
async def get_theme_weights() -> Dict[str, Any]:
    """Get theme source weight mappings"""
    
    try:
        weights = config_manager.get_theme_source_weights()
        
        return {
            "theme_weights": weights,
            "themes_count": len(weights)
        }
        
    except Exception as e:
        logger.error(f"Error getting theme weights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get theme weights"
        )


@router.put("/weights/{theme_name}")
async def update_theme_weights(theme_name: str, weights: ThemeWeights) -> Dict[str, Any]:
    """Update theme source weights"""
    
    try:
        success = await config_manager.update_theme_weights(theme_name, weights.weights)
        
        if success:
            return {
                "message": f"Successfully updated weights for theme: {theme_name}",
                "theme_name": theme_name,
                "weights": weights.weights,
                "total_weight": sum(weights.weights.values())
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update weights for theme: {theme_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating theme weights for {theme_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update theme weights: {e}"
        )


@router.get("/features")
async def get_feature_flags() -> Dict[str, Any]:
    """Get feature flags"""
    
    try:
        features = config_manager.get_feature_flags()
        
        return {
            "features": features,
            "count": len(features)
        }
        
    except Exception as e:
        logger.error(f"Error getting feature flags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feature flags"
        )


@router.put("/features/{feature_name}")
async def update_feature_flag(feature_name: str, enabled: bool = Body(...)) -> Dict[str, Any]:
    """Update a feature flag"""
    
    try:
        success = await config_manager.update_feature_flag(feature_name, enabled)
        
        if success:
            return {
                "message": f"Successfully {'enabled' if enabled else 'disabled'} feature: {feature_name}",
                "feature_name": feature_name,
                "enabled": enabled
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update feature flag: {feature_name}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feature flag {feature_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feature flag: {e}"
        )


@router.get("/model")
async def get_model_config() -> Dict[str, Any]:
    """Get model configuration"""
    
    try:
        model_config = config_manager.get_model_config()
        
        return {
            "model_config": model_config
        }
        
    except Exception as e:
        logger.error(f"Error getting model config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model configuration"
        )


@router.get("/scoring")
async def get_scoring_config() -> Dict[str, Any]:
    """Get scoring configuration"""
    
    try:
        scoring_config = config_manager.get_scoring_config()
        
        return {
            "scoring_config": scoring_config
        }
        
    except Exception as e:
        logger.error(f"Error getting scoring config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scoring configuration"
        )


@router.get("/scheduler")
async def get_scheduler_config() -> Dict[str, Any]:
    """Get scheduler configuration"""
    
    try:
        scheduler_config = config_manager.get_scheduler_config()
        
        return {
            "scheduler_config": scheduler_config
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scheduler configuration"
        )


@router.post("/reload")
async def reload_config() -> Dict[str, Any]:
    """Reload configuration from file"""
    
    try:
        config = await config_manager.load_config()
        summary = config_manager.get_config_summary()
        
        return {
            "message": "Configuration reloaded successfully",
            "summary": summary,
            "reloaded_at": config_manager.last_loaded.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload configuration: {e}"
        )


@router.get("/validate")
async def validate_config() -> Dict[str, Any]:
    """Validate current configuration"""
    
    try:
        await config_manager._validate_config(config_manager.config)
        
        return {
            "message": "Configuration validation passed",
            "valid": True,
            "summary": config_manager.get_config_summary()
        }
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration validation failed: {e}"
        )


@router.get("/backup")
async def create_config_backup() -> Dict[str, Any]:
    """Create a backup of current configuration"""
    
    try:
        # Save current config which creates a backup
        success = await config_manager.save_config()
        
        if success:
            return {
                "message": "Configuration backup created successfully",
                "config_file": config_manager.config_file,
                "backup_created": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create configuration backup"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating config backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create backup: {e}"
        )