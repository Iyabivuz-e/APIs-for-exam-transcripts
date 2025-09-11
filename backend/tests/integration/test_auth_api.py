"""
Integration tests for authentication API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.permissions import UserRole
from app.core.security import hash_password


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""
    
    @pytest.fixture
    def test_user_data(self):
        """Test user data for authentication tests."""
        return {
            "email": "test@example.com",
            "password": "password123"
        }
    
    @pytest.fixture
    def create_test_user(self, db_session: Session, test_user_data):
        """Create a test user in the database."""
        hashed_password = hash_password(test_user_data["password"])
        user = User(
            email=test_user_data["email"],
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify the user was actually saved and can be retrieved
        db_user = db_session.query(User).filter(User.email == test_user_data["email"]).first()
        print(f"User retrieved from DB: {db_user}")
        if db_user:
            print(f"Stored hashed password: {db_user.hashed_password}")
            print(f"Plain password for testing: {test_user_data['password']}")
        
        return user
    
    def test_login_success(self, client: TestClient, create_test_user, test_user_data):
        """Test successful login."""
        # Arrange
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        # Debug: Check if user was created
        print(f"Created user: {create_test_user}")
        print(f"User email: {create_test_user.email}")
        print(f"User role: {create_test_user.role}")
        
        # Act
        response = client.post("/auth/login", json=login_data)
        
        # Debug: Print response details
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login with invalid email."""
        # Arrange
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        # Act
        response = client.post("/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["error"] is True
        assert "Invalid email or password" in data["message"]
    
    def test_login_invalid_password(self, client: TestClient, create_test_user, test_user_data):
        """Test login with invalid password."""
        # Arrange
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        
        # Act
        response = client.post("/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid credentials" in data["detail"]
    
    def test_login_invalid_data_format(self, client: TestClient):
        """Test login with invalid data format."""
        # Test missing password
        login_data = {
            "email": "test@example.com"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 422
        
        # Test invalid email format
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 422
    
    def test_get_current_user_info(self, client: TestClient, create_test_user, test_user_data):
        """Test getting current user info."""
        # First login to get token
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test getting user info
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["role"] == "user"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_get_current_user_info_unauthorized(self, client: TestClient):
        """Test getting user info without authentication."""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_get_current_user_info_invalid_token(self, client: TestClient):
        """Test getting user info with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_refresh_token(self, client: TestClient, create_test_user, test_user_data):
        """Test token refresh."""
        # First login to get token
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        original_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {original_token}"}
        
        # Test token refresh
        response = client.post("/auth/refresh", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        
        # New token should be different from original
        new_token = data["access_token"]
        assert new_token != original_token
    
    def test_refresh_token_unauthorized(self, client: TestClient):
        """Test token refresh without authentication."""
        response = client.post("/auth/refresh")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_logout(self, client: TestClient, create_test_user, test_user_data):
        """Test user logout."""
        # First login to get token
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test logout
        response = client.post("/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"
    
    def test_logout_unauthorized(self, client: TestClient):
        """Test logout without authentication."""
        response = client.post("/auth/logout")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
