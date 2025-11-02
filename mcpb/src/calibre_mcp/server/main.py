"""
Main entry point for the Calibre MCP Server.
"""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import books, metadata, library, search, users
from .middleware import RequestLoggingMiddleware
from .core.exception_handlers import add_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Add exception handlers
    add_exception_handlers(app)

    # Include API routers
    app.include_router(books.router, prefix=f"{settings.API_V1_STR}/books", tags=["books"])
    app.include_router(metadata.router, prefix=f"{settings.API_V1_STR}/metadata", tags=["metadata"])
    app.include_router(library.router, prefix=f"{settings.API_V1_STR}/library", tags=["library"])
    app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
    app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the server using uvicorn."""
    uvicorn.run(
        "calibre_mcp.server.main:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
        log_level="info",
    )


if __name__ == "__main__":
    run_server(debug=settings.DEBUG)
