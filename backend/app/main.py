"""
FastAPI Application Factory

This module contains the FastAPI application factory and main entry point.
It configures middleware, routers, database connections, and logging.
"""

import logging
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
        from auto_seed_users import auto_create_users_if_needed
        await auto_create_users_if_needed()
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
