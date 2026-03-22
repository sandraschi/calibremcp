"""
CalibreMCP - FastMCP 2.14.1+ Server for Calibre E-book Library Management

Efficient and secure access to Calibre libraries, supporting both local and remote access.
Provides tools for browsing, searching, and managing e-books with proper authentication.
"""

__version__ = "1.0.0"
__author__ = "Sandra"
__description__ = "FastMCP 2.14.1+ server for Calibre e-book library management"

# CRITICAL: Suppress ALL protocol-breaking output before any imports
import os
import sys
import warnings

# Aggressively ignore all warnings (especially Pydantic V2 warnings during import)
warnings.filterwarnings("ignore")
# Also suppress warnings from dependencies
os.environ["PYTHONWARNINGS"] = "ignore"
# Ensure we don't get Pydantic V2 warnings if possible
try:
    from pydantic import PydanticDeprecatedSince20

    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
except ImportError:
    pass

# For MCP stdio transport, stderr must be clean or redirected
# Detect if we're running in stdio mode (Antigravity IDE or Claude Desktop)
_is_stdio = not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True

# Save original streams for restoration
_original_stdout = sys.stdout
_original_stderr = sys.stderr

# TEMPORARILY DISABLE all complex initialization for debugging
# This might be causing the hang
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("calibre_mcp.init")
logger.info("DEBUG: __init__.py starting")

# For MCP stdio transport, stderr must be clean or redirected
# Detect if we're running in stdio mode (Antigravity IDE or Claude Desktop)
# _is_stdio = not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True

# Save original streams for restoration
# _original_stdout = sys.stdout
# _original_stderr = sys.stderr

# Redirect stderr AND stdout to a file to capture early crashes/output without breaking JSON-RPC
# Note: logging_config.py will still log to files
# import tempfile

# try:
#     debug_log_path = os.path.join(tempfile.gettempdir(), "calibre_mcp_startup.log")
#     _log_file = open(debug_log_path, "w", encoding="utf-8", buffering=1)
#     sys.stderr = _log_file
#     sys.stdout = _log_file
#     # Write immediate marker
#     _log_file.write(f"--- Calibre MCP Startup {__version__} ---\n")
# except Exception:
#     pass

logger.info("DEBUG: __init__.py complex initialization disabled")

# Now safe to proceed with standard imports

# Core exports - clean imports
from .calibre_api import CalibreAPIClient, CalibreAPIError
from .config import CalibreConfig
from .exceptions import BookNotFoundError, CalibreError  # noqa: F401
from .models import (
    Author,
    Book,
    Comment,
    Data,
    Identifier,
    Library,
    LibraryInfo,
    Rating,
    Series,
    Tag,
)  # noqa: F401
from .storage import LocalStorage, StorageBackend

# DO NOT import server or tools here - causes circular import deadlock
# Server and tools are imported only when actually running the server
# from .server import create_app, mcp
# from . import tools  # noqa: F401


# Lazy import for mcp instance to avoid circular imports in tests
def _get_mcp():
    """Lazy import of mcp instance for testing."""
    from .server import mcp

    return mcp


__all__ = [
    "CalibreConfig",
    "CalibreAPIClient",
    "CalibreAPIError",
    "CalibreError",
    "BookNotFoundError",
    "Book",
    "Author",
    "Series",
    "Tag",
    "Rating",
    "Comment",
    "Data",
    "Identifier",
    "Library",
    "LibraryInfo",
    "StorageBackend",
    "LocalStorage",
    "_get_mcp",  # For testing only
]
