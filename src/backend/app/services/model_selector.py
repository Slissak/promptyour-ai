"""
Context-Aware Model Selection Service
Selects optimal model based on subject, grade level, and cost
"""
from typing import Dict, List, Tuple, Optional
from app.models.schemas import ProcessedContext, ModelChoice, SubjectType, GradeLevel
from app.core.logging import get_logger

logger = get_logger(__name__)


class ContextualModelSelector:
    """Selects models based on subject + grade level matrix with cost optimization"""
    
    def __init__(self):
        # Model registry with capabilities and costs
        self.model_registry = {
            "claude-3-opus": {
                "provider": "anthropic",
                "cost_per_1k_tokens": 0.075,
                "strengths": [
                    (SubjectType.MATH, GradeLevel.COLLEGE),
                    (SubjectType.MATH, GradeLevel.PROFESSIONAL),
                    (SubjectType.SCIENCE, GradeLevel.COLLEGE),
                    (SubjectType.SCIENCE, GradeLevel.PROFESSIONAL),
                    (SubjectType.CODE, GradeLevel.PROFESSIONAL),
                    (SubjectType.CREATIVE, GradeLevel.COLLEGE),
                    (SubjectType.CREATIVE, GradeLevel.PROFESSIONAL)
                ],
                "performance_tier": 1,
                "max_tokens": 4096
            },
            
            "claude-3-sonnet": {
                "provider": "anthropic",
                "cost_per_1k_tokens": 0.015,
                "strengths": [
                    (SubjectType.MATH, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.MATH, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.SCIENCE, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.CODE, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.CODE, GradeLevel.COLLEGE),
                    (SubjectType.ENGLISH, GradeLevel.COLLEGE),
                    (SubjectType.HISTORY, GradeLevel.COLLEGE)
                ],
                "performance_tier": 2,
                "max_tokens": 4096
            },
            
            "claude-3-haiku": {
                "provider": "anthropic", 
                "cost_per_1k_tokens": 0.0025,
                "strengths": [
                    (SubjectType.MATH, GradeLevel.ELEMENTARY),
                    (SubjectType.SCIENCE, GradeLevel.ELEMENTARY),
                    (SubjectType.SCIENCE, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.ENGLISH, GradeLevel.ELEMENTARY),
                    (SubjectType.ENGLISH, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.HISTORY, GradeLevel.ELEMENTARY),
                    (SubjectType.HISTORY, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.GENERAL, GradeLevel.ELEMENTARY)
                ],
                "performance_tier": 3,
                "max_tokens": 4096
            },
            
            "gpt-4": {
                "provider": "openai",
                "cost_per_1k_tokens": 0.06,
                "strengths": [
                    (SubjectType.CREATIVE, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.CREATIVE, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.ENGLISH, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.HISTORY, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.GENERAL, GradeLevel.COLLEGE),
                    (SubjectType.GENERAL, GradeLevel.PROFESSIONAL)
                ],
                "performance_tier": 1,
                "max_tokens": 8192
            },
            
            "gpt-3.5-turbo": {
                "provider": "openai",
                "cost_per_1k_tokens": 0.002,
                "strengths": [
                    (SubjectType.GENERAL, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.GENERAL, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.CODE, GradeLevel.ELEMENTARY),
                    (SubjectType.CODE, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.CREATIVE, GradeLevel.ELEMENTARY)
                ],
                "performance_tier": 3,
                "max_tokens": 4096
            }
        }
        
        # Fallback hierarchy when no exact match
        self.fallback_models = {
            SubjectType.MATH: ["claude-3-sonnet", "claude-3-opus", "gpt-4"],
            SubjectType.SCIENCE: ["claude-3-sonnet", "claude-3-opus", "gpt-4"], 
            SubjectType.CODE: ["claude-3-sonnet", "claude-3-opus", "gpt-4"],
            SubjectType.CREATIVE: ["gpt-4", "claude-3-opus", "claude-3-sonnet"],
            SubjectType.ENGLISH: ["gpt-4", "claude-3-sonnet", "claude-3-opus"],
            SubjectType.HISTORY: ["gpt-4", "claude-3-sonnet", "claude-3-opus"],
            SubjectType.GENERAL: ["claude-3-sonnet", "gpt-4", "gpt-3.5-turbo"]
        }

    async def select_model(self, context: ProcessedContext) -> ModelChoice:
        """Select optimal model based on subject, grade level, and cost"""
        
        logger.info(
            "Selecting model",
            subject=context.subject,
            grade_level=context.grade_level,
            complexity_score=context.complexity_score
        )
        
        # 1. Find models that handle this subject + grade level combination
        suitable_models = self._find_suitable_models(context.subject, context.grade_level)
        
        # 2. If no exact match, use fallback logic
        if not suitable_models:
            suitable_models = self._get_fallback_models(context)
        
        # 3. Score models based on cost, performance, and context
        scored_models = self._score_models(suitable_models, context)
        
        # 4. Select best model
        best_model_name = max(scored_models, key=scored_models.get)
        best_model_config = self.model_registry[best_model_name]
        
        # 5. Calculate estimated cost
        estimated_cost = self._calculate_estimated_cost(
            best_model_name, 
            context.estimated_tokens
        )
        
        model_choice = ModelChoice(
            model=best_model_name,
            provider=best_model_config["provider"],
            confidence=scored_models[best_model_name],
            reasoning=self._generate_reasoning(
                best_model_name, 
                context.subject, 
                context.grade_level,
                estimated_cost
            ),
            estimated_cost=estimated_cost
        )
        
        logger.info(
            "Model selected",
            model=best_model_name,
            provider=best_model_config["provider"],
            confidence=model_choice.confidence,
            estimated_cost=estimated_cost
        )
        
        return model_choice

    def _find_suitable_models(self, subject: SubjectType, grade_level: GradeLevel) -> List[str]:
        """Find models that explicitly handle this subject + grade level"""
        suitable = []
        
        for model_name, config in self.model_registry.items():
            if (subject, grade_level) in config["strengths"]:
                suitable.append(model_name)
        
        return suitable

    def _get_fallback_models(self, context: ProcessedContext) -> List[str]:
        """Get fallback models when no exact match exists"""
        fallback_list = self.fallback_models.get(context.subject, ["claude-3-sonnet"])
        
        # Filter by complexity - higher complexity needs better models
        if context.complexity_score > 0.7:
            # High complexity - use only tier 1 and 2 models
            return [m for m in fallback_list if self.model_registry[m]["performance_tier"] <= 2]
        elif context.complexity_score > 0.4:
            # Medium complexity - use tier 1, 2, and 3 models  
            return fallback_list
        else:
            # Low complexity - prefer cheaper models
            return sorted(fallback_list, key=lambda m: self.model_registry[m]["cost_per_1k_tokens"])

    def _score_models(self, models: List[str], context: ProcessedContext) -> Dict[str, float]:
        """Score models based on performance, cost, and context fit"""
        scores = {}
        
        for model in models:
            config = self.model_registry[model]
            
            # Base score from performance tier (higher tier = higher score)
            tier_score = (4 - config["performance_tier"]) / 3  # 1.0 for tier 1, 0.33 for tier 3
            
            # Cost efficiency score (lower cost = higher score for same tier)
            cost_score = 1.0 / (config["cost_per_1k_tokens"] * 100)  # Normalize
            cost_score = min(cost_score, 1.0)  # Cap at 1.0
            
            # Context match score
            exact_match = (context.subject, context.grade_level) in config["strengths"]
            context_score = 1.0 if exact_match else 0.5
            
            # Complexity appropriateness
            if context.complexity_score > 0.7 and config["performance_tier"] > 2:
                complexity_penalty = 0.5  # Penalize weak models for complex tasks
            elif context.complexity_score < 0.3 and config["performance_tier"] == 1:
                complexity_penalty = 0.8  # Slight penalty for overkill (but don't exclude)
            else:
                complexity_penalty = 1.0
            
            # Combine scores (weighted)
            final_score = (
                tier_score * 0.4 +           # 40% performance
                cost_score * 0.3 +           # 30% cost efficiency  
                context_score * 0.3          # 30% context match
            ) * complexity_penalty
            
            scores[model] = final_score
        
        return scores

    def _calculate_estimated_cost(self, model_name: str, estimated_tokens: int) -> float:
        """Calculate estimated cost for the request"""
        cost_per_1k = self.model_registry[model_name]["cost_per_1k_tokens"]
        return (estimated_tokens / 1000) * cost_per_1k

    def _generate_reasoning(self, model: str, subject: SubjectType, grade_level: GradeLevel, cost: float) -> str:
        """Generate human-readable reasoning for model selection"""
        config = self.model_registry[model]
        
        exact_match = (subject, grade_level) in config["strengths"]
        
        if exact_match:
            return f"Selected {model} as it's optimized for {subject.value} at {grade_level.value} level. Estimated cost: ${cost:.4f}"
        else:
            return f"Selected {model} as best fallback for {subject.value} tasks. Performance tier {config['performance_tier']}, cost: ${cost:.4f}"

    def get_available_models(self) -> Dict[str, Dict]:
        """Get all available models and their configurations"""
        return self.model_registry.copy()