"""
Database Initialization Module

Handles database setup, migrations, and initial data creation in a structured way.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

from app.config.settings import get_settings
from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.exceptions import ValidationError

logger = get_logger(__name__)


class DatabaseInitializer:
    """Handles database initialization and setup."""
    
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.inspector = inspect(db.bind)
    
    async def initialize(self) -> None:
        """Initialize database if needed."""
        try:
            if self._should_create_initial_users():
                await self._create_initial_users()
            else:
                logger.info("🚫 Auto user creation disabled or not needed")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
            if self.settings.environment == "production":
                raise ValidationError("Database initialization failed")
    
    def _should_create_initial_users(self) -> bool:
        """Check if initial users should be created."""
        if not self.settings.auto_create_users:
            return False
            
        # Check if users already exist
        user_count = self.db.query(User).count()
        if user_count > 0:
            logger.info(f"Users already exist in database (count: {user_count})")
            return False
            
        return True
    
    async def _create_initial_users(self) -> None:
        """Create initial users for the application."""
        logger.info("🌱 Creating initial users...")
        
        default_users = [
            {
                "email": "admin@example.com",
                "password": "admin123",  # TODO: Generate secure password in production
                "role": UserRole.ADMIN
            },
            {
                "email": "supervisor@example.com", 
                "password": "supervisor123",
                "role": UserRole.SUPERVISOR
            },
            {
                "email": "student@example.com",
                "password": "student123", 
                "role": UserRole.USER
            }
        ]
        
        created_users = []
        for user_data in default_users:
            try:
                # Check if user already exists
                existing_user = self.db.query(User).filter(
                    User.email == user_data["email"]
                ).first()
                
                if existing_user:
                    logger.info(f"User {user_data['email']} already exists, skipping")
                    continue
                
                # Create new user
                hashed_password = hash_password(user_data["password"])
                user = User(
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    role=user_data["role"]
                )
                
                self.db.add(user)
                created_users.append(user_data["email"])
                
            except Exception as e:
                logger.error(f"Failed to create user {user_data['email']}: {str(e)}")
                self.db.rollback()
                raise
        
        if created_users:
            self.db.commit()
            logger.info(f"✅ Created {len(created_users)} initial users: {', '.join(created_users)}")
        else:
            logger.info("No new users created")


async def initialize_database() -> None:
    """Initialize database with proper error handling."""
    settings = get_settings()
    
    if settings.environment == "production":
        logger.info("🔧 Initializing production database...")
    
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        try:
            initializer = DatabaseInitializer(db)
            await initializer.initialize()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        # Don't crash in production, but log the error
        if settings.environment != "production":
            raise
