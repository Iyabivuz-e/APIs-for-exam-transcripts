"""
Logging Configuration Module

Provides structured logging with correlation IDs and proper formatting for production use.
"""

import logging
import sys
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

from app.config.settings import get_settings

# Context variable to store correlation ID across async contexts
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationFilter(logging.Filter):
    """
    Logging filter to add correlation ID to log records.
    """

    def filter(self, record):
        record.correlation_id = correlation_id.get() or "unknown"
        return True


class StructuredLogger:
    """
    Structured logger with correlation ID support.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """Setup logger with appropriate handlers and formatters."""
        settings = get_settings()
        
        if self.logger.hasHandlers():
            return

        self.logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        handler = logging.StreamHandler(sys.stdout)
        handler.addFilter(CorrelationFilter())
        
        if settings.environment == "production":
            # JSON formatter for production
            formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(name)s %(levelname)s %(correlation_id)s %(message)s"
            )
        else:
            # Human-readable formatter for development
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s"
            )
        
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def info(self, message: str, **kwargs):
        """Log info message with optional extra fields."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional extra fields."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message with optional extra fields."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional extra fields."""
        self.logger.debug(message, extra=kwargs)


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


@contextmanager
def correlation_context(correlation_id_value: Optional[str] = None):
    """
    Context manager to set correlation ID for the current async context.
    
    Args:
        correlation_id_value: Correlation ID to use, generates one if None
    """
    if correlation_id_value is None:
        correlation_id_value = str(uuid.uuid4())[:8]
    
    token = correlation_id.set(correlation_id_value)
    try:
        yield correlation_id_value
    finally:
        correlation_id.reset(token)


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id.get()
