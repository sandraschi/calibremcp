"""
CalibreMCP - FastMCP 2.10.1 Server for Calibre E-book Library Management

Efficient and secure access to Calibre libraries, supporting both local and remote access.
Provides tools for browsing, searching, and managing e-books with proper authentication.
"""

__version__ = "2.0.0"
__author__ = "Sandra"
__description__ = "FastMCP 2.10.1 server for Calibre e-book library management"

# Core exports - hybrid imports for maximum compatibility
try:
    from .calibre_api import CalibreAPI, CalibreAPIClient, CalibreAPIError  # noqa: F401
    from .config import Config, CalibreConfig  # noqa: F401
    from .exceptions import CalibreError, BookNotFoundError  # noqa: F401
    from .models import Book, BookMetadata, BookFormat, BookStatus  # noqa: F401
    from .mcp_server import CalibreMCPServer  # noqa: F401
    from .server import create_app, mcp  # noqa: F401
    from .storage import StorageBackend, LocalStorage  # noqa: F401
    
    # Import tools to register them with the MCP server
    from . import tools  # noqa: F401
    
except ImportError as e:
    # Fall back to absolute imports (when running script directly)
    try:
        from calibre_mcp.server import mcp
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.calibre_api import CalibreAPIClient, CalibreAPIError
    except ImportError:
        # Last resort - add current directory to path
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from server import mcp
        from config import CalibreConfig
        from calibre_api import CalibreAPIClient, CalibreAPIError

__all__ = [
    "mcp",
    "CalibreConfig", 
    "CalibreAPIClient",
    "CalibreAPIError",
    "CalibreMCPServer",
    "create_app",
    "Config",
    "Book",
    "BookMetadata",
    "BookFormat",
    "BookStatus",
    "StorageBackend",
    "LocalStorage"
]
