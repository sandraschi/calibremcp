"""
Tests for the Calibre MCP server implementation.

These tests verify that the MCP server is properly implemented
and follows FastMCP 2.10 standards.
"""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp import FastMCP

# Add src to path for local testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.calibre_mcp.server import (
    CalibreMCPServer,
    BookSearchResult,
    LibraryInfo,
    test_calibre_connection,
)


@pytest.fixture
def mock_mcp():
    """Create a mock FastMCP instance for testing."""
    mcp = MagicMock(spec=FastMCP)
    mcp.tool = MagicMock(return_value=lambda f: f)  # Decorator that returns the function
    return mcp


@pytest.fixture
def calibre_server(mock_mcp, tmp_path):
    """Create a test instance of CalibreMCPServer."""
    # Create a temporary library directory
    lib_path = tmp_path / "test_library"
    lib_path.mkdir()
    
    # Create a mock metadata.db file
    (lib_path / "metadata.db").touch()
    
    # Initialize server with test library
    server = CalibreMCPServer(library_path=str(lib_path), debug=True)
    server.mcp = mock_mcp  # Replace with mock
    
    return server


@pytest.mark.asyncio
async def test_server_initialization(calibre_server):
    """Test that the server initializes correctly."""
    assert calibre_server is not None
    assert hasattr(calibre_server, "mcp")
    assert calibre_server.library_path is not None
    
    # Verify tools are registered
    assert calibre_server.mcp.tool.called
    
    # Check that the default library is set up
    assert "main" in calibre_server.available_libraries


@pytest.mark.asyncio
async def test_list_books(calibre_server):
    """Test listing books from the library."""
    # Mock the API client response
    mock_books = [
        {
            "id": 1,
            "title": "Test Book 1",
            "authors": ["Author One"],
            "formats": ["EPUB"],
            "tags": ["test"],
            "languages": ["en"],
        },
        {
            "id": 2,
            "title": "Test Book 2",
            "authors": ["Author Two"],
            "formats": ["PDF"],
            "tags": ["test"],
            "languages": ["en"],
        },
    ]
    
    # Mock the API client
    with patch("src.calibre_mcp.server.CalibreAPIClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.list_books.return_value = mock_books
        
        # Call the method
        result = await calibre_server.list_books()
        
        # Verify the result
        assert len(result) == 2
        assert result[0].title == "Test Book 1"
        assert result[1].title == "Test Book 2"
        
        # Verify the API client was called
        mock_instance.list_books.assert_called_once()


@pytest.mark.asyncio
async def test_get_book(calibre_server):
    """Test getting details for a specific book."""
    # Mock the API client response
    mock_book = {
        "id": 1,
        "title": "Test Book",
        "authors": ["Author One"],
        "formats": ["EPUB", "PDF"],
        "tags": ["test"],
        "languages": ["en"],
        "series": "Test Series",
        "series_index": 1,
        "rating": 5,
        "comments": "A test book",
    }
    
    # Mock the API client
    with patch("src.calibre_mcp.server.CalibreAPIClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.get_book.return_value = mock_book
        
        # Call the method
        result = await calibre_server.get_book(book_id=1)
        
        # Verify the result
        assert result.title == "Test Book"
        assert result.authors == ["Author One"]
        assert "EPUB" in result.formats
        
        # Verify the API client was called with the correct ID
        mock_instance.get_book.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_test_calibre_connection():
    """Test the connection test function."""
    # Mock the API client
    with patch("src.calibre_mcp.server.CalibreAPIClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.test_connection.return_value = {
            "connected": True,
            "version": "6.0.0",
            "library_name": "Test Library",
            "total_books": 100,
        }
        
        # Call the function
        result = await test_calibre_connection()
        
        # Verify the result
        assert result.connected is True
        assert result.library_name == "Test Library"
        assert result.total_books == 100


@pytest.mark.asyncio
async def test_list_libraries(calibre_server):
    """Test listing available libraries."""
    # Set up test libraries
    calibre_server.available_libraries = {
        "main": "/path/to/main/library",
        "it": "/path/to/it/library",
        "japanese": "/path/to/japanese/library",
    }
    
    # Mock the API client
    with patch("src.calibre_mcp.server.CalibreAPIClient") as mock_client:
        mock_instance = mock_client.return_value
        
        # Call the method
        result = await calibre_server.list_libraries()
        
        # Verify the result
        assert len(result.libraries) == 3
        assert result.libraries[0].name == "main"
        assert result.libraries[1].name == "it"
        assert result.libraries[2].name == "japanese"
        assert result.current_library == "main"


@pytest.mark.asyncio
async def test_switch_library(calibre_server):
    """Test switching to a different library."""
    # Set up test libraries
    calibre_server.available_libraries = {
        "main": "/path/to/main/library",
        "it": "/path/to/it/library",
    }
    
    # Mock the API client
    with patch("src.calibre_mcp.server.CalibreAPIClient") as mock_client:
        mock_instance = mock_client.return_value
        
        # Call the method
        result = await calibre_server.switch_library("it")
        
        # Verify the result
        assert result.current_library == "it"
        assert calibre_server.current_library == "it"
        
        # Verify the API client was reinitialized with the new library path
        mock_client.assert_called_with(
            library_path="/path/to/it/library",
            config=calibre_server.config
        )


# Add more test cases for other methods...


if __name__ == "__main__":
    pytest.main(["-v", "test_mcp_server.py"])
