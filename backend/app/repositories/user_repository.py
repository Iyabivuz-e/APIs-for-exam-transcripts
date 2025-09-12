"""
User Repository Module

This module contains the repository class for user-related database operations.
Implements the repository pattern for data access abstraction.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.permissions import UserRole
from app.core.security import hash_password
from app.core.exceptions import DatabaseError, ValidationError
from app.core.logging import get_logger, get_correlation_id
from app.models.user import User

logger = get_logger(__name__)


class UserRepository:
    """
    Repository for user-related database operations.

    Provides methods for CRUD operations and user-specific queries.
    """

    def __init__(self, db: Session):
        """
        Initialize user repository.

        Args:
            db: Database session
        """
        self.db = db

    async def create(
        self, email: str, password: str, role: UserRole = UserRole.USER
    ) -> User:
        """
        Create a new user.

        Args:
            email: User's email address
            password: Plain text password (will be hashed)
            role: User's role

        Returns:
            User: Created user instance
            
        Raises:
            ValidationError: If user data validation fails
            DatabaseError: If database operation fails
        """
        correlation_id = get_correlation_id()
        
        try:
            logger.info(
                "Creating new user",
                extra={
                    "correlation_id": correlation_id,
                    "email": email,
                    "role": role.value
                }
            )
            
            hashed_password = hash_password(password)
            user = User(email=email, hashed_password=hashed_password, role=role)
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(
                "User created successfully",
                extra={
                    "correlation_id": correlation_id,
                    "user_id": user.id,
                    "email": email
                }
            )
            
            return user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(
                "User creation failed - integrity constraint violation",
                extra={
                    "correlation_id": correlation_id,
                    "email": email,
                    "error": str(e.orig)
                }
            )
            raise ValidationError(f"User with email {email} already exists")
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(
                "User creation failed - database error",
                extra={
                    "correlation_id": correlation_id,
                    "email": email,
                    "error": str(e)
                }
            )
            raise DatabaseError("Failed to create user") from e
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "User creation failed - unexpected error",
                extra={
                    "correlation_id": correlation_id,
                    "email": email,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise DatabaseError("Unexpected error during user creation") from e

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's ID (UUID string)

        Returns:
            User or None: User if found, None otherwise
            
        Raises:
            DatabaseError: If database query fails
        """
        correlation_id = get_correlation_id()
        
        try:
            logger.debug(
                "Fetching user by ID",
                extra={
                    "correlation_id": correlation_id,
                    "user_id": user_id
                }
            )
            
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if user:
                logger.debug(
                    "User found by ID",
                    extra={
                        "correlation_id": correlation_id,
                        "user_id": user_id,
                        "email": user.email
                    }
                )
            else:
                logger.debug(
                    "User not found by ID",
                    extra={
                        "correlation_id": correlation_id,
                        "user_id": user_id
                    }
                )
            
            return user
            
        except SQLAlchemyError as e:
            logger.error(
                "Failed to fetch user by ID",
                extra={
                    "correlation_id": correlation_id,
                    "user_id": user_id,
                    "error": str(e)
                }
            )
            raise DatabaseError("Failed to retrieve user") from e

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User or None: User if found, None otherwise
            
        Raises:
            DatabaseError: If database query fails
        """
        correlation_id = get_correlation_id()
        
        try:
            logger.debug(
                "Fetching user by email",
                extra={
                    "correlation_id": correlation_id,
                    "email": email
                }
            )
            
            user = self.db.query(User).filter(User.email == email).first()
            
            if user:
                logger.debug(
                    "User found by email",
                    extra={
                        "correlation_id": correlation_id,
                        "user_id": user.id,
                        "email": email
                    }
                )
            else:
                logger.debug(
                    "User not found by email",
                    extra={
                        "correlation_id": correlation_id,
                        "email": email
                    }
                )
            
            return user
            
        except SQLAlchemyError as e:
            logger.error(
                "Failed to fetch user by email",
                extra={
                    "correlation_id": correlation_id,
                    "email": email,
                    "error": str(e)
                }
            )
            raise DatabaseError("Failed to retrieve user") from e

    async def get_all(
        self, skip: int = 0, limit: int = 100, role_filter: UserRole | None = None
    ) -> list[User]:
        """
        Get all users with optional filtering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            role_filter: Optional role to filter by

        Returns:
            List[User]: List of users
        """
        query = self.db.query(User)

        if role_filter:
            query = query.filter(User.role == role_filter)

        return query.offset(skip).limit(limit).all()

    async def update(
        self,
        user_id: str,
        email: str | None = None,
        password: str | None = None,
        role: UserRole | None = None,
    ) -> User | None:
        """
        Update user information.

        Args:
            user_id: User's ID (UUID string)
            email: New email address
            password: New password (will be hashed)
            role: New role

        Returns:
            User or None: Updated user if found, None otherwise
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        if email is not None:
            user.email = email

        if password is not None:
            user.hashed_password = hash_password(password)

        if role is not None:
            user.role = role

        self.db.commit()
        self.db.refresh(user)

        return user

    async def delete(self, user_id: str) -> bool:
        """
        Delete user by ID.

        Args:
            user_id: User's ID (UUID string)

        Returns:
            bool: True if user was deleted, False if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()

        return True

    async def exists_by_email(self, email: str) -> bool:
        """
        Check if user exists by email.

        Args:
            email: Email address to check

        Returns:
            bool: True if user exists, False otherwise
        """
        user = await self.get_by_email(email)
        return user is not None

    async def count(self, role_filter: UserRole | None = None) -> int:
        """
        Count total number of users.

        Args:
            role_filter: Optional role to filter by

        Returns:
            int: Total number of users
        """
        query = self.db.query(User)

        if role_filter:
            query = query.filter(User.role == role_filter)

        return query.count()

    async def get_admins(self) -> list[User]:
        """
        Get all admin users.

        Returns:
            List[User]: List of admin users
        """
        return await self.get_all(role_filter=UserRole.ADMIN)

    async def get_supervisors(self) -> list[User]:
        """
        Get all supervisor users.

        Returns:
            List[User]: List of supervisor users
        """
        return await self.get_all(role_filter=UserRole.SUPERVISOR)

    async def search_users(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """
        Search users by email.

        Args:
            search_term: Search term to match against email
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[User]: List of matching users
        """
        return (
            self.db.query(User)
            .filter(User.email.ilike(f"%{search_term}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
