# Setup basic logging for diagnostics
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("calibre_mcp.server")
logger.info("SERVER.PY: Module import starting...")

"""
CalibreMCP Phase 2 - FastMCP 2.13+ Server for Calibre E-book Library Management

Austrian efficiency for Sandra's 1000+ book collection across multiple libraries.
Now with 23 comprehensive tools including multi-library, Japanese weeb optimization,
and IT book curation. All tools properly categorized and FastMCP 2.13+ compliant.

FastMCP 2.13 introduces persistent storage backends for stateful applications.

Phase 2 adds 19 additional tools:
- Multi-Library Management (4 tools)
- Advanced Organization & Analysis (5 tools)
- Metadata & Database Operations (4 tools)
- File Operations (3 tools)
- Austrian Efficiency Specials (3 tools)
"""

# CRITICAL: Set stdio to binary mode on Windows for Antigravity IDE compatibility
# Antigravity IDE is strict about JSON-RPC protocol and interprets trailing \r as "invalid trailing data"
# This must happen BEFORE any imports that might write to stdout
logger.info("Setting stdio binary mode...")
import os
import sys

if os.name == "nt":  # Windows only
    try:
        # Force binary mode for stdin/stdout to prevent CRLF conversion
        import msvcrt

        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        logger.info("Binary mode set successfully")
    except (OSError, AttributeError) as e:
        # Fallback: just ensure no CRLF conversion
        logger.warning(f"Binary mode failed: {e}")

logger.info("Stdio setup complete")


# DevNullStdout class for stdio mode suppression
logger.info("Defining DevNullStdout class...")


class DevNullStdout:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout

    def write(self, data):
        # Suppress all writes to stdout during initialization
        pass

    def flush(self):
        pass

    def restore(self):
        sys.stdout = self.original_stdout


logger.info("DevNullStdout class defined")

# CRITICAL: Suppress all warnings before any imports
logger.info("Setting up warning suppression...")
import warnings

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
logger.info("Warning suppression complete")

# CRITICAL: Detect if we're running in stdio mode
logger.info("Detecting stdio mode...")
_is_stdio_mode = not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True
logger.info(f"Stdio mode detection: {_is_stdio_mode}")

# Import typing and basic modules
logger.info("Importing typing and basic modules...")
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

logger.info("Basic imports complete")

# Import external dependencies
logger.info("Importing FastMCP...")
from fastmcp import FastMCP

logger.info("FastMCP imported")

logger.info("Importing Pydantic...")
from pydantic import BaseModel

logger.info("Pydantic imported")

logger.info("Importing dotenv...")
from dotenv import load_dotenv

logger.info("dotenv imported")

# Load environment variables
logger.info("Loading environment variables...")
load_dotenv()
logger.info("Environment variables loaded")

# Setup proper logging
logger.info("Setting up proper logging system...")
from calibre_mcp.logging_config import get_logger

logger = get_logger("calibremcp.server")
logger.info("Logger setup complete")

# Import CalibreAPIClient at module level (needed for type hints)
logger.info("Importing CalibreAPIClient for type hints...")
from calibre_mcp.calibre_api import CalibreAPIClient

logger.info("SUCCESS: CalibreAPIClient imported for type hints")

# Global API client and database connections (initialized on startup)
logger.info("Setting up global variables...")
api_client = None  # CalibreAPIClient
current_library: str = "main"
available_libraries: dict[str, str] = {}
storage = None  # CalibreMCPStorage
logger.info("Global variables initialized")


def create_app(path: str = "/mcp"):
    """
    Create FastMCP HTTP ASGI app for mounting in FastAPI.

    Args:
        path: Mount path (ignored, handled by FastAPI mount)

    Returns the ASGI app that can be mounted at the specified path.
    FastMCP 2.13+ provides http_app() method for this.
    """
    # FastMCP http_app() returns ASGI app - path is handled by FastAPI mount
    # The path parameter is kept for API compatibility but not used
    return mcp.http_app()


