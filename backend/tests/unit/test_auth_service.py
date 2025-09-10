"""
Unit tests for authentication service.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.user import User
from app.core.permissions import UserRole


class TestAuthService:
    """Test cases for AuthService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_user_repo(self):
        """Mock user repository."""
        return Mock()
    
    @pytest.fixture
    def auth_service(self, mock_db_session, mock_user_repo):
        """Create auth service with mocked dependencies."""
        service = AuthService(mock_db_session)
        service.user_repo = mock_user_repo
        return service
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        user = User()
        user.id = 1
        user.email = "test@example.com"
        user.hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeOPNEHVMZSFyUFGS"  # "password123"
        user.role = UserRole.USER
        user.created_at = datetime.now()
        user.updated_at = datetime.now()
        return user
    
    @pytest.fixture
    def login_request(self):
        """Create a sample login request."""
        return LoginRequest(email="test@example.com", password="password123")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_user_repo, sample_user, login_request):
        """Test successful user authentication."""
        # Arrange
        mock_user_repo.get_by_email = AsyncMock(return_value=sample_user)
        
        with patch('app.services.auth_service.verify_password', return_value=True):
            # Act
            result = await auth_service.authenticate_user(login_request)
            
            # Assert
            assert result is not None
            assert result.email == sample_user.email
            assert result.id == sample_user.id
            mock_user_repo.get_by_email.assert_called_once_with(login_request.email)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self, auth_service, mock_user_repo, login_request):
        """Test authentication with invalid email."""
        # Arrange
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        
        # Act
        result = await auth_service.authenticate_user(login_request)
        
        # Assert
        assert result is None
        mock_user_repo.get_by_email.assert_called_once_with(login_request.email)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, auth_service, mock_user_repo, sample_user, login_request):
        """Test authentication with invalid password."""
        # Arrange
        mock_user_repo.get_by_email = AsyncMock(return_value=sample_user)
        
        with patch('app.services.auth_service.verify_password', return_value=False):
            # Act
            result = await auth_service.authenticate_user(login_request)
            
            # Assert
            assert result is None
            mock_user_repo.get_by_email.assert_called_once_with(login_request.email)
    
    @pytest.mark.asyncio
    async def test_create_access_token_for_user(self, auth_service, sample_user):
        """Test access token creation."""
        # Arrange
        mock_token = "test_access_token_12345"
        
        with patch('app.services.auth_service.create_access_token', return_value=mock_token), \
             patch('app.services.auth_service.get_settings') as mock_settings:
            
            mock_settings.return_value.access_token_expire_minutes = 30
            
            # Act
            result = await auth_service.create_access_token_for_user(sample_user)
            
            # Assert
            assert isinstance(result, TokenResponse)
            assert result.access_token == mock_token
            assert result.token_type == "bearer"
            assert result.expires_in == 1800  # 30 minutes * 60 seconds
            assert result.user.email == sample_user.email
            assert result.user.role == sample_user.role
    
    @pytest.mark.asyncio
    async def test_login_success(self, auth_service, sample_user, login_request):
        """Test successful login flow."""
        # Arrange
        from app.schemas.user import User as UserSchema
        
        user_schema = UserSchema(
            id=sample_user.id,
            email=sample_user.email,
            role=sample_user.role,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at
        )
        
        mock_token_response = TokenResponse(
            access_token="test_token",
            token_type="bearer",
            expires_in=1800,
            user=user_schema
        )
        
        # Mock the methods
        auth_service.authenticate_user = AsyncMock(return_value=sample_user)
        auth_service.create_access_token_for_user = AsyncMock(return_value=mock_token_response)
        
        # Act
        result = await auth_service.login(login_request)
        
        # Assert
        assert result is not None
        assert result == mock_token_response
        auth_service.authenticate_user.assert_called_once_with(login_request)
        auth_service.create_access_token_for_user.assert_called_once_with(sample_user)
    
    @pytest.mark.asyncio
    async def test_login_failure(self, auth_service, login_request):
        """Test login failure with invalid credentials."""
        # Arrange
        auth_service.authenticate_user = AsyncMock(return_value=None)
        
        # Act
        result = await auth_service.login(login_request)
        
        # Assert
        assert result is None
        auth_service.authenticate_user.assert_called_once_with(login_request)
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, auth_service, sample_user):
        """Test token refresh."""
        # Arrange
        from app.schemas.user import User as UserSchema
        
        user_schema = UserSchema(
            id=sample_user.id,
            email=sample_user.email,
            role=sample_user.role,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at
        )
        
        mock_token_response = TokenResponse(
            access_token="new_test_token",
            token_type="bearer",
            expires_in=1800,
            user=user_schema
        )
        
        auth_service.create_access_token_for_user = AsyncMock(return_value=mock_token_response)
        
        # Act
        result = await auth_service.refresh_token(sample_user)
        
        # Assert
        assert result == mock_token_response
        auth_service.create_access_token_for_user.assert_called_once_with(sample_user)
    
    @pytest.mark.asyncio
    async def test_logout(self, auth_service, sample_user):
        """Test user logout."""
        # Act
        result = await auth_service.logout(sample_user)
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_authenticate_user_with_different_roles(self, auth_service, mock_user_repo, login_request):
        """Test authentication with different user roles."""
        # Test admin user
        admin_user = User()
        admin_user.id = 2
        admin_user.email = "admin@example.com"
        admin_user.hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeOPNEHVMZSFyUFGS"
        admin_user.role = UserRole.ADMIN
        
        mock_user_repo.get_by_email = AsyncMock(return_value=admin_user)
        
        with patch('app.services.auth_service.verify_password', return_value=True):
            result = await auth_service.authenticate_user(login_request)
            
            assert result is not None
            assert result.role == UserRole.ADMIN
    
    @pytest.mark.asyncio
    async def test_create_access_token_with_custom_expiry(self, auth_service, sample_user):
        """Test access token creation with custom expiry time."""
        # Arrange
        mock_token = "custom_expiry_token"
        custom_expiry_minutes = 60
        
        # Mock the settings to return the custom expiry time
        auth_service.settings.access_token_expire_minutes = custom_expiry_minutes
        
        with patch('app.services.auth_service.create_access_token', return_value=mock_token):
            # Act
            result = await auth_service.create_access_token_for_user(sample_user)
            
            # Assert
            assert result.expires_in == custom_expiry_minutes * 60  # Convert to seconds
    
    def test_auth_service_initialization(self, mock_db_session):
        """Test auth service initialization."""
        # Act
        service = AuthService(mock_db_session)
        
        # Assert
        assert service.db == mock_db_session
        assert service.user_repo is not None
        assert service.settings is not None
