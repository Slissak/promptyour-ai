"""
Dynamic Model Evaluation Scanner
Periodically scrapes web for model evaluations, leaderboards, and benchmarks
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

from app.core.config import settings
from app.core.logging import get_logger
from app.core.config_manager import config_manager
from app.models.schemas import ThemeType

logger = get_logger(__name__)


class ModelEvaluationScanner:
    """Scans the web for model evaluations and creates theme-aligned rankings"""
    
    def __init__(self):
        # Configuration will be loaded from config_manager
        self.evaluation_sources = {}
        self.theme_weights = {}

    async def run_full_scan(self) -> Dict[str, Any]:
        """Run complete scan of all evaluation sources"""
        
        # Load current configuration
        await self._load_configuration()
        
        logger.info("Starting full model evaluation scan")
        scan_start = datetime.utcnow()
        
        results = {
            "scan_id": f"scan_{int(scan_start.timestamp())}",
            "started_at": scan_start.isoformat(),
            "sources_scanned": 0,
            "models_found": 0,
            "evaluations_collected": 0,
            "errors": []
        }
        
        all_model_data = {}
        
        # Scrape each evaluation source
        for source_name, source_config in self.evaluation_sources.items():
            try:
                logger.info(f"Scraping {source_name}")
                source_data = await self._scrape_source(source_name, source_config)
                
                if source_data:
                    all_model_data[source_name] = source_data
                    results["sources_scanned"] += 1
                    results["evaluations_collected"] += len(source_data)
                    
                    logger.info(
                        f"Successfully scraped {source_name}",
                        models_found=len(source_data),
                        evaluations=len(source_data)
                    )
                else:
                    logger.warning(f"No data found for {source_name}")
                    
            except Exception as e:
                error_msg = f"Failed to scrape {source_name}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                
        # Calculate theme-aligned scores
        theme_rankings = await self._calculate_theme_rankings(all_model_data)
        
        # Create final model evaluation data
        model_evaluations = await self._create_model_evaluations(all_model_data, theme_rankings)
        
        results.update({
            "completed_at": datetime.utcnow().isoformat(),
            "models_found": len(model_evaluations),
            "theme_rankings": theme_rankings,
            "model_evaluations": model_evaluations
        })
        
        logger.info(
            "Model evaluation scan completed",
            duration_minutes=(datetime.utcnow() - scan_start).total_seconds() / 60,
            models_found=len(model_evaluations),
            sources_scanned=results["sources_scanned"]
        )
        
        return results

    async def _scrape_source(self, source_name: str, source_config: Dict) -> Optional[Dict[str, Any]]:
        """Scrape a specific evaluation source"""
        
        scraping_config = source_config["scraping_config"]
        
        try:
            if source_config["type"] == "leaderboard":
                return await self._scrape_leaderboard(source_config["url"], scraping_config)
            elif source_config["type"] == "arena":
                return await self._scrape_arena(source_config["url"], scraping_config)
            elif source_config["type"] == "benchmark":
                return await self._scrape_benchmark(source_config["url"], scraping_config)
            else:
                logger.warning(f"Unknown source type: {source_config['type']}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {source_name}: {str(e)}")
            return None

    async def _scrape_leaderboard(self, url: str, config: Dict) -> Dict[str, Any]:
        """Scrape HTML leaderboard tables"""
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                html = await response.text()
                
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.select_one(config["selector"])
        
        if not table:
            raise Exception("Leaderboard table not found")
        
        # Parse table data
        models_data = {}
        headers = [th.get_text().strip() for th in table.find("thead").find_all("th")]
        
        model_col_idx = headers.index(config["model_column"])
        score_col_indices = {
            col: headers.index(col) for col in config["score_columns"] 
            if col in headers
        }
        
        for row in table.find("tbody").find_all("tr"):
            cells = row.find_all("td")
            if len(cells) <= model_col_idx:
                continue
                
            model_name = cells[model_col_idx].get_text().strip()
            model_name = self._normalize_model_name(model_name)
            
            scores = {}
            for score_name, col_idx in score_col_indices.items():
                if col_idx < len(cells):
                    score_text = cells[col_idx].get_text().strip()
                    score = self._parse_score(score_text)
                    if score is not None:
                        scores[score_name] = score
            
            if model_name and scores:
                models_data[model_name] = {
                    "model": model_name,
                    "scores": scores,
                    "source": "leaderboard",
                    "scraped_at": datetime.utcnow().isoformat()
                }
        
        return models_data

    async def _scrape_arena(self, url: str, config: Dict) -> Dict[str, Any]:
        """Scrape arena-style evaluation data"""
        
        # Try API endpoint first
        if "api_endpoint" in config:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(config["api_endpoint"]) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._parse_arena_data(data, config)
            except Exception as e:
                logger.warning(f"API scraping failed, falling back to HTML: {e}")
        
        # Fallback to HTML scraping
        return await self._scrape_leaderboard(url, config)

    async def _scrape_benchmark(self, url: str, config: Dict) -> Dict[str, Any]:
        """Scrape benchmark results from GitHub or research papers"""
        
        if config["type"] == "github_readme":
            return await self._scrape_github_readme(url, config)
        elif config["type"] == "github_results":
            return await self._scrape_github_results(url, config)
        else:
            # Generic benchmark scraping
            return await self._scrape_leaderboard(url, config)

    async def _scrape_github_readme(self, url: str, config: Dict) -> Dict[str, Any]:
        """Scrape model scores from GitHub README files"""
        
        # Convert GitHub URL to raw content URL
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(raw_url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                content = await response.text()
        
        # Extract scores using regex pattern
        pattern = config["score_pattern"]
        matches = re.findall(pattern, content)
        
        models_data = {}
        for match in matches:
            if len(match) >= 2:
                model_name = self._normalize_model_name(match[0])
                score = self._parse_score(match[1])
                
                if model_name and score is not None:
                    models_data[model_name] = {
                        "model": model_name,
                        "scores": {"overall": score},
                        "source": "github_readme",
                        "scraped_at": datetime.utcnow().isoformat()
                    }
        
        return models_data

    async def _scrape_github_results(self, url: str, config: Dict) -> Dict[str, Any]:
        """Scrape results from GitHub repository result files"""
        
        models_data = {}
        base_url = url.replace("/blob/main", "/raw/main").replace("/tree/main", "/raw/main")
        
        for results_file in config["results_files"]:
            try:
                file_url = urljoin(base_url, results_file)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_url) as response:
                        if response.status != 200:
                            continue
                        
                        if results_file.endswith('.json'):
                            data = await response.json()
                            file_models = self._parse_json_results(data, config)
                        else:  # Markdown
                            content = await response.text()
                            file_models = self._parse_markdown_results(content, config)
                        
                        models_data.update(file_models)
                        
            except Exception as e:
                logger.warning(f"Failed to scrape {results_file}: {e}")
                continue
        
        return models_data

    def _parse_arena_data(self, data: Dict, config: Dict) -> Dict[str, Any]:
        """Parse arena leaderboard JSON data"""
        
        models_data = {}
        
        if isinstance(data, list):
            for item in data:
                if config["model_field"] in item and config["score_field"] in item:
                    model_name = self._normalize_model_name(item[config["model_field"]])
                    score = item[config["score_field"]]
                    
                    if model_name and score is not None:
                        models_data[model_name] = {
                            "model": model_name,
                            "scores": {"rating": score},
                            "source": "arena",
                            "scraped_at": datetime.utcnow().isoformat()
                        }
        
        return models_data

    def _parse_json_results(self, data: Dict, config: Dict) -> Dict[str, Any]:
        """Parse JSON result files"""
        
        models_data = {}
        
        # Handle different JSON structures
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    model_name = self._normalize_model_name(key)
                    models_data[model_name] = {
                        "model": model_name,
                        "scores": {"overall": value},
                        "source": "json_results",
                        "scraped_at": datetime.utcnow().isoformat()
                    }
                elif isinstance(value, dict) and "score" in value:
                    model_name = self._normalize_model_name(key)
                    models_data[model_name] = {
                        "model": model_name,
                        "scores": {"overall": value["score"]},
                        "source": "json_results",
                        "scraped_at": datetime.utcnow().isoformat()
                    }
        
        return models_data

    def _parse_markdown_results(self, content: str, config: Dict) -> Dict[str, Any]:
        """Parse markdown result tables"""
        
        models_data = {}
        
        # Look for table patterns in markdown
        table_pattern = r'\|([^|]+)\|([^|]+)\|'
        matches = re.findall(table_pattern, content)
        
        for match in matches:
            if len(match) >= 2:
                model_name = self._normalize_model_name(match[0].strip())
                score = self._parse_score(match[1].strip())
                
                if model_name and score is not None:
                    models_data[model_name] = {
                        "model": model_name,
                        "scores": {"overall": score},
                        "source": "markdown_results",
                        "scraped_at": datetime.utcnow().isoformat()
                    }
        
        return models_data

    def _normalize_model_name(self, raw_name: str) -> str:
        """Normalize model names for consistency"""
        
        # Remove common prefixes/suffixes
        name = raw_name.strip()
        name = re.sub(r'^(meta-llama/|microsoft/|google/|anthropic/)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'-(chat|instruct|base)$', '', name, flags=re.IGNORECASE)
        
        # Use model aliases from configuration
        model_config = config_manager.get_model_config()
        name_mappings = model_config.get('model_aliases', {
            "gpt-4-turbo": "gpt-4",
            "claude-3-opus-20240229": "claude-3-opus",
            "claude-3-sonnet-20240229": "claude-3-sonnet",
            "claude-3-haiku-20240307": "claude-3-haiku",
            "gemini-pro": "gemini-pro",
            "llama-2-70b": "llama-2-70b"
        })
        
        return name_mappings.get(name.lower(), name)

    def _parse_score(self, score_text: str) -> Optional[float]:
        """Parse score from text, handling various formats"""
        
        # Remove common non-numeric characters
        clean_text = re.sub(r'[%,\s]', '', score_text)
        
        # Try to extract number
        number_match = re.search(r'([0-9]*\.?[0-9]+)', clean_text)
        
        if number_match:
            try:
                return float(number_match.group(1))
            except ValueError:
                return None
        
        return None

    async def _calculate_theme_rankings(self, all_model_data: Dict[str, Dict]) -> Dict[str, List[Dict]]:
        """Calculate theme-aligned rankings from all evaluation data"""
        
        theme_rankings = {}
        
        # Get theme weights from config
        theme_source_weights = config_manager.get_theme_source_weights()
        
        for theme in ThemeType:
            theme_scores = {}
            theme_weights = theme_source_weights.get(theme.value, {})
            
            # For each model, calculate weighted theme score
            for source_name, source_data in all_model_data.items():
                source_weight = theme_weights.get(source_name, 0)
                
                if source_weight == 0:
                    continue  # This source doesn't contribute to this theme
                
                for model_name, model_data in source_data.items():
                    if model_name not in theme_scores:
                        theme_scores[model_name] = {"total_weight": 0, "weighted_score": 0}
                    
                    # Get overall score for this model from this source
                    model_scores = model_data["scores"]
                    overall_score = model_scores.get("overall") or model_scores.get("Average") or 0
                    
                    if overall_score > 0:
                        theme_scores[model_name]["weighted_score"] += overall_score * source_weight
                        theme_scores[model_name]["total_weight"] += source_weight
            
            # Normalize scores and rank
            normalized_scores = []
            for model_name, score_data in theme_scores.items():
                if score_data["total_weight"] > 0:
                    normalized_score = score_data["weighted_score"] / score_data["total_weight"]
                    normalized_scores.append({
                        "model": model_name,
                        "score": normalized_score,
                        "sources_count": len([s for s in theme_weights.keys() if s in all_model_data])
                    })
            
            # Sort by score and add rank
            normalized_scores.sort(key=lambda x: x["score"], reverse=True)
            for i, model_data in enumerate(normalized_scores):
                model_data["rank"] = i + 1
            
            theme_rankings[theme.value] = normalized_scores
        
        return theme_rankings

    async def _create_model_evaluations(self, all_model_data: Dict, theme_rankings: Dict) -> Dict[str, Any]:
        """Create final model evaluation data structure"""
        
        model_evaluations = {}
        
        # Get all unique models
        all_models = set()
        for source_data in all_model_data.values():
            all_models.update(source_data.keys())
        
        for model_name in all_models:
            model_eval = {
                "model": model_name,
                "overall_score": 0,
                "theme_scores": {},
                "source_scores": {},
                "last_updated": datetime.utcnow().isoformat(),
                "sources_count": 0
            }
            
            # Collect scores from all sources
            total_score = 0
            source_count = 0
            
            for source_name, source_data in all_model_data.items():
                if model_name in source_data:
                    model_data = source_data[model_name]
                    source_scores = model_data["scores"]
                    
                    # Overall score
                    overall_score = source_scores.get("overall") or source_scores.get("Average") or 0
                    if overall_score > 0:
                        total_score += overall_score
                        source_count += 1
                    
                    model_eval["source_scores"][source_name] = source_scores
            
            # Calculate overall score
            if source_count > 0:
                model_eval["overall_score"] = total_score / source_count
                model_eval["sources_count"] = source_count
            
            # Add theme scores
            for theme_name, theme_data in theme_rankings.items():
                theme_model = next((m for m in theme_data if m["model"] == model_name), None)
                if theme_model:
                    model_eval["theme_scores"][theme_name] = {
                        "score": theme_model["score"],
                        "rank": theme_model["rank"]
                    }
            
            model_evaluations[model_name] = model_eval
        
        return model_evaluations

    async def get_cached_evaluations(self, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Get cached evaluation data if recent enough"""
        
        # TODO: Implement database caching
        # For now, return None to force fresh scraping
        return None

    async def _load_configuration(self):
        """Load evaluation configuration from config manager"""
        await config_manager.load_config()
        
        # Get evaluation sources (active only)
        self.evaluation_sources = config_manager.get_evaluation_sources(active_only=True)
        
        # Theme weights are now loaded from config dynamically in _calculate_theme_rankings
        logger.info(f"Loaded {len(self.evaluation_sources)} active evaluation sources")
        
    async def get_source_info(self) -> Dict[str, Any]:
        """Get information about all configured evaluation sources"""
        
        # Load configuration if not already loaded
        if not self.evaluation_sources:
            await self._load_configuration()
        
        return {
            "sources": self.evaluation_sources,
            "theme_weights": config_manager.get_theme_source_weights(),
            "supported_themes": [theme.value for theme in ThemeType]
        }