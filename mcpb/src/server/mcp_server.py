"""
MCP (Message Control Protocol) Server for Calibre MCP.

This module implements the stdio-based MCP server that communicates with the host application.
"""

import asyncio
import logging
import signal
import sys
from typing import Any

from fastmcp import MCPMessage, MCPServer

from ..tools.compat import MCPServerError
from .config import settings
from .core.exception_handlers import BookNotFoundError, CalibreError

logger = logging.getLogger(__name__)


class CalibreMCPServer(MCPServer):
    """Calibre MCP Server implementation."""

    def __init__(self, library_path: str | None = None, **kwargs):
        """Initialize the MCP server.

        Args:
            library_path: Path to the Calibre library
            **kwargs: Additional arguments passed to MCPServer
        """
        super().__init__(**kwargs)
        self.library_path = library_path
        self.running = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

        # Register MCP commands
        self.register_command("ping", self.handle_ping)
        self.register_command("get_books", self.handle_get_books)
        self.register_command("get_book", self.handle_get_book)
        self.register_command("add_book", self.handle_add_book)
        self.register_command("update_book", self.handle_update_book)
        self.register_command("delete_book", self.handle_delete_book)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutting down MCP server...")
        self.running = False

        # Close the event loop if it exists
        try:
            loop = asyncio.get_running_loop()
            loop.stop()
        except RuntimeError:
            pass

    async def start(self):
        """Start the MCP server."""
        if self.running:
            return

        self.running = True
        logger.info("Starting Calibre MCP Server")

        try:
            # Start the MCP server
            await super().start()

            # Keep the server running
            while self.running:
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("MCP server was cancelled")
        except Exception:
            logger.exception("Error in MCP server")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the MCP server."""
        if not self.running:
            return

        logger.info("Stopping MCP server...")
        self.running = False

        try:
            await super().stop()
        except Exception:
            logger.exception("Error stopping MCP server")

    # Command handlers

    async def handle_ping(self, message: MCPMessage) -> dict[str, Any]:
        """Handle ping command."""
        return {"status": "ok", "message": "pong"}

    async def handle_get_books(self, message: MCPMessage) -> dict[str, Any]:
        """Handle get_books command."""
        try:
            # TODO: Implement actual book listing from Calibre library
            books = [
                {"id": 1, "title": "Sample Book 1", "author": "Author 1"},
                {"id": 2, "title": "Sample Book 2", "author": "Author 2"},
            ]
            return {"status": "ok", "books": books}
        except Exception as e:
            raise MCPServerError(f"Failed to get books: {str(e)}")

    async def handle_get_book(self, message: MCPMessage) -> dict[str, Any]:
        """Handle get_book command."""
        try:
            book_id = message.params.get("id")
            if not book_id:
                raise MCPServerError("Missing required parameter: id")

            # TODO: Implement actual book retrieval from Calibre library
            if book_id == "1":
                book = {"id": 1, "title": "Sample Book 1", "author": "Author 1"}
            else:
                raise BookNotFoundError(book_id)

            return {"status": "ok", "book": book}

        except CalibreError:
            raise
        except Exception as e:
            raise MCPServerError(f"Failed to get book: {str(e)}")

    async def handle_add_book(self, message: MCPMessage) -> dict[str, Any]:
        """Handle add_book command."""
        try:
            # TODO: Implement actual book addition to Calibre library
            book_data = message.params.get("book")
            if not book_data:
                raise MCPServerError("Missing required parameter: book")

            # Simulate adding a book
            book_id = 123  # Would come from the database

            return {"status": "ok", "message": "Book added successfully", "book_id": book_id}

        except Exception as e:
            raise MCPServerError(f"Failed to add book: {str(e)}")

    async def handle_update_book(self, message: MCPMessage) -> dict[str, Any]:
        """Handle update_book command."""
        try:
            book_id = message.params.get("id")
            updates = message.params.get("updates", {})

            if not book_id:
                raise MCPServerError("Missing required parameter: id")

            if not updates:
                raise MCPServerError("No updates provided")

            # TODO: Implement actual book update in Calibre library

            return {"status": "ok", "message": "Book updated successfully", "book_id": book_id}

        except Exception as e:
            raise MCPServerError(f"Failed to update book: {str(e)}")

    async def handle_delete_book(self, message: MCPMessage) -> dict[str, Any]:
        """Handle delete_book command."""
        try:
            book_id = message.params.get("id")
            if not book_id:
                raise MCPServerError("Missing required parameter: id")

            # TODO: Implement actual book deletion from Calibre library

            return {"status": "ok", "message": "Book deleted successfully", "book_id": book_id}

        except Exception as e:
            raise MCPServerError(f"Failed to delete book: {str(e)}")


def create_mcp_server(library_path: str | None = None) -> CalibreMCPServer:
    """Create and configure the MCP server."""
    return CalibreMCPServer(
        library_path=library_path or settings.LIBRARY_PATH, name="calibre-mcp", version="0.1.0"
    )


def run_mcp_server(library_path: str | None = None):
    """Run the MCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    # Create and run the server
    server = create_mcp_server(library_path)

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception:
        logger.exception("Error in MCP server")
        sys.exit(1)
    finally:
        asyncio.run(server.stop())


if __name__ == "__main__":
    run_mcp_server()
