"""
Authentication Service Module

This module contains business logic for authentication operations
including login, token management, and user authentication.
"""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    """
    Service class for authentication operations.

    Handles user authentication, token creation, and related business logic.
    """

    def __init__(self, db: Session):
        """
        Initialize authentication service.

        Args:
            db: Database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.settings = get_settings()

    async def authenticate_user(self, login_request: LoginRequest) -> User | None:
        """
        Authenticate user with email and password.

        Args:
            login_request: Login request containing email and password

        Returns:
            User or None: Authenticated user if credentials are valid, None otherwise
        """
        user = await self.user_repo.get_by_email(login_request.email)

        if not user:
            return None

        if not verify_password(login_request.password, user.hashed_password):
            return None

        return user

    async def create_access_token_for_user(self, user: User) -> TokenResponse:
        """
        Create access token for authenticated user.

        Args:
            user: Authenticated user

        Returns:
            TokenResponse: Token response with access token and user info
        """
        # Create token data
        token_data = {"sub": user.email, "user_id": user.id, "role": user.role}

        # Create access token
        access_token_expires = timedelta(
            minutes=self.settings.access_token_expire_minutes
        )
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )

        # Import here to avoid circular imports
        from app.schemas.user import User as UserSchema

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.settings.access_token_expire_minutes
            * 60,  # Convert to seconds
            user=UserSchema.from_orm(user),
        )

    async def login(self, login_request: LoginRequest) -> TokenResponse | None:
        """
        Complete login flow: authenticate and create token.

        Args:
            login_request: Login request containing credentials

        Returns:
            TokenResponse or None: Token response if login successful, None otherwise
        """
        user = await self.authenticate_user(login_request)

        if not user:
            return None

        return await self.create_access_token_for_user(user)

    async def refresh_token(self, user: User) -> TokenResponse:
        """
        Refresh access token for user.

        Args:
            user: Current authenticated user

        Returns:
            TokenResponse: New token response
        """
        return await self.create_access_token_for_user(user)

    async def logout(self, user: User) -> bool:
        """
        Logout user (placeholder for token blacklisting).

        Args:
            user: User to logout

        Returns:
            bool: True if logout successful
        """
        # Current implementation relies on client-side token disposal
        # Future enhancement: Implement Redis-based token blacklisting for enhanced security
        return True
