"""
Application Settings

This module contains all configuration settings for the application.
Uses Pydantic BaseSettings for environment variable management and validation.
"""

import logging
from functools import lru_cache
from typing import List, Union, Optional

from pydantic import validator, Field
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
    
    # PostgreSQL settings for production
    postgres_ssl_mode: str = "require"  # Can be disabled if needed

    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS - Use a string field that we'll parse manually
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:8080,https://api-is-for-exam-transcripts.vercel.app,https://apis-for-exam-transcripts.vercel.app",
        alias="ALLOWED_ORIGINS"
    )
    
    # Additional CORS setting for production
    frontend_url: Optional[str] = None  # Can be set via environment variable

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

    @property
    def database_connection_url(self) -> str:
        """Get the proper database URL with SSL configuration for production."""
        # If using PostgreSQL in production, add SSL configuration
        if self.database_url.startswith("postgresql"):
            # Check if SSL mode is already in the URL
            if "sslmode=" not in self.database_url:
                separator = "&" if "?" in self.database_url else "?"
                return f"{self.database_url}{separator}sslmode={self.postgres_ssl_mode}"
        return self.database_url

    @property
    def cors_origins(self) -> List[str]:
        """Get all CORS origins including dynamically added ones."""
        # Parse allowed_origins_str into a list
        origins = [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]
        
        # Add frontend_url if provided
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        
        # In development, allow broader access for testing
        if self.is_development:
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8080",
                "http://127.0.0.1:8080"
            ])
        
        return list(set(origins))  # Remove duplicates

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow field aliases from environment variables
        populate_by_name = True


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
