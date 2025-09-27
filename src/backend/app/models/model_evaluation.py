"""
Database models for dynamic model evaluation and leaderboard data
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Index

from app.db.database import Base


class ModelLeaderboard(Base):
    """Store model evaluation data from various leaderboards and benchmarks"""
    
    __tablename__ = "model_leaderboards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Model identification
    model_name = Column(String, nullable=False, index=True)
    model_provider = Column(String, nullable=False)
    model_version = Column(String, nullable=True)
    
    # Source information
    source_name = Column(String, nullable=False, index=True)  # "MMLU", "HumanEval", "HellaSwag", etc.
    source_url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # "benchmark", "leaderboard", "evaluation"
    
    # Scoring data
    overall_score = Column(Float, nullable=True)  # Overall score if available
    score_details = Column(JSON, nullable=True)   # Detailed breakdown by category
    
    # Theme-aligned scores (calculated from benchmark data)
    academic_score = Column(Float, nullable=True)      # For academic_help theme
    creative_score = Column(Float, nullable=True)      # For creative_writing theme
    coding_score = Column(Float, nullable=True)        # For coding_programming theme
    business_score = Column(Float, nullable=True)      # For business_professional theme
    research_score = Column(Float, nullable=True)      # For research_analysis theme
    problem_solving_score = Column(Float, nullable=True)  # For problem_solving theme
    tutoring_score = Column(Float, nullable=True)      # For tutoring_education theme
    general_score = Column(Float, nullable=True)       # For general_questions theme
    
    # Metadata
    evaluation_date = Column(DateTime, nullable=True)  # When the evaluation was conducted
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    confidence_level = Column(Float, nullable=True)    # Confidence in the data quality
    
    # Raw data for debugging
    raw_data = Column(JSON, nullable=True)
    
    # Composite indices for efficient queries
    __table_args__ = (
        Index('idx_model_source_evaluation', 'model_name', 'source_name', 'evaluation_date'),
        Index('idx_model_themes', 'model_name', 'academic_score', 'creative_score', 'coding_score'),
    )


class EvaluationSource(Base):
    """Track evaluation sources and their scraping configuration"""
    
    __tablename__ = "evaluation_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source identification
    source_name = Column(String, unique=True, nullable=False)
    source_url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # "benchmark", "leaderboard", "paper"
    
    # Scraping configuration
    scraping_config = Column(JSON, nullable=False)  # URLs, selectors, parsing rules
    update_frequency_hours = Column(Integer, default=24, nullable=False)  # How often to scrape
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_scraped = Column(DateTime, nullable=True)
    last_successful_scrape = Column(DateTime, nullable=True)
    scraping_errors = Column(Text, nullable=True)
    
    # Mapping configuration for themes
    theme_mapping_config = Column(JSON, nullable=True)  # How to map scores to our themes
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ModelRanking(Base):
    """Aggregated model rankings based on all evaluation sources"""
    
    __tablename__ = "model_rankings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Model identification
    model_name = Column(String, nullable=False, index=True)
    model_provider = Column(String, nullable=False)
    
    # Overall ranking
    overall_rank = Column(Integer, nullable=False)
    overall_score = Column(Float, nullable=False)
    
    # Theme-specific rankings
    academic_rank = Column(Integer, nullable=True)
    academic_score = Column(Float, nullable=True)
    
    creative_rank = Column(Integer, nullable=True)
    creative_score = Column(Float, nullable=True)
    
    coding_rank = Column(Integer, nullable=True)
    coding_score = Column(Float, nullable=True)
    
    business_rank = Column(Integer, nullable=True)
    business_score = Column(Float, nullable=True)
    
    research_rank = Column(Integer, nullable=True)
    research_score = Column(Float, nullable=True)
    
    problem_solving_rank = Column(Integer, nullable=True)
    problem_solving_score = Column(Float, nullable=True)
    
    tutoring_rank = Column(Integer, nullable=True)
    tutoring_score = Column(Float, nullable=True)
    
    general_rank = Column(Integer, nullable=True)
    general_score = Column(Float, nullable=True)
    
    # Additional metrics
    cost_efficiency_rank = Column(Integer, nullable=True)  # Performance per dollar
    speed_rank = Column(Integer, nullable=True)            # Tokens per second
    reliability_score = Column(Float, nullable=True)       # Based on evaluation consistency
    
    # Metadata
    ranking_version = Column(String, default="1.0", nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_sources_count = Column(Integer, nullable=False)   # How many sources contributed
    confidence_level = Column(Float, nullable=False)       # Confidence in ranking
    
    # Composite index for efficient theme-based queries
    __table_args__ = (
        Index('idx_rankings_overall', 'overall_rank', 'overall_score'),
        Index('idx_rankings_theme_academic', 'academic_rank', 'academic_score'),
        Index('idx_rankings_theme_creative', 'creative_rank', 'creative_score'),
        Index('idx_rankings_theme_coding', 'coding_rank', 'coding_score'),
        Index('idx_rankings_calculated', 'calculated_at', 'ranking_version'),
    )


class ScrapingJob(Base):
    """Track scraping jobs and their status"""
    
    __tablename__ = "scraping_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job identification
    job_type = Column(String, nullable=False)  # "full_scan", "incremental", "single_source"
    source_name = Column(String, nullable=True, index=True)  # If scraping specific source
    
    # Job status
    status = Column(String, default="pending", nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    models_found = Column(Integer, default=0, nullable=False)
    evaluations_added = Column(Integer, default=0, nullable=False)
    evaluations_updated = Column(Integer, default=0, nullable=False)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Metadata
    job_config = Column(JSON, nullable=True)  # Specific configuration for this job
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Index for job monitoring
    __table_args__ = (
        Index('idx_scraping_jobs_status', 'status', 'created_at'),
        Index('idx_scraping_jobs_source', 'source_name', 'status'),
    )