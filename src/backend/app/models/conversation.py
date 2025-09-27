"""
Conversation and Message database models
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Conversation(Base):
    """Conversation model for grouping messages"""
    
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model storing complete interaction data"""
    
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    
    # User input
    user_message = Column(Text, nullable=False)
    subject = Column(String, nullable=False)
    grade_level = Column(String, nullable=False)
    additional_context = Column(Text, nullable=True)
    complexity_score = Column(Float, nullable=False)
    
    # System processing
    system_prompt = Column(Text, nullable=False)
    selected_model = Column(String, nullable=False)
    model_provider = Column(String, nullable=False)
    selection_reasoning = Column(Text, nullable=False)
    selection_confidence = Column(Float, nullable=False)
    
    # LLM response
    ai_response = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    
    # Success indicators
    request_successful = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    evaluations = relationship("MessageEvaluation", back_populates="message", cascade="all, delete-orphan")


class MessageEvaluation(Base):
    """Store evaluations for messages (user ratings + LLM judge scores)"""
    
    __tablename__ = "message_evaluations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False, index=True)
    
    # User evaluation
    user_rating = Column(Integer, nullable=True)  # 1-5 scale
    user_feedback = Column(Text, nullable=True)
    
    # LLM judge evaluation  
    llm_judge_relevance = Column(Float, nullable=True)    # 1-10 scale
    llm_judge_accuracy = Column(Float, nullable=True)     # 1-10 scale
    llm_judge_completeness = Column(Float, nullable=True) # 1-10 scale
    llm_judge_clarity = Column(Float, nullable=True)      # 1-10 scale
    llm_judge_overall = Column(Float, nullable=True)      # 1-10 scale
    judge_model = Column(String, nullable=True)
    judge_reasoning = Column(Text, nullable=True)
    
    # Metadata
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    evaluation_version = Column(String, default="1.0", nullable=False)
    
    # Relationships
    message = relationship("Message", back_populates="evaluations")