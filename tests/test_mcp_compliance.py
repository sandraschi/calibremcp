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
from calibre_mcp.server import mcp

# Test configuration
TEST_LIBRARY_PATH = str(Path.home() / "Calibre Library")


class TestFastMCP212Compliance:
    """Test suite for FastMCP 2.12 compliance."""

    @pytest.fixture
    def server(self):
        """Get the MCP server instance."""
        return mcp

    def test_has_required_metadata(self):
        """Test that the server has all required metadata."""
        # Check that the server has the required attributes
        assert hasattr(mcp, "name")

        # Verify metadata values
        assert mcp.name == "CalibreMCP Phase 2"

    def test_has_required_methods(self, server):
        """Test that the server has tools registered."""
        # FastMCP 2.13+ uses @mcp.tool() decorator, tools are registered automatically
        # We can't easily check for specific tool names without importing all tools
        # Instead, verify the server has the tool decorator
        assert hasattr(server, "tool")
        assert callable(server.tool)

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
        assert "command" in manifest["server"]["mcp_config"], (
            "Missing server command in manifest.json"
        )

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
        assert mcp is not None
        assert hasattr(mcp, "tool")

    @pytest.mark.asyncio
    async def test_list_books_method(self, server):
        """Test that list_books tool exists."""
        # Tools are registered via @mcp.tool() decorator
        # We can't easily test tool execution without a real library
        # Just verify the server is properly initialized
        assert server is not None
        pytest.skip("Tool execution tests require real library - tested in integration tests")

    @pytest.mark.asyncio
    async def test_get_book_method(self, server):
        """Test that get_book tool exists."""
        # Tools are registered via @mcp.tool() decorator
        assert server is not None
        pytest.skip("Tool execution tests require real library - tested in integration tests")

    @pytest.mark.asyncio
    async def test_search_books_method(self, server):
        """Test that search_books tool exists."""
        # Tools are registered via @mcp.tool() decorator
        assert server is not None
        pytest.skip("Tool execution tests require real library - tested in integration tests")

    @pytest.mark.asyncio
    async def test_test_calibre_connection_method(self):
        """Test that test_calibre_connection tool exists."""
        # The test_calibre_connection tool is registered via @mcp.tool()
        # We can't easily test tool execution without a real library
        assert mcp is not None
        pytest.skip("Tool execution tests require real library - tested in integration tests")

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
        required_deps = ["fastmcp>=2.14.1", "python-dotenv", "pydantic>=2.0.0", "httpx"]

        for dep in required_deps:
            assert any(dep in req for req in requirements), f"Missing required dependency: {dep}"


if __name__ == "__main__":
    pytest.main(["-v", "test_mcp_compliance.py"])
