"""
Exam Repository Module

This module contains the repository class for exam-related database operations.
Implements the repository pattern for data access abstraction.
"""

from datetime import date
from typing import Optional, List

from sqlalchemy import and_, asc, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.exceptions import DatabaseError, ValidationError
from app.core.logging import get_logger, get_correlation_id
from app.models.exam import Exam
from app.models.user_exam import UserExam

logger = get_logger(__name__)


class ExamRepository:
    """
    Repository for exam-related database operations.

    Provides methods for CRUD operations and exam-specific queries.
    """

    def __init__(self, db: Session):
        """
        Initialize exam repository.

        Args:
            db: Database session
        """
        self.db = db

    async def create(self, title: str, exam_date: date) -> Exam:
        """
        Create a new exam.

        Args:
            title: Exam title
            exam_date: Date of the exam

        Returns:
            Exam: Created exam instance
            
        Raises:
            ValidationError: If exam data validation fails
            DatabaseError: If database operation fails
        """
        correlation_id = get_correlation_id()
        
        try:
            logger.info(
                "Creating new exam",
                extra={
                    "correlation_id": correlation_id,
                    "title": title,
                    "exam_date": exam_date.isoformat()
                }
            )
            
            exam = Exam(title=title, date=exam_date)
            
            self.db.add(exam)
            self.db.commit()
            self.db.refresh(exam)
            
            logger.info(
                "Exam created successfully",
                extra={
                    "correlation_id": correlation_id,
                    "exam_id": exam.id,
                    "title": title
                }
            )
            
            return exam
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                "Exam creation failed - integrity constraint violation",
                extra={
                    "correlation_id": correlation_id,
                    "title": title,
                    "error": str(e.orig)
                }
            )
            raise ValidationError(f"Exam creation failed due to data constraints")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                "Exam creation failed - database error",
                extra={
                    "correlation_id": correlation_id,
                    "title": title,
                    "error": str(e)
                }
            )
            raise DatabaseError("Failed to create exam") from e
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "Exam creation failed - unexpected error",
                extra={
                    "correlation_id": correlation_id,
                    "title": title,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise DatabaseError("Unexpected error during exam creation") from e

    async def get_by_id(self, exam_id: str) -> Optional[Exam]:
        """
        Get exam by ID.

        Args:
            exam_id: Exam's ID (UUID string)

        Returns:
            Exam or None: Exam if found, None otherwise
            
        Raises:
            DatabaseError: If database query fails
        """
        correlation_id = get_correlation_id()
        
        try:
            logger.debug(
                "Fetching exam by ID",
                extra={
                    "correlation_id": correlation_id,
                    "exam_id": exam_id
                }
            )
            
            exam = self.db.query(Exam).filter(Exam.id == exam_id).first()
            
            if exam:
                logger.debug(
                    "Exam found by ID",
                    extra={
                        "correlation_id": correlation_id,
                        "exam_id": exam_id,
                        "title": exam.title
                    }
                )
            else:
                logger.debug(
                    "Exam not found by ID",
                    extra={
                        "correlation_id": correlation_id,
                        "exam_id": exam_id
                    }
                )
            
            return exam
            
        except SQLAlchemyError as e:
            logger.error(
                "Failed to fetch exam by ID",
                extra={
                    "correlation_id": correlation_id,
                    "exam_id": exam_id,
                    "error": str(e)
                }
            )
            raise DatabaseError("Failed to retrieve exam") from e

    async def get_by_title(self, title: str) -> Exam | None:
        """
        Get exam by title.

        Args:
            title: Exam title

        Returns:
            Exam or None: Exam if found, None otherwise
        """
        return self.db.query(Exam).filter(Exam.title == title).first()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        title_filter: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "date",
        sort_order: str = "asc",
    ) -> list[Exam]:
        """
        Get all exams with optional filtering, sorting, and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            title_filter: Optional title to filter by (partial match)
            date_from: Optional start date filter
            date_to: Optional end date filter
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)

        Returns:
            List[Exam]: List of exams
        """
        query = self.db.query(Exam)

        # Apply filters
        if title_filter:
            query = query.filter(Exam.title.ilike(f"%{title_filter}%"))

        if date_from:
            query = query.filter(Exam.date >= date_from)

        if date_to:
            query = query.filter(Exam.date <= date_to)

        # Apply sorting
        sort_column = getattr(Exam, sort_by, Exam.date)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        return query.offset(skip).limit(limit).all()

    async def update(
        self,
        exam_id: str,
        title: str | None = None,
        exam_date: date | None = None,
    ) -> Exam | None:
        """
        Update exam information.

        Args:
            exam_id: Exam's ID (UUID string)
            title: New title
            exam_date: New date

        Returns:
            Exam or None: Updated exam if found, None otherwise
        """
        exam = await self.get_by_id(exam_id)
        if not exam:
            return None

        if title is not None:
            exam.title = title

        if exam_date is not None:
            exam.date = exam_date

        self.db.commit()
        self.db.refresh(exam)

        return exam

    async def delete(self, exam_id: str) -> bool:
        """
        Delete exam by ID.

        Args:
            exam_id: Exam's ID (UUID string)

        Returns:
            bool: True if exam was deleted, False if not found
        """
        exam = await self.get_by_id(exam_id)
        if not exam:
            return False

        self.db.delete(exam)
        self.db.commit()

        return True

    async def exists_by_title(self, title: str) -> bool:
        """
        Check if exam exists by title.

        Args:
            title: Title to check

        Returns:
            bool: True if exam exists, False otherwise
        """
        exam = await self.get_by_title(title)
        return exam is not None

    async def count(
        self,
        title_filter: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        """
        Count total number of exams with optional filtering.

        Args:
            title_filter: Optional title to filter by
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            int: Total number of exams
        """
        query = self.db.query(Exam)

        if title_filter:
            query = query.filter(Exam.title.ilike(f"%{title_filter}%"))

        if date_from:
            query = query.filter(Exam.date >= date_from)

        if date_to:
            query = query.filter(Exam.date <= date_to)

        return query.count()

    async def get_user_exams(self, user_id: str) -> list[UserExam]:
        """
        Get all exams for a specific user.

        Args:
            user_id: User's ID (UUID string)

        Returns:
            List[UserExam]: List of user exam associations
        """
        return (
            self.db.query(UserExam)
            .filter(UserExam.user_id == user_id)
            .options(joinedload(UserExam.exam))
            .all()
        )

    async def assign_exam_to_user(self, user_id: str, exam_id: str) -> UserExam | None:
        """
        Assign an exam to a user.

        Args:
            user_id: User's ID (UUID string)
            exam_id: Exam's ID (UUID string)

        Returns:
            UserExam or None: Created association if successful, None if already exists
        """
        # Check if association already exists
        existing = (
            self.db.query(UserExam)
            .filter(and_(UserExam.user_id == user_id, UserExam.exam_id == exam_id))
            .first()
        )

        if existing:
            return None  # User already has this exam

        user_exam = UserExam(user_id=user_id, exam_id=exam_id)

        self.db.add(user_exam)
        self.db.commit()
        self.db.refresh(user_exam)

        return user_exam

    async def assign_vote(
        self, user_id: str, exam_id: str, vote: float
    ) -> UserExam | None:
        """
        Assign a vote to a user's exam.

        Args:
            user_id: User's ID (UUID string)
            exam_id: Exam's ID (UUID string)
            vote: Vote/grade to assign

        Returns:
            UserExam or None: Updated association if found, None otherwise
        """
        user_exam = (
            self.db.query(UserExam)
            .filter(and_(UserExam.user_id == user_id, UserExam.exam_id == exam_id))
            .first()
        )

        if not user_exam:
            return None

        user_exam.vote = vote

        self.db.commit()
        self.db.refresh(user_exam)

        return user_exam

    async def get_exam_statistics(self, exam_id: str) -> dict:
        """
        Get statistics for a specific exam.

        Args:
            exam_id: Exam's ID (UUID string)

        Returns:
            dict: Dictionary containing exam statistics
        """
        user_exams = self.db.query(UserExam).filter(UserExam.exam_id == exam_id).all()

        total_users = len(user_exams)
        graded_exams = [ue for ue in user_exams if ue.vote is not None]
        graded_count = len(graded_exams)
        pending_count = total_users - graded_count

        average_vote = 0.0
        if graded_exams:
            average_vote = sum(ue.vote for ue in graded_exams) / graded_count

        return {
            "user_count": total_users,
            "graded_count": graded_count,
            "pending_count": pending_count,
            "average_vote": round(average_vote, 2),
        }
