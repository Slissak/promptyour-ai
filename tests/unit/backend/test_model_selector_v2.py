"""
Unit tests for ThemeBasedModelSelector
"""
import pytest
from unittest.mock import AsyncMock, patch
from backend.app.services.model_selector_v2 import ThemeBasedModelSelector
from backend.app.models.schemas import ProcessedContext, ModelChoice, ThemeType


@pytest.fixture
def model_selector():
    """Create model selector instance"""
    return ThemeBasedModelSelector()


@pytest.fixture
def sample_context():
    """Create sample processed context"""
    return ProcessedContext(
        theme=ThemeType.CODING_PROGRAMMING,
        question="How do I implement binary search in Python?",
        context="I'm learning algorithms",
        inferred_subject="programming",
        inferred_complexity="intermediate",
        complexity_score=0.6,
        estimated_tokens=150,
        processing_confidence=0.85,
        requires_clarification=False,
    )


@pytest.fixture
def patch_load_config():
    with patch(
        "backend.app.services.model_selector_v2.ThemeBasedModelSelector._load_configuration",
        new_callable=AsyncMock,
    ) as mock_load_config:
        yield mock_load_config


@pytest.mark.usefixtures("patch_load_config")
class TestModelSelectorV2:
    """Test cases for ThemeBasedModelSelector"""

    @pytest.mark.asyncio
    async def test_select_model_returns_model_choice(
        self, model_selector, sample_context
    ):
        """Test that select_model returns a ModelChoice object"""
        # Mock configuration loading
        model_selector.theme_model_rankings = {
            ThemeType.CODING_PROGRAMMING: {
                "primary": ["gpt-4", "claude-3-opus", "gemini-pro"],
                "budget": ["gpt-3.5-turbo", "llama-2"],
            }
        }
        model_selector.complexity_models = {
            "intermediate": {
                "preferred": ["gpt-4", "claude-3-opus"],
                "minimum": ["gpt-3.5-turbo"],
            }
        }
        model_selector.base_models = {}

        result = await model_selector.select_model(sample_context, "balanced")

        assert isinstance(result, ModelChoice)
        assert result.model is not None
        assert result.provider is not None
        assert 0 <= result.confidence <= 1
        assert result.estimated_cost >= 0

    @pytest.mark.asyncio
    async def test_theme_candidates_selection(self, model_selector):
        """Test that theme candidates are selected correctly"""
        model_selector.theme_model_rankings = {
            ThemeType.CODING_PROGRAMMING: {
                "primary": ["gpt-4", "claude-3-opus", "gemini-pro"],
                "budget": ["gpt-3.5-turbo", "llama-2"],
            }
        }

        # Test premium tier
        candidates = model_selector._get_theme_candidates(
            ThemeType.CODING_PROGRAMMING, "premium"
        )
        assert len(candidates) <= 3
        assert "gpt-4" in candidates

        # Test budget tier
        candidates = model_selector._get_theme_candidates(
            ThemeType.CODING_PROGRAMMING, "budget"
        )
        assert "gpt-3.5-turbo" in candidates or "llama-2" in candidates

        # Test balanced tier
        candidates = model_selector._get_theme_candidates(
            ThemeType.CODING_PROGRAMMING, "balanced"
        )
        assert len(candidates) >= 2

    @pytest.mark.asyncio
    async def test_complexity_filtering(self, model_selector):
        """Test that models are filtered by complexity"""
        model_selector.complexity_models = {
            "beginner": {
                "preferred": ["gpt-3.5-turbo", "llama-2"],
                "minimum": ["gpt-3.5-turbo"],
            },
            "professional": {
                "preferred": ["gpt-4", "claude-3-opus"],
                "minimum": ["gpt-4"],
            },
        }

        candidates = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"]

        # Test beginner complexity
        filtered = model_selector._filter_by_complexity(candidates, "beginner")
        assert "gpt-3.5-turbo" in filtered

        # Test professional complexity
        filtered = model_selector._filter_by_complexity(candidates, "professional")
        assert "gpt-4" in filtered or "claude-3-opus" in filtered

    @pytest.mark.asyncio
    async def test_budget_tier_selection(self, model_selector, sample_context):
        """Test different budget tier selections"""
        model_selector.theme_model_rankings = {
            ThemeType.CODING_PROGRAMMING: {
                "primary": ["gpt-4", "claude-3-opus"],
                "budget": ["gpt-3.5-turbo"],
            }
        }
        model_selector.complexity_models = {
            "intermediate": {"preferred": ["gpt-4"], "minimum": ["gpt-3.5-turbo"]}
        }
        model_selector.base_models = {}

        # Premium should prefer expensive models
        result = await model_selector.select_model(sample_context, "premium")
        assert result.model in ["gpt-4", "claude-3-opus"]

        # Budget should prefer cheaper models
        result = await model_selector.select_model(sample_context, "budget")
        # Just verify it returns a valid model
        assert result.model is not None

    @pytest.mark.asyncio
    async def test_model_choice_reasoning(self, model_selector, sample_context):
        """Test that model choice includes reasoning"""
        model_selector.theme_model_rankings = {
            ThemeType.CODING_PROGRAMMING: {
                "primary": ["gpt-4"],
                "budget": ["gpt-3.5-turbo"],
            }
        }
        model_selector.complexity_models = {
            "intermediate": {"preferred": ["gpt-4"], "minimum": ["gpt-3.5-turbo"]}
        }
        model_selector.base_models = {}

        result = await model_selector.select_model(sample_context)

        assert result.reasoning is not None
        assert len(result.reasoning) > 0

    @pytest.mark.asyncio
    async def test_confidence_score_range(self, model_selector, sample_context):
        """Test that confidence score is within valid range"""
        model_selector.theme_model_rankings = {
            ThemeType.CODING_PROGRAMMING: {
                "primary": ["gpt-4"],
                "budget": ["gpt-3.5-turbo"],
            }
        }
        model_selector.complexity_models = {
            "intermediate": {"preferred": ["gpt-4"], "minimum": ["gpt-3.5-turbo"]}
        }
        model_selector.base_models = {}

        result = await model_selector.select_model(sample_context)

        assert 0.0 <= result.confidence <= 1.0

    @pytest.mark.asyncio
    async def test_different_themes(self, model_selector):
        """Test model selection for different themes"""
        model_selector.theme_model_rankings = {
            ThemeType.CREATIVE_WRITING: {
                "primary": ["claude-3-opus", "gpt-4"],
                "budget": ["gpt-3.5-turbo"],
            },
            ThemeType.ACADEMIC_HELP: {
                "primary": ["gpt-4", "gemini-pro"],
                "budget": ["gpt-3.5-turbo"],
            },
        }
        model_selector.complexity_models = {
            "intermediate": {"preferred": ["gpt-4"], "minimum": ["gpt-3.5-turbo"]}
        }
        model_selector.base_models = {}

        # Test creative writing
        creative_context = ProcessedContext(
            theme=ThemeType.CREATIVE_WRITING,
            question="Write a story",
            context=None,
            inferred_subject="creative writing",
            inferred_complexity="intermediate",
            complexity_score=0.5,
            estimated_tokens=100,
            processing_confidence=0.8,
            requires_clarification=False,
        )

        result = await model_selector.select_model(creative_context)
        assert result.model in ["claude-3-opus", "gpt-4", "gpt-3.5-turbo"]

        # Test academic help
        academic_context = ProcessedContext(
            theme=ThemeType.ACADEMIC_HELP,
            question="Explain calculus",
            context=None,
            inferred_subject="mathematics",
            inferred_complexity="intermediate",
            complexity_score=0.6,
            estimated_tokens=120,
            processing_confidence=0.85,
            requires_clarification=False,
        )

        result = await model_selector.select_model(academic_context)
        assert result.model in ["gpt-4", "gemini-pro", "gpt-3.5-turbo"]
