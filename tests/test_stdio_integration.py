"""
Integration tests for the Calibre MCP server using STDIO interface.

These tests verify that the server is properly set up and can handle requests
through the standard input/output interface as required by FastMCP 2.10.1.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict

import pytest

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the server module


class TestCalibreMCPSTDIO:
    """Integration tests for the Calibre MCP server using STDIO interface."""

    @pytest.fixture
    async def server_process(self):
        """Start the server process for testing."""
        # Start the server in a subprocess with STDIO
        server_path = Path(__file__).parent.parent / "src" / "calibre_mcp" / "server.py"
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(server_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Give the server a moment to start
        await asyncio.sleep(1)
        
        yield process
        
        # Cleanup
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

    @pytest.fixture
    async def client(self, server_process):
        """Create a test client that communicates with the server via STDIO."""
        async def send_request(method: str, params: Dict = None, request_id: int = 1) -> Dict:
            request = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or {},
                "id": request_id
            }
            
            # Send the request
            server_process.stdin.write((json.dumps(request) + "\n").encode())
            await server_process.stdin.drain()
            
            # Read the response
            line = await server_process.stdout.readline()
            return json.loads(line.decode().strip())
            
        return send_request

    @pytest.mark.asyncio
    async def test_list_books(self, client):
        """Test the list_books method via STDIO."""
        response = await client("list_books", {"limit": 5})
        assert "result" in response
        assert isinstance(response["result"], list)

    @pytest.mark.asyncio
    async def test_get_book_details(self, client):
        """Test the get_book_details method via STDIO."""
        # First, get a list of books to get a valid book ID
        list_response = await client("list_books", {"limit": 1})
        
        if not list_response.get("result"):
            pytest.skip("No books found in the library to test with")
            
        book_id = list_response["result"][0].get("book_id")
        
        if not book_id:
            pytest.skip("Could not get a valid book ID from the server")
        
        # Now test getting book details
        response = await client("get_book_details", {"book_id": book_id})
        assert "result" in response
        assert response["result"].get("book_id") == book_id

    @pytest.mark.asyncio
    async def test_search_books(self, client):
        """Test the search_books method via STDIO."""
        response = await client("search_books", {"text": "test"})
        assert "result" in response
        assert isinstance(response["result"], list)

    @pytest.mark.asyncio
    async def test_list_libraries(self, client):
        """Test the list_libraries method via STDIO."""
        response = await client("list_libraries", {})
        assert "result" in response
        assert "libraries" in response["result"]
        assert "current_library" in response["result"]


if __name__ == "__main__":
    pytest.main(["-v", "test_stdio_integration.py"])
