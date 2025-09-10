"""
Security Module

This module handles JWT token creation, validation, and password hashing.
Provides utilities for authentication and authorization.
"""

from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.config.settings import get_settings


class SecurityManager:
    """
    Handles security operations including JWT tokens and password hashing.
    """

    def __init__(self):
        """Initialize security manager with settings."""
        self.settings = get_settings()

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """
        Create JWT access token.

        Args:
            data: Token payload data
            expires_delta: Custom expiration time delta

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, self.settings.secret_key, algorithm=self.settings.algorithm
        )

        return encoded_jwt

    def verify_token(self, token: str) -> dict | None:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            dict: Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token, self.settings.secret_key, algorithms=[self.settings.algorithm]
            )
            return payload
        except JWTError:
            return None

    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare against

        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )


# Global security manager instance
security_manager = SecurityManager()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Token payload data
        expires_delta: Custom expiration time delta

    Returns:
        str: Encoded JWT token
    """
    return security_manager.create_access_token(data, expires_delta)


def verify_token(token: str) -> dict | None:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token to verify

    Returns:
        dict: Decoded token payload or None if invalid
    """
    return security_manager.verify_token(token)


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return security_manager.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    return security_manager.verify_password(plain_password, hashed_password)
