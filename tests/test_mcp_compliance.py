"""
Calibre MCP Server - FastMCP 2.12 Compliance Tests

This test suite verifies that the Calibre MCP server is fully compliant
with FastMCP 2.12 standards and MCPB packaging requirements.
"""

import json
import sys
from pathlib import Path

import pytest

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the server module
from src.calibre_mcp.server import (
    CalibreMCPServer,
    test_calibre_connection,
)

# Test configuration
TEST_LIBRARY_PATH = str(Path.home() / "Calibre Library")


class TestFastMCP212Compliance:
    """Test suite for FastMCP 2.12 compliance."""

    @pytest.fixture
    def server(self):
        """Create a test server instance."""
        return CalibreMCPServer(library_path=TEST_LIBRARY_PATH, debug=True)

    def test_has_required_metadata(self):
        """Test that the server has all required metadata."""
        # Check that the server has the required attributes
        server = CalibreMCPServer(library_path=TEST_LIBRARY_PATH)
        
        # Required FastMCP 2.12 attributes
        assert hasattr(server, "name")
        assert hasattr(server, "version")
        assert hasattr(server, "description")
        
        # Verify metadata values
        assert server.name == "calibre-mcp"
        assert isinstance(server.version, str)
        assert "." in server.version  # Version should be in semver format
        assert len(server.description) > 0

    def test_has_required_methods(self, server):
        """Test that the server implements all required methods."""
        # Required FastMCP methods
        required_methods = [
            "list_books",
            "get_book",
            "search_books",
            "test_calibre_connection",
            "list_libraries",
            "switch_library",
            "get_library_stats",
            "cross_library_search",
        ]
        
        for method in required_methods:
            assert hasattr(server, method), f"Missing required method: {method}"
            assert callable(getattr(server, method)), f"{method} is not callable"

    def test_mcpb_manifest_exists(self):
        """Test that the MCPB manifest file exists and is valid JSON."""
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        assert manifest_path.exists(), "manifest.json not found"
        
        # Verify it's valid JSON
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in manifest.json: {e}")
        
        # Check required MCPB fields
        required_fields = ["manifest_version", "name", "version", "server"]
        
        for field in required_fields:
            assert field in manifest, f"Missing required field in manifest.json: {field}"
        
        # Check server configuration
        assert "type" in manifest["server"], "Missing server type in manifest.json"
        assert "entry_point" in manifest["server"], "Missing server entry_point in manifest.json"
        
        # Check MCP configuration
        assert "mcp_config" in manifest["server"], "Missing mcp_config in manifest.json"
        assert "command" in manifest["server"]["mcp_config"], "Missing server command in manifest.json"
        
        # Check user configuration
        assert "user_config" in manifest, "Missing user_config in manifest.json"
        assert isinstance(manifest["user_config"], dict), "user_config should be a dictionary"
        
        # Check tools
        assert "tools" in manifest, "Missing tools in manifest.json"
        assert isinstance(manifest["tools"], list), "Tools should be a list"
        assert len(manifest["tools"]) > 0, "No tools defined in manifest.json"

    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that the server initializes correctly."""
        server = CalibreMCPServer(library_path=TEST_LIBRARY_PATH)
        assert server is not None
        
        # Verify the API client is initialized
        assert hasattr(server, "api_client")
        
        # Verify the library path is set
        assert server.library_path == TEST_LIBRARY_PATH
        
        # Verify available libraries
        assert isinstance(server.available_libraries, dict)
        assert "main" in server.available_libraries  # Should have at least the main library

    @pytest.mark.asyncio
    async def test_list_books_method(self, server):
        """Test the list_books method."""
        # This is a basic test - actual implementation may vary
        try:
            result = await server.list_books(limit=5)
            
            # Verify the result has the expected structure
            assert isinstance(result, list)
            
            # If there are books, verify their structure
            if result:
                book = result[0]
                assert hasattr(book, "book_id")
                assert hasattr(book, "title")
                assert hasattr(book, "authors")
                assert isinstance(book.authors, list)
        except Exception as e:
            pytest.fail(f"list_books failed: {e}")

    @pytest.mark.asyncio
    async def test_get_book_method(self, server):
        """Test the get_book method."""
        # First get a list of books to test with
        books = await server.list_books(limit=1)
        
        if not books:
            pytest.skip("No books found in the library to test with")
        
        # Test getting book details
        book_id = books[0].book_id
        book = await server.get_book(book_id)
        
        # Verify the result
        assert book is not None
        assert book.book_id == book_id
        assert hasattr(book, "title")
        assert hasattr(book, "authors")
        assert isinstance(book.authors, list)

    @pytest.mark.asyncio
    async def test_search_books_method(self, server):
        """Test the search_books method."""
        # Test with a simple query
        results = await server.search_books("test")
        
        # Verify the result structure
        assert isinstance(results, list)
        
        # If there are results, verify their structure
        if results:
            book = results[0]
            assert hasattr(book, "book_id")
            assert hasattr(book, "title")
            assert hasattr(book, "authors")

    @pytest.mark.asyncio
    async def test_test_calibre_connection_method(self):
        """Test the test_calibre_connection method."""
        result = await test_calibre_connection()
        
        # Verify the result structure
        assert hasattr(result, "connected")
        assert isinstance(result.connected, bool)
        
        if result.connected:
            assert hasattr(result, "server_version")
            assert hasattr(result, "library_name")
            assert hasattr(result, "total_books")

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists and has required fields."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"
        
        # Basic check for required sections
        pyproject_content = pyproject_path.read_text(encoding="utf-8")
        assert "[build-system]" in pyproject_content
        assert "[project]" in pyproject_content
        assert "name = " in pyproject_content
        assert "version = " in pyproject_content

    def test_requirements_txt_exists(self):
        """Test that requirements.txt exists."""
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt not found"
        
        # Check for required dependencies
        requirements = requirements_path.read_text(encoding="utf-8").splitlines()
        required_deps = ["fastmcp>=2.12.0", "python-dotenv", "pydantic>=2.0.0", "httpx"]
        
        for dep in required_deps:
            assert any(dep in req for req in requirements), f"Missing required dependency: {dep}"


if __name__ == "__main__":
    pytest.main(["-v", "test_mcp_compliance.py"])
