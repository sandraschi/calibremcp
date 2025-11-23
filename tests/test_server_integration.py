"""
Integration tests for the Calibre MCP server.

These tests verify that the server is properly set up and can handle requests.
"""

import os
import sys
from pathlib import Path
from typing import Dict

import pytest
import pytest_asyncio

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the server module
from calibre_mcp.server import mcp
from calibre_mcp.config import CalibreConfig


class TestCalibreMCPServer:
    """Integration tests for the Calibre MCP server."""

    @pytest_asyncio.fixture
    async def client(self):
        """Create a test client that uses the FastMCP instance."""
        # Create a test config with authentication
        config = CalibreConfig(
            username="admin",  # Default Calibre username
            password="admin123",  # Default Calibre password
            server_url="http://localhost:8080",  # Default Calibre server URL
        )

        # Set environment variables for authentication
        os.environ["CALIBRE_USERNAME"] = config.username or ""
        os.environ["CALIBRE_PASSWORD"] = config.password or ""

        # Get all registered tools from the FastMCP instance
        tools = await mcp.get_tools()
        print("\nRegistered tools in FastMCP instance:")
        for tool_name in tools:
            print(f"- {tool_name}")
        print()  # Add a newline for better readability

        # Create a test client that calls MCP tools through the FastMCP instance
        async def call_method(method: str, params: Dict = None) -> Dict:
            try:
                # Get the tool from the FastMCP instance
                tools = await mcp.get_tools()
                if method not in tools:
                    return {
                        "error": f"Tool '{method}' not found in FastMCP instance. Available tools: {', '.join(tools.keys())}"
                    }

                # Get the tool and call its run() method
                tool = tools[method]
                tool_result = await tool.run(arguments=params or {})
                # The actual data is in the 'data' attribute of the ToolResult
                return {"result": tool_result.data}

            except Exception as e:
                return {"error": str(e), "type": type(e).__name__}

        yield call_method

    @pytest.mark.asyncio
    async def test_server_initialization(self, client):
        """Test that the server initializes correctly and responds to requests."""
        # Test a simple method to verify the server is working
        response = await client("list_books", {"limit": 1})
        assert "result" in response, f"Expected 'result' in response, got: {response}"
        assert "error" not in response, f"Server returned an error: {response.get('error')}"
        assert isinstance(response["result"], list), (
            f"Expected result to be a list, got: {type(response['result'])}"
        )

    @pytest.mark.asyncio
    async def test_list_books_method(self, client):
        """Test the list_books method."""
        response = await client("list_books", {"limit": 5})
        assert "result" in response, f"Expected 'result' in response, got: {response}"
        assert "error" not in response, f"Server returned an error: {response.get('error')}"
        assert isinstance(response["result"], list), (
            f"Expected result to be a list, got: {type(response['result'])}"
        )

    @pytest.mark.asyncio
    async def test_manage_books_details_method(self, client):
        """Test the manage_books details operation."""
        # First, get a list of books to get a valid book ID
        list_response = await client("query_books", {"operation": "list", "limit": 1})

        if not list_response.get("result") or not list_response["result"].get("items"):
            pytest.skip("No books found in the library to test with")

        book_id = list_response["result"]["items"][0].get("id")

        if not book_id:
            pytest.skip("Could not get a valid book ID from the server")

        # Now test getting book details using manage_books portmanteau tool
        response = await client("manage_books", {"operation": "details", "book_id": str(book_id)})
        assert "result" in response, f"Expected 'result' in response, got: {response}"
        assert "error" not in response, f"Server returned an error: {response.get('error')}"
        assert response["result"].get("success") is True
        assert "book" in response["result"]

    @pytest.mark.asyncio
    async def test_query_books_search_method(self, client):
        """Test the query_books search operation."""
        response = await client("query_books", {"operation": "search", "text": "test"})
        assert "result" in response, f"Expected 'result' in response, got: {response}"
        assert "error" not in response, f"Server returned an error: {response.get('error')}"
        assert isinstance(response["result"], list), (
            f"Expected result to be a list, got: {type(response['result'])}"
        )

    @pytest.mark.asyncio
    async def test_list_libraries_method(self, client):
        """Test the list_libraries method."""
        response = await client("list_libraries", {})
        assert "result" in response, f"Expected 'result' in response, got: {response}"
        assert "error" not in response, f"Server returned an error: {response.get('error')}"
        assert isinstance(response["result"], dict), (
            f"Expected result to be a dict, got: {type(response['result'])}"
        )
        assert "libraries" in response["result"], (
            f"Expected 'libraries' in result, got: {response['result'].keys()}"
        )
        assert "current_library" in response["result"], (
            f"Expected 'current_library' in result, got: {response['result'].keys()}"
        )


if __name__ == "__main__":
    pytest.main(["-v", "test_server_integration.py"])