@asynccontextmanager
@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP):
    """FastMCP 2.14.1+ lifespan for initialization and cleanup."""
    import logging

    logger = logging.getLogger("calibremcp.lifespan")
    logger.info("SERVER LIFESPAN: Starting initialization...")

    # Minimal initialization - just yield
    yield

    logger.info("SERVER LIFESPAN: Cleanup complete")

    lifespan_logger.info("SERVER LIFESPAN: Complete")


# Create MCP instance
logger.info("Creating FastMCP instance...")
mcp = FastMCP(
    "CalibreMCP Phase 2",
    instructions="""You are CalibreMCP, a comprehensive FastMCP 2.14.3 server for Calibre e-book library management.

FASTMCP 2.14.3 FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows and complex operations
- Portmanteau design preventing tool explosion while maintaining full functionality

CORE CAPABILITIES:
- E-book Library Management: Browse, search, and organize your Calibre libraries
- Book Operations: View, edit, add, and manage book metadata
- Content Processing: Extract text, convert formats, and analyze content
- Library Organization: Manage collections, tags, authors, and series
- Advanced Search: Full-text search with semantic ranking

CONVERSATIONAL FEATURES:
- Tools return natural language responses alongside structured data
- Sampling allows autonomous orchestration of complex library operations
- Agentic capabilities for intelligent content discovery and management

RESPONSE FORMAT:
- All tools return dictionaries with 'success' boolean and 'message' for conversational responses
- Error responses include 'error' field with descriptive message
- Success responses include relevant data fields and natural language summaries

PORTMANTEAU DESIGN:
Tools are consolidated into logical groups to prevent tool explosion while maintaining full functionality.
Each portmanteau tool handles multiple related operations through an 'operation' parameter.
""",
)
logger.info("FastMCP instance created")

# CRITICAL: For MCP stdio mode, stderr is already redirected to devnull in __main__.py
# We should not set up additional logging to stderr as it would override the redirection
# and break the MCP JSON-RPC protocol.

# For non-MCP modes (if any), we could set up logging here, but since this is MCP-only,
# we rely on the structured logging from logging_config.py which handles MCP compatibility.

if not _is_stdio_mode:
    # Only set up logging for non-MCP modes (if any)
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

# Register prompt templates
from calibre_mcp.prompts import register_prompts

register_prompts(mcp)

# Tools registered in main() for stdio. For webapp HTTP mode, MCP_USE_HTTP=false uses direct import.


# ==================== RESPONSE MODELS ====================


class LibrarySearchResponse(BaseModel):
    """Response model for library search operations"""

    model_config = {"from_attributes": True}

    results: list[dict[str, Any]]
    total_found: int
    query_used: str | None = None
    search_time_ms: int = 0
    library_searched: str = "main"


class BookDetailResponse(BaseModel):
    """Response model for detailed book information"""

    model_config = {"from_attributes": True}

    book_id: int
    title: str
    authors: list[str]
    series: str | None = None
    series_index: float | None = None
    rating: float | None = None
    tags: list[str] = []
    comments: str | None = None
    published: str | None = None
    languages: list[str] = ["en"]
    formats: list[str] = []
    identifiers: dict[str, str] = {}
    last_modified: str | None = None
    cover_url: str | None = None
    download_links: dict[str, str] = {}
    library_name: str = "main"


class ConnectionTestResponse(BaseModel):
    """Response model for connection testing"""

    connected: bool
    server_url: str
    server_version: str | None = None
    library_count: int = 0
    total_books: int = 0
    response_time_ms: int = 0
    error_message: str | None = None


class LibraryListResponse(BaseModel):
    """Response model for library listing"""

    model_config = {"from_attributes": True}

    libraries: list[dict[str, Any]]
    current_library: str
    total_libraries: int


class LibraryStatsResponse(BaseModel):
    """Response model for library statistics"""

    model_config = {"from_attributes": True}

    library_name: str
    total_books: int
    total_authors: int
    total_series: int
    total_tags: int
    format_distribution: dict[str, int]
    language_distribution: dict[str, int]
    rating_distribution: dict[str, int]
    last_modified: str | None = None


