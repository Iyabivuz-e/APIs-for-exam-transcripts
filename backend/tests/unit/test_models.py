"""
Unit tests for User model

Tests the User model functionality including validation,
relationships, and role-based permissions.
"""

import pytest
from datetime import datetime

from app.models.user import User, UserRole
from app.core.security import hash_password


class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, test_db):
        """Test user creation."""
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            role=UserRole.USER
        )
        
        test_db.add(user)
        test_db.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_email_unique(self, test_db):
        """Test that user emails are unique."""
        # Create first user
        user1 = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            role=UserRole.USER
        )
        test_db.add(user1)
        test_db.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="test@example.com",
            hashed_password=hash_password("password456"),
            role=UserRole.ADMIN
        )
        test_db.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            test_db.commit()
    
    def test_user_roles(self):
        """Test user role enum values."""
        assert UserRole.USER == "user"
        assert UserRole.SUPERVISOR == "supervisor"
        assert UserRole.ADMIN == "admin"
    
    def test_user_representation(self, test_db):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            hashed_password=hash_password("password123"),
            role=UserRole.USER
        )
        
        test_db.add(user)
        test_db.commit()
        
        user_str = str(user)
        assert "test@example.com" in user_str
        assert "user" in user_str
