"""
User database models
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, JSON, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """User model for authentication and preferences"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    
    # User preferences for model selection
    preferences = Column(JSON, default=dict, nullable=True)
    
    # Budget settings
    daily_budget = Column(Float, default=10.0, nullable=False)
    monthly_budget = Column(Float, default=100.0, nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    user_usage = relationship("UserUsage", back_populates="user", uselist=False)


class UserUsage(Base):
    """Track user's daily and monthly usage/costs"""
    
    __tablename__ = "user_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Daily tracking
    daily_cost = Column(Float, default=0.0, nullable=False)
    daily_requests = Column(Float, default=0, nullable=False)
    daily_reset_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Monthly tracking
    monthly_cost = Column(Float, default=0.0, nullable=False) 
    monthly_requests = Column(Float, default=0, nullable=False)
    monthly_reset_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Limits
    daily_budget_exceeded = Column(Boolean, default=False, nullable=False)
    monthly_budget_exceeded = Column(Boolean, default=False, nullable=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships  
    user = relationship("User", back_populates="user_usage")