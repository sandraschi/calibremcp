"""
Basic tests for Calibre MCP server.

These tests verify the basic functionality of the Calibre MCP server.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path for local testing
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the server module
from calibre_mcp import _get_mcp, CalibreConfig, CalibreAPIClient
from calibre_mcp.server import mcp

# Test configuration
TEST_LIBRARY_PATH = str(Path.home() / "Calibre Library")


def test_imports():
    """Test that all required modules can be imported."""
    # This just verifies that the imports work
    assert mcp is not None
    assert CalibreConfig is not None
    assert CalibreAPIClient is not None


def test_mcp_initialization():
    """Test that the MCP server initializes correctly."""
    # The mcp object should be an instance of FastMCP
    assert hasattr(mcp, "tool"), "mcp should have a 'tool' decorator"
    assert callable(mcp.tool), "mcp.tool should be callable"


def test_config_defaults():
    """Test that the config has the expected defaults."""
    config = CalibreConfig()

    # Check some default values
    assert config.server_url == "http://localhost:8080"
    assert config.timeout == 30
    assert config.default_limit == 50
    assert config.max_limit == 200
    assert config.library_name == "main"


@patch("calibre_mcp.calibre_api.httpx.AsyncClient")
def test_calibre_api_client(mock_client):
    """Test the Calibre API client initialization."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"version": "6.0.0", "title": "Test Library"}

    # Configure the mock client
    mock_instance = mock_client.return_value.__aenter__.return_value
    mock_instance.get.return_value = mock_response

    # Test the client
    config = CalibreConfig(server_url="http://localhost:8080")
    client = CalibreAPIClient(config)

    # Verify the client was created with the correct config
    assert client.config.server_url == "http://localhost:8080"


if __name__ == "__main__":
    pytest.main(["-v", "test_basic.py"])