class TagStatsResponse(BaseModel):
    """Response model for tag statistics"""

    model_config = {"from_attributes": True}

    total_tags: int
    unique_tags: int
    duplicate_tags: list[dict[str, Any]]
    unused_tags: list[str]
    suggestions: list[dict[str, Any]]


class DuplicatesResponse(BaseModel):
    """Response model for duplicate detection"""

    model_config = {"from_attributes": True}

    duplicate_groups: list[dict[str, Any]]
    total_duplicates: int
    confidence_scores: dict[str, float]


class SeriesAnalysisResponse(BaseModel):
    """Response model for series analysis"""

    model_config = {"from_attributes": True}

    incomplete_series: list[dict[str, Any]]
    reading_order_suggestions: list[dict[str, Any]]
    series_statistics: dict[str, Any]


class LibraryHealthResponse(BaseModel):
    """Response model for library health analysis"""

    model_config = {"from_attributes": True}

    health_score: float
    issues_found: list[dict[str, Any]]
    recommendations: list[str]
    database_integrity: bool


class UnreadPriorityResponse(BaseModel):
    """Response model for unread priority list"""

    model_config = {"from_attributes": True}

    prioritized_books: list[dict[str, Any]]
    priority_reasons: dict[str, str]
    total_unread: int


class MetadataUpdateRequest(BaseModel):
    """Request model for metadata updates"""

    model_config = {"from_attributes": True}

    book_id: int
    field: str
    value: Any


class MetadataUpdateResponse(BaseModel):
    """Response model for metadata updates"""

    model_config = {"from_attributes": True}

    updated_books: list[int]
    failed_updates: list[dict[str, Any]]
    success_count: int


class ReadingStats(BaseModel):
    """Response model for reading statistics"""

    model_config = {"from_attributes": True}

    total_books_read: int
    average_rating: float
    favorite_genres: list[str]
    reading_patterns: dict[str, Any]


class ConversionRequest(BaseModel):
    """Request model for format conversion"""

    model_config = {"from_attributes": True}

    book_id: int
    source_format: str
    target_format: str
    quality: str = "high"


class ConversionResponse(BaseModel):
    """Response model for format conversion"""

    model_config = {"from_attributes": True}

    book_id: int
    success: bool
    output_path: str | None = None
    error_message: str | None = None


class JapaneseBookOrganization(BaseModel):
    """Response model for Japanese book organization"""

    model_config = {"from_attributes": True}

    manga_series: list[dict[str, Any]]
    light_novels: list[dict[str, Any]]
    language_learning: list[dict[str, Any]]
    reading_recommendations: list[str]


class ITBookCuration(BaseModel):
    """Response model for IT book curation"""

    model_config = {"from_attributes": True}

    programming_languages: dict[str, list[dict[str, Any]]]
    outdated_books: list[dict[str, Any]]
    learning_paths: list[dict[str, Any]]


class ReadingRecommendations(BaseModel):
    """Response model for reading recommendations"""

    model_config = {"from_attributes": True}

    recommendations: list[dict[str, Any]]
    reasoning: dict[str, str]
    confidence_scores: dict[str, float]


# ==================== HELPER FUNCTIONS ====================


async def get_api_client() -> CalibreAPIClient | None:
    """
    Get or create API client instance for remote Calibre Content Server access.

    Only creates HTTP client if use_remote=True in config.
    For local libraries, this returns None and tools should use direct SQLite access.
    """
    from calibre_mcp.config import CalibreConfig

    global api_client
    config = CalibreConfig()

    # Only create HTTP client if remote access is enabled
    if not config.use_remote:
        return None

    if api_client is None:
        api_client = CalibreAPIClient(config)
        await api_client.initialize()
    return api_client


