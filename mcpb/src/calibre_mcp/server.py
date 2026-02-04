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
import os
import sys

if os.name == "nt":  # Windows only
    try:
        # Force binary mode for stdin/stdout to prevent CRLF conversion
        import msvcrt

        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    except (OSError, AttributeError):
        # Fallback: just ensure no CRLF conversion
        pass


# DevNullStdout class for stdio mode suppression
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


# CRITICAL: Suppress all warnings before any imports
# MCP stdio protocol requires clean stdout/stderr for JSON-RPC communication
import warnings

# Suppress all warnings immediately and aggressively
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")
# Suppress specific warning categories
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# For MCP stdio transport, we need to prevent ANY output to stderr
# Warnings are printed to stderr, which breaks JSON-RPC protocol
# Note: This is handled in __main__.py before imports

# CRITICAL: Detect if we're running in stdio mode (MCP server)
# MCP servers use stdio transport, so stdout must be clean for JSON-RPC
_is_stdio_mode = not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncContextManager

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel

# Standard imports - no fallbacks needed
from .calibre_api import CalibreAPIClient
from .config import CalibreConfig

# Import structured logging
from .logging_config import get_logger, log_error, log_operation, setup_logging
from .storage.persistence import CalibreMCPStorage, set_storage

# Load environment variables
load_dotenv()

# Logger will be re-initialized in main() after logging setup
logger = get_logger("calibremcp.server")

# Global API client and database connections (initialized on startup)
api_client: CalibreAPIClient | None = None
current_library: str = "main"
available_libraries: dict[str, str] = {}
storage: CalibreMCPStorage | None = None


