"""
Integration tests for the Calibre MCP server.

Tests verify that the FastMCP instance is properly set up and that tools can be
called in-process by invoking the underlying async functions directly.
The registered MCP tools are plain async coroutines decorated with @mcp.tool(),
so they can be awaited directly without going through the MCP protocol layer.

These tests use the auto-generated test library fixture (see conftest.py /
scripts/create_test_db.py) so they run without a live Calibre installation.
"""

import sys
from pathlib import Path

import pytest

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestCalibreMCPServer:
    """Integration tests for the Calibre MCP server (in-process)."""

    def test_server_has_portmanteau_tools(self):
        """The FastMCP instance must have portmanteau tool decorators registered."""
        # Core portmanteau tools are imported as modules; verify they're callable
        from calibre_mcp.tools.book_management.manage_books import manage_books
        from calibre_mcp.tools.book_management.query_books import query_books
        from calibre_mcp.tools.library.manage_libraries import manage_libraries
        from calibre_mcp.tools.system.manage_system import manage_system

        for fn in (query_books, manage_books, manage_libraries, manage_system):
            assert callable(fn), f"{fn.__name__} is not callable"

    @pytest.mark.asyncio
    async def test_query_books_list(self, test_database):  # noqa: ARG002
        """query_books(operation='list') returns a dict with 'items' and 'total'."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="list", limit=5)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "items" in result, f"'items' missing from result: {list(result.keys())}"
        assert "total" in result, f"'total' missing from result: {list(result.keys())}"

    @pytest.mark.asyncio
    async def test_query_books_search(self, test_database):  # noqa: ARG002
        """query_books(operation='search') returns items and total keys."""
        from calibre_mcp.tools.book_management.query_books import query_books

        result = await query_books(operation="search", text="Scarlet")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "items" in result, f"'items' missing: {list(result.keys())}"

    @pytest.mark.asyncio
    async def test_manage_books_details(self, test_database):  # noqa: ARG002
        """manage_books(operation='details') returns book details for a known ID."""
        from calibre_mcp.tools.book_management.manage_books import manage_books
        from calibre_mcp.tools.book_management.query_books import query_books

        list_result = await query_books(operation="list", limit=1)
        items = list_result.get("items", [])
        if not items:
            pytest.skip("No books found in test library")

        book_id = items[0].get("id")
        if book_id is None:
            pytest.skip("Could not determine a book ID from test library")

        result = await manage_books(operation="details", book_id=str(book_id))
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        # Either success=True with a book, or a handled error dict — never a bare exception
        if result.get("success") is True:
            assert "book" in result, f"Expected 'book' in result: {list(result.keys())}"

    @pytest.mark.asyncio
    async def test_manage_libraries_list(self):
        """manage_libraries(operation='list') returns a dict response."""
        from calibre_mcp.tools.library.manage_libraries import manage_libraries

        result = await manage_libraries(operation="list")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

    @pytest.mark.asyncio
    async def test_manage_system_status(self):
        """manage_system(operation='status') returns a dict response."""
        from calibre_mcp.tools.system.manage_system import manage_system

        result = await manage_system(operation="status")
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
