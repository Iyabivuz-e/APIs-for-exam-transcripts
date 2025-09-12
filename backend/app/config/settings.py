"""
Application Settings

This module contains all configuration settings for the application.
Uses Pydantic BaseSettings for environment variable management and validation.
"""

import logging
from functools import lru_cache
from typing import List, Literal, Optional, Union

from pydantic import Field, validator
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
        auto_create_users: Auto-create default users (development only)
    """

    # Environment - Use Literal for type safety
    environment: Literal["development", "staging", "production"] = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"

    # Database
    database_url: str = Field(
        default="sqlite:///./exam_transcripts.db",
        description="Database connection URL"
    )
    test_database_url: str = Field(
        default="sqlite:///./test_exam_transcripts.db",
        description="Test database connection URL"
    )

    # PostgreSQL settings for production
    postgres_ssl_mode: str = "require"  # Can be disabled if needed

    # Security
    secret_key: str = Field(
        default="your-super-secret-key-change-this-in-production",
        min_length=32,
        description="JWT secret key - must be changed in production"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS - Use a string field that we'll parse manually
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:8080,https://api-is-for-exam-transcripts.vercel.app,https://apis-for-exam-transcripts.vercel.app",
        alias="ALLOWED_ORIGINS",
    )

    # Additional CORS setting for production
    frontend_url: Optional[str] = None  # Can be set via environment variable

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )

    # API Documentation - disabled in production by default
    enable_docs: bool = Field(
        default=True,
        description="Enable API documentation endpoints"
    )
    
    # Development features
    auto_create_users: bool = Field(
        default=True,
        description="Auto-create default users (development only)"
    )

    @validator("database_url")
    def validate_database_url(cls, v, values):
        """Validate database URL for production."""
        environment = values.get("environment", "development")
        if environment == "production" and "sqlite" in v.lower():
            raise ValueError("SQLite is not recommended for production. Use PostgreSQL.")
        return v

    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Validate secret key in production."""
        environment = values.get("environment", "development")
        if environment == "production" and len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters in production")
        if (
            environment == "production"
            and v == "your-super-secret-key-change-this-in-production"
        ):
            raise ValueError("Secret key must be changed in production environment")
        return v

    @validator("enable_docs")
    def validate_docs_in_production(cls, v, values):
        """Disable docs in production unless explicitly enabled."""
        environment = values.get("environment", "development")
        if environment == "production" and v is True:
            # Log warning but allow override
            import warnings
            warnings.warn("API documentation is enabled in production")
        return v
    
    @validator("auto_create_users")
    def validate_auto_create_users(cls, v, values):
        """Disable auto user creation in production."""
        environment = values.get("environment", "development")
        if environment == "production" and v is True:
            raise ValueError("auto_create_users must be disabled in production")
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
        origins = [
            origin.strip()
            for origin in self.allowed_origins_str.split(",")
            if origin.strip()
        ]

        # Add frontend_url if provided
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)

        # In development, allow broader access for testing
        if self.is_development:
            origins.extend(
                [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:8080",
                    "http://127.0.0.1:8080",
                ]
            )

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
