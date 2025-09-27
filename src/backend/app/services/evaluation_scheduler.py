"""
Evaluation Scheduler Service
Manages periodic scanning of model evaluations and updates rankings
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

from app.services.model_evaluation_scanner import ModelEvaluationScanner
from app.services.model_selector_v2 import ThemeBasedModelSelector
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EvaluationScheduler:
    """Manages scheduled evaluation scanning and model ranking updates"""
    
    def __init__(self):
        self.scanner = ModelEvaluationScanner()
        self.model_selector = None  # Will be injected
        
        # Scheduling configuration
        self.scan_intervals = {
            "full_scan": timedelta(hours=24),      # Full scan every 24 hours
            "incremental": timedelta(hours=6),     # Check for updates every 6 hours
            "leaderboard_only": timedelta(hours=2) # Quick leaderboard checks every 2 hours
        }
        
        self.is_running = False
        self.last_scans = {
            "full_scan": None,
            "incremental": None,
            "leaderboard_only": None
        }
        
        self.scan_stats = {
            "total_scans": 0,
            "successful_scans": 0,
            "failed_scans": 0,
            "models_tracked": 0,
            "last_update": None
        }

    async def start_scheduler(self, model_selector: ThemeBasedModelSelector):
        """Start the evaluation scheduler"""
        
        if self.is_running:
            logger.warning("Evaluation scheduler is already running")
            return
        
        self.model_selector = model_selector
        self.is_running = True
        
        logger.info("Starting evaluation scheduler")
        
        # Start the main scheduler loop
        asyncio.create_task(self._scheduler_loop())
        
        # Run initial scan
        asyncio.create_task(self._run_initial_scan())

    async def stop_scheduler(self):
        """Stop the evaluation scheduler"""
        
        self.is_running = False
        logger.info("Evaluation scheduler stopped")

    async def _scheduler_loop(self):
        """Main scheduler loop"""
        
        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                # Check if it's time for each type of scan
                await self._check_and_run_scan("full_scan", current_time)
                await self._check_and_run_scan("incremental", current_time)
                await self._check_and_run_scan("leaderboard_only", current_time)
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(300)  # Continue after error

    async def _check_and_run_scan(self, scan_type: str, current_time: datetime):
        """Check if a scan type is due and run it"""
        
        last_scan = self.last_scans[scan_type]
        interval = self.scan_intervals[scan_type]
        
        if last_scan is None or (current_time - last_scan) >= interval:
            logger.info(f"Starting {scan_type}")
            await self._run_scan(scan_type)

    async def _run_initial_scan(self):
        """Run initial scan on startup"""
        
        await asyncio.sleep(10)  # Wait a bit for system to be ready
        
        try:
            # Check if we have recent cached data
            cached_data = await self.scanner.get_cached_evaluations(max_age_hours=12)
            
            if cached_data:
                logger.info("Using cached evaluation data")
                await self._update_model_selector(cached_data)
            else:
                logger.info("No recent cached data, running initial full scan")
                await self._run_scan("full_scan")
                
        except Exception as e:
            logger.error(f"Error in initial scan: {e}")

    async def _run_scan(self, scan_type: str):
        """Run a specific type of scan"""
        
        scan_start = datetime.utcnow()
        
        try:
            logger.info(f"Starting {scan_type} scan")
            
            if scan_type == "full_scan":
                results = await self.scanner.run_full_scan()
            elif scan_type == "incremental":
                results = await self._run_incremental_scan()
            elif scan_type == "leaderboard_only":
                results = await self._run_leaderboard_scan()
            else:
                raise ValueError(f"Unknown scan type: {scan_type}")
            
            # Update model selector with new data
            if results and "model_evaluations" in results:
                await self._update_model_selector(results["model_evaluations"])
            
            # Update tracking
            self.last_scans[scan_type] = scan_start
            self.scan_stats["total_scans"] += 1
            self.scan_stats["successful_scans"] += 1
            self.scan_stats["last_update"] = scan_start.isoformat()
            
            if "models_found" in results:
                self.scan_stats["models_tracked"] = results["models_found"]
            
            scan_duration = (datetime.utcnow() - scan_start).total_seconds()
            
            logger.info(
                f"Completed {scan_type} scan",
                duration_seconds=scan_duration,
                models_found=results.get("models_found", 0),
                sources_scanned=results.get("sources_scanned", 0)
            )
            
        except Exception as e:
            self.scan_stats["failed_scans"] += 1
            logger.error(f"Failed {scan_type} scan: {e}")

    async def _run_incremental_scan(self) -> Dict[str, Any]:
        """Run incremental scan - only check sources that update frequently"""
        
        # For now, run full scan - in production, this would be optimized
        # to only check specific fast-updating sources
        return await self.scanner.run_full_scan()

    async def _run_leaderboard_scan(self) -> Dict[str, Any]:
        """Run quick leaderboard-only scan"""
        
        # For now, run full scan - in production, this would be optimized
        # to only check live leaderboards like ChatBot Arena
        return await self.scanner.run_full_scan()

    async def _update_model_selector(self, model_evaluations: Dict[str, Any]):
        """Update the model selector with fresh evaluation data"""
        
        if not self.model_selector:
            logger.warning("Model selector not available for update")
            return
        
        try:
            # Transform the evaluation data into the format expected by model selector
            dynamic_scores = {}
            
            for model_name, eval_data in model_evaluations.items():
                dynamic_scores[model_name] = {
                    "overall_score": eval_data.get("overall_score", 0) * 100,  # Convert to 0-100 scale
                    "theme_scores": {},
                    "sources_count": eval_data.get("sources_count", 0),
                    "last_updated": eval_data.get("last_updated")
                }
                
                # Add theme-specific scores
                theme_scores = eval_data.get("theme_scores", {})
                for theme_name, theme_data in theme_scores.items():
                    dynamic_scores[model_name]["theme_scores"][theme_name] = theme_data.get("score", 0) * 100
            
            # Update the model selector
            self.model_selector.update_dynamic_evaluations(dynamic_scores)
            
            logger.info(
                "Updated model selector with fresh evaluation data",
                models_updated=len(dynamic_scores)
            )
            
        except Exception as e:
            logger.error(f"Failed to update model selector: {e}")

    async def force_scan(self, scan_type: str = "full_scan") -> Dict[str, Any]:
        """Force an immediate scan (for manual triggering)"""
        
        logger.info(f"Force triggering {scan_type} scan")
        await self._run_scan(scan_type)
        
        return self.get_scheduler_status()

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        
        return {
            "is_running": self.is_running,
            "last_scans": {
                scan_type: last_scan.isoformat() if last_scan else None
                for scan_type, last_scan in self.last_scans.items()
            },
            "scan_intervals": {
                scan_type: interval.total_seconds() / 3600  # Convert to hours
                for scan_type, interval in self.scan_intervals.items()
            },
            "statistics": self.scan_stats,
            "next_scans": self._get_next_scan_times()
        }

    def _get_next_scan_times(self) -> Dict[str, Optional[str]]:
        """Calculate next scan times"""
        
        next_scans = {}
        current_time = datetime.utcnow()
        
        for scan_type, interval in self.scan_intervals.items():
            last_scan = self.last_scans[scan_type]
            
            if last_scan:
                next_scan = last_scan + interval
                next_scans[scan_type] = next_scan.isoformat()
            else:
                next_scans[scan_type] = "pending"
        
        return next_scans

    async def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get summary of current model evaluations"""
        
        if not self.model_selector:
            return {"error": "Model selector not available"}
        
        # Get current dynamic scores
        dynamic_scores = self.model_selector.dynamic_model_scores
        
        if not dynamic_scores:
            return {"message": "No evaluation data available"}
        
        # Create summary
        models_by_overall_score = sorted(
            [(model, data.get("overall_score", 0)) for model, data in dynamic_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        theme_leaders = {}
        for model, data in dynamic_scores.items():
            theme_scores = data.get("theme_scores", {})
            for theme, score in theme_scores.items():
                if theme not in theme_leaders or score > theme_leaders[theme][1]:
                    theme_leaders[theme] = (model, score)
        
        return {
            "total_models": len(dynamic_scores),
            "last_updated": self.model_selector.last_evaluation_update.isoformat() 
                           if self.model_selector.last_evaluation_update else None,
            "top_models_overall": models_by_overall_score[:10],
            "theme_leaders": theme_leaders,
            "data_freshness": self._calculate_data_freshness()
        }

    def _calculate_data_freshness(self) -> str:
        """Calculate how fresh the evaluation data is"""
        
        if not self.model_selector or not self.model_selector.last_evaluation_update:
            return "no_data"
        
        age = datetime.now() - self.model_selector.last_evaluation_update
        
        if age < timedelta(hours=1):
            return "very_fresh"
        elif age < timedelta(hours=6):
            return "fresh"
        elif age < timedelta(hours=24):
            return "acceptable"
        elif age < timedelta(days=3):
            return "stale"
        else:
            return "very_stale"


# Global scheduler instance
evaluation_scheduler = EvaluationScheduler()