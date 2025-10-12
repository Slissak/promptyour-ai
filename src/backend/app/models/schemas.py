"""
Pydantic schemas for request/response models

NOTE: Themes, Audiences, and Response Styles are now loaded from YAML config files:
- config/themes.yaml
- config/audiences.yaml
- config/response_styles.yaml

To modify available options, edit those files instead of this code.
"""
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.config_loader import get_config_loader


# ===== DYNAMIC ENUMS FROM CONFIG =====
# These enums are generated from YAML config files for easy modification

def _create_enum_from_config(enum_name: str, config_loader_method: str, fallback_values: List[str] = None) -> type:
    """Create an Enum dynamically from config loader with fallback values"""
    config_loader = get_config_loader()
    ids = getattr(config_loader, config_loader_method)()

    # Use fallback values if config didn't load
    if not ids and fallback_values:
        ids = fallback_values

    # Create enum members: {ID_UPPER: "id_value", ...}
    enum_members = {id_val.upper(): id_val for id_val in ids}

    return Enum(enum_name, enum_members, type=str)


# Generate enums from config files with fallback values
ThemeType = _create_enum_from_config(
    "ThemeType",
    "get_theme_ids",
    fallback_values=["academic_help", "creative_writing", "coding_programming", "business_professional",
                     "personal_learning", "research_analysis", "problem_solving", "tutoring_education", "general_questions"]
)
AudienceType = _create_enum_from_config(
    "AudienceType",
    "get_audience_ids",
    fallback_values=["small_kids", "teenagers", "adults", "university_level", "professionals", "seniors"]
)
ResponseStyle = _create_enum_from_config(
    "ResponseStyle",
    "get_response_style_ids",
    fallback_values=["paragraph_brief", "structured_detailed", "instructions_only", "comprehensive"]
)

# Add docstrings
ThemeType.__doc__ = "Themes loaded from config/themes.yaml - Edit that file to modify options"
AudienceType.__doc__ = "Audiences loaded from config/audiences.yaml - Edit that file to modify options"
ResponseStyle.__doc__ = "Response Styles loaded from config/response_styles.yaml - Edit that file to modify options"


