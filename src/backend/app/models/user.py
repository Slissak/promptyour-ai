"""
User database models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.app.db.database import Base
from shared_python.db.models.usage import UserUsage

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

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
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    user_usage = relationship("UserUsage", back_populates="user", uselist=False)
