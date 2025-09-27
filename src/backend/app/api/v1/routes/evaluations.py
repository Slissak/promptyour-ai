"""
Model Evaluation API Routes
Endpoints for accessing model evaluation data and triggering scans
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, status
from fastapi.responses import JSONResponse

from app.services.evaluation_scheduler import evaluation_scheduler
from app.services.model_evaluation_scanner import ModelEvaluationScanner
from app.models.schemas import ThemeType
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Global scanner instance for manual operations
scanner = ModelEvaluationScanner()


@router.get("/status")
async def get_evaluation_status() -> Dict[str, Any]:
    """Get current status of the evaluation system"""
    
    try:
        scheduler_status = evaluation_scheduler.get_scheduler_status()
        evaluation_summary = await evaluation_scheduler.get_evaluation_summary()
        
        return {
            "scheduler": scheduler_status,
            "evaluations": evaluation_summary,
            "sources": len(scanner.evaluation_sources)
        }
        
    except Exception as e:
        logger.error(f"Error getting evaluation status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get evaluation status"
        )


@router.post("/scan")
async def trigger_evaluation_scan(
    background_tasks: BackgroundTasks,
    scan_type: str = Query(default="full_scan", description="Type of scan: full_scan, incremental, leaderboard_only")
) -> Dict[str, Any]:
    """Trigger a manual evaluation scan"""
    
    valid_scan_types = ["full_scan", "incremental", "leaderboard_only"]
    
    if scan_type not in valid_scan_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scan_type. Must be one of: {valid_scan_types}"
        )
    
    logger.info(f"Manual {scan_type} scan triggered")
    
    # Run scan in background
    background_tasks.add_task(evaluation_scheduler.force_scan, scan_type)
    
    return {
        "message": f"{scan_type} scan triggered",
        "scan_type": scan_type,
        "status": "started",
        "note": "Scan is running in background. Check /status for updates."
    }


@router.get("/models")
async def get_model_rankings(
    theme: Optional[str] = Query(None, description="Filter by theme"),
    limit: int = Query(default=20, le=100, description="Maximum number of models to return"),
    sort_by: str = Query(default="overall", description="Sort by: overall, theme_score, cost_efficiency")
) -> Dict[str, Any]:
    """Get model rankings and evaluation data"""
    
    try:
        # Validate theme if provided
        if theme:
            try:
                theme_enum = ThemeType(theme)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid theme. Must be one of: {[t.value for t in ThemeType]}"
                )
        
        evaluation_summary = await evaluation_scheduler.get_evaluation_summary()
        
        if "error" in evaluation_summary or "message" in evaluation_summary:
            return evaluation_summary
        
        # Get model rankings
        top_models = evaluation_summary.get("top_models_overall", [])
        theme_leaders = evaluation_summary.get("theme_leaders", {})
        
        result = {
            "total_models": evaluation_summary.get("total_models", 0),
            "last_updated": evaluation_summary.get("last_updated"),
            "data_freshness": evaluation_summary.get("data_freshness", "unknown"),
            "rankings": {
                "overall": top_models[:limit],
                "by_theme": theme_leaders
            }
        }
        
        # If specific theme requested, add detailed theme rankings
        if theme:
            theme_specific = theme_leaders.get(theme)
            if theme_specific:
                result["theme_focus"] = {
                    "theme": theme,
                    "leader": theme_specific,
                    "note": f"Leader for {theme} theme"
                }
            else:
                result["theme_focus"] = {
                    "theme": theme,
                    "note": f"No specific data available for {theme} theme"
                }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model rankings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model rankings"
        )


@router.get("/models/{model_name}")
async def get_model_details(model_name: str) -> Dict[str, Any]:
    """Get detailed evaluation data for a specific model"""
    
    try:
        evaluation_summary = await evaluation_scheduler.get_evaluation_summary()
        
        if "error" in evaluation_summary:
            return evaluation_summary
        
        # Check if we have data for this model
        if not evaluation_scheduler.model_selector:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model evaluation system not ready"
            )
        
        model_info = evaluation_scheduler.model_selector.get_model_info(model_name)
        
        if not model_info["base_config"] and not model_info["dynamic_scores"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model '{model_name}' not found in evaluation data"
            )
        
        return {
            "model": model_name,
            "model_info": model_info,
            "last_updated": evaluation_summary.get("last_updated"),
            "data_freshness": evaluation_summary.get("data_freshness")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model details for {model_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get details for model '{model_name}'"
        )


@router.get("/themes/{theme}/recommendations")
async def get_theme_recommendations(theme: str) -> Dict[str, Any]:
    """Get model recommendations for a specific theme"""
    
    try:
        # Validate theme
        try:
            theme_enum = ThemeType(theme)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid theme '{theme}'. Must be one of: {[t.value for t in ThemeType]}"
            )
        
        if not evaluation_scheduler.model_selector:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Model evaluation system not ready"
            )
        
        recommendations = evaluation_scheduler.model_selector.get_theme_recommendations(theme_enum)
        
        # Add dynamic evaluation data if available
        evaluation_summary = await evaluation_scheduler.get_evaluation_summary()
        theme_leaders = evaluation_summary.get("theme_leaders", {})
        
        if theme in theme_leaders:
            recommendations["current_leader"] = {
                "model": theme_leaders[theme][0],
                "score": theme_leaders[theme][1]
            }
        
        recommendations["data_freshness"] = evaluation_summary.get("data_freshness", "unknown")
        recommendations["last_updated"] = evaluation_summary.get("last_updated")
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting theme recommendations for {theme}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations for theme '{theme}'"
        )


@router.get("/sources")
async def get_evaluation_sources() -> Dict[str, Any]:
    """Get information about evaluation sources"""
    
    try:
        source_info = scanner.get_source_info()
        
        # Add scheduler status for each source
        scheduler_status = evaluation_scheduler.get_scheduler_status()
        
        return {
            "sources": source_info["sources"],
            "theme_weights": source_info["theme_weights"],
            "supported_themes": source_info["supported_themes"],
            "scheduler_info": {
                "is_running": scheduler_status["is_running"],
                "last_scans": scheduler_status["last_scans"],
                "next_scans": scheduler_status["next_scans"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting evaluation sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get evaluation sources information"
        )


@router.get("/health")
async def evaluation_health_check() -> Dict[str, Any]:
    """Health check for evaluation system"""
    
    try:
        scheduler_status = evaluation_scheduler.get_scheduler_status()
        evaluation_summary = await evaluation_scheduler.get_evaluation_summary()
        
        # Determine overall health
        health_status = "healthy"
        
        if not scheduler_status["is_running"]:
            health_status = "degraded"
        elif evaluation_summary.get("data_freshness") in ["stale", "very_stale"]:
            health_status = "degraded"
        elif "error" in evaluation_summary:
            health_status = "unhealthy"
        
        health_data = {
            "status": health_status,
            "scheduler_running": scheduler_status["is_running"],
            "data_freshness": evaluation_summary.get("data_freshness", "unknown"),
            "total_models": evaluation_summary.get("total_models", 0),
            "last_update": evaluation_summary.get("last_updated"),
            "scan_stats": scheduler_status["statistics"]
        }
        
        if health_status == "healthy":
            return health_data
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_data
            )
            
    except Exception as e:
        logger.error(f"Evaluation health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@router.post("/scheduler/start")
async def start_scheduler() -> Dict[str, Any]:
    """Start the evaluation scheduler"""
    
    try:
        if not evaluation_scheduler.model_selector:
            # Get model selector from somewhere - this would normally be dependency injected
            from app.services.model_selector_v2 import ThemeBasedModelSelector
            model_selector = ThemeBasedModelSelector()
            await evaluation_scheduler.start_scheduler(model_selector)
        else:
            if evaluation_scheduler.is_running:
                return {"message": "Scheduler is already running", "status": "running"}
            else:
                await evaluation_scheduler.start_scheduler(evaluation_scheduler.model_selector)
        
        return {
            "message": "Evaluation scheduler started",
            "status": "running"
        }
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start evaluation scheduler"
        )


@router.post("/scheduler/stop")
async def stop_scheduler() -> Dict[str, Any]:
    """Stop the evaluation scheduler"""
    
    try:
        await evaluation_scheduler.stop_scheduler()
        
        return {
            "message": "Evaluation scheduler stopped",
            "status": "stopped"
        }
        
    except Exception as e:
        logger.error(f"Failed to stop scheduler: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop evaluation scheduler"
        )