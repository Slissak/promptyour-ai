from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ThemeType(str, Enum):
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
    SMALL_KIDS = "small_kids"
    TEENAGERS = "teenagers"
    ADULTS = "adults"
    UNIVERSITY_LEVEL = "university_level"
    PROFESSIONALS = "professionals"
    SENIORS = "seniors"

class ResponseStyle(str, Enum):
    PARAGRAPH_BRIEF = "paragraph_brief"
    STRUCTURED_DETAILED = "structured_detailed"
    INSTRUCTIONS_ONLY = "instructions_only"
    COMPREHENSIVE = "comprehensive"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    id: str
    role: MessageRole
    content: str
    timestamp: str
    model: Optional[str] = None
    provider: Optional[str] = None
    metadata: Optional[dict] = None

class LLMRequest(BaseModel):
    model: str
    system_prompt: str
    user_message: str
    max_tokens: int
    temperature: float
    enable_reasoning: bool = False
    message_history: Optional[List[ChatMessage]] = None

class LLMResponse(BaseModel):
    content: str
    model: str
    provider: str
    tokens_used: int
    cost: float
    response_time_ms: int
    message_id: str
    thinking: Optional[str] = None
