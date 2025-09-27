"""
Logging configuration
"""
import logging
import sys
from typing import Dict, Any

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging():
    """Configure structured logging"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


def log_request(method: str, path: str, **kwargs: Dict[str, Any]):
    """Log HTTP requests"""
    logger = get_logger("http")
    logger.info("HTTP request", method=method, path=path, **kwargs)


def log_model_request(model: str, prompt_tokens: int, **kwargs: Dict[str, Any]):
    """Log model API requests"""
    logger = get_logger("models")
    logger.info("Model request", model=model, prompt_tokens=prompt_tokens, **kwargs)


def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log errors with context"""
    logger = get_logger("error")
    logger.error(
        "Application error",
        error=str(error),
        error_type=type(error).__name__,
        context=context or {}
    )