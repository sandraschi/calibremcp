"""
CalibreMCP - FastMCP 2.10.1 Server for Calibre E-book Library Management

Efficient and secure access to Calibre libraries, supporting both local and remote access.
Provides tools for browsing, searching, and managing e-books with proper authentication.
"""

__version__ = "1.0.0"
__author__ = "Sandra"
__description__ = "FastMCP 2.10.1 server for Calibre e-book library management"

# Core exports - clean imports
# Import tools to register them with the MCP server
from . import tools  # noqa: F401
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
from .server import create_app, mcp
from .storage import LocalStorage, StorageBackend

__all__ = [
    "mcp",
    "CalibreConfig",
    "CalibreAPIClient",
    "CalibreAPIError",
    "CalibreError",
    "BookNotFoundError",
    "create_app",
    "Config",
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
    "BookMetadata",
    "BookFormat",
    "BookStatus",
    "StorageBackend",
    "LocalStorage",
]
