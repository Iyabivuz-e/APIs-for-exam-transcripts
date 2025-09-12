"""
FastAPI Application Factory

This module contains the FastAPI application factory and main entry point.
It configures middleware, routers, database connections, and structured logging.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import routes as auth_routes
from app.api.private import admin, supervisor, users
from app.api.public import exams as public_exams
from app.config.settings import get_settings
from app.core.exceptions import add_exception_handlers
from app.core.logging import get_logger, correlation_context
from app.core.database import initialize_database
from app.db.session import create_tables

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    settings = get_settings()
    
    # Startup
    with correlation_context():
        logger.info(f"Starting Exam Transcripts API in {settings.environment} mode")
        
        try:
            await create_tables()
            await initialize_database()
            logger.info("🚀 Application startup complete")
        except Exception as e:
            logger.error(f"Application startup failed: {str(e)}", exc_info=True)
            if settings.environment == "production":
                # Don't crash production on startup errors, but log them
                logger.error("Production startup encountered errors but continuing...")
            else:
                raise

    yield

    # Shutdown
    with correlation_context():
        logger.info("🔥 Shutting down Exam Transcripts API")

        # Add any cleanup logic here if needed
        try:
            # Cleanup resources
            logger.info("🧹 Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}", exc_info=True)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    # Create FastAPI app with appropriate settings
    app_config = {
        "title": "Exam Transcripts API",
        "description": "API for managing exam transcripts and user authentication",
        "version": "1.0.0",
        "lifespan": lifespan,
    }
    
    # Conditional settings based on environment
    if settings.environment == "production":
        app_config.update({
            "docs_url": "/docs" if settings.enable_docs else None,
            "redoc_url": "/redoc" if settings.enable_docs else None,
            "openapi_url": "/openapi.json" if settings.enable_docs else None,
        })

    app = FastAPI(**app_config)

    # Add exception handlers
    add_exception_handlers(app)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Correlation-ID",
        ],
    )

    # Include API routers
    app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
    app.include_router(public_exams.router, prefix="/public", tags=["Public"])
    app.include_router(users.router, prefix="/private/users", tags=["Users"])
    app.include_router(admin.router, prefix="/private/admin", tags=["Admin"])
    app.include_router(supervisor.router, prefix="/private/supervisor", tags=["Supervisor"])

    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint for monitoring and load balancers.

        Returns:
            dict: API status and system information
        """
        with correlation_context():
            logger.debug("Health check requested")
            return {
                "status": "healthy",
                "service": "Exam Transcripts API",
                "version": "1.0.0",
                "environment": settings.environment,
            }

    @app.get("/", tags=["Root"])
    async def root():
        """
        Root endpoint with basic API information.

        Returns:
            dict: API welcome message and available endpoints
        """
        with correlation_context():
            logger.debug("Root endpoint accessed")
            return {
                "message": "Welcome to Exam Transcripts API",
                "version": "1.0.0",
                "docs": (
                    "/docs"
                    if settings.enable_docs
                    else "Documentation disabled in production"
                ),
                "health": "/health",
                "environment": settings.environment,
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
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
