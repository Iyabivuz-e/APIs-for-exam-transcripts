"""
Permissions Module

This module handles role-based access control and permissions.
Defines user roles and permission checking utilities.
"""

from enum import Enum

from fastapi import HTTPException, status


class UserRole(str, Enum):
    """
    User roles enumeration.

    Attributes:
        ADMIN: Administrator role with full access
        SUPERVISOR: Supervisor role with exam grading permissions
        USER: Regular user role with limited access
    """

    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    USER = "user"


class PermissionChecker:
    """
    Handles permission checking for different user roles.
    """

    @staticmethod
    def check_admin_permission(user_role: str) -> None:
        """
        Check if user has admin permissions.

        Args:
            user_role: User's role

        Raises:
            HTTPException: If user doesn't have admin permissions
        """
        if user_role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required",
            )

    @staticmethod
    def check_supervisor_permission(user_role: str) -> None:
        """
        Check if user has supervisor permissions.

        Args:
            user_role: User's role

        Raises:
            HTTPException: If user doesn't have supervisor permissions
        """
        if user_role != UserRole.SUPERVISOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supervisor permissions required",
            )

    @staticmethod
    def check_supervisor_or_admin_permission(user_role: str) -> None:
        """
        Check if user has supervisor or admin permissions.

        Args:
            user_role: User's role

        Raises:
            HTTPException: If user doesn't have required permissions
        """
        allowed_roles = [UserRole.SUPERVISOR, UserRole.ADMIN]
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supervisor or admin permissions required",
            )

    @staticmethod
    def check_user_permission(user_role: str) -> None:
        """
        Check if user has basic user permissions.

        Args:
            user_role: User's role

        Raises:
            HTTPException: If user doesn't have user permissions
        """
        valid_roles = [UserRole.USER, UserRole.SUPERVISOR, UserRole.ADMIN]
        if user_role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Valid user role required"
            )


# Global permission checker instance
permission_checker = PermissionChecker()


def require_admin(user_role: str) -> None:
    """
    Decorator helper to require admin permissions.

    Args:
        user_role: User's role

    Raises:
        HTTPException: If user doesn't have admin permissions
    """
    permission_checker.check_admin_permission(user_role)


def require_supervisor(user_role: str) -> None:
    """
    Decorator helper to require supervisor permissions.

    Args:
        user_role: User's role

    Raises:
        HTTPException: If user doesn't have supervisor permissions
    """
    permission_checker.check_supervisor_permission(user_role)


def require_supervisor_or_admin(user_role: str) -> None:
    """
    Decorator helper to require supervisor or admin permissions.

    Args:
        user_role: User's role

    Raises:
        HTTPException: If user doesn't have required permissions
    """
    permission_checker.check_supervisor_or_admin_permission(user_role)


def require_user(user_role: str) -> None:
    """
    Decorator helper to require user permissions.

    Args:
        user_role: User's role

    Raises:
        HTTPException: If user doesn't have user permissions
    """
    permission_checker.check_user_permission(user_role)
