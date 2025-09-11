"""
Integration tests for authentication endpoints

Tests the complete authentication flow including login,
token validation, and protected endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.models.user import User, UserRole
from app.core.security import hash_password


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""
    
    def test_login_success(self, client: TestClient, test_db):
        """Test successful login."""
        # Create test user
        hashed_password = hash_password("password123")
        user = User(
            email="test@example.com",
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        test_db.add(user)
        test_db.commit()
        
        # Test login
        response = client.post(
            "/auth/login",
            data={"username": "test@example.com", "password": "password123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient, test_db):
        """Test login with wrong password."""
        # Create test user
        hashed_password = hash_password("password123")
        user = User(
            email="test@example.com",
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        test_db.add(user)
        test_db.commit()
        
        # Test login with wrong password
        response = client.post(
            "/auth/login",
            data={"username": "test@example.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
    
    def test_login_user_not_found(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "password123"}
        )
        
        assert response.status_code == 401
    
    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get("/private/users/me")
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self, client: TestClient, test_db):
        """Test accessing protected endpoint with valid token."""
        # Create test user
        hashed_password = hash_password("password123")
        user = User(
            email="test@example.com",
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        test_db.add(user)
        test_db.commit()
        
        # Login to get token
        login_response = client.post(
            "/auth/login",
            data={"username": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        response = client.get(
            "/private/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
    
    def test_admin_endpoint_access_control(self, client: TestClient, test_db):
        """Test that admin endpoints require admin role."""
        # Create regular user
        hashed_password = hash_password("password123")
        user = User(
            email="user@example.com",
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        test_db.add(user)
        test_db.commit()
        
        # Login as regular user
        login_response = client.post(
            "/auth/login",
            data={"username": "user@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Try to access admin endpoint
        response = client.get(
            "/private/admin/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403  # Forbidden
