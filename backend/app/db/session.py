"""
Database Session Module

This module handles database connection, session management, and table creation.
Provides utilities for managing SQLAlchemy sessions and database operations.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import get_settings
from app.db.base import Base

# Import all models to ensure they are registered with SQLAlchemy
# This prevents relationship resolution errors
try:
    from app.models.user import User  # noqa: F401
    from app.models.exam import Exam  # noqa: F401  
    from app.models.user_exam import UserExam  # noqa: F401
except ImportError:
    # Models might not be available during initial setup
    pass


class DatabaseManager:
    """
    Manages database connections and sessions.
    """

    def __init__(self):
        """Initialize database manager with settings."""
        self.settings = get_settings()
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database engine and session factory."""
        # Use test database URL if in test environment
        database_url = (
            self.settings.test_database_url
            if self.settings.environment == "test"
            else self.settings.database_connection_url  # Use the property with SSL config
        )

        # Create engine with appropriate settings
        if database_url.startswith("sqlite"):
            # SQLite specific settings
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                echo=self.settings.environment == "development",
            )
        else:
            # PostgreSQL settings with SSL and connection pooling
            connect_args = {}
            if self.settings.is_production:
                # Production PostgreSQL settings
                connect_args.update({
                    "sslmode": self.settings.postgres_ssl_mode,
                    "connect_timeout": 30,
                })
            
            self.engine = create_engine(
                database_url, 
                echo=self.settings.environment == "development",
                connect_args=connect_args,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=300,    # Recycle connections every 5 minutes
            )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session.

        Yields:
            Session: SQLAlchemy database session
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def create_tables(self):
        """
        Create all database tables.

        This method creates all tables defined in the models.
        Should be called during application startup.
        """
        # Import all models to ensure they are registered with Base
        from app.models import exam, user, user_exam  # noqa: F401

        Base.metadata.create_all(bind=self.engine)

    async def drop_tables(self):
        """
        Drop all database tables.

        This method is useful for testing and development.
        Use with caution in production environments.
        """
        Base.metadata.drop_all(bind=self.engine)


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.

    This function is used as a FastAPI dependency to inject
    database sessions into route handlers.

    Yields:
        Session: SQLAlchemy database session
    """
    yield from db_manager.get_session()


async def create_tables():
    """
    Create all database tables.

    Wrapper function for the database manager's create_tables method.
    """
    await db_manager.create_tables()


async def drop_tables():
    """
    Drop all database tables.

    Wrapper function for the database manager's drop_tables method.
    """
    await db_manager.drop_tables()