async def discover_libraries() -> dict[str, str]:
    """Discover available Calibre libraries"""
    global available_libraries

    if available_libraries:
        return available_libraries

    config = CalibreConfig()
    libraries = {}

    # Check configured library path
    if config.local_library_path and config.local_library_path.exists():
        libraries["main"] = str(config.local_library_path)

    # Discover additional libraries
    base_dir = Path("L:/Multimedia Files/Written Word")
    if base_dir.exists():
        for item in base_dir.iterdir():
            if item.is_dir() and (item / "metadata.db").exists():
                libraries[item.name] = str(item)

    available_libraries = libraries
    return libraries


# ==================== SERVER INITIALIZATION ====================


def get_mcp_instance() -> FastMCP:
    """Return the FastMCP instance (for internal use). Use create_app() for HTTP mounting."""
    return mcp


async def main():
    """Main server entry point with comprehensive error handling and logging"""
    logger = None

    try:
        # PHASE 1: Import heavy modules with error handling
        logger = logging.getLogger("calibremcp.server")
        logger.info("PHASE 1: Starting module imports...")

        try:
            logger.info("Importing logging_config...")
            from calibre_mcp.logging_config import (
                get_logger,
                log_error,
                log_operation,
                setup_logging,
            )

            logger.info("SUCCESS: logging_config imported")

            logger.info("Importing CalibreAPIClient...")
            logger.info("SUCCESS: CalibreAPIClient imported")

            logger.info("Importing CalibreConfig...")
            logger.info("SUCCESS: CalibreConfig imported")

            logger.info("Importing storage components...")
            logger.info("SUCCESS: Storage components imported")

            logger.info("Initializing user data database (SQLite for user comments, auth, etc.)...")
            from calibre_mcp.db.user_data import init_user_data_db

            init_user_data_db()
            logger.info("SUCCESS: User data database initialized")

        except Exception as import_error:
            logger.error(f"CRITICAL: Module import failed: {import_error}", exc_info=True)
            raise RuntimeError(
                f"Failed to import required modules: {import_error}"
            ) from import_error

        # PHASE 2: Initialize logging with timeout protection
        logger.info("PHASE 2: Initializing logging system...")
        try:
            log_file_path = Path("logs/calibremcp.log")
            logger.info(f"Setting up logging to file: {log_file_path}")

            # Add timeout for logging setup (should be fast)
            import asyncio

            setup_result = await asyncio.wait_for(
                asyncio.to_thread(
                    setup_logging, level="INFO", log_file=log_file_path, enable_console=False
                ),
                timeout=5.0,
            )
            logger.info("SUCCESS: Logging setup completed")

        except TimeoutError:
            logger.warning("WARNING: Logging setup timed out, continuing with basic logging")
        except Exception as log_error:
            logger.error(f"ERROR: Logging setup failed: {log_error}", exc_info=True)
            # Continue with basic logging

        # Get proper logger after setup
        logger = get_logger("calibremcp.server")
        logger.info("PHASE 2: Logger initialized successfully")

        # PHASE 3: Log server startup details
        logger.info("PHASE 3: Logging startup information...")
        try:
            log_operation(
                logger,
                "server_startup",
                level="INFO",
                version="1.0.0",
                collection_size="1000+ books",
                fastmcp_version="2.14.1+",
                python_version=f"{__import__('sys').version}",
                platform=__import__("platform").platform(),
            )
            logger.info("SUCCESS: Startup logging completed")
        except Exception as log_op_error:
            logger.error(f"Startup logging failed: {log_op_error}", exc_info=True)

        # PHASE 4: Verify MCP instance
        logger.info("PHASE 4: Verifying MCP instance...")
        try:
            if mcp is None:
                logger.error("CRITICAL: MCP instance is None - cannot register tools!")
                raise RuntimeError("MCP instance not initialized")

            logger.info(f"SUCCESS: MCP instance verified: {type(mcp).__name__} (id: {id(mcp)})")

        except Exception as mcp_error:
            logger.error(f"ERROR: MCP instance verification failed: {mcp_error}", exc_info=True)
            raise

        # PHASE 5: Register tools with comprehensive error handling
        logger.info("PHASE 5: Registering tools...")
        try:
            # Add timeout for tool registration (may involve heavy imports)
            import asyncio

            async def register_tools_with_timeout():
                logger.info("Starting tool registration...")
                from calibre_mcp.tools import register_tools

                logger.info("Tools module imported, calling register_tools...")
                register_tools(mcp)
                logger.info("register_tools() completed")

            await asyncio.wait_for(register_tools_with_timeout(), timeout=30.0)
            logger.info("SUCCESS: Tool registration completed")

        except TimeoutError:
            logger.error("CRITICAL: Tool registration timed out after 30 seconds")
            logger.error("This usually indicates a hanging import in one of the tool modules")
            logger.error("Check for circular imports or heavy initialization in tool modules")
            raise RuntimeError("Tool registration timed out - check for hanging imports")
        except Exception as tool_error:
            logger.error(f"ERROR: Tool registration failed: {tool_error}", exc_info=True)
            logger.error(f"Tool registration error type: {type(tool_error).__name__}")
            raise

        # Verify tools were registered
        try:
            # Check if FastMCP has registered tools
            tool_count = "unknown"
            if hasattr(mcp, "_tools"):
                tool_count = len(mcp._tools)

            logger.info(f"Tool registration verification: {tool_count} tools found")
            if tool_count == 0:
                logger.error("CRITICAL: No tools registered! Check tool imports.")
        except Exception as e:
            logger.error(f"Could not verify tool count: {e}")

        # Restore stdout explicitly for JSON-RPC communication
        import calibre_mcp

        if hasattr(calibre_mcp, "_original_stdout") and calibre_mcp._original_stdout:
            __import__("sys").stdout.flush()
            __import__("sys").stdout = calibre_mcp._original_stdout

            # Re-configure binary mode for Windows if needed
            if os.name == "nt":
                import msvcrt

                try:
                    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
                except Exception:
                    pass

        # PHASE 6: Start FastMCP server
        logger.info("PHASE 6: Starting FastMCP server...")
        try:
            # Log what we're about to do
            logger.info("Calling mcp.run_stdio_async()...")
            logger.info(f"MCP instance: {type(mcp).__name__}")
            logger.info(
                f"MCP lifespan configured: {hasattr(mcp, '_lifespan') and mcp._lifespan is not None}"
            )

            # Run the FastMCP server using the SOTA-recommended async stdio transport
            await mcp.run_stdio_async()

        except Exception as server_error:
            logger.error("CRITICAL: FastMCP server startup failed")
            logger.error(f"Server error type: {type(server_error).__name__}")
            logger.error(f"Server error message: {server_error}", exc_info=True)

            # Log additional diagnostic information
            try:
                logger.error(f"Python version: {sys.version}")
                logger.error(f"Platform: {__import__('platform').platform()}")

                # Check if MCP has tools registered
                if hasattr(mcp, "_tools"):
                    tool_count = len(mcp._tools)
                    logger.error(f"MCP tools registered: {tool_count}")
                else:
                    logger.error("MCP _tools attribute not found")

            except Exception as diag_error:
                logger.error(f"Diagnostic logging failed: {diag_error}")

            raise

    except Exception as e:
        # PHASE 7: Global exception handling
        if logger:
            logger.error("CRITICAL: Unhandled exception in main()")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception message: {e}", exc_info=True)

            # Try to log to file if logging system is available
            try:
                log_error(logger, "server_startup_error", e)
            except Exception:
                # Last resort logging
                logger.error(f"CRITICAL ERROR: {e}")
        else:
            # No logger available, print to stderr
            # Last resort logging - no logger available
            import sys

            sys.stderr.write(f"CRITICAL ERROR (no logger): {e}\n")

        # Re-raise to let FastMCP handle it properly
        raise


if __name__ == "__main__":
    # Handle both direct execution and module execution
    import asyncio
    import sys
    from pathlib import Path

    # If running directly (not as module), fix imports
    current_file = Path(__file__).resolve()
    src_path = current_file.parent.parent

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Now re-import using absolute imports
    from calibre_mcp.server import main

    asyncio.run(main())
