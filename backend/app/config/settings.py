"""
Application Settings

This module contains all configuration settings for the application.
Uses Pydantic BaseSettings for environment variable management and validation.
"""

import logging
from functools import lru_cache
from typing import List, Union

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        environment: Current environment (development, staging, production)
        host: Server host address
        port: Server port number
        database_url: Database connection URL
        test_database_url: Test database connection URL
        secret_key: JWT secret key for token signing
        algorithm: JWT algorithm for token encoding
        access_token_expire_minutes: JWT token expiration time in minutes
        allowed_origins: List of allowed CORS origins
        log_level: Logging level
        enable_docs: Enable API documentation endpoints
    """

    # Environment
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./exam_transcripts.db"
    test_database_url: str = "sqlite:///./test_exam_transcripts.db"

    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8080", "https://api-is-for-exam-transcripts.vercel.app", "https://apis-for-exam-transcripts.vercel.app"]

    # Logging
    log_level: str = "INFO"

    # API Documentation
    enable_docs: bool = True

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed_environments = ["development", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of: {allowed_environments}")
        return v

    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Validate secret key in production."""
        if (
            values.get("environment") == "production"
            and v == "your-super-secret-key-change-this-in-production"
        ):
            raise ValueError("Secret key must be changed in production environment")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    @validator("enable_docs")
    def validate_docs_in_production(cls, v, values):
        """Disable docs in production unless explicitly enabled."""
        if values.get("environment") == "production" and v is True:
            # Allow override but warn
            return v
        elif values.get("environment") == "production":
            return False
        return v

    @property
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.environment == "development"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
