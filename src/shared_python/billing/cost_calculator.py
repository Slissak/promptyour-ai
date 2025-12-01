
from shared_python.config.config_loader import get_config_loader

class CostCalculator:
    """Calculates the cost of LLM requests based on token usage and pricing data."""

    def __init__(self):
        config_loader = get_config_loader()
        self.pricing_data = config_loader.get_pricing_data()

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate the cost of a request given the model and token counts."""
        if model not in self.pricing_data:
            # Fallback for unknown models
            return 0.0

        pricing = self.pricing_data[model]
        input_cost = (prompt_tokens / 1000) * pricing.get('input_cost_per_1k_tokens', 0.0)
        output_cost = (completion_tokens / 1000) * pricing.get('output_cost_per_1k_tokens', 0.0)

        return input_cost + output_cost
