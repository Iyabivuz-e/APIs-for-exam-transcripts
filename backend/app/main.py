"""
FastAPI Application Factory

This module contains the FastAPI application factory and main entry point.
It configures middleware, routers, and database connections.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import routes as auth_routes
from app.api.private import admin, supervisor, users
from app.api.public import exams as public_exams
from app.config.settings import get_settings
from app.core.exceptions import add_exception_handlers
from app.db.session import create_tables


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
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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

    @app.on_event("startup")
    async def startup_event():
        """Initialize database tables on startup."""
        await create_tables()

    @app.get("/", tags=["Health"])
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
    )