@asynccontextmanager
async def server_lifespan(mcp_instance: FastMCP) -> AsyncContextManager[None]:
    """FastMCP 2.13 server lifespan for initialization and cleanup."""
    global api_client, current_library, available_libraries, storage, logger

    # Startup
    logger = get_logger("calibremcp.server")
    log_operation(logger, "server_lifespan_startup", level="INFO")

    try:
        # Initialize storage
        storage_instance = CalibreMCPStorage(mcp_instance)
        await storage_instance.initialize()
        set_storage(storage_instance)
        storage = storage_instance
        logger.info("FastMCP 2.13 storage initialized")

        # Initialize config and discover libraries FIRST
        from .config import CalibreConfig
        from .config_discovery import get_active_calibre_library
        from .db.database import init_database

        config = CalibreConfig()

        # Auto-discover libraries using CalibreConfig's discovery system
        if config.auto_discover_libraries:
            discovered_libs = config.discover_libraries()
            if discovered_libs:
                logger.info(f"Auto-discovered {len(discovered_libs)} Calibre libraries")

        # Restore current library from persistent storage
        persisted_library = await storage.get_current_library()
        if persisted_library:
            current_library = persisted_library
            logger.info(f"Restored current library from storage: {current_library}")

        # Discover libraries (using utils for backward compatibility)
        libraries = await discover_libraries()
        available_libraries = libraries
        log_operation(
            logger,
            "library_discovery",
            level="INFO",
            discovered_libraries=list(libraries.keys()),
            current_library=current_library,
        )

        # CRITICAL: Auto-load default library - ensure database is ALWAYS initialized
        # Priority: 1) persisted library, 2) config.local_library_path, 3) active library from Calibre config, 4) first discovered library

        library_to_load = None
        library_name_loaded = None

        # Try persisted library first
        if persisted_library and libraries.get(persisted_library):
            library_to_load = Path(libraries[persisted_library])
            library_name_loaded = persisted_library
            logger.info(f"Using persisted library: {persisted_library}")
        # Try config.local_library_path
        elif config.local_library_path and (config.local_library_path / "metadata.db").exists():
            library_to_load = config.local_library_path
            # Find library name from discovered libraries
            for name, path in libraries.items():
                if Path(path) == library_to_load:
                    library_name_loaded = name
                    break
            if not library_name_loaded:
                library_name_loaded = library_to_load.name
            logger.info(f"Using library from config: {library_to_load}")
        # Try active library from Calibre's own config
        else:
            active_lib = get_active_calibre_library()
            if (
                active_lib
                and active_lib.path.exists()
                and (active_lib.path / "metadata.db").exists()
            ):
                library_to_load = active_lib.path
                library_name_loaded = active_lib.name
                logger.info(f"Using active Calibre library: {active_lib.name} at {active_lib.path}")
        # Fallback to first discovered library
        if not library_to_load and libraries:
            first_lib_path = list(libraries.values())[0]
            library_to_load = Path(first_lib_path)
            library_name_loaded = list(libraries.keys())[0]
            logger.info(
                f"Auto-loading first discovered library: {library_name_loaded} at {library_to_load}"
            )

        # Initialize database with the selected library
        if library_to_load:
            metadata_db = library_to_load / "metadata.db"
            if metadata_db.exists():
                try:
                    init_database(str(metadata_db.absolute()), echo=False)
                    current_library = library_name_loaded or library_to_load.name
                    # Update config to use this library
                    config.local_library_path = library_to_load
                    # Persist to storage
                    try:
                        await storage.set_current_library(current_library)
                    except Exception as storage_e:
                        logger.warning(f"Could not persist library to storage: {storage_e}")
                    logger.info(
                        f"SUCCESS: Database initialized with library: {current_library} at {library_to_load}"
                    )
                except Exception as e:
                    logger.error(f"Failed to initialize database: {e}", exc_info=True)
                    raise RuntimeError(f"Cannot initialize database at {metadata_db}: {e}") from e
            else:
                error_msg = f"metadata.db not found at {metadata_db.absolute()}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        else:
            # Last resort: try to discover from CalibreConfig
            if config.discovered_libraries:
                first_discovered = list(config.discovered_libraries.values())[0]
                library_to_load = first_discovered.path
                metadata_db = library_to_load / "metadata.db"
                if metadata_db.exists():
                    try:
                        init_database(str(metadata_db.absolute()), echo=False)
                        current_library = first_discovered.name
                        config.local_library_path = library_to_load
                        await storage.set_current_library(current_library)
                        logger.info(
                            f"Database initialized with discovered library: {current_library} at {library_to_load}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to initialize database: {e}", exc_info=True)
                        raise RuntimeError(
                            f"Cannot initialize database at {metadata_db}: {e}"
                        ) from e
                else:
                    error_msg = f"metadata.db not found at {metadata_db.absolute()}"
                    logger.error(error_msg)
                    raise FileNotFoundError(error_msg)
            else:
                error_msg = "No libraries discovered, cannot initialize database"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        log_operation(logger, "server_lifespan_ready", level="INFO")

        yield  # Server runs here

    finally:
        # Shutdown
        log_operation(logger, "server_lifespan_shutdown", level="INFO")

        # Save current library state
        if storage:
            try:
                await storage.set_current_library(current_library)
                logger.info(f"Saved current library to storage: {current_library}")
            except Exception as e:
                logger.warning(f"Failed to save library state: {e}")

        # Cleanup database connections if needed
        # (FastMCP will handle storage cleanup)

        log_operation(logger, "server_lifespan_complete", level="INFO")


# Initialize FastMCP server with lifespan
# Persistent storage is configured in CalibreMCPStorage class
# which uses DiskStore in platform-appropriate directory:
# Windows: %APPDATA%\calibre-mcp (survives Windows restarts)
# macOS: ~/Library/Application Support/calibre-mcp
# Linux: ~/.local/share/calibre-mcp
mcp = FastMCP("CalibreMCP Phase 2", lifespan=server_lifespan)

# CRITICAL: After server initialization, restore stdout for stdio mode
# This allows the server to communicate via JSON-RPC while preventing initialization logging
if _is_stdio_mode:
    if hasattr(sys.stdout, "restore"):
        sys.stdout.restore()
        # Now we can safely write to stdout for JSON-RPC communication

    # Note: Original logging functionality is restored via setup_logging()

    # Set up proper logging to stderr only (not stdout)
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # Critical: log to stderr, not stdout
    )

# Register prompt templates
from .prompts import register_prompts

register_prompts(mcp)


# ==================== RESPONSE MODELS ====================


class LibrarySearchResponse(BaseModel):
    """Response model for library search operations"""

    results: list[dict[str, Any]]
    total_found: int
    query_used: str | None = None
    search_time_ms: int = 0
    library_searched: str = "main"


class BookDetailResponse(BaseModel):
    """Response model for detailed book information"""

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

    libraries: list[dict[str, Any]]
    current_library: str
    total_libraries: int


