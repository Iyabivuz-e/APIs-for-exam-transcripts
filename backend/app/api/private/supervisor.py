"""
Supervisor API Routes Module

This module contains supervisor-only API endpoints for grading exams.
Requires supervisor role for access.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_supervisor_user, get_db
from app.models.user import User
from app.models.user_exam import UserExam
from app.repositories.exam_repository import ExamRepository
from app.schemas.exam import VoteAssignment

router = APIRouter()


@router.get("/ungraded-assignments", response_model=dict)
async def get_ungraded_assignments(
    current_user: User = Depends(get_current_supervisor_user),
    db: Session = Depends(get_db),
):
    """
    Get all ungraded exam assignments for vote assignment (Supervisor only).

    Args:
        current_user: Current supervisor user
        db: Database session

    Returns:
        dict: List of ungraded assignments with user and exam details

    Raises:
        HTTPException: If access denied
    """
    # Get all ungraded user exam assignments
    ungraded_assignments = (
        db.query(UserExam)
        .filter(UserExam.vote.is_(None))
        .options(joinedload(UserExam.user), joinedload(UserExam.exam))
        .all()
    )

    assignments_data = []
    for assignment in ungraded_assignments:
        assignments_data.append(
            {
                "user_id": assignment.user_id,
                "user_email": assignment.user.email,
                "user_full_name": assignment.user.email,  # Use email as display name since no first/last name
                "exam_id": assignment.exam_id,
                "exam_title": assignment.exam.title,
                "exam_date": assignment.exam.date.isoformat(),
            }
        )

    return {
        "success": True,
        "assignments": assignments_data,
        "total": len(assignments_data),
    }


@router.put("/exams/{exam_id}/vote", response_model=dict)
async def assign_vote_to_exam(
    exam_id: str,
    vote_data: VoteAssignment,
    current_user: User = Depends(get_current_supervisor_user),
    db: Session = Depends(get_db),
):
    """
    Assign a vote to a user's exam (Supervisor only).

    Args:
        exam_id: ID of the exam to grade
        vote_data: Vote assignment data (user_id and vote)
        current_user: Current supervisor user
        db: Database session

    Returns:
        dict: Vote assignment confirmation

    Raises:
        HTTPException: If exam or user not found, or assignment doesn't exist
    """
    exam_repo = ExamRepository(db)

    # Verify exam exists
    exam = await exam_repo.get_by_id(exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Assign vote to user exam
    user_exam = await exam_repo.assign_vote(
        user_id=vote_data.user_id, exam_id=exam_id, vote=vote_data.vote
    )

    if not user_exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User exam assignment not found",
        )

    return {
        "success": True,
        "message": f"Vote {vote_data.vote} assigned successfully",
        "assignment": {
            "user_id": user_exam.user_id,
            "exam_id": user_exam.exam_id,
            "vote": user_exam.vote,
            "letter_grade": user_exam.get_letter_grade(),
        },
    }
