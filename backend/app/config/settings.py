"""
Application Settings

This module contains all configuration settings for the application.
Uses Pydantic BaseSettings for environment variable management and validation.
"""

from functools import lru_cache

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
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

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
