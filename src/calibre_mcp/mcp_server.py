"""
Calibre MCP Server - FastMCP 2.10.1 compliant server for Calibre ebook management.

This module implements the MCP server interface for interacting with Calibre libraries,
providing tools for managing ebooks, metadata, and library operations.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastmcp import FastMCP, MCPServerError

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
                
        raise MCPServerError(
            "Could not find Calibre library. Please specify the library path."
        )
    
    def _setup_tools(self) -> None:
        """Register all MCP tools from the tools directory."""
        # Import the register_tools function from the tools package
        from .tools import register_tools
        
        # Register all tools from the tools package
        register_tools(self.mcp)
        
        # Register any server-specific tools here
        self.mcp.tool(
            name="get_library_info",
            description="Get information about the current Calibre library",
            parameters={},
        )(self.get_library_info)
        
        logger.info(f"Registered {len(self.mcp.tools)} tools")
    
    async def get_library_info(self) -> Dict[str, Any]:
        """Get information about the current Calibre library.
        
        Returns:
            Dictionary containing library information.
        """
        try:
            # This would be replaced with actual Calibre API calls
            return {
                "library_path": str(self.library_path),
                "book_count": 0,  # Would be populated with actual count
                "formats": [],    # Would list available formats
                "last_updated": None,  # Would be actual timestamp
            }
        except Exception as e:
            logger.error(f"Error getting library info: {e}")
            raise MCPServerError(f"Failed to get library info: {e}")
    
    async def list_books(
        self,
        query: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """List books in the library with optional filtering.
        
        Args:
            query: Search query to filter books.
            limit: Maximum number of books to return.
            offset: Offset for pagination.
            
        Returns:
            Dictionary containing book list and pagination info.
        """
        try:
            # This would be replaced with actual Calibre API calls
            books = [
                {
                    "id": 1,
                    "title": "Example Book 1",
                    "authors": ["Author One", "Author Two"],
                    "formats": ["EPUB", "PDF"],
                    "tags": ["fiction", "sci-fi"],
                    "rating": 4.5,
                    "publisher": "Example Publisher",
                    "pubdate": "2023-01-01",
                    "size": 1024000,  # in bytes
                },
                # More example books...
            ]
            
            # Apply pagination (would be done by Calibre in real implementation)
            paginated_books = books[offset : offset + limit]
            
            return {
                "books": paginated_books,
                "total_count": len(books),
                "offset": offset,
                "limit": limit,
            }
            
        except Exception as e:
            logger.error(f"Error listing books: {e}")
            raise MCPServerError(f"Failed to list books: {e}")
    
    async def get_book(self, book_id: int) -> Dict[str, Any]:
        """Get details for a specific book.
        
        Args:
            book_id: ID of the book to retrieve.
            
        Returns:
            Dictionary containing book details.
        """
        try:
            # This would be replaced with actual Calibre API calls
            if book_id == 1:
                return {
                    "id": book_id,
                    "title": "Example Book 1",
                    "authors": ["Author One", "Author Two"],
                    "formats": ["EPUB", "PDF"],
                    "tags": ["fiction", "sci-fi"],
                    "rating": 4.5,
                    "publisher": "Example Publisher",
                    "pubdate": "2023-01-01",
                    "size": 1024000,  # in bytes
                    "description": "This is an example book description.",
                    "series": "Example Series",
                    "series_index": 1,
                    "languages": ["English"],
                    "identifiers": {
                        "isbn": "1234567890",
                        "goodreads": "12345678",
                    },
                }
            else:
                raise MCPServerError(f"Book with ID {book_id} not found")
                
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
