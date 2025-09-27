"""
Pydantic schemas for request/response models
"""
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ThemeType(str, Enum):
    """Predefined themes for dropdown selection"""
    ACADEMIC_HELP = "academic_help"
    CREATIVE_WRITING = "creative_writing"
    CODING_PROGRAMMING = "coding_programming"
    BUSINESS_PROFESSIONAL = "business_professional"
    PERSONAL_LEARNING = "personal_learning"
    RESEARCH_ANALYSIS = "research_analysis"
    PROBLEM_SOLVING = "problem_solving"
    TUTORING_EDUCATION = "tutoring_education"
    GENERAL_QUESTIONS = "general_questions"


class AudienceType(str, Enum):
    """Target audience for response tailoring"""
    SMALL_KIDS = "small_kids"           # Ages 5-10
    TEENAGERS = "teenagers"             # Ages 11-17  
    ADULTS = "adults"                   # Ages 18-65
    UNIVERSITY_LEVEL = "university_level"  # College/University
    PROFESSIONALS = "professionals"     # Industry experts
    SENIORS = "seniors"                 # Ages 65+


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
    theme: ThemeType = Field(..., description="Selected theme from dropdown")
    audience: AudienceType = Field(AudienceType.ADULTS, description="Target audience for response")
    context: Optional[str] = Field(None, description="Additional context sentences provided by user")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for history")
    message_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Previous messages in conversation")
    force_model: Optional[str] = Field(None, description="Force use of specific model")
    force_provider: Optional[str] = Field(None, description="Force use of specific provider")


class ProcessedContext(BaseModel):
    """Processed and enriched context from user input"""
    # Original input
    question: str
    theme: ThemeType
    audience: AudienceType
    context: Optional[str]
    conversation_id: Optional[str]
    
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


class LLMResponse(BaseModel):
    """Response from LLM provider"""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost: float
    response_time_ms: int
    message_id: str


class ChatResponse(BaseModel):
    """Final response to user"""
    content: str
    model_used: str
    provider: str
    message_id: str
    cost: float
    response_time_ms: int
    reasoning: str = Field(..., description="Why this model was chosen")


class QuickResponse(BaseModel):
    """Quick one-liner response to user"""
    content: str = Field(..., description="One-line answer to the question")
    model_used: str
    provider: str
    message_id: str
    cost: float
    response_time_ms: int


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