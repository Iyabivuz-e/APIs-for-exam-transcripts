"""
FastAPI Application Factory

This module contains the FastAPI application factory and main entry point.
It configures middleware, routers, database connections, and logging.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import routes as auth_routes
from app.api.private import admin, supervisor, users
from app.api.public import exams as public_exams
from app.config.settings import get_settings
from app.core.exceptions import add_exception_handlers
from app.db.session import create_tables


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format=(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            if settings.is_production
            else "%(levelname)s:     %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Reduce noise from third-party libraries in production
    if settings.is_production:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    setup_logging()
    await create_tables()

    logger = logging.getLogger(__name__)
    settings = get_settings()
    logger.info(f"Starting Exam Transcripts API in {settings.environment} mode")

    # Auto-create users if needed (for free tier Render)
    try:
        # Check if we should create users
        create_users_env = os.getenv("CREATE_INITIAL_USERS", "false").lower()
        database_url = os.getenv("DATABASE_URL", "")

        if create_users_env in ["true", "1", "yes"] and database_url.startswith(
            "postgresql"
        ):
            from app.core.security import hash_password
            from app.db.session import get_db
            from app.models.user import User, UserRole
            from sqlalchemy import text, inspect

            logger.info("🌱 Auto-creating initial users for production...")

            # Get database session
            db_gen = get_db()
            db = next(db_gen)

            try:
                # Check database schema compatibility
                inspector = inspect(db.bind)
                
                # Initialize schema compatibility flag
                schema_compatible = True
                
                # Check if user table exists
                tables = inspector.get_table_names()
                if "user" not in tables:
                    logger.info("📋 User table not found - database will be initialized")
                    schema_compatible = True
                else:
                    # Check if user table uses UUID or integer IDs
                    columns = inspector.get_columns("user")
                    id_column = None
                    for col in columns:
                        if col["name"] == "id":
                            id_column = col
                            break
                    
                    if id_column:
                        column_type = str(id_column["type"]).upper()
                        if "INTEGER" in column_type or "SERIAL" in column_type:
                            logger.warning("⚠️ Database schema mismatch detected!")
                            logger.warning("⚠️ Production database uses integer IDs but application expects UUIDs")
                            
                            # Check if database is empty - if so, recreate with correct schema
                            try:
                                user_count = db.execute(text('SELECT COUNT(*) FROM "user"')).scalar()
                                if user_count == 0:
                                    logger.info("🔄 Database is empty, recreating schema with UUID support...")
                                    
                                    # Drop existing tables and recreate with correct schema
                                    db.execute(text('DROP TABLE IF EXISTS "user_exam" CASCADE'))
                                    db.execute(text('DROP TABLE IF EXISTS "exam" CASCADE'))  
                                    db.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
                                    db.commit()
                                    
                                    # Force table recreation by calling create_tables again
                                    from app.db.base import Base
                                    Base.metadata.create_all(bind=db.bind)
                                    
                                    logger.info("✅ Schema recreated with UUID support!")
                                    
                                    # Now proceed with user creation
                                    schema_compatible = True
                                else:
                                    logger.warning("⚠️ Database has existing data - manual migration required")
                                    logger.warning("⚠️ Use the migration endpoint: POST /private/admin/migration/migrate-to-uuid")
                                    logger.warning("⚠️ Skipping auto-user creation to prevent errors")
                                    schema_compatible = False
                                    
                            except Exception as e:
                                logger.error(f"Failed to check/fix database schema: {e}")
                                schema_compatible = False
                        else:
                            logger.info(f"✅ Database schema compatible (ID type: {column_type})")
                            schema_compatible = True
                    else:
                        logger.warning("⚠️ User table has no id column")
                        schema_compatible = False

                # Only create users if schema is compatible
                if schema_compatible:
                    # Check if users already exist
                    existing_count = db.query(User).count()

                    if existing_count > 0:
                        logger.info(
                            f"✅ Database already has {existing_count} users, skipping auto-creation"
                        )
                    else:
                        # Create users
                        users_to_create = [
                            ("admin@example.com", "admin123", UserRole.ADMIN),
                            (
                                "supervisor@example.com",
                                "supervisor123",
                                UserRole.SUPERVISOR,
                            ),
                            ("user@example.com", "user123", UserRole.USER),
                            ("john.doe@example.com", "password123", UserRole.USER),
                            ("jane.smith@example.com", "password123", UserRole.USER),
                        ]

                        logger.info(f"👥 Creating {len(users_to_create)} initial users...")

                        for email, password, role in users_to_create:
                            hashed_password = hash_password(password)
                            user = User(
                                email=email, hashed_password=hashed_password, role=role
                            )
                            db.add(user)
                            logger.info(f"✅ Added user: {email} ({role.value})")

                        db.commit()

                        final_count = db.query(User).count()
                        logger.info(
                            f"🎉 Successfully created {final_count} users in production database!"
                        )

                        logger.info("📧 Login credentials available:")
                        logger.info("👤 Admin: admin@example.com / admin123")
                        logger.info("👤 Supervisor: supervisor@example.com / supervisor123")
                        logger.info("👤 User: user@example.com / user123")
                        logger.info("👤 User: john.doe@example.com / password123")
                        logger.info("👤 User: jane.smith@example.com / password123")

            finally:
                db.close()
        else:
            logger.info("🚫 Auto user creation disabled or not needed")

    except Exception as e:
        logger.warning(f"Auto user creation failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Exam Transcripts API")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_settings()

    app = FastAPI(
        title="Exam Transcripts API",
        description="RESTful API for managing exam transcripts with role-based access control",
        version="0.1.0",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Add exception handlers
    add_exception_handlers(app)

    # Include routers
    app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
    app.include_router(public_exams.router, prefix="/public", tags=["Public"])
    app.include_router(users.router, prefix="/private/users", tags=["User"])
    app.include_router(admin.router, prefix="/private/admin", tags=["Admin"])
    app.include_router(
        supervisor.router, prefix="/private/supervisor", tags=["Supervisor"]
    )
    
    # Include migration endpoints
    from app.api.admin import migration as migration_routes
    app.include_router(
        migration_routes.router, prefix="/private/admin/migration", tags=["Migration"]
    )

    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint.

        Returns:
            dict: API status and version information
        """
        return {
            "status": "healthy",
            "service": "Exam Transcripts API",
            "version": "0.1.0",
            "environment": settings.environment,
        }

    @app.get("/", tags=["Health"])
    async def root():
        """
        Root endpoint with basic API information.

        Returns:
            dict: API welcome message and links
        """
        return {
            "message": "Welcome to Exam Transcripts API",
            "version": "0.1.0",
            "docs": (
                "/docs"
                if settings.enable_docs
                else "Documentation disabled in production"
            ),
            "health": "/health",
        }

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
