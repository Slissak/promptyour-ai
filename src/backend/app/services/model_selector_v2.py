"""
Updated Model Selection Service for Redesigned Input Processing
Integrates with theme-based input and dynamic model evaluation data
"""
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json

from app.models.schemas import ProcessedContext, ModelChoice, ThemeType
from app.core.logging import get_logger
from app.core.config_manager import config_manager

logger = get_logger(__name__)


class ThemeBasedModelSelector:
    """Model selector optimized for theme-based input processing with dynamic evaluation data"""
    
    def __init__(self):
        # Configuration will be loaded from config_manager
        self.base_models = {}
        self.theme_model_rankings = {}
        self.complexity_models = {}
        
        # Dynamic evaluation data (populated by web scraping tool)
        self.dynamic_model_scores = {}
        self.last_evaluation_update = None

    async def select_model(self, context: ProcessedContext, budget_tier: str = "balanced") -> ModelChoice:
        """Select optimal model based on theme, complexity, and dynamic evaluations"""
        
        # Load configuration
        await self._load_configuration()
        
        logger.info(
            "Selecting model for theme-based input",
            theme=context.theme,
            inferred_subject=context.inferred_subject,
            inferred_complexity=context.inferred_complexity,
            complexity_score=context.complexity_score,
            budget_tier=budget_tier
        )

        # 1. Get candidate models based on theme
        theme_candidates = self._get_theme_candidates(context.theme, budget_tier)
        
        # 2. Filter by complexity requirements
        complexity_filtered = self._filter_by_complexity(theme_candidates, context.inferred_complexity)
        
        # 3. Apply dynamic evaluation scoring
        scored_models = self._apply_dynamic_scoring(complexity_filtered, context)
        
        # 4. Select best model considering cost and performance
        selected_model = self._select_optimal_model(scored_models, context, budget_tier)
        
        # 5. Create model choice with reasoning
        model_choice = self._create_model_choice(selected_model, context, scored_models)
        
        logger.info(
            "Model selected",
            selected_model=model_choice.model,
            provider=model_choice.provider,
            confidence=model_choice.confidence,
            estimated_cost=model_choice.estimated_cost,
            reasoning=model_choice.reasoning
        )
        
        return model_choice

    def _get_theme_candidates(self, theme: ThemeType, budget_tier: str) -> List[str]:
        """Get candidate models based on theme and budget tier"""
        
        theme_config = self.theme_model_rankings[theme]
        
        if budget_tier == "premium":
            # Use primary models regardless of cost
            return theme_config["primary"][:3]  # Top 3 choices
        elif budget_tier == "budget":
            # Prefer budget-friendly models
            budget_models = theme_config["budget"]
            primary_models = theme_config["primary"]
            return budget_models + [m for m in primary_models if m not in budget_models][:4]
        else:  # balanced
            # Mix of primary and budget models
            primary = theme_config["primary"][:2]
            budget = theme_config["budget"][:1]
            return primary + budget

    def _filter_by_complexity(self, candidates: List[str], complexity: str) -> List[str]:
        """Filter candidates based on complexity requirements"""
        
        if complexity not in self.complexity_models:
            return candidates  # No filtering if complexity not recognized
        
        preferred_for_complexity = self.complexity_models[complexity]["preferred"]
        
        # Reorder candidates to prefer complexity-appropriate models
        reordered = []
        
        # First, add candidates that are preferred for this complexity
        for model in preferred_for_complexity:
            if model in candidates and model not in reordered:
                reordered.append(model)
        
        # Then add remaining candidates
        for model in candidates:
            if model not in reordered:
                reordered.append(model)
        
        return reordered

    def _apply_dynamic_scoring(self, candidates: List[str], context: ProcessedContext) -> Dict[str, float]:
        """Apply dynamic evaluation scores from web scraping"""
        
        scores = {}
        
        for model in candidates:
            # Start with base score
            base_score = self._calculate_base_score(model, context)
            
            # Apply dynamic evaluation data if available
            dynamic_score = self._get_dynamic_score(model, context)
            
            # Combine scores (70% base, 30% dynamic evaluations)
            if dynamic_score is not None:
                final_score = (base_score * 0.7) + (dynamic_score * 0.3)
            else:
                final_score = base_score
            
            scores[model] = final_score
        
        return scores

    def _calculate_base_score(self, model: str, context: ProcessedContext) -> float:
        """Calculate base score from static model configuration"""
        
        if model not in self.base_models:
            return 0.5  # Default score for unknown models
        
        model_config = self.base_models[model]
        
        # Theme alignment score
        theme_alignment = self._get_theme_alignment_score(model, context.theme)
        
        # Complexity appropriateness score
        complexity_alignment = self._get_complexity_alignment_score(model, context.inferred_complexity)
        
        # Cost efficiency score (inverse of cost)
        cost_efficiency = 1.0 / (model_config["cost_per_1k_tokens"] * 100 + 1)
        
        # Subject alignment score
        subject_alignment = self._get_subject_alignment_score(model, context.inferred_subject)
        
        # Weighted combination
        final_score = (
            theme_alignment * 0.3 +
            complexity_alignment * 0.3 +
            subject_alignment * 0.3 +
            cost_efficiency * 0.1
        )
        
        return min(final_score, 1.0)

    def _get_theme_alignment_score(self, model: str, theme: ThemeType) -> float:
        """Score how well model aligns with theme"""
        
        theme_config = self.theme_model_rankings[theme]
        primary_models = theme_config["primary"]
        budget_models = theme_config["budget"]
        
        if model in primary_models:
            # Higher score for earlier position in primary list
            position = primary_models.index(model)
            return 1.0 - (position * 0.1)  # 1.0, 0.9, 0.8, etc.
        elif model in budget_models:
            position = budget_models.index(model)
            return 0.6 - (position * 0.1)  # 0.6, 0.5, 0.4, etc.
        else:
            return 0.3  # Not specifically recommended for this theme

    def _get_complexity_alignment_score(self, model: str, complexity: str) -> float:
        """Score how well model handles the complexity level"""
        
        if complexity not in self.complexity_models:
            return 0.7  # Default score
        
        preferred_models = self.complexity_models[complexity]["preferred"]
        
        if model in preferred_models:
            position = preferred_models.index(model)
            return 1.0 - (position * 0.1)
        else:
            return 0.5

    def _get_subject_alignment_score(self, model: str, subject: str) -> float:
        """Score how well model handles specific subject"""
        
        if model not in self.base_models:
            return 0.5
        
        model_config = self.base_models[model]
        strengths = model_config["strengths"]
        
        # Map subjects to strength categories
        subject_strength_mapping = {
            "mathematics": "reasoning",
            "programming": "reasoning",
            "creative writing": "creative",
            "science": "reasoning",
            "business": "analysis",
            "research": "analysis",
            "general knowledge": "general"
        }
        
        required_strength = subject_strength_mapping.get(subject, "general")
        
        if required_strength in strengths:
            return 0.9
        elif "reasoning" in strengths and required_strength in ["reasoning", "analysis"]:
            return 0.8
        else:
            return 0.6

    def _get_dynamic_score(self, model: str, context: ProcessedContext) -> Optional[float]:
        """Get score from dynamic evaluation data (web scraping results)"""
        
        # Check if we have recent dynamic evaluation data
        if not self.dynamic_model_scores or not self.last_evaluation_update:
            return None
        
        # Check if data is recent (less than 7 days old)
        from datetime import timedelta
        if datetime.now() - self.last_evaluation_update > timedelta(days=7):
            return None
        
        # Get model score from dynamic data
        model_data = self.dynamic_model_scores.get(model, {})
        
        # Get theme-specific score if available
        theme_scores = model_data.get("theme_scores", {})
        theme_score = theme_scores.get(context.theme.value)
        
        if theme_score is not None:
            return theme_score / 100.0  # Normalize to 0-1
        
        # Fallback to overall score
        overall_score = model_data.get("overall_score")
        if overall_score is not None:
            return overall_score / 100.0
        
        return None

    def _select_optimal_model(self, scored_models: Dict[str, float], context: ProcessedContext, budget_tier: str) -> str:
        """Select the optimal model from scored candidates"""
        
        if not scored_models:
            return "claude-3-sonnet"  # Safe fallback
        
        # Sort by score (descending)
        sorted_models = sorted(scored_models.items(), key=lambda x: x[1], reverse=True)
        
        # Apply cost constraints for budget tier
        if budget_tier == "budget":
            # Get budget threshold from configuration
            model_config = config_manager.get_model_config()
            budget_limit = model_config.get('cost_tiers', {}).get('budget', 0.01)
            
            budget_models = [
                (model, score) for model, score in sorted_models
                if self.base_models.get(model, {}).get("cost_per_1k_tokens", 1.0) <= budget_limit
            ]
            if budget_models:
                return budget_models[0][0]
        
        # Return highest scoring model
        return sorted_models[0][0]

    def _create_model_choice(self, selected_model: str, context: ProcessedContext, scored_models: Dict[str, float]) -> ModelChoice:
        """Create ModelChoice object with reasoning"""
        
        if selected_model not in self.base_models:
            # Fallback for unknown model
            return ModelChoice(
                model=selected_model,
                provider="unknown",
                confidence=0.5,
                reasoning=f"Selected {selected_model} (unknown model configuration)",
                estimated_cost=0.01
            )
        
        model_config = self.base_models[selected_model]
        score = scored_models.get(selected_model, 0.5)
        
        # Calculate estimated cost
        estimated_cost = (context.estimated_tokens / 1000) * model_config["cost_per_1k_tokens"]
        
        # Generate reasoning
        reasoning = self._generate_selection_reasoning(
            selected_model, 
            context, 
            score,
            model_config
        )
        
        return ModelChoice(
            model=selected_model,
            provider=model_config["provider"],
            confidence=score,
            reasoning=reasoning,
            estimated_cost=estimated_cost
        )

    def _generate_selection_reasoning(self, model: str, context: ProcessedContext, score: float, config: Dict) -> str:
        """Generate human-readable reasoning for model selection"""
        
        reasons = []
        
        # Theme-based reasoning
        theme_config = self.theme_model_rankings[context.theme]
        if model in theme_config["primary"]:
            reasons.append(f"optimized for {context.theme.value.replace('_', ' ')}")
        
        # Complexity-based reasoning
        if context.inferred_complexity in self.complexity_models:
            complexity_config = self.complexity_models[context.inferred_complexity]
            if model in complexity_config["preferred"]:
                reasons.append(f"well-suited for {context.inferred_complexity} level tasks")
        
        # Cost consideration
        if config["cost_per_1k_tokens"] < 0.01:
            reasons.append("cost-effective choice")
        elif config["cost_per_1k_tokens"] > 0.05:
            reasons.append("premium model for high-quality output")
        
        # Dynamic evaluation data
        if self.dynamic_model_scores and model in self.dynamic_model_scores:
            reasons.append("performs well in recent evaluations")
        
        reasoning = f"Selected {model} ({config['tier']} tier): " + ", ".join(reasons)
        reasoning += f". Confidence: {score:.2f}"
        
        return reasoning

    def update_dynamic_evaluations(self, evaluation_data: Dict[str, Any]):
        """Update model rankings with fresh evaluation data from web scraping"""
        
        self.dynamic_model_scores = evaluation_data
        self.last_evaluation_update = datetime.now()
        
        logger.info(
            "Updated dynamic model evaluations",
            models_count=len(evaluation_data),
            update_time=self.last_evaluation_update
        )

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get comprehensive information about a model"""
        
        base_info = self.base_models.get(model, {})
        dynamic_info = self.dynamic_model_scores.get(model, {})
        
        return {
            "base_config": base_info,
            "dynamic_scores": dynamic_info,
            "last_updated": self.last_evaluation_update.isoformat() if self.last_evaluation_update else None
        }

    async def _load_configuration(self):
        """Load model and theme configuration from config manager"""
        await config_manager.load_config()
        
        # Get model configuration
        model_config = config_manager.get_model_config()
        
        # Build base models from tier preferences
        tier_preferences = model_config.get('tier_preferences', {})
        cost_tiers = model_config.get('cost_tiers', {})
        
        # Create base models registry from configuration
        self.base_models = {
            "gpt-4": {
                "provider": "openai",
                "cost_per_1k_tokens": cost_tiers.get("premium", 1.0),
                "max_tokens": 8192,
                "strengths": ["reasoning", "creative", "complex_analysis"],
                "weaknesses": ["cost", "speed"],
                "tier": "premium"
            },
            "gpt-3.5-turbo": {
                "provider": "openai", 
                "cost_per_1k_tokens": cost_tiers.get("budget", 0.01),
                "max_tokens": 4096,
                "strengths": ["speed", "cost_effective", "general"],
                "weaknesses": ["complex_reasoning", "specialized_tasks"],
                "tier": "budget"
            },
            "claude-3-opus": {
                "provider": "anthropic",
                "cost_per_1k_tokens": cost_tiers.get("premium", 1.0),
                "max_tokens": 4096,
                "strengths": ["reasoning", "analysis", "writing"],
                "weaknesses": ["cost", "speed"],
                "tier": "premium"
            },
            "claude-3-sonnet": {
                "provider": "anthropic",
                "cost_per_1k_tokens": cost_tiers.get("balanced", 0.05),
                "max_tokens": 4096,
                "strengths": ["balanced", "coding", "reasoning"],
                "weaknesses": ["none_major"],
                "tier": "balanced"
            },
            "claude-3-haiku": {
                "provider": "anthropic",
                "cost_per_1k_tokens": cost_tiers.get("budget", 0.01),
                "max_tokens": 4096,
                "strengths": ["speed", "cost", "simple_tasks"],
                "weaknesses": ["complex_reasoning", "specialized"],
                "tier": "budget"
            },
            "gemini-pro": {
                "provider": "google",
                "cost_per_1k_tokens": cost_tiers.get("budget", 0.01),
                "max_tokens": 2048,
                "strengths": ["multimodal", "cost", "speed"],
                "weaknesses": ["reasoning", "writing_quality"],
                "tier": "budget"
            }
        }
        
        # Build theme rankings from tier preferences
        self.theme_model_rankings = {
            ThemeType.ACADEMIC_HELP: {
                "primary": tier_preferences.get("balanced", ["claude-3-sonnet", "gpt-4"]),
                "budget": tier_preferences.get("budget", ["claude-3-haiku", "gpt-3.5-turbo"]),
                "reasoning": "Academic help requires strong reasoning and clear explanations"
            },
            ThemeType.CREATIVE_WRITING: {
                "primary": tier_preferences.get("premium", ["gpt-4", "claude-3-opus"]),
                "budget": tier_preferences.get("budget", ["gpt-3.5-turbo", "claude-3-haiku"]),
                "reasoning": "Creative writing benefits from advanced language models"
            },
            ThemeType.CODING_PROGRAMMING: {
                "primary": tier_preferences.get("balanced", ["claude-3-sonnet", "gpt-4"]),
                "budget": tier_preferences.get("budget", ["claude-3-haiku", "gpt-3.5-turbo"]),
                "reasoning": "Coding requires strong logical reasoning and technical accuracy"
            },
            ThemeType.BUSINESS_PROFESSIONAL: {
                "primary": tier_preferences.get("premium", ["gpt-4", "claude-3-opus"]),
                "budget": tier_preferences.get("balanced", ["claude-3-sonnet", "gpt-3.5-turbo"]),
                "reasoning": "Business contexts need professional tone and strategic thinking"
            },
            ThemeType.PERSONAL_LEARNING: {
                "primary": tier_preferences.get("balanced", ["claude-3-sonnet", "claude-3-haiku"]),
                "budget": tier_preferences.get("budget", ["claude-3-haiku", "gpt-3.5-turbo"]),
                "reasoning": "Personal learning benefits from clear, patient explanations"
            },
            ThemeType.RESEARCH_ANALYSIS: {
                "primary": tier_preferences.get("premium", ["claude-3-opus", "gpt-4"]),
                "budget": tier_preferences.get("balanced", ["claude-3-sonnet", "gpt-3.5-turbo"]),
                "reasoning": "Research requires deep analysis and comprehensive coverage"
            },
            ThemeType.PROBLEM_SOLVING: {
                "primary": tier_preferences.get("balanced", ["claude-3-sonnet", "gpt-4"]),
                "budget": tier_preferences.get("budget", ["claude-3-haiku", "gpt-3.5-turbo"]),
                "reasoning": "Problem solving requires systematic reasoning and creativity"
            },
            ThemeType.TUTORING_EDUCATION: {
                "primary": tier_preferences.get("balanced", ["claude-3-sonnet", "gpt-4"]),
                "budget": tier_preferences.get("budget", ["claude-3-haiku", "gpt-3.5-turbo"]),
                "reasoning": "Tutoring needs clear explanations adapted to user level"
            },
            ThemeType.GENERAL_QUESTIONS: {
                "primary": tier_preferences.get("budget", ["claude-3-haiku", "gpt-3.5-turbo"]),
                "budget": tier_preferences.get("budget", ["claude-3-haiku", "gpt-3.5-turbo"]),
                "reasoning": "General questions can be handled efficiently by faster models"
            }
        }
        
        # Build complexity models from themes configuration
        themes_config = config_manager.get_themes()
        self.complexity_models = {
            "beginner": {
                "preferred": tier_preferences.get("budget", ["claude-3-haiku", "gpt-3.5-turbo"]),
                "reasoning": "Simpler models often better for beginner-friendly explanations"
            },
            "intermediate": {
                "preferred": tier_preferences.get("balanced", ["claude-3-sonnet", "gpt-4"]),
                "reasoning": "Balanced models work well for intermediate complexity"
            },
            "advanced": {
                "preferred": tier_preferences.get("premium", ["gpt-4", "claude-3-opus"]),
                "reasoning": "Advanced topics require sophisticated reasoning"
            },
            "academic": {
                "preferred": tier_preferences.get("premium", ["claude-3-opus", "gpt-4"]),
                "reasoning": "Academic work needs thorough analysis and accuracy"
            },
            "professional": {
                "preferred": tier_preferences.get("premium", ["gpt-4", "claude-3-opus"]),
                "reasoning": "Professional contexts demand high-quality, reliable output"
            }
        }
        
        logger.info(f"Loaded model configuration with {len(self.base_models)} models")

    async def get_theme_recommendations(self, theme: ThemeType) -> Dict[str, Any]:
        """Get model recommendations for a specific theme"""
        
        # Load configuration if not already loaded
        if not self.base_models:
            await self._load_configuration()
        
        return {
            "theme": theme.value,
            "recommendations": self.theme_model_rankings.get(theme, {}),
            "available_models": list(self.base_models.keys())
        }