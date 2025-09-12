"""
Custom Exceptions Module

This module defines custom exception classes and exception handlers for the application.
Provides centralized error handling and consistent error responses with structured logging.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger, get_correlation_id

logger = get_logger(__name__)


class BaseCustomException(Exception):
    """
    Base custom exception class.

    Attributes:
        message: Error message
        status_code: HTTP status code
        detail: Additional error details
    """

    def __init__(self, message: str, status_code: int = 500, detail: str = None):
        """
        Initialize custom exception.

        Args:
            message: Error message
            status_code: HTTP status code
            detail: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class AuthenticationError(BaseCustomException):
    """
    Authentication related errors.
    """

    def __init__(self, message: str = "Authentication failed", detail: str = None):
        """
        Initialize authentication error.

        Args:
            message: Error message
            detail: Additional error details
        """
        super().__init__(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED, detail=detail
        )


class AuthorizationError(BaseCustomException):
    """
    Authorization related errors.
    """

    def __init__(self, message: str = "Access denied", detail: str = None):
        """
        Initialize authorization error.

        Args:
            message: Error message
            detail: Additional error details
        """
        super().__init__(
            message=message, status_code=status.HTTP_403_FORBIDDEN, detail=detail
        )


class ValidationError(BaseCustomException):
    """
    Data validation errors.
    """

    def __init__(self, message: str = "Validation failed", detail: str = None):
        """
        Initialize validation error.

        Args:
            message: Error message
            detail: Additional error details
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class NotFoundError(BaseCustomException):
    """
    Resource not found errors.
    """

    def __init__(self, message: str = "Resource not found", detail: str = None):
        """
        Initialize not found error.

        Args:
            message: Error message
            detail: Additional error details
        """
        super().__init__(
            message=message, status_code=status.HTTP_404_NOT_FOUND, detail=detail
        )


class ConflictError(BaseCustomException):
    """
    Resource conflict errors.
    """

    def __init__(self, message: str = "Resource conflict", detail: str = None):
        """
        Initialize conflict error.

        Args:
            message: Error message
            detail: Additional error details
        """
        super().__init__(
            message=message, status_code=status.HTTP_409_CONFLICT, detail=detail
        )


class DatabaseError(BaseCustomException):
    """
    Database operation errors.
    """

    def __init__(self, message: str = "Database operation failed", detail: str = None):
        """
        Initialize database error.

        Args:
            message: Error message
            detail: Additional error details
        """
        super().__init__(
            message=message, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=detail
        )
        """
        Initialize conflict error.

        Args:
            message: Error message
            detail: Additional error details
        """
        super().__init__(
            message=message, status_code=status.HTTP_409_CONFLICT, detail=detail
        )


async def custom_exception_handler(
    request: Request, exc: BaseCustomException
) -> JSONResponse:
    """
    Handle custom exceptions and return formatted JSON response.

    Args:
        request: FastAPI request object
        exc: Custom exception instance

    Returns:
        JSONResponse: Formatted error response
    """
    correlation_id_value = get_correlation_id()
    
    # Log the exception with context
    logger.warning(
        f"Custom exception: {exc.message}",
        extra={
            "exception_type": exc.__class__.__name__,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url),
            "method": request.method,
            "correlation_id": correlation_id_value
        }
    )
    
    content = {
        "error": True,
        "message": exc.message,
        "status_code": exc.status_code,
        "correlation_id": correlation_id_value
    }

    if exc.detail:
        content["detail"] = exc.detail

    return JSONResponse(status_code=exc.status_code, content=content)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions and return formatted JSON response.

    Args:
        request: FastAPI request object
        exc: HTTP exception instance

    Returns:
        JSONResponse: Formatted error response
    """
    correlation_id_value = get_correlation_id()
    
    # Log HTTP exceptions with context
    if exc.status_code >= 500:
        # Server errors - log as error
        logger.error(
            f"HTTP {exc.status_code}: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": str(request.url),
                "method": request.method,
                "correlation_id": correlation_id_value
            }
        )
    else:
        # Client errors - log as warning
        logger.warning(
            f"HTTP {exc.status_code}: {exc.detail}",
            extra={
                "status_code": exc.status_code,
                "path": str(request.url),
                "method": request.method,
                "correlation_id": correlation_id_value
            }
        )
    
    content = {
        "error": True,
        "message": exc.detail,
        "status_code": exc.status_code,
        "correlation_id": correlation_id_value
    }

    return JSONResponse(status_code=exc.status_code, content=content)


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Handle validation exceptions and return formatted JSON response.

    Args:
        request: FastAPI request object
        exc: Validation exception instance

    Returns:
        JSONResponse: Formatted error response
    """
    correlation_id_value = get_correlation_id()
    
    # Log validation errors
    logger.warning(
        f"Validation error: {str(exc)}",
        extra={
            "path": str(request.url),
            "method": request.method,
            "correlation_id": correlation_id_value
        }
    )
    
    content = {
        "error": True,
        "message": "Validation error",
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "detail": str(exc),
        "correlation_id": correlation_id_value
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=content
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions and return formatted JSON response.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse: Formatted error response
    """
    correlation_id_value = get_correlation_id()
    
    # Log unexpected errors with full stack trace
    logger.error(
        f"Unexpected error: {str(exc)}",
        exc_info=True,
        extra={
            "exception_type": exc.__class__.__name__,
            "path": str(request.url),
            "method": request.method,
            "correlation_id": correlation_id_value
        }
    )
    
    content = {
        "error": True,
        "message": "Internal server error",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "correlation_id": correlation_id_value
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content
    )


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add custom exception handlers to FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(BaseCustomException, custom_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)  # Catch-all
    
    logger.info("Exception handlers registered successfully")
