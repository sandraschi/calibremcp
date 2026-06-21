"""
Integration tests for the Calibre MCP server via the STDIO interface.

These tests spawn the server as a subprocess and send raw JSON-RPC messages.
They require a running/accessible Calibre library and are therefore tagged
``integration`` — they are excluded from the default CI run with ``-m 'not integration'``.
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

pytestmark = pytest.mark.integration


class TestCalibreMCPSTDIO:
    """Integration tests for the Calibre MCP server using the STDIO interface."""

    @pytest.fixture
    async def server_process(self):
        """Start the server process for STDIO testing."""
        server_path = Path(__file__).parent.parent / "src" / "calibre_mcp" / "server.py"
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(server_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.sleep(1)
        yield process
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5)
        except TimeoutError:
            process.kill()
            await process.wait()

    @pytest.fixture
    async def client(self, server_process):
        """Return a coroutine that sends a JSON-RPC request and reads the response."""

        async def send_request(method: str, params: dict | None = None, request_id: int = 1) -> dict:
            request = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or {},
                "id": request_id,
            }
            server_process.stdin.write((json.dumps(request) + "\n").encode())
            await server_process.stdin.drain()
            line = await server_process.stdout.readline()
            return json.loads(line.decode().strip())

        return send_request

    @pytest.mark.asyncio
    async def test_query_books_list(self, client):
        """query_books(operation='list') via STDIO returns a result dict."""
        response = await client("query_books", {"operation": "list", "limit": 5})
        assert "result" in response
        result = response["result"]
        assert "items" in result or "error" in result

    @pytest.mark.asyncio
    async def test_manage_books_details(self, client):
        """manage_books(operation='details') via STDIO returns details for a valid ID."""
        list_response = await client("query_books", {"operation": "list", "limit": 1})
        items = list_response.get("result", {}).get("items", [])
        if not items:
            pytest.skip("No books found in the library")
        book_id = items[0].get("id")
        if not book_id:
            pytest.skip("Could not determine a book ID")
        response = await client("manage_books", {"operation": "details", "book_id": str(book_id)})
        assert "result" in response
        assert response["result"].get("success") is True
        assert "book" in response["result"]

    @pytest.mark.asyncio
    async def test_query_books_search(self, client):
        """query_books(operation='search') via STDIO returns a result dict."""
        response = await client("query_books", {"operation": "search", "text": "test"})
        assert "result" in response
        assert "items" in response["result"] or "error" in response["result"]

    @pytest.mark.asyncio
    async def test_manage_libraries_list(self, client):
        """manage_libraries(operation='list') via STDIO returns library info."""
        response = await client("manage_libraries", {"operation": "list"})
        assert "result" in response
        result = response["result"]
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
