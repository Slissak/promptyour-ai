
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Float, Boolean, UUID
from sqlalchemy.orm import relationship

from backend.app.db.base_class import Base

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

    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="user_usage")
