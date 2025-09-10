"""
Base Schemas Module

This module contains base Pydantic schemas and common response models
used throughout the application for request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base Pydantic schema with common configuration.

    All schemas should inherit from this base class to ensure
    consistent configuration across the application.
    """

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy models
        validate_assignment=True,  # Validate on assignment
        arbitrary_types_allowed=True,  # Allow arbitrary types
        str_strip_whitespace=True,  # Strip whitespace from strings
    )


class TimestampMixin(BaseModel):
    """
    Mixin for schemas that include timestamp fields.

    Provides common timestamp fields for created_at and updated_at.
    """

    created_at: datetime
    updated_at: datetime


class BaseResponse(BaseSchema):
    """
    Base response schema for API responses.

    Provides common fields for API responses including
    success status and optional message.
    """

    success: bool = True
    message: str | None = None


class ErrorResponse(BaseSchema):
    """
    Error response schema for API error responses.

    Provides consistent error response format with
    error flag, message, and optional details.
    """

    error: bool = True
    message: str
    status_code: int
    detail: str | None = None


class PaginationParams(BaseSchema):
    """
    Pagination parameters schema.

    Used for paginated endpoints to specify page number and size.
    """

    page: int = 1
    page_size: int = 10

    def get_offset(self) -> int:
        """
        Calculate offset for database queries.

        Returns:
            int: Offset value for database pagination
        """
        return (self.page - 1) * self.page_size

    def get_limit(self) -> int:
        """
        Get limit for database queries.

        Returns:
            int: Limit value for database pagination
        """
        return self.page_size


class PaginatedResponse(BaseResponse):
    """
    Paginated response schema for list endpoints.

    Provides metadata about pagination along with the data.
    """

    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        data: list,
        total: int,
        page: int,
        page_size: int,
        message: str | None = None,
    ):
        """
        Create paginated response with calculated metadata.

        Args:
            data: List of items for current page
            total: Total number of items
            page: Current page number
            page_size: Number of items per page
            message: Optional success message

        Returns:
            PaginatedResponse: Response with pagination metadata
        """
        total_pages = (total + page_size - 1) // page_size  # Ceiling division

        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            message=message,
        )
