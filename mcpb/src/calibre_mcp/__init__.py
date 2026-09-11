"""
CalibreMCP - FastMCP 2.14.1+ Server for Calibre E-book Library Management
"""

import contextlib
import os
import sys
import warnings
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _metadata_version

from pydantic import PydanticDeprecatedSince20

from .calibre_api import CalibreAPIClient, CalibreAPIError
from .config import CalibreConfig
from .exceptions import BookNotFoundError, CalibreError
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
)
from .storage import LocalStorage, StorageBackend

try:
    __version__ = _metadata_version("calibremcp")
except PackageNotFoundError:
    __version__ = "1.8.6"
__author__ = "Sandra"
__description__ = "FastMCP 2.14.1+ server for Calibre e-book library management"

warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"
with contextlib.suppress(ImportError):
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

_is_stdio = not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True

_original_stdout = sys.stdout
_original_stderr = sys.stderr

# DO NOT import server or tools here - causes circular import deadlock
# Server and tools are imported only when actually running the server
# from .server import create_app, mcp
# from . import tools


# Lazy import for mcp instance to avoid circular imports in tests
def _get_mcp():
    """Lazy import of mcp instance for testing."""
    from .server import mcp

    return mcp


def main():
    """Run the CalibreMCP server."""
    import asyncio

    from .server import main as server_main

    asyncio.run(server_main())


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
    "main",
]
