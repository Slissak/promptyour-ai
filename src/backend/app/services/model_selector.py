"""
Context-Aware Model Selection Service
Selects optimal model based on subject, grade level, and cost
"""
from typing import Dict, List
from backend.app.models.schemas import ProcessedContext, ModelChoice, SubjectType, GradeLevel
from backend.app.core.logging import get_logger
from shared_python.billing.cost_calculator import CostCalculator

logger = get_logger(__name__)


class ContextualModelSelector:
    """Selects models based on subject + grade level matrix with cost optimization"""

    def __init__(self):
        self.cost_calculator = CostCalculator()
        # Model registry with capabilities
        self.model_registry = {
            "claude-3-opus": {
                "provider": "anthropic",
                "strengths": [
                    (SubjectType.MATH, GradeLevel.COLLEGE),
                    (SubjectType.MATH, GradeLevel.PROFESSIONAL),
                    (SubjectType.SCIENCE, GradeLevel.COLLEGE),
                    (SubjectType.SCIENCE, GradeLevel.PROFESSIONAL),
                    (SubjectType.CODE, GradeLevel.PROFESSIONAL),
                    (SubjectType.CREATIVE, GradeLevel.COLLEGE),
                    (SubjectType.CREATIVE, GradeLevel.PROFESSIONAL),
                ],
                "performance_tier": 1,
                "max_tokens": 4096,
            },
            "claude-3-sonnet": {
                "provider": "anthropic",
                "strengths": [
                    (SubjectType.MATH, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.MATH, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.SCIENCE, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.CODE, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.CODE, GradeLevel.COLLEGE),
                    (SubjectType.ENGLISH, GradeLevel.COLLEGE),
                    (SubjectType.HISTORY, GradeLevel.COLLEGE),
                ],
                "performance_tier": 2,
                "max_tokens": 4096,
            },
            "claude-3-haiku": {
                "provider": "anthropic",
                "strengths": [
                    (SubjectType.MATH, GradeLevel.ELEMENTARY),
                    (SubjectType.SCIENCE, GradeLevel.ELEMENTARY),
                    (SubjectType.SCIENCE, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.ENGLISH, GradeLevel.ELEMENTARY),
                    (SubjectType.ENGLISH, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.HISTORY, GradeLevel.ELEMENTARY),
                    (SubjectType.HISTORY, GradeLevel.MIDDLE_school),
                    (SubjectType.GENERAL, GradeLevel.ELEMENTARY),
                ],
                "performance_tier": 3,
                "max_tokens": 4096,
            },
            "gpt-4": {
                "provider": "openai",
                "strengths": [
                    (SubjectType.CREATIVE, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.CREATIVE, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.ENGLISH, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.HISTORY, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.GENERAL, GradeLevel.COLLEGE),
                    (SubjectType.GENERAL, GradeLevel.PROFESSIONAL),
                ],
                "performance_tier": 1,
                "max_tokens": 8192,
            },
            "gpt-3.5-turbo": {
                "provider": "openai",
                "strengths": [
                    (SubjectType.GENERAL, GradeLevel.HIGH_SCHOOL),
                    (SubjectType.GENERAL, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.CODE, GradeLevel.ELEMENTARY),
                    (SubjectType.CODE, GradeLevel.MIDDLE_SCHOOL),
                    (SubjectType.CREATIVE, GradeLevel.ELEMENTARY),
                ],
                "performance_tier": 3,
                "max_tokens": 4096,
            },
        }

        # Fallback hierarchy when no exact match
        self.fallback_models = {
            SubjectType.MATH: ["claude-3-sonnet", "claude-3-opus", "gpt-4"],
            SubjectType.SCIENCE: ["claude-3-sonnet", "claude-3-opus", "gpt-4"],
            SubjectType.CODE: ["claude-3-sonnet", "claude-3-opus", "gpt-4"],
            SubjectType.CREATIVE: ["gpt-4", "claude-3-opus", "claude-3-sonnet"],
            SubjectType.ENGLISH: ["gpt-4", "claude-3-sonnet", "claude-3-opus"],
            SubjectType.HISTORY: ["gpt-4", "claude-3-sonnet", "claude-3-opus"],
            SubjectType.GENERAL: ["claude-3-sonnet", "gpt-4", "gpt-3.5-turbo"],
        }

    async def select_model(self, context: ProcessedContext) -> ModelChoice:
        suitable_models = self._find_suitable_models(context.subject, context.grade_level)
        if not suitable_models:
            suitable_models = self._get_fallback_models(context)

        scored_models = self._score_models(suitable_models, context)
        best_model_name = max(scored_models, key=scored_models.get)
        best_model_config = self.model_registry[best_model_name]

        estimated_cost = self.cost_calculator.calculate_cost(best_model_name, context.estimated_tokens, context.estimated_tokens) # Assuming input and output tokens are the same for estimation

        return ModelChoice(
            model=best_model_name,
            provider=best_model_config["provider"],
            confidence=scored_models[best_model_name],
            reasoning=self._generate_reasoning(best_model_name, context.subject, context.grade_level, estimated_cost),
            estimated_cost=estimated_cost,
        )

    def _find_suitable_models(self, subject: SubjectType, grade_level: GradeLevel) -> List[str]:
        # ... (implementation remains the same)
        suitable = []
        for model_name, config in self.model_registry.items():
            if (subject, grade_level) in config["strengths"]:
                suitable.append(model_name)
        return suitable

    def _get_fallback_models(self, context: ProcessedContext) -> List[str]:
        # ... (implementation remains the same)
        fallback_list = self.fallback_models.get(context.subject, ["claude-3-sonnet"])
        if context.complexity_score > 0.7:
            return [m for m in fallback_list if self.model_registry[m]["performance_tier"] <= 2]
        elif context.complexity_score > 0.4:
            return fallback_list
        else:
            return sorted(fallback_list, key=lambda m: self.cost_calculator.pricing_data.get(m, {}).get('input_cost_per_1k_tokens', 999))

    def _score_models(self, models: List[str], context: ProcessedContext) -> Dict[str, float]:
        # ... (implementation remains the same)
        scores = {}
        for model in models:
            config = self.model_registry[model]
            tier_score = (4 - config["performance_tier"]) / 3
            cost_price = self.cost_calculator.pricing_data.get(model, {}).get('input_cost_per_1k_tokens', 999)
            cost_score = 1.0 / (cost_price * 100 + 1) # Normalize
            context_score = 1.0 if (context.subject, context.grade_level) in config["strengths"] else 0.5
            complexity_penalty = 1.0
            if context.complexity_score > 0.7 and config["performance_tier"] > 2:
                complexity_penalty = 0.5
            elif context.complexity_score < 0.3 and config["performance_tier"] == 1:
                complexity_penalty = 0.8
            final_score = (tier_score * 0.4 + cost_score * 0.3 + context_score * 0.3) * complexity_penalty
            scores[model] = final_score
        return scores

    def _generate_reasoning(self, model: str, subject: SubjectType, grade_level: GradeLevel, cost: float) -> str:
        # ... (implementation remains the same)
        config = self.model_registry[model]
        exact_match = (subject, grade_level) in config["strengths"]
        if exact_match:
            return f"Selected {model} as it's optimized for {subject.value} at {grade_level.value} level. Estimated cost: ${cost:.4f}"
        else:
            return f"Selected {model} as best fallback for {subject.value} tasks. Performance tier {config['performance_tier']}, cost: ${cost:.4f}"

    def get_available_models(self) -> Dict[str, Dict]:
        return self.model_registry.copy()
