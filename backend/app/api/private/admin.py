from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.permissions import require_admin
from app.models.user import User as UserModel
from app.repositories.exam_repository import ExamRepository
from app.repositories.user_repository import UserRepository
from app.schemas.exam import Exam, ExamCreate
from app.schemas.user import User
from app.schemas.user import User as UserResponse

router = APIRouter()


@router.post("/exams", response_model=Exam)
async def create_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create a new exam - only admin can do this"""
    require_admin(current_user.role)

    exam_repo = ExamRepository(db)

    return await exam_repo.create(exam_data.title, exam_data.date)


@router.delete("/exams/{exam_id}")
async def delete_exam(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Delete an exam - only admin can do this"""
    require_admin(current_user.role)

    exam_repo = ExamRepository(db)

    # Check if exam exists
    exam = await exam_repo.get_by_id(exam_id)
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
        )

    # Delete the exam
    await exam_repo.delete(exam_id)

    return {"message": "Exam deleted successfully"}


@router.get("/users", response_model=List[User])
async def get_users(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    """Get all users (Admin and Supervisor access)"""
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user_repo = UserRepository(db)
    all_users = await user_repo.get_all()

    # For supervisors, only return users with "user" role
    if current_user.role == "supervisor":
        return [user for user in all_users if user.role == "user"]

    # For admins, return all users
    return all_users
