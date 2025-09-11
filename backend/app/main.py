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
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" if settings.is_production
        else "%(levelname)s:     %(message)s",
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
        create_users_env = os.getenv('CREATE_INITIAL_USERS', 'false').lower()
        database_url = os.getenv('DATABASE_URL', '')
        
        if create_users_env in ['true', '1', 'yes'] and database_url.startswith('postgresql'):
            from app.db.session import get_db
            from app.models.user import User, UserRole
            from app.core.security import hash_password
            
            logger.info("🌱 Auto-creating initial users for production...")
            
            # Get database session
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                # Check if users already exist
                existing_count = db.query(User).count()
                
                if existing_count > 0:
                    logger.info(f"✅ Database already has {existing_count} users, skipping auto-creation")
                else:
                    # Create users
                    users_to_create = [
                        ("admin@example.com", "admin123", UserRole.ADMIN),
                        ("supervisor@example.com", "supervisor123", UserRole.SUPERVISOR),
                        ("user@example.com", "user123", UserRole.USER),
                        ("john.doe@example.com", "password123", UserRole.USER),
                        ("jane.smith@example.com", "password123", UserRole.USER)
                    ]
                    
                    logger.info(f"👥 Creating {len(users_to_create)} initial users...")
                    
                    for email, password, role in users_to_create:
                        hashed_password = hash_password(password)
                        user = User(email=email, hashed_password=hashed_password, role=role)
                        db.add(user)
                        logger.info(f"✅ Added user: {email} ({role.value})")
                    
                    db.commit()
                    
                    final_count = db.query(User).count()
                    logger.info(f"🎉 Successfully created {final_count} users in production database!")
                    
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
            "docs": "/docs" if settings.enable_docs else "Documentation disabled in production",
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
