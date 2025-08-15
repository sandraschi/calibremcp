"""
Exception handlers for the Calibre MCP Server.
"""
from typing import Dict, Any, Callable, Awaitable

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class CalibreError(Exception):
    """Base exception for Calibre MCP errors."""
    def __init__(self, message: str, status_code: int = 400, **kwargs):
        self.message = message
        self.status_code = status_code
        self.details = kwargs
        super().__init__(message)

class BookNotFoundError(CalibreError):
    """Raised when a book is not found."""
    def __init__(self, book_id: str, **kwargs):
        super().__init__(
            f"Book with ID {book_id} not found",
            status_code=404,
            book_id=book_id,
            **kwargs
        )

class LibraryError(CalibreError):
    """Raised for library-related errors."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=500, **kwargs)

def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to the FastAPI application."""
    @app.exception_handler(CalibreError)
    async def calibre_error_handler(request: Request, exc: CalibreError):
        error_response = {
            "error": {
                "code": exc.__class__.__name__,
                "message": str(exc.message),
                "details": exc.details
            }
        }
        logger.error(f"Calibre error: {exc}", exc_info=exc)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        error_response = {
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
        logger.error(f"HTTP error: {exc}")
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=exc.headers
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error_response = {
            "error": {
                "code": "ValidationError",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        }
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        error_response = {
            "error": {
                "code": "ValidationError",
                "message": "Invalid data format",
                "details": exc.errors()
            }
        }
        logger.error(f"Pydantic validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception occurred")
        error_response = {
            "error": {
                "code": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": str(exc) if app.debug else None
            }
        }
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )
