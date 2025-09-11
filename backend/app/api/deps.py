"""
API Dependencies Module

This module contains FastAPI dependencies for dependency injection.
Provides utilities for database sessions, authentication, and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.permissions import (require_admin, require_supervisor,
                                  require_supervisor_or_admin)
from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenData

# Security scheme for JWT Bearer tokens
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials containing JWT token
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Verify and decode token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user information from token
    try:
        token_data = TokenData(**payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(token_data.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (placeholder for future user activation feature).

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive (future implementation)
    """
    # Future implementation: Check if user is active
    # if not current_user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Inactive user"
    #     )

    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and ensure they have admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current admin user

    Raises:
        HTTPException: If user doesn't have admin permissions
    """
    require_admin(current_user.role)
    return current_user


async def get_current_supervisor_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and ensure they have supervisor role.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current supervisor user

    Raises:
        HTTPException: If user doesn't have supervisor permissions
    """
    require_supervisor(current_user.role)
    return current_user


async def get_current_supervisor_or_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current user and ensure they have supervisor or admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current supervisor or admin user

    Raises:
        HTTPException: If user doesn't have required permissions
    """
    require_supervisor_or_admin(current_user.role)
    return current_user


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Get current user if authenticated, otherwise return None.

    Used for endpoints that can work with or without authentication.

    Args:
        credentials: Optional HTTP authorization credentials
        db: Database session

    Returns:
        User or None: Current user if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        # Use the existing get_current_user dependency
        return get_current_user(credentials, db)
    except HTTPException:
        return None


class CommonQueryParams:
    """
    Common query parameters for list endpoints.

    Provides pagination and sorting parameters that can be reused
    across different list endpoints.
    """

    def __init__(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        """
        Initialize common query parameters.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
        """
        self.page = max(1, page)  # Ensure page is at least 1
        self.page_size = min(max(1, page_size), 100)  # Limit page size to 100
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()

    @property
    def offset(self) -> int:
        """
        Calculate offset for database queries.

        Returns:
            int: Offset value
        """
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """
        Get limit for database queries.

        Returns:
            int: Limit value
        """
        return self.page_size


def get_pagination_params(page: int = 1, page_size: int = 10) -> CommonQueryParams:
    """
    Dependency for getting pagination parameters.

    Args:
        page: Page number
        page_size: Number of items per page

    Returns:
        CommonQueryParams: Pagination parameters
    """
    return CommonQueryParams(page=page, page_size=page_size)
