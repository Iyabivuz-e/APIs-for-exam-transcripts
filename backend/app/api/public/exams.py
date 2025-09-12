"""
Public Exams API Routes Module

This module contains public API endpoints for viewing exams.
These endpoints do not require authentication and allow filtering and sorting.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import CommonQueryParams, get_db, get_pagination_params
from app.repositories.exam_repository import ExamRepository
from app.schemas.exam import Exam

router = APIRouter()


@router.get("/exams", response_model=dict)
async def get_public_exams(
    title: str | None = Query(None, description="Filter by exam title (partial match)"),
    date_from: date | None = Query(None, description="Filter exams from this date"),
    date_to: date | None = Query(None, description="Filter exams until this date"),
    sort_by: str = Query("date", description="Sort field (date, title, created_at)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)"),
    pagination: CommonQueryParams = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    """
    Get list of available exams (public endpoint).

    This endpoint allows anyone to view the list of available exams
    with filtering by title and date, plus sorting capabilities.

    Args:
        title: Optional title filter (partial match)
        date_from: Optional start date filter
        date_to: Optional end date filter
        sort_by: Field to sort by
        sort_order: Sort order (ascending or descending)
        pagination: Pagination parameters
        db: Database session

    Returns:
        dict: List of exams with pagination metadata
    """
    exam_repo = ExamRepository(db)

    # Validate sort parameters
    valid_sort_fields = ["date", "title", "created_at", "updated_at"]
    if sort_by not in valid_sort_fields:
        sort_by = "date"

    if sort_order.lower() not in ["asc", "desc"]:
        sort_order = "asc"

    # Get exams with filtering and pagination
    exams = await exam_repo.get_all(
        skip=pagination.offset,
        limit=pagination.limit,
        title_filter=title,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # Get total count for pagination
    total_count = await exam_repo.count(
        title_filter=title, date_from=date_from, date_to=date_to
    )

    # Calculate pagination metadata
    total_pages = (total_count + pagination.page_size - 1) // pagination.page_size

    # Convert to schema
    exam_list = [Exam.from_orm(exam) for exam in exams]

    return {
        "exams": exam_list,
        "pagination": {
            "total": total_count,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total_pages": total_pages,
        },
        "filters": {
            "title": title,
            "date_from": date_from,
            "date_to": date_to,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
    }


@router.get("/exams/{exam_id}", response_model=dict)
async def get_public_exam_details(exam_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific exam (public endpoint).

    Args:
        exam_id: ID of the exam to retrieve
        db: Database session

    Returns:
        dict: Exam details with basic statistics

    Raises:
        HTTPException: If exam is not found
    """
    from fastapi import HTTPException, status

    exam_repo = ExamRepository(db)

    # Get exam
    exam = await exam_repo.get_by_id(exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Get basic statistics (public safe)
    stats = await exam_repo.get_exam_statistics(exam_id)

    return {
        "exam": Exam.from_orm(exam),
        "statistics": {
            "total_participants": stats["user_count"],
            "completion_rate": round(
                (
                    (stats["graded_count"] / stats["user_count"] * 100)
                    if stats["user_count"] > 0
                    else 0
                ),
                2,
            ),
            # Note: Not showing average_vote in public API for privacy
        },
    }