class LibraryStatsResponse(BaseModel):
    """Response model for library statistics"""

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

    total_tags: int
    unique_tags: int
    duplicate_tags: list[dict[str, Any]]
    unused_tags: list[str]
    suggestions: list[dict[str, Any]]


class DuplicatesResponse(BaseModel):
    """Response model for duplicate detection"""

    duplicate_groups: list[dict[str, Any]]
    total_duplicates: int
    confidence_scores: dict[str, float]


class SeriesAnalysisResponse(BaseModel):
    """Response model for series analysis"""

    incomplete_series: list[dict[str, Any]]
    reading_order_suggestions: list[dict[str, Any]]
    series_statistics: dict[str, Any]


class LibraryHealthResponse(BaseModel):
    """Response model for library health analysis"""

    health_score: float
    issues_found: list[dict[str, Any]]
    recommendations: list[str]
    database_integrity: bool


class UnreadPriorityResponse(BaseModel):
    """Response model for unread priority list"""

    prioritized_books: list[dict[str, Any]]
    priority_reasons: dict[str, str]
    total_unread: int


class MetadataUpdateRequest(BaseModel):
    """Request model for metadata updates"""

    book_id: int
    field: str
    value: Any


class MetadataUpdateResponse(BaseModel):
    """Response model for metadata updates"""

    updated_books: list[int]
    failed_updates: list[dict[str, Any]]
    success_count: int


class ReadingStats(BaseModel):
    """Response model for reading statistics"""

    total_books_read: int
    average_rating: float
    favorite_genres: list[str]
    reading_patterns: dict[str, Any]


class ConversionRequest(BaseModel):
    """Request model for format conversion"""

    book_id: int
    source_format: str
    target_format: str
    quality: str = "high"


class ConversionResponse(BaseModel):
    """Response model for format conversion"""

    book_id: int
    success: bool
    output_path: str | None = None
    error_message: str | None = None


class JapaneseBookOrganization(BaseModel):
    """Response model for Japanese book organization"""

    manga_series: list[dict[str, Any]]
    light_novels: list[dict[str, Any]]
    language_learning: list[dict[str, Any]]
    reading_recommendations: list[str]


class ITBookCuration(BaseModel):
    """Response model for IT book curation"""

    programming_languages: dict[str, list[dict[str, Any]]]
    outdated_books: list[dict[str, Any]]
    learning_paths: list[dict[str, Any]]


class ReadingRecommendations(BaseModel):
    """Response model for reading recommendations"""

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


def create_app() -> FastMCP:
    """Create and configure the FastMCP application"""
    return mcp


def main():
    """Main server entry point"""
    try:
        # Initialize logging (file only, no console for stdio transport)
        # CRITICAL: Console logging breaks MCP stdio protocol (JSON-RPC on stdout)
        log_file_path = Path("logs/calibremcp.log")
        setup_logging(
            level="INFO",
            log_file=log_file_path,
            enable_console=False,  # Disable console for MCP stdio transport
        )

        # Re-get logger after setup (logging config changed)
        logger = get_logger("calibremcp.server")

        # Log server startup
        log_operation(
            logger,
            "server_startup",
            level="INFO",
            version="1.0.0",
            collection_size="1000+ books",
            fastmcp_version="2.13.0+",
        )

        # Register tools with FastMCP server
        # Tools with @mcp.tool() auto-register when imported (FastMCP 2.12+)
        # BaseTool classes need explicit registration
        # NOTE: Server lifespan handles initialization (database, libraries, storage)
        from .tools import register_tools

        register_tools(mcp)

        # Run the FastMCP server (handles event loop internally)
        # Server lifespan handles initialization/cleanup (FastMCP 2.13+)
        # Disable banner for STDIO transport (Rich console fails on Windows STDIO)
        mcp.run(show_banner=False)

    except Exception as e:
        # Log error to file only (no stdout/stderr output for MCP stdio protocol)
        log_error(logger, "server_startup_error", e)
        # Re-raise to let FastMCP handle it properly
        raise


if __name__ == "__main__":
    # Handle both direct execution and module execution
    import sys
    from pathlib import Path

    # If running directly (not as module), fix imports
    # Add src directory to path to allow absolute imports
    current_file = Path(__file__).resolve()
    src_path = current_file.parent.parent  # Go from src/calibre_mcp/server.py to src/

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # Now re-import using absolute imports
    from calibre_mcp.server import main

    main()
