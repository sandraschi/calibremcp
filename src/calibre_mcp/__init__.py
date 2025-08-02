"""
CalibreMCP - FastMCP 2.10 Server for Calibre E-book Library Management

Efficient and secure access to Calibre libraries, supporting both local and remote access.
Provides tools for browsing, searching, and managing e-books with proper authentication.
"""

__version__ = "2.0.0"
__author__ = "Sandra"
__description__ = "FastMCP 2.10 server for Calibre e-book library management"

# Core exports - hybrid imports for maximum compatibility
try:
    # Try relative imports first (when running as module)
    from .server import mcp, init as init_server
    from .config import CalibreConfig, RemoteServerConfig
    from .auth import AuthManager
    from .storage import get_storage_backend, LocalStorage, RemoteStorage
    from .models import Book, LibraryInfo
    from .exceptions import (
        CalibreError,
        AuthError,
        BookNotFoundError,
        ServerConnectionError
    )
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
    "CalibreAPIError"
]
