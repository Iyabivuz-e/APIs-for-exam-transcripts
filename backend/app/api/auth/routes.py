"""
Authentication Routes Module

This module contains authentication-related API endpoints
including login, logout, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.

    Args:
        login_request: User credentials (email and password)
        db: Database session

    Returns:
        TokenResponse: Access token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    auth_service = AuthService(db)
    token_response = await auth_service.login(login_request)

    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Refresh user's access token.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        TokenResponse: New access token and user information
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_token(current_user)


@router.post("/logout", response_model=AuthResponse)
async def logout(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Logout current user.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        AuthResponse: Logout confirmation
    """
    auth_service = AuthService(db)
    success = await auth_service.logout(current_user)

    return AuthResponse(success=success, message="Successfully logged out")


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.

    Args:
        current_user: Currently authenticated user

    Returns:
        dict: Current user information
    """
    from app.schemas.user import User as UserSchema

    return {
        "user": UserSchema.from_orm(current_user),
        "permissions": {
            "can_create_exams": current_user.can_create_exams(),
            "can_grade_exams": current_user.can_grade_exams(),
            "is_admin": current_user.is_admin,
            "is_supervisor": current_user.is_supervisor,
            "is_user": current_user.is_user,
        },
    }
