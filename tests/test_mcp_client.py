"""Tests for MCP client connection and communication."""

import json
import asyncio
import pytest
from unittest.mock import AsyncMock
from typing import Dict

import httpx
from fastmcp import MCPClient, MCPTool, MCPError

# Test server configuration
TEST_SERVER_HOST = "127.0.0.1"
TEST_SERVER_PORT = 8000
TEST_SERVER_URL = f"http://{TEST_SERVER_HOST}:{TEST_SERVER_PORT}"


class TestMCPClientConnection:
    """Test suite for MCP client connection and basic operations."""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment."""
        # Create a test client
        self.client = MCPClient(TEST_SERVER_URL)

        # Mock the HTTP client
        self.mock_http_client = AsyncMock()
        self.client._client = self.mock_http_client

        # Setup default mock responses
        self.mock_http_client.get.return_value = self._mock_response(200, {"result": "pong"})

        yield

        # Cleanup
        await self.client.close()

    def _mock_response(self, status_code: int, data: Dict) -> AsyncMock:
        """Create a mock HTTP response."""
        response = AsyncMock()
        response.status_code = status_code
        response.json.return_value = data
        return response

    @pytest.mark.asyncio
    async def test_ping_server(self):
        """Test basic server ping."""
        # Setup mock response
        self.mock_http_client.get.return_value = self._mock_response(200, {"result": "pong"})

        # Call the ping method
        response = await self.client.ping()

        # Verify the response
        assert response == "pong"

        # Verify the HTTP call
        self.mock_http_client.get.assert_called_once_with("/ping")

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing available tools."""
        # Setup mock response
        mock_tools = {
            "tools": [
                {"name": "book_tools.list_books", "description": "List books"},
                {"name": "book_tools.get_book", "description": "Get book details"},
            ]
        }
        self.mock_http_client.get.return_value = self._mock_response(200, mock_tools)

        # Call the list_tools method
        tools = await self.client.list_tools()

        # Verify the response
        assert len(tools) == 2
        assert "book_tools.list_books" in [t["name"] for t in tools]

        # Verify the HTTP call
        self.mock_http_client.get.assert_called_once_with("/tools")

    @pytest.mark.asyncio
    async def test_call_tool(self):
        """Test calling a tool with parameters."""
        # Setup mock response
        mock_result = {"id": "book1", "title": "Test Book"}
        self.mock_http_client.post.return_value = self._mock_response(200, {"result": mock_result})

        # Call a tool
        result = await self.client.call_tool("book_tools.get_book", book_id="book1")

        # Verify the response
        assert result == mock_result

        # Verify the HTTP call
        self.mock_http_client.post.assert_called_once()
        call_args = self.mock_http_client.post.call_args
        assert call_args[0][0] == "/tools/call"
        assert json.loads(call_args[1]["data"]) == {
            "tool": "book_tools.get_book",
            "args": {"book_id": "book1"},
        }

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling for various scenarios."""
        # Test HTTP error
        self.mock_http_client.get.side_effect = httpx.HTTPError("Connection error")

        with pytest.raises(MCPError) as exc_info:
            await self.client.ping()
        assert "Connection error" in str(exc_info.value)

        # Test server error response
        self.mock_http_client.get.return_value = self._mock_response(
            500, {"error": "Internal server error"}
        )

        with pytest.raises(MCPError) as exc_info:
            await self.client.ping()
        assert "Internal server error" in str(exc_info.value)

        # Test invalid JSON response
        response = AsyncMock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        self.mock_http_client.get.return_value = response

        with pytest.raises(MCPError) as exc_info:
            await self.client.ping()
        assert "Invalid JSON response" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling for slow responses."""
        # Create a client with a short timeout
        client = MCPClient(TEST_SERVER_URL, timeout=0.1)

        # Setup a mock that will take longer than the timeout
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(1)  # Longer than the 0.1s timeout
            return self._mock_response(200, {"result": "pong"})

        self.mock_http_client.get.side_effect = slow_response

        # Should raise a timeout error
        with pytest.raises(MCPError) as exc_info:
            await client.ping()
        assert "timeout" in str(exc_info.value).lower()

        # Cleanup
        await client.close()


class TestMCPToolIntegration:
    """Integration tests for MCP tool usage."""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment."""
        # Create a test client
        self.client = MCPClient(TEST_SERVER_URL)

        # Mock the HTTP client
        self.mock_http_client = AsyncMock()
        self.client._client = self.mock_http_client

        # Setup default mock responses
        self.mock_http_client.get.return_value = self._mock_response(200, {"result": "pong"})

        # Define a test tool
        class TestTool(MCPTool):
            name = "test_tool"
            description = "A test tool"

            async def hello(self, name: str) -> str:
                """Say hello to someone."""
                return f"Hello, {name}!"

            async def add_numbers(self, a: int, b: int) -> int:
                """Add two numbers."""
                return a + b

        self.test_tool = TestTool()

        yield

        # Cleanup
        await self.client.close()

    def _mock_response(self, status_code: int, data: Dict) -> AsyncMock:
        """Create a mock HTTP response."""
        response = AsyncMock()
        response.status_code = status_code
        response.json.return_value = data
        return response

    @pytest.mark.asyncio
    async def test_tool_registration(self):
        """Test registering and using a tool."""
        # Register the tool with the client
        await self.client.register_tool(self.test_tool)

        # Test calling the hello method
        result = await self.test_tool.hello("World")
        assert result == "Hello, World!"

        # Test calling the add_numbers method
        result = await self.test_tool.add_numbers(2, 3)
        assert result == 5

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test error handling in tool methods."""
        # Register the tool with the client
        await self.client.register_tool(self.test_tool)

        # Test with invalid arguments
        with pytest.raises(TypeError):
            await self.test_tool.add_numbers("two", "three")

        # Test with missing arguments
        with pytest.raises(TypeError):
            await self.test_tool.add_numbers(2)  # Missing 'b' argument
