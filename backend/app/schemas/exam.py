"""
Exam Schemas Module

This module contains Pydantic schemas for exam-related operations
including exam creation, updates, and response models.
"""

from datetime import date as date_type

from pydantic import Field, validator

from app.schemas.base import BaseSchema, TimestampMixin


class ExamBase(BaseSchema):
    """
    Base exam schema with common exam fields.

    Contains fields that are shared across different exam schemas.
    """

    title: str = Field(..., min_length=1, max_length=255, description="Exam title")
    date: date_type = Field(..., description="Exam date")


class ExamCreate(ExamBase):
    """
    Schema for exam creation requests.

    Used when creating new exams, includes validation for business rules.
    """

    @validator("title")
    def validate_title(cls, v):
        """
        Validate exam title.

        Args:
            v: Title value

        Returns:
            str: Validated title

        Raises:
            ValueError: If title is invalid
        """
        if not v or not v.strip():
            raise ValueError("Exam title cannot be empty")

        # Remove extra whitespace
        title = " ".join(v.split())

        if len(title) < 3:
            raise ValueError("Exam title must be at least 3 characters long")

        return title

    @validator("date")
    def validate_date(cls, v):
        """
        Validate exam date.

        Args:
            v: Date value

        Returns:
            date: Validated date

        Raises:
            ValueError: If date is invalid
        """
        from datetime import date as date_cls

        if v < date_cls.today():
            raise ValueError("Exam date cannot be in the past")

        return v


class ExamUpdate(BaseSchema):
    """
    Schema for exam update requests.

    Allows updating exam information with optional fields.
    """

    title: str | None = Field(
        None, min_length=1, max_length=255, description="New exam title"
    )
    date: date_type | None = Field(None, description="New exam date")

    @validator("title")
    def validate_title(cls, v):
        """
        Validate exam title if provided.

        Args:
            v: Title value

        Returns:
            str: Validated title or None
        """
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Exam title cannot be empty")

        title = " ".join(v.split())

        if len(title) < 3:
            raise ValueError("Exam title must be at least 3 characters long")

        return title


class Exam(ExamBase, TimestampMixin):
    """
    Schema for exam responses.

    Used when returning exam information in API responses.
    """

    id: str = Field(..., description="Exam's unique identifier (UUID)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ExamWithStats(Exam):
    """
    Extended exam schema with statistics.

    Includes computed fields like user count and average vote.
    """

    user_count: int = Field(..., description="Number of users assigned to this exam")
    average_vote: float = Field(..., description="Average vote for this exam")
    graded_count: int = Field(..., description="Number of graded submissions")
    pending_count: int = Field(..., description="Number of pending submissions")


class ExamListResponse(BaseSchema):
    """
    Schema for exam list responses.

    Contains list of exams with pagination and filtering metadata.
    """

    exams: list[Exam] = Field(..., description="List of exams")
    total: int = Field(..., description="Total number of exams")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of exams per page")
    total_pages: int = Field(..., description="Total number of pages")


class ExamFilterParams(BaseSchema):
    """
    Schema for exam filtering parameters.

    Used for filtering and sorting exam lists.
    """

    title: str | None = Field(None, description="Filter by exam title (partial match)")
    date_from: date_type | None = Field(None, description="Filter exams from this date")
    date_to: date_type | None = Field(None, description="Filter exams until this date")
    sort_by: str | None = Field(
        "date", description="Sort field (date, title, created_at)"
    )
    sort_order: str | None = Field("asc", description="Sort order (asc, desc)")

    @validator("sort_by")
    def validate_sort_by(cls, v):
        """
        Validate sort field.

        Args:
            v: Sort field value

        Returns:
            str: Validated sort field
        """
        allowed_fields = ["date", "title", "created_at", "updated_at"]
        if v not in allowed_fields:
            raise ValueError(f"Sort field must be one of: {allowed_fields}")
        return v

    @validator("sort_order")
    def validate_sort_order(cls, v):
        """
        Validate sort order.

        Args:
            v: Sort order value

        Returns:
            str: Validated sort order
        """
        allowed_orders = ["asc", "desc"]
        if v.lower() not in allowed_orders:
            raise ValueError(f"Sort order must be one of: {allowed_orders}")
        return v.lower()


class UserExamResponse(BaseSchema):
    """
    Schema for user-exam association responses.

    Used when returning exam information for a specific user.
    """

    exam_id: str = Field(..., description="Exam ID (UUID)")
    exam_title: str = Field(..., description="Exam title")
    exam_date: date_type = Field(..., description="Exam date")
    vote: float | None = Field(None, description="User's vote for this exam")
    is_graded: bool = Field(..., description="Whether the exam has been graded")
    grade_status: str = Field(..., description="Grade status (Graded/Pending)")
    letter_grade: str = Field(..., description="Letter grade (A, B, C, D, F, N/A)")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class VoteAssignment(BaseSchema):
    """
    Schema for vote assignment requests.

    Used by supervisors to assign votes to user exams.
    """

    user_id: str = Field(..., description="ID of the user to assign vote to (UUID)")
    exam_id: str = Field(..., description="ID of the exam to assign vote for (UUID)")
    vote: float = Field(..., ge=0, le=100, description="Vote/grade (0-100)")

    @validator("vote")
    def validate_vote(cls, v):
        """
        Validate vote value.

        Args:
            v: Vote value

        Returns:
            float: Validated vote
        """
        if not (0 <= v <= 100):
            raise ValueError("Vote must be between 0 and 100")
        return round(v, 2)  # Round to 2 decimal places
