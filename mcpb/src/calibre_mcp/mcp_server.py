"""
Calibre MCP Server - FastMCP 2.10.1 compliant server for Calibre ebook management.

This module implements the MCP server interface for interacting with Calibre libraries,
providing tools for managing ebooks, metadata, and library operations.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from fastmcp import FastMCP, MCPServerError

from .db import init_database

# Import the tool registration function
from .tools import register_tools as register_all_tools

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("calibremcp")


class CalibreMCPServer:
    """MCP server for Calibre ebook management."""

    def __init__(
        self,
        library_path: Optional[Union[str, Path]] = None,
        host: str = "localhost",
        port: int = 8000,
        debug: bool = False,
    ) -> None:
        """Initialize the Calibre MCP server.

        Args:
            library_path: Path to the Calibre library. If None, will use default.
            host: Host to bind the server to.
            port: Port to bind the server to.
            debug: Enable debug logging.
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.library_path = Path(library_path) if library_path else self._find_default_library()

        if debug:
            logger.setLevel(logging.DEBUG)

        # Initialize FastMCP
        self.mcp = FastMCP(
            name="calibremcp",
            version="1.0.0",
            description="MCP server for Calibre ebook management",
        )

        # Set up tools
        self._setup_tools()

        logger.info(f"Initialized Calibre MCP server with library at {self.library_path}")

    def _find_default_library(self) -> Path:
        """Find the default Calibre library path.

        Returns:
            Path to the default Calibre library.

        Raises:
            MCPServerError: If default library cannot be found.
        """
        # Common locations for Calibre libraries
        possible_paths = [
            Path.home() / "Calibre Library",
            Path.home() / "Documents" / "Calibre Library",
            Path.home() / "My Documents" / "Calibre Library",
            Path(os.getenv("CALIBRE_LIBRARY", "")),
        ]

        for path in possible_paths:
            if path and path.exists() and (path / "metadata.db").exists():
                return path

        raise MCPServerError("Could not find Calibre library. Please specify the library path.")

    def _setup_tools(self):
        """Register all MCP tools."""
        # Initialize database connection
        db_path = str(self.library_path / "metadata.db")
        init_database(db_path)

        # Register all tools using the discovery system
        register_all_tools(self.mcp)

        # Register any server-specific tools here
        @self.mcp.tool(
            name="get_library_info", description="Get information about the current Calibre library"
        )
        async def get_library_info():
            return await self.get_library_info()

        logger.info(f"Registered {len(self.mcp.tools)} tools")

    async def get_library_info(self) -> Dict[str, Any]:
        """Get information about the current Calibre library.

        This is a legacy method kept for backward compatibility.
        Prefer using the LibraryTools methods instead.

        Returns:
            Dictionary containing library information.
        """
        from .tools.library_tools import LibraryTools

        library_tools = LibraryTools(self.mcp)

        # Get basic info
        stats = library_tools.library_service.get_library_stats()

        return {
            "path": str(self.library_path),
            "name": self.library_path.name,
            "book_count": stats.total_books,
            "author_count": stats.total_authors,
            "series_count": stats.total_series,
            "last_updated": stats.recent_books[0].timestamp.isoformat()
            if stats.recent_books
            else None,
        }

    async def list_books(
        self,
        query: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """List books in the library with optional filtering.

        This is a legacy method kept for backward compatibility.
        Prefer using the BookTools.list_books method instead.
        """
        from .tools.book_tools import BookTools

        book_tools = BookTools(self.mcp)
        return await book_tools.list_books(query=query, limit=limit, offset=offset)

    async def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Get details for a specific book.

        This is a legacy method kept for backward compatibility.
        Prefer using the BookTools.get_book method instead.

        Args:
            book_id: ID of the book to retrieve.

        Returns:
            Dictionary containing book details or None if not found.
        """
        try:
            from .tools.book_tools import BookTools

            book_tools = BookTools(self.mcp)
            return await book_tools.get_book(book_id=book_id)
        except MCPServerError:
            raise
        except Exception as e:
            logger.error(f"Error getting book {book_id}: {e}")
            raise MCPServerError(f"Failed to get book: {e}")

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info(f"Starting Calibre MCP server on {self.host}:{self.port}")
        await self.mcp.run(host=self.host, port=self.port)


async def main() -> None:
    """Run the Calibre MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="Calibre MCP Server")
    parser.add_argument(
        "--library",
        type=str,
        help="Path to Calibre library (default: auto-detect)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind to (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    try:
        server = CalibreMCPServer(
            library_path=args.library,
            host=args.host,
            port=args.port,
            debug=args.debug,
        )
        await server.run()
    except Exception as e:
        logger.error(f"Error running Calibre MCP server: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
