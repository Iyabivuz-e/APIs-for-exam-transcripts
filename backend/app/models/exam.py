"""
Exam Model

This module defines the Exam database model for the exam transcripts system.
Exams can be associated with multiple users through the UserExam association table.
"""

from sqlalchemy import Column, Date, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Exam(Base):
    """
    Exam database model.

    Represents an exam in the system with title and date information.
    Exams can be assigned to multiple users with individual votes/grades.

    Attributes:
        title: Exam title/name (must be unique)
        date: Date when the exam was/will be conducted
        user_exams: Relationship to user exam records (with votes)
    """

    # Exam identification fields
    title = Column(String(255), unique=True, index=True, nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Relationships
    user_exams = relationship(
        "UserExam", back_populates="exam", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """
        String representation of the exam.

        Returns:
            str: Exam representation with title and date
        """
        return f"<Exam(title='{self.title}', date='{self.date}')>"

    @property
    def formatted_date(self) -> str:
        """
        Get formatted date string.

        Returns:
            str: Date formatted as YYYY-MM-DD
        """
        return self.date.strftime("%Y-%m-%d") if self.date else ""

    def get_user_count(self) -> int:
        """
        Get number of users assigned to this exam.

        Returns:
            int: Number of users with this exam
        """
        return len(self.user_exams)

    def get_average_vote(self) -> float:
        """
        Calculate average vote for this exam.

        Returns:
            float: Average vote or 0.0 if no votes
        """
        votes = [ue.vote for ue in self.user_exams if ue.vote is not None]
        return sum(votes) / len(votes) if votes else 0.0

    def has_user(self, user_id: int) -> bool:
        """
        Check if a specific user is assigned to this exam.

        Args:
            user_id: ID of the user to check

        Returns:
            bool: True if user is assigned to this exam
        """
        return any(ue.user_id == user_id for ue in self.user_exams)
