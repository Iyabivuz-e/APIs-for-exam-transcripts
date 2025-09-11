"""
Authentication Schemas Module

This module contains Pydantic schemas for authentication-related operations
including login requests, token responses, and user registration.
"""

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema
from app.schemas.user import User


class LoginRequest(BaseSchema):
    """
    Schema for user login requests.

    Used for user authentication with email and password.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenResponse(BaseSchema):
    """
    Schema for authentication token responses.

    Returned after successful login with access token and user information.
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(
        default="bearer", description="Token type (always 'bearer')"
    )
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: User = Field(..., description="Authenticated user information")


class TokenData(BaseSchema):
    """
    Schema for JWT token payload data.

    Used internally for token validation and user identification.
    """

    sub: str = Field(..., description="Subject (user email)")
    user_id: str = Field(..., description="User ID (UUID)")
    role: str = Field(..., description="User role")
    exp: int | None = Field(None, description="Expiration timestamp")


class RefreshTokenRequest(BaseSchema):
    """
    Schema for token refresh requests.

    Used when requesting a new access token using a refresh token.
    """

    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseSchema):
    """
    Schema for password reset requests.

    Used when user requests password reset via email.
    """

    email: EmailStr = Field(..., description="User's email address")


class PasswordResetConfirm(BaseSchema):
    """
    Schema for password reset confirmation.

    Used when user confirms password reset with token and new password.
    """

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, description="New password (min 8 characters)"
    )


class ChangePasswordRequest(BaseSchema):
    """
    Schema for password change requests.

    Used when authenticated user wants to change their password.
    """

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, description="New password (min 8 characters)"
    )


class AuthResponse(BaseSchema):
    """
    Generic authentication response schema.

    Used for responses that only need to indicate success/failure with a message.
    """

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")


class UserRegistration(BaseSchema):
    """
    Schema for user registration requests.

    Extended version of user creation for public registration endpoints.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ..., min_length=8, description="User's password (min 8 characters)"
    )
    confirm_password: str = Field(..., description="Password confirmation")

    def validate_passwords_match(self):
        """
        Validate that password and confirm_password match.

        Raises:
            ValueError: If passwords don't match
        """
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
