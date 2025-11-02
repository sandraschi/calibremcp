#!/usr/bin/env python3
"""
Integration tests for CalibreMCP Server Tools
Test complete MCP tool workflows and Claude Desktop integration
"""

import unittest
from unittest.mock import AsyncMock, patch
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibre_mcp.server import (
    list_books,
    get_book_details,
    search_books,
    test_calibre_connection,
    LibrarySearchResponse,
    BookDetailResponse,
    ConnectionTestResponse,
)
from calibre_mcp.calibre_api import CalibreAPIError


class TestMCPToolIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for MCP tools"""

    def setUp(self):
        """Set up test environment"""
        self.mock_books_data = [
            {
                "id": 1,
                "title": "Python Programming",
                "authors": ["Guido van Rossum"],
                "series": "Programming Series",
                "series_index": 1,
                "rating": 5,
                "tags": ["programming", "python"],
                "languages": ["en"],
                "formats": ["EPUB", "PDF"],
                "last_modified": "2025-01-15",
                "cover_url": "http://localhost:8080/get/cover/1",
            },
            {
                "id": 2,
                "title": "JavaScript Guide",
                "authors": ["Brendan Eich"],
                "series": None,
                "series_index": None,
                "rating": 4,
                "tags": ["programming", "javascript"],
                "languages": ["en"],
                "formats": ["EPUB"],
                "last_modified": "2025-01-10",
                "cover_url": "http://localhost:8080/get/cover/2",
            },
        ]

    @patch("calibre_mcp.server.get_api_client")
    async def test_list_books_success(self, mock_get_client):
        """Test successful list_books operation"""
        # Mock API client
        mock_client = AsyncMock()
        mock_client.search_library.return_value = self.mock_books_data
        mock_get_client.return_value = mock_client

        # Test list_books
        result = await list_books(query="programming", limit=25, sort="rating")

        # Verify response structure
        self.assertIsInstance(result, LibrarySearchResponse)
        self.assertEqual(len(result.results), 2)
        self.assertEqual(result.total_found, 2)
        self.assertEqual(result.query_used, "programming")
        self.assertGreater(result.search_time_ms, 0)

        # Verify first book result
        book1 = result.results[0]
        self.assertEqual(book1.book_id, 1)
        self.assertEqual(book1.title, "Python Programming")
        self.assertEqual(book1.authors, ["Guido van Rossum"])
        self.assertEqual(book1.series, "Programming Series")
        self.assertEqual(book1.rating, 5)
        self.assertIn("programming", book1.tags)
        self.assertIn("EPUB", book1.formats)

        # Verify API was called correctly
        mock_client.search_library.assert_called_once_with(
            query="programming", limit=25, sort="rating"
        )

    @patch("calibre_mcp.server.get_api_client")
    async def test_list_books_no_query(self, mock_get_client):
        """Test list_books without query (browse all)"""
        mock_client = AsyncMock()
        mock_client.search_library.return_value = self.mock_books_data
        mock_get_client.return_value = mock_client

        result = await list_books(limit=50, sort="title")

        self.assertIsInstance(result, LibrarySearchResponse)
        self.assertEqual(len(result.results), 2)
        self.assertIsNone(result.query_used)

        mock_client.search_library.assert_called_once_with(query=None, limit=50, sort="title")

    @patch("calibre_mcp.server.get_api_client")
    async def test_list_books_error_handling(self, mock_get_client):
        """Test list_books error handling"""
        mock_client = AsyncMock()
        mock_client.search_library.side_effect = CalibreAPIError("Connection failed")
        mock_get_client.return_value = mock_client

        result = await list_books(query="test")

        # Should return empty response on error
        self.assertIsInstance(result, LibrarySearchResponse)
        self.assertEqual(len(result.results), 0)
        self.assertEqual(result.total_found, 0)
        self.assertEqual(result.search_time_ms, 0)

    @patch("calibre_mcp.server.get_api_client")
    async def test_list_books_limit_validation(self, mock_get_client):
        """Test list_books limit validation"""
        mock_client = AsyncMock()
        mock_client.search_library.return_value = []
        mock_get_client.return_value = mock_client

        # Test limit too high
        await list_books(limit=500)
        mock_client.search_library.assert_called_with(
            query=None,
            limit=200,
            sort="title",  # Should cap at 200
        )

        # Test limit too low
        await list_books(limit=0)
        mock_client.search_library.assert_called_with(
            query=None,
            limit=1,
            sort="title",  # Should enforce minimum 1
        )

    @patch("calibre_mcp.server.get_api_client")
    async def test_get_book_details_success(self, mock_get_client):
        """Test successful get_book_details operation"""
        mock_client = AsyncMock()
        mock_book_data = {
            "title": "Advanced Python",
            "authors": ["Expert Author"],
            "series": "Python Mastery",
            "series_index": 2,
            "rating": 5,
            "tags": ["python", "advanced"],
            "comments": "Comprehensive guide to advanced Python features",
            "published": "2024-01-01",
            "languages": ["en"],
            "formats": ["EPUB", "PDF", "MOBI"],
            "identifiers": {"isbn": "1234567890", "goodreads": "987654"},
            "last_modified": "2025-01-20",
            "cover_url": "http://localhost:8080/get/cover/123",
            "download_links": {
                "EPUB": "http://localhost:8080/get/EPUB/123",
                "PDF": "http://localhost:8080/get/PDF/123",
            },
        }
        mock_client.get_book_details.return_value = mock_book_data
        mock_get_client.return_value = mock_client

        result = await get_book_details(123)

        # Verify response structure
        self.assertIsInstance(result, BookDetailResponse)
        self.assertEqual(result.book_id, 123)
        self.assertEqual(result.title, "Advanced Python")
        self.assertEqual(result.authors, ["Expert Author"])
        self.assertEqual(result.series, "Python Mastery")
        self.assertEqual(result.series_index, 2)
        self.assertEqual(result.rating, 5)
        self.assertIn("python", result.tags)
        self.assertEqual(result.comments, "Comprehensive guide to advanced Python features")
        self.assertEqual(result.published, "2024-01-01")
        self.assertIn("EPUB", result.formats)
        self.assertEqual(result.identifiers["isbn"], "1234567890")
        self.assertIn("EPUB", result.download_links)

        mock_client.get_book_details.assert_called_once_with(123)

    @patch("calibre_mcp.server.get_api_client")
    async def test_get_book_details_not_found(self, mock_get_client):
        """Test get_book_details for non-existent book"""
        mock_client = AsyncMock()
        mock_client.get_book_details.return_value = None
        mock_get_client.return_value = mock_client

        result = await get_book_details(99999)

        self.assertIsInstance(result, BookDetailResponse)
        self.assertEqual(result.book_id, 99999)
        self.assertEqual(result.title, "Book not found")
        self.assertEqual(result.authors, [])
        self.assertEqual(result.formats, [])

    @patch("calibre_mcp.server.get_api_client")
    async def test_get_book_details_error_handling(self, mock_get_client):
        """Test get_book_details error handling"""
        mock_client = AsyncMock()
        mock_client.get_book_details.side_effect = CalibreAPIError("Server error")
        mock_get_client.return_value = mock_client

        result = await get_book_details(123)

        self.assertIsInstance(result, BookDetailResponse)
        self.assertEqual(result.book_id, 123)
        self.assertIn("Error:", result.title)

    @patch("calibre_mcp.server.get_api_client")
    async def test_search_books_success(self, mock_get_client):
        """Test successful search_books operation"""
        mock_client = AsyncMock()
        mock_client.advanced_search.return_value = self.mock_books_data
        mock_get_client.return_value = mock_client

        result = await search_books(text="programming", fields=["title", "tags"], operator="OR")

        # Verify response structure
        self.assertIsInstance(result, LibrarySearchResponse)
        self.assertEqual(len(result.results), 2)
        self.assertEqual(result.total_found, 2)
        self.assertIn("programming", result.query_used)
        self.assertIn("title, tags", result.query_used)
        self.assertIn("(OR)", result.query_used)

        # Verify API was called correctly
        mock_client.advanced_search.assert_called_once_with(
            text="programming", fields=["title", "tags"], operator="OR"
        )

    @patch("calibre_mcp.server.get_api_client")
    async def test_search_books_default_fields(self, mock_get_client):
        """Test search_books with default fields"""
        mock_client = AsyncMock()
        mock_client.advanced_search.return_value = []
        mock_get_client.return_value = mock_client

        await search_books(text="test")

        # Should use default fields
        mock_client.advanced_search.assert_called_once_with(
            text="test", fields=["title", "authors", "tags", "comments"], operator="AND"
        )

    @patch("calibre_mcp.server.get_api_client")
    async def test_search_books_and_operator(self, mock_get_client):
        """Test search_books with AND operator"""
        mock_client = AsyncMock()
        mock_client.advanced_search.return_value = []
        mock_get_client.return_value = mock_client

        await search_books(text="python", fields=["title", "authors"], operator="AND")

        mock_client.advanced_search.assert_called_once_with(
            text="python", fields=["title", "authors"], operator="AND"
        )

    @patch("calibre_mcp.server.get_api_client")
    async def test_test_calibre_connection_success(self, mock_get_client):
        """Test successful connection test"""
        mock_client = AsyncMock()
        mock_server_info = {
            "version": "6.0.0",
            "library_name": "Sandra's Library",
            "total_books": 1250,
            "capabilities": ["search", "metadata", "covers", "downloads"],
        }
        mock_client.test_connection.return_value = mock_server_info
        mock_get_client.return_value = mock_client

        result = await test_calibre_connection()

        # Verify response structure
        self.assertIsInstance(result, ConnectionTestResponse)
        self.assertTrue(result.connected)
        self.assertEqual(result.server_version, "6.0.0")
        self.assertEqual(result.library_name, "Sandra's Library")
        self.assertEqual(result.total_books, 1250)
        self.assertGreater(result.response_time_ms, 0)
        self.assertIsNone(result.error_message)
        self.assertIn("search", result.server_capabilities)

        mock_client.test_connection.assert_called_once()

    @patch("calibre_mcp.server.get_api_client")
    async def test_test_calibre_connection_failure(self, mock_get_client):
        """Test connection test failure"""
        mock_client = AsyncMock()
        mock_client.test_connection.side_effect = CalibreAPIError("Connection refused")
        mock_get_client.return_value = mock_client

        result = await test_calibre_connection()

        self.assertIsInstance(result, ConnectionTestResponse)
        self.assertFalse(result.connected)
        self.assertIsNone(result.server_version)
        self.assertIsNone(result.library_name)
        self.assertIsNone(result.total_books)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Connection refused", result.error_message)
        self.assertEqual(result.server_capabilities, [])


class TestWorkflowIntegration(unittest.IsolatedAsyncioTestCase):
    """Test complete workflow scenarios"""

    @patch("calibre_mcp.server.get_api_client")
    async def test_book_discovery_workflow(self, mock_get_client):
        """Test complete book discovery workflow"""
        mock_client = AsyncMock()

        # Step 1: Browse recent books
        recent_books = [
            {"id": 1, "title": "New Book", "authors": ["Author"], "tags": [], "formats": ["EPUB"]}
        ]
        mock_client.search_library.return_value = recent_books
        mock_get_client.return_value = mock_client

        browse_result = await list_books(sort="date", limit=10)
        self.assertEqual(len(browse_result.results), 1)

        # Step 2: Search for specific topic
        programming_books = [
            {
                "id": 2,
                "title": "Python Guide",
                "authors": ["Coder"],
                "tags": ["programming"],
                "formats": ["PDF"],
            }
        ]
        mock_client.advanced_search.return_value = programming_books

        search_result = await search_books("python programming", ["title", "tags"])
        self.assertEqual(len(search_result.results), 1)

        # Step 3: Get detailed information
        book_details = {
            "title": "Python Guide",
            "authors": ["Coder"],
            "formats": ["PDF", "EPUB"],
            "download_links": {"PDF": "http://localhost:8080/get/PDF/2"},
        }
        mock_client.get_book_details.return_value = book_details

        details_result = await get_book_details(2)
        self.assertEqual(details_result.title, "Python Guide")
        self.assertIn("PDF", details_result.formats)

    @patch("calibre_mcp.server.get_api_client")
    async def test_library_health_check_workflow(self, mock_get_client):
        """Test library health check workflow"""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Test connection first
        mock_client.test_connection.return_value = {
            "version": "6.0.0",
            "library_name": "Test Library",
            "total_books": 500,
        }

        connection_result = await test_calibre_connection()
        self.assertTrue(connection_result.connected)
        self.assertEqual(connection_result.total_books, 500)

        # Browse library to verify accessibility
        mock_client.search_library.return_value = [
            {"id": 1, "title": "Test Book", "authors": ["Author"], "tags": [], "formats": ["EPUB"]}
        ]

        browse_result = await list_books(limit=5)
        self.assertEqual(len(browse_result.results), 1)

    @patch("calibre_mcp.server.get_api_client")
    async def test_series_exploration_workflow(self, mock_get_client):
        """Test series exploration workflow"""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Search for series
        series_books = [
            {
                "id": 1,
                "title": "Foundation",
                "series": "Foundation Series",
                "series_index": 1,
                "authors": ["Isaac Asimov"],
                "tags": ["sci-fi"],
                "formats": ["EPUB"],
            },
            {
                "id": 2,
                "title": "Foundation and Empire",
                "series": "Foundation Series",
                "series_index": 2,
                "authors": ["Isaac Asimov"],
                "tags": ["sci-fi"],
                "formats": ["EPUB"],
            },
        ]
        mock_client.advanced_search.return_value = series_books

        search_result = await search_books("Foundation", ["series", "title"])
        self.assertEqual(len(search_result.results), 2)

        # Get details for first book in series
        book1_details = {
            "title": "Foundation",
            "series": "Foundation Series",
            "series_index": 1,
            "authors": ["Isaac Asimov"],
        }
        mock_client.get_book_details.return_value = book1_details

        details_result = await get_book_details(1)
        self.assertEqual(details_result.series, "Foundation Series")
        self.assertEqual(details_result.series_index, 1)


class TestErrorRecovery(unittest.IsolatedAsyncioTestCase):
    """Test error recovery and graceful degradation"""

    @patch("calibre_mcp.server.get_api_client")
    async def test_server_down_recovery(self, mock_get_client):
        """Test graceful handling when Calibre server is down"""
        mock_client = AsyncMock()
        mock_client.test_connection.side_effect = CalibreAPIError("Connection refused")
        mock_client.search_library.side_effect = CalibreAPIError("Connection refused")
        mock_get_client.return_value = mock_client

        # All operations should fail gracefully
        connection_result = await test_calibre_connection()
        self.assertFalse(connection_result.connected)

        list_result = await list_books()
        self.assertEqual(len(list_result.results), 0)

        search_result = await search_books("test")
        self.assertEqual(len(search_result.results), 0)

    @patch("calibre_mcp.server.get_api_client")
    async def test_partial_failure_recovery(self, mock_get_client):
        """Test recovery from partial failures"""
        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        # Connection works but search fails
        mock_client.test_connection.return_value = {"version": "6.0.0"}
        mock_client.search_library.side_effect = CalibreAPIError("Search timeout")

        # Connection test should succeed
        connection_result = await test_calibre_connection()
        self.assertTrue(connection_result.connected)

        # Search should fail gracefully
        search_result = await list_books("test")
        self.assertEqual(len(search_result.results), 0)


if __name__ == "__main__":
    unittest.main()
