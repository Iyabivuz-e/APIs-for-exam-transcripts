"""
User Model

This module defines the User database model for the exam transcripts system.
Users can have roles (admin, supervisor, user) and can be associated with multiple exams.
"""

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.core.permissions import UserRole
from app.db.base import Base


class User(Base):
    """
    User database model.

    Represents a user in the exam transcripts system with authentication
    and role-based access control capabilities.

    Attributes:
        email: User's unique email address (used for authentication)
        hashed_password: Bcrypt hashed password
        role: User's role (admin, supervisor, or user)
        user_exams: Relationship to user's exam records
    """

    # User authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # User role for access control
    role = Column(String(20), default=UserRole.USER.value, nullable=False)

    # Relationships
    user_exams = relationship(
        "UserExam", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def user_role(self) -> UserRole:
        """Get role as UserRole enum."""
        return UserRole(self.role)

    @user_role.setter
    def user_role(self, role: UserRole) -> None:
        """Set role from UserRole enum."""
        self.role = role.value

    def __repr__(self) -> str:
        """
        String representation of the user.

        Returns:
            str: User representation with email and role
        """
        return f"<User(email='{self.email}', role='{self.role}')>"

    @property
    def is_admin(self) -> bool:
        """
        Check if user has admin role.

        Returns:
            bool: True if user is admin, False otherwise
        """
        return self.role == UserRole.ADMIN.value

    @property
    def is_supervisor(self) -> bool:
        """
        Check if user has supervisor role.

        Returns:
            bool: True if user is supervisor, False otherwise
        """
        return self.role == UserRole.SUPERVISOR.value

    @property
    def is_user(self) -> bool:
        """
        Check if user has regular user role.

        Returns:
            bool: True if user is regular user, False otherwise
        """
        return self.role == UserRole.USER.value

    def can_create_exams(self) -> bool:
        """
        Check if user can create exams.

        Returns:
            bool: True if user can create exams (admin only)
        """
        return self.is_admin

    def can_grade_exams(self) -> bool:
        """
        Check if user can grade exams.

        Returns:
            bool: True if user can grade exams (supervisor only)
        """
        return self.is_supervisor
