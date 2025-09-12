"""
User API Routes Module

This module contains user API endpoints for viewing personal exam data.
Requires authentication for access.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.repositories.exam_repository import ExamRepository
from app.schemas.exam import UserExamResponse

router = APIRouter()


@router.post("/exams/{exam_id}/register", response_model=dict)
async def register_for_exam(
    exam_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Register current user for an exam.

    Enforces business rule: "An user can have more than one exam,
    but not the same exam multiple times"

    Args:
        exam_id: ID of the exam to register for
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: Registration confirmation

    Raises:
        HTTPException: If exam not found or user already registered
    """
    exam_repo = ExamRepository(db)

    # Verify exam exists
    exam = await exam_repo.get_by_id(exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Register user for exam (respects unique constraint)
    user_exam = await exam_repo.assign_exam_to_user(current_user.id, exam_id)

    if not user_exam:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already registered for this exam",
        )

    return {
        "success": True,
        "message": f"Successfully registered for exam '{exam.title}'",
        "registration": {
            "exam_id": exam.id,
            "exam_title": exam.title,
            "exam_date": exam.date.isoformat(),
            "status": "registered",
        },
    }


@router.get("/me/exams", response_model=dict)
async def get_my_exams(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """
    Get current user's exam assignments and grades.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        dict: User's exam information with grades and statistics
    """
    exam_repo = ExamRepository(db)

    # Get user's exams
    user_exams = await exam_repo.get_user_exams(current_user.id)

    # Convert to response format
    exam_responses = []
    for user_exam in user_exams:
        exam_responses.append(
            UserExamResponse(
                exam_id=user_exam.exam.id,
                exam_title=user_exam.exam.title,
                exam_date=user_exam.exam.date,
                vote=user_exam.vote,
                is_graded=user_exam.is_graded,
                grade_status=user_exam.grade_status,
                letter_grade=user_exam.get_letter_grade(),
            )
        )

    # Calculate statistics
    total_exams = len(exam_responses)
    graded_exams = [er for er in exam_responses if er.is_graded]
    graded_count = len(graded_exams)
    pending_count = total_exams - graded_count

    average_grade = 0.0
    if graded_exams:
        average_grade = sum(er.vote for er in graded_exams) / graded_count

    return {
        "exams": exam_responses,
        "statistics": {
            "total_exams": total_exams,
            "graded_exams": graded_count,
            "pending_exams": pending_count,
            "average_grade": round(average_grade, 2) if average_grade else None,
            "completion_rate": round(
                (graded_count / total_exams * 100) if total_exams > 0 else 0, 2
            ),
        },
    }
