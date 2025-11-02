"""
Request logging middleware for the Calibre MCP Server.
"""

import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive=receive)

        # Skip logging for health checks
        if request.url.path == "/health":
            return await self.app(scope, receive, send)

        # Log request
        start_time = time.time()
        response = await self._log_request(request)

        # Process request
        try:
            response = await self.app(scope, receive, send)
            return response
        except Exception:
            logger.exception("Error processing request")
            raise
        finally:
            # Calculate request duration
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = "{0:.2f}".format(process_time)

            # Log response
            status_code = 500
            if hasattr(response, "status_code"):
                status_code = response.status_code

            logger.info(
                f"{request.method} {request.url.path} {status_code} {formatted_process_time}ms"
            )

    async def _log_request(self, request: Request) -> None:
        """Log the incoming request."""
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )

        # Log query parameters if present
        if request.query_params:
            logger.debug(f"Query params: {dict(request.query_params)}")

        # Log request body for non-GET requests
        if request.method not in ["GET", "HEAD"]:
            try:
                body = await request.body()
                if body:
                    logger.debug(f"Request body: {body.decode()}")
            except Exception as e:
                logger.warning(f"Failed to log request body: {e}")


# Add the middleware to FastAPI
async def add_request_logging(app):
    """Add request logging middleware to the FastAPI app."""
    app.add_middleware(RequestLoggingMiddleware)
    return app