class MessageRole(str, Enum):
    """Message roles for conversation history"""
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Individual message in conversation history"""
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message", min_length=1)
    timestamp: Optional[str] = Field(None, description="ISO timestamp of the message")
    model: Optional[str] = Field(None, description="Model used for assistant messages")
    provider: Optional[str] = Field(None, description="Provider used for assistant messages")


class QuickInput(BaseModel):
    """Input structure for quick one-liner responses"""
    question: str = Field(..., description="The user's main question or request", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for history")
    message_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Previous messages in conversation")
    force_model: Optional[str] = Field(None, description="Force use of specific model")
    force_provider: Optional[str] = Field(None, description="Force use of specific provider")


class UserInput(BaseModel):
    """Complete user input structure"""
    question: str = Field(..., description="The user's main question or request", min_length=1)
    theme: Optional[ThemeType] = Field(None, description="Selected theme from dropdown (optional)")
    audience: Optional[AudienceType] = Field(None, description="Target audience for response (optional, defaults to adults if not specified)")
    response_style: Optional[ResponseStyle] = Field(None, description="Response style preference for output formatting and length (optional, defaults to structured_detailed if not specified)")
    context: Optional[str] = Field(None, description="Additional context sentences provided by user")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for history")
    message_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Previous messages in conversation")
    force_model: Optional[str] = Field(None, description="Force use of specific model")
    force_provider: Optional[str] = Field(None, description="Force use of specific provider")


class ProcessedContext(BaseModel):
    """Processed and enriched context from user input"""
    # Original input
    question: str
    theme: Optional[ThemeType] = None
    audience: Optional[AudienceType] = None
    response_style: Optional[ResponseStyle] = None
    context: Optional[str] = None
    conversation_id: Optional[str] = None
    
    # Inferred/processed fields
    inferred_subject: str = Field(..., description="Auto-detected subject area")
    inferred_complexity: str = Field(..., description="Auto-detected complexity level")
    complexity_score: float = Field(..., description="Complexity score 0-1")
    estimated_tokens: int = Field(..., description="Estimated token count for LLM call")
    
    # Processing metadata
    processing_confidence: float = Field(..., description="Confidence in auto-detection 0-1")
    requires_clarification: bool = Field(default=False, description="Whether input needs user clarification")


class ModelChoice(BaseModel):
    """Selected model with reasoning"""
    model: str = Field(..., description="Selected model name")
    provider: str = Field(..., description="Model provider (openai, anthropic, etc)")
    confidence: float = Field(..., description="Selection confidence 0-1")
    reasoning: str = Field(..., description="Why this model was selected")
    estimated_cost: float = Field(..., description="Estimated cost in USD")


class LLMRequest(BaseModel):
    """Request to LLM provider"""
    model: str
    system_prompt: str
    user_message: str
    max_tokens: int = 4000
    temperature: float = 0.7
    enable_reasoning: bool = False  # Whether to enable extended thinking/reasoning
    reasoning_effort: Optional[str] = None  # For OpenAI models: "high", "medium", "low"
    reasoning_budget_tokens: Optional[int] = None  # For Anthropic models: token budget (min 1024)


class LLMResponse(BaseModel):
    """Response from LLM provider"""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost: float
    response_time_ms: int
    message_id: str
    thinking: Optional[str] = None  # Internal reasoning/thinking (not shown to user)


class ChatResponse(BaseModel):
    """Final response to user"""
    content: str
    model_used: str
    provider: str
    message_id: str
    cost: float
    response_time_ms: int
    reasoning: str = Field(..., description="Why this model was chosen")
    system_prompt: str = Field(..., description="System prompt used for this response")
    raw_response: Optional[str] = Field(None, description="RAW model response (no system prompt) for comparison")
    thinking: Optional[str] = Field(None, description="Internal model reasoning/thinking (stored but not displayed to user)")


class QuickResponse(BaseModel):
    """Quick one-liner response to user"""
    content: str = Field(..., description="One-line answer to the question")
    model_used: str
    provider: str
    message_id: str
    cost: float
    response_time_ms: int
    system_prompt: str = Field(..., description="System prompt used for this response")
    thinking: Optional[str] = Field(None, description="Internal model reasoning/thinking (stored but not displayed to user)")


class RawInput(BaseModel):
    """Input structure for RAW responses - no prompt engineering"""
    question: str = Field(..., description="The user's question - sent directly to model without any prompt engineering", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")
    message_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Previous messages in conversation")
    force_model: Optional[str] = Field(None, description="Force use of specific model")
    force_provider: Optional[str] = Field(None, description="Force use of specific provider")


class RawResponse(BaseModel):
    """RAW response from model - no system prompt, no prompt engineering"""
    content: str = Field(..., description="RAW model output with no prompt engineering")
    model_used: str
    provider: str
    message_id: str
    cost: float
    response_time_ms: int
    system_prompt: str = Field(default="", description="System prompt (always empty for RAW responses)")
    thinking: Optional[str] = Field(None, description="Internal model reasoning/thinking (stored but not displayed to user)")


class UserRating(BaseModel):
    """User's rating of a response"""
    message_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback: Optional[str] = Field(None, description="Optional text feedback")


class EvaluationResult(BaseModel):
    """LLM judge evaluation result"""
    message_id: str
    relevance_score: float = Field(..., ge=0, le=10)
    accuracy_score: float = Field(..., ge=0, le=10)
    completeness_score: float = Field(..., ge=0, le=10)
    clarity_score: float = Field(..., ge=0, le=10)
    overall_score: float = Field(..., ge=0, le=10)
    judge_model: str
    created_at: datetime


class ModelPerformance(BaseModel):
    """Model performance metrics"""
    model: str
    theme: ThemeType
    complexity: str
    avg_user_rating: float
    avg_judge_score: float
    avg_cost: float
    avg_response_time: float
    total_uses: int
    success_rate: float
    last_updated: datetime