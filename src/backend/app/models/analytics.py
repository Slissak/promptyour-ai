"""
Analytics and performance tracking models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class ModelPerformance(Base):
    """Track model performance metrics over time"""
    
    __tablename__ = "model_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Model identification
    model_name = Column(String, nullable=False, index=True)
    model_provider = Column(String, nullable=False)
    
    # Context
    subject = Column(String, nullable=False, index=True)
    grade_level = Column(String, nullable=False, index=True)
    
    # Performance metrics
    avg_user_rating = Column(Float, nullable=False)        # Average 1-5 user rating
    avg_judge_score = Column(Float, nullable=False)        # Average 1-10 LLM judge score
    avg_cost_per_request = Column(Float, nullable=False)   # Average cost in USD
    avg_response_time_ms = Column(Integer, nullable=False) # Average response time
    
    # Usage statistics
    total_requests = Column(Integer, nullable=False)
    successful_requests = Column(Integer, nullable=False)
    failed_requests = Column(Integer, nullable=False)
    success_rate = Column(Float, nullable=False)           # Percentage
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Metadata
    data_points_count = Column(Integer, nullable=False)    # Number of evaluations
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_model_context_performance', 'model_name', 'subject', 'grade_level'),
        Index('idx_performance_period', 'period_start', 'period_end'),
    )


class DailyMetrics(Base):
    """Daily aggregated system metrics"""
    
    __tablename__ = "daily_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    date = Column(DateTime, nullable=False, index=True)
    
    # Usage metrics
    total_requests = Column(Integer, nullable=False)
    successful_requests = Column(Integer, nullable=False)
    failed_requests = Column(Integer, nullable=False)
    unique_users = Column(Integer, nullable=False)
    
    # Cost metrics
    total_cost_usd = Column(Float, nullable=False)
    avg_cost_per_request = Column(Float, nullable=False)
    
    # Performance metrics
    avg_response_time_ms = Column(Integer, nullable=False)
    avg_user_rating = Column(Float, nullable=True)
    avg_judge_score = Column(Float, nullable=True)
    
    # Model distribution
    most_used_model = Column(String, nullable=True)
    model_distribution = Column(String, nullable=True)  # JSON string
    
    # Subject distribution  
    subject_distribution = Column(String, nullable=True)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ModelSelection(Base):
    """Track model selection decisions for analysis"""
    
    __tablename__ = "model_selections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Request context
    subject = Column(String, nullable=False, index=True)
    grade_level = Column(String, nullable=False, index=True)
    complexity_score = Column(Float, nullable=False)
    
    # Selection process
    available_models = Column(String, nullable=False)      # JSON list
    model_scores = Column(String, nullable=False)          # JSON dict
    selected_model = Column(String, nullable=False, index=True)
    selection_confidence = Column(Float, nullable=False)
    selection_reasoning = Column(String, nullable=False)
    
    # Alternative models considered
    second_choice = Column(String, nullable=True)
    third_choice = Column(String, nullable=True)
    
    # Outcome (to be updated later)
    was_optimal_choice = Column(Boolean, nullable=True)    # Determined by evaluation
    user_rating = Column(Integer, nullable=True)           # 1-5 scale
    judge_score = Column(Float, nullable=True)             # 1-10 scale
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    evaluated_at = Column(DateTime, nullable=True)
    
    # Index for analysis queries
    __table_args__ = (
        Index('idx_selection_context', 'subject', 'grade_level', 'selected_model'),
        Index('idx_selection_outcome', 'selected_model', 'was_optimal_choice'),
    )


class ErrorLog(Base):
    """Track errors and failures for system monitoring"""
    
    __tablename__ = "error_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Error context
    component = Column(String, nullable=False, index=True)  # input_processor, model_selector, etc.
    error_type = Column(String, nullable=False, index=True) # Exception type
    error_message = Column(String, nullable=False)
    
    # Request context (if available)
    user_id = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    grade_level = Column(String, nullable=True)
    selected_model = Column(String, nullable=True)
    
    # Error details
    stack_trace = Column(String, nullable=True)
    request_data = Column(String, nullable=True)  # JSON string
    
    # Resolution
    resolved = Column(Boolean, default=False, nullable=False)
    resolution_notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    resolved_at = Column(DateTime, nullable=True)