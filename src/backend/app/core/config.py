"""
Application configuration settings
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    REDIS_URL: str = Field(..., description="Redis connection URL")
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, description="Anthropic API key") 
    GOOGLE_AI_API_KEY: Optional[str] = Field(None, description="Google AI API key")
    OPENROUTER_API_KEY: Optional[str] = Field(None, description="OpenRouter API key")
    
    # LM Studio Configuration
    LM_STUDIO_URL: str = Field(default="http://localhost:1234/v1", description="LM Studio API URL")
    LM_STUDIO_API_KEY: str = Field(default="lm-studio", description="LM Studio API key (usually not needed)")
    PREFERRED_LLM_PROVIDER: str = Field(default="auto", description="Preferred LLM provider (openrouter, lm_studio, auto)")
    PREFER_LOCAL_LLM: bool = Field(default=True, description="Prefer local LLM over cloud when available")
    
    # Security
    JWT_SECRET: str = Field(..., description="JWT secret key")
    ENCRYPT_KEY: str = Field(..., description="Encryption key (32 bytes)")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiry minutes")
    
    # Application
    API_HOST: str = Field(default="localhost", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Frontend URL")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )
    
    # External Services
    SENTRY_DSN: Optional[str] = Field(None, description="Sentry DSN")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Cost Management
    DEFAULT_DAILY_BUDGET: float = Field(default=10.0, description="Default daily budget")
    DEFAULT_MONTHLY_BUDGET: float = Field(default=100.0, description="Default monthly budget")
    
    # Model Configuration
    DEFAULT_MODEL: str = Field(default="claude-3-haiku", description="Default LLM model")
    FALLBACK_MODEL: str = Field(default="gpt-3.5-turbo", description="Fallback LLM model")
    MAX_TOKENS: int = Field(default=4000, description="Maximum tokens per request")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Rate limit per hour")
    
    # Cache Settings
    CACHE_TTL: int = Field(default=3600, description="Cache TTL in seconds")
    
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic"""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


# Global settings instance
settings = Settings()