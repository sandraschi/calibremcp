"""
CalibreMCP - FastMCP 2.10.1 Server for Calibre E-book Library Management

Efficient and secure access to Calibre libraries, supporting both local and remote access.
Provides tools for browsing, searching, and managing e-books with proper authentication.
"""

__version__ = "1.0.0"
__author__ = "Sandra"
__description__ = "FastMCP 2.10.1 server for Calibre e-book library management"

# Core exports - clean imports
from .calibre_api import CalibreAPIClient, CalibreAPIError
from .config import CalibreConfig
from .exceptions import CalibreError, BookNotFoundError
from .models import Book, BookMetadata, BookFormat, BookStatus
from .mcp_server import CalibreMCPServer
from .server import create_app, mcp
from .storage import StorageBackend, LocalStorage
    
    # Import tools to register them with the MCP server
from . import tools

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
