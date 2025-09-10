"""
User-Exam Association Model

This module defines the UserExam association model that links users to exams
with vote/grade information. This model handles the many-to-many relationship
between users and exams while storing the vote for each user-exam combination.
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserExam(Base):
    """
    User-Exam association model.

    This model represents the relationship between a user and an exam,
    including the vote/grade assigned by a supervisor. It enforces the
    business rule that a user cannot have the same exam multiple times.

    Attributes:
        user_id: Foreign key to User model
        exam_id: Foreign key to Exam model
        vote: Numerical vote/grade for the exam (can be null if not graded yet)
        user: Relationship to User model
        exam: Relationship to Exam model
    """

    # Foreign key relationships
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    exam_id = Column(
        Integer, ForeignKey("exam.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Vote/grade for this user-exam combination
    vote = Column(Float, nullable=True)  # Null means not graded yet

    # Relationships
    user = relationship("User", back_populates="user_exams")
    exam = relationship("Exam", back_populates="user_exams")

    # Composite unique constraint to prevent duplicate user-exam combinations
    __table_args__ = (
        UniqueConstraint('user_id', 'exam_id', name='uq_user_exam'),
        {"sqlite_autoincrement": True}
    )

    def __repr__(self) -> str:
        """
        String representation of the user-exam association.

        Returns:
            str: UserExam representation with user_id, exam_id, and vote
        """
        return f"<UserExam(user_id={self.user_id}, exam_id={self.exam_id}, vote={self.vote})>"

    @property
    def is_graded(self) -> bool:
        """
        Check if this exam has been graded for the user.

        Returns:
            bool: True if vote is assigned, False otherwise
        """
        return self.vote is not None

    @property
    def grade_status(self) -> str:
        """
        Get human-readable grade status.

        Returns:
            str: "Graded" if vote is assigned, "Pending" otherwise
        """
        return "Graded" if self.is_graded else "Pending"

    def set_vote(self, vote: float) -> None:
        """
        Set the vote for this user-exam combination.

        Args:
            vote: Numerical vote to assign

        Raises:
            ValueError: If vote is not within valid range (0-100)
        """
        if not (0 <= vote <= 100):
            raise ValueError("Vote must be between 0 and 100")
        self.vote = vote

    def clear_vote(self) -> None:
        """
        Clear the vote for this user-exam combination.
        """
        self.vote = None

    def get_letter_grade(self) -> str:
        """
        Convert numerical vote to letter grade.

        Returns:
            str: Letter grade (A, B, C, D, F) or "N/A" if not graded
        """
        if not self.is_graded:
            return "N/A"

        if self.vote >= 90:
            return "A"
        elif self.vote >= 80:
            return "B"
        elif self.vote >= 70:
            return "C"
        elif self.vote >= 60:
            return "D"
        else:
            return "F"
