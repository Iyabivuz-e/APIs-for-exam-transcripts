"""
User Schemas Module

This module contains Pydantic schemas for user-related operations
including registration, authentication, and user management.
"""

from pydantic import EmailStr, Field, validator

from app.core.permissions import UserRole
from app.schemas.base import BaseSchema, TimestampMixin


class UserBase(BaseSchema):
    """
    Base user schema with common user fields.

    Contains fields that are shared across different user schemas.
    """

    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """
    Schema for user creation requests.

    Used when creating new users, includes password and optional role.
    """

    password: str = Field(
        ..., min_length=8, description="User's password (min 8 characters)"
    )
    role: UserRole | None = Field(default=UserRole.USER, description="User's role")

    @validator("password")
    def validate_password(cls, v):
        """
        Validate password strength.

        Args:
            v: Password value

        Returns:
            str: Validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one number
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")

        # Check for at least one letter
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")

        return v


class UserLogin(BaseSchema):
    """
    Schema for user login requests.

    Used for authentication with email and password.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserUpdate(BaseSchema):
    """
    Schema for user update requests.

    Allows updating user information with optional fields.
    """

    email: EmailStr | None = Field(None, description="New email address")
    password: str | None = Field(None, min_length=8, description="New password")
    role: UserRole | None = Field(None, description="New role")

    @validator("password")
    def validate_password(cls, v):
        """
        Validate password strength if provided.

        Args:
            v: Password value

        Returns:
            str: Validated password or None
        """
        if v is None:
            return v

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")

        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")

        return v


class User(UserBase, TimestampMixin):
    """
    Schema for user responses.

    Used when returning user information in API responses.
    Excludes sensitive information like password.
    """

    id: str = Field(..., description="User's unique identifier (UUID)")
    role: UserRole = Field(..., description="User's role")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class UserProfile(User):
    """
    Extended user schema with additional profile information.

    Includes computed fields and additional user statistics.
    """

    is_admin: bool = Field(..., description="Whether user is an admin")
    is_supervisor: bool = Field(..., description="Whether user is a supervisor")
    is_user: bool = Field(..., description="Whether user is a regular user")


class UserWithExams(User):
    """
    User schema that includes exam information.

    Used when returning user data with their associated exams.
    """

    exam_count: int = Field(..., description="Number of exams assigned to user")
    graded_exams: int = Field(..., description="Number of graded exams")
    pending_exams: int = Field(..., description="Number of pending exams")
    average_grade: float | None = Field(
        None, description="Average grade across all exams"
    )


class UserListResponse(BaseSchema):
    """
    Schema for user list responses.

    Contains list of users with pagination metadata.
    """

    users: list[User] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of users per page")
    total_pages: int = Field(..., description="Total number of pages")
