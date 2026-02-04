#!/usr/bin/env python3
"""
Unit tests for CalibreMCP API Client
Austrian efficiency: comprehensive testing without overthinking
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibre_mcp.calibre_api import CalibreAPIClient, CalibreAPIError
from calibre_mcp.config import CalibreConfig


class TestCalibreConfig(unittest.TestCase):
    """Test cases for CalibreConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = CalibreConfig()

        self.assertEqual(config.server_url, "http://localhost:8080")
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.default_limit, 50)
        self.assertIsNone(config.username)
        self.assertIsNone(config.password)

    def test_config_validation(self):
        """Test configuration validation"""
        # Test server URL normalization
        config = CalibreConfig(server_url="localhost:8080")
        self.assertEqual(config.server_url, "http://localhost:8080")

        config = CalibreConfig(server_url="https://example.com/")
        self.assertEqual(config.server_url, "https://example.com")

        # Test timeout validation
        config = CalibreConfig(timeout=1)
        self.assertEqual(config.timeout, 5)  # Minimum enforced

        config = CalibreConfig(timeout=1000)
        self.assertEqual(config.timeout, 300)  # Maximum enforced

    def test_auth_properties(self):
        """Test authentication properties"""
        config = CalibreConfig()
        self.assertFalse(config.has_auth)
        self.assertIsNone(config.get_auth())

        config = CalibreConfig(username="user", password="pass")
        self.assertTrue(config.has_auth)
        self.assertEqual(config.get_auth(), ("user", "pass"))

    def test_base_url_property(self):
        """Test base URL property"""
        config = CalibreConfig(server_url="http://localhost:8080")
        self.assertEqual(config.base_url, "http://localhost:8080/ajax")

    @patch.dict(
        os.environ,
        {
            "CALIBRE_SERVER_URL": "http://test.com",
            "CALIBRE_USERNAME": "testuser",
            "CALIBRE_TIMEOUT": "45",
        },
    )
    def test_environment_variables(self):
        """Test loading from environment variables"""
        config = CalibreConfig.load_config()

        self.assertEqual(config.server_url, "http://test.com")
        self.assertEqual(config.username, "testuser")
        self.assertEqual(config.timeout, 45)


class TestCalibreAPIClient(unittest.IsolatedAsyncioTestCase):
    """Test cases for CalibreAPIClient"""

    def setUp(self):
        """Set up test environment"""
        self.config = CalibreConfig(server_url="http://localhost:8080", timeout=30, max_retries=3)
        self.client = CalibreAPIClient(self.config)

    async def asyncTearDown(self):
        """Clean up after tests"""
        await self.client.close()

    async def test_client_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.config, self.config)
        self.assertIsNone(self.client._client)

        # Test client creation
        http_client = await self.client._get_client()
        self.assertIsNotNone(http_client)
        self.assertIsNotNone(self.client._client)

    @patch("httpx.AsyncClient.request")
    async def test_successful_request(self, mock_request):
        """Test successful HTTP request"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value = mock_response

        result = await self.client._make_request("test-endpoint")

        self.assertEqual(result, {"result": "success"})
        mock_request.assert_called_once()

    @patch("httpx.AsyncClient.request")
    async def test_authentication_error(self, mock_request):
        """Test authentication error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        with self.assertRaises(CalibreAPIError) as context:
            await self.client._make_request("test-endpoint")

        self.assertIn("Authentication failed", str(context.exception))

    @patch("httpx.AsyncClient.request")
    async def test_not_found_error(self, mock_request):
        """Test 404 error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        with self.assertRaises(CalibreAPIError) as context:
            await self.client._make_request("test-endpoint")

        self.assertIn("Calibre server not found", str(context.exception))

    @patch("httpx.AsyncClient.request")
    async def test_retry_logic(self, mock_request):
        """Test request retry logic"""
        # First two attempts timeout, third succeeds
        timeout_side_effect = [
            Exception("Timeout"),
            Exception("Timeout"),
            MagicMock(status_code=200, json=lambda: {"success": True}),
        ]
        mock_request.side_effect = timeout_side_effect

        # Should succeed after retries
        result = await self.client._make_request("test-endpoint")
        self.assertEqual(result, {"success": True})
        self.assertEqual(mock_request.call_count, 3)

    @patch("httpx.AsyncClient.request")
    async def test_test_connection(self, mock_request):
        """Test connection testing"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "version": "6.0.0",
            "library_map": {"": "Test Library"},
            "search_result": {"total_num": 100},
        }
        mock_request.return_value = mock_response

        result = await self.client.test_connection()

        self.assertEqual(result["version"], "6.0.0")
        self.assertEqual(result["library_name"], "Test Library")
        self.assertEqual(result["total_books"], 100)
        self.assertIn("search", result["capabilities"])

    @patch("httpx.AsyncClient.request")
    async def test_search_library(self, mock_request):
        """Test library search functionality"""
        # Mock search request
        search_response = MagicMock()
        search_response.status_code = 200
        search_response.json.return_value = {"book_ids": [1, 2, 3]}

        # Mock books metadata request
        books_response = MagicMock()
        books_response.status_code = 200
        books_response.json.return_value = {
            "1": {"title": "Book 1", "authors": ["Author 1"]},
            "2": {"title": "Book 2", "authors": ["Author 2"]},
            "3": {"title": "Book 3", "authors": ["Author 3"]},
        }

        mock_request.side_effect = [search_response, books_response]

        results = await self.client.search_library(query="test", limit=10)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["title"], "Book 1")
        self.assertEqual(results[1]["authors"], ["Author 2"])

    @patch("httpx.AsyncClient.request")
    async def test_get_book_details(self, mock_request):
        """Test getting book details"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test Book",
            "authors": ["Test Author"],
            "series": "Test Series",
            "rating": 5,
            "tags": ["fiction", "test"],
            "formats": {"EPUB": "/path/to/book.epub", "PDF": "/path/to/book.pdf"},
        }
        mock_request.return_value = mock_response

        result = await self.client.get_book_details(123)

        self.assertEqual(result["title"], "Test Book")
        self.assertEqual(result["authors"], ["Test Author"])
        self.assertEqual(result["series"], "Test Series")
        self.assertEqual(result["rating"], 5)
        self.assertIn("EPUB", result["formats"])
        self.assertIn("PDF", result["formats"])
        self.assertIn("cover_url", result)
        self.assertIn("download_links", result)

    @patch("httpx.AsyncClient.request")
    async def test_advanced_search(self, mock_request):
        """Test advanced search with field targeting"""
        # Mock search request
        search_response = MagicMock()
        search_response.status_code = 200
        search_response.json.return_value = {"book_ids": [1, 2]}

        # Mock books metadata request
        books_response = MagicMock()
        books_response.status_code = 200
        books_response.json.return_value = {
            "1": {"title": "Programming Book", "tags": ["programming"]},
            "2": {"title": "Python Guide", "tags": ["python", "programming"]},
        }

        mock_request.side_effect = [search_response, books_response]

        results = await self.client.advanced_search(
            text="programming", fields=["title", "tags"], operator="OR"
        )

        self.assertEqual(len(results), 2)
        # Verify the search query was constructed correctly
        search_call = mock_request.call_args_list[0]
        query_param = search_call[1]["params"]["query"]
        self.assertIn("title:programming OR tags:programming", query_param)

    def test_download_links_generation(self):
        """Test download link generation"""
        formats = {"EPUB": "/path/to/book.epub", "PDF": "/path/to/book.pdf"}
        links = self.client._generate_download_links(123, formats)

        expected_epub = "http://localhost:8080/get/EPUB/123"
        expected_pdf = "http://localhost:8080/get/PDF/123"

        self.assertEqual(links["EPUB"], expected_epub)
        self.assertEqual(links["PDF"], expected_pdf)


class TestErrorHandling(unittest.IsolatedAsyncioTestCase):
    """Test error handling scenarios"""

    def setUp(self):
        """Set up test environment"""
        self.config = CalibreConfig()
        self.client = CalibreAPIClient(self.config)

    async def asyncTearDown(self):
        """Clean up after tests"""
        await self.client.close()

    @patch("httpx.AsyncClient.request")
    async def test_connection_error(self, mock_request):
        """Test connection error handling"""
        mock_request.side_effect = Exception("Connection refused")

        with self.assertRaises(CalibreAPIError) as context:
            await self.client._make_request("test")

        self.assertIn("Request failed", str(context.exception))

    @patch("httpx.AsyncClient.request")
    async def test_json_decode_error(self, mock_request):
        """Test JSON decode error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Plain text response"
        mock_request.return_value = mock_response

        result = await self.client._make_request("test")
        self.assertEqual(result, {"result": "Plain text response"})

    async def test_search_with_no_results(self):
        """Test search with no results"""
        with patch.object(self.client, "_make_request") as mock_request:
            mock_request.return_value = {"book_ids": []}

            results = await self.client.search_library("nonexistent")
            self.assertEqual(results, [])

    async def test_book_details_not_found(self):
        """Test getting details for non-existent book"""
        with patch.object(self.client, "_make_request") as mock_request:
            mock_request.return_value = {}

            result = await self.client.get_book_details(99999)
            self.assertEqual(result, {})


class TestQuickLibraryTest(unittest.IsolatedAsyncioTestCase):
    """Test quick library test function"""

    @patch("calibre_mcp.calibre_api.CalibreAPIClient.test_connection")
    @patch("calibre_mcp.calibre_api.CalibreAPIClient.close")
    async def test_successful_quick_test(self, mock_close, mock_test):
        """Test successful quick library test"""
        mock_test.return_value = {"version": "6.0.0"}

        from calibre_mcp.calibre_api import quick_library_test

        result = await quick_library_test("http://localhost:8080")

        self.assertTrue(result)
        mock_test.assert_called_once()
        mock_close.assert_called_once()

    @patch("calibre_mcp.calibre_api.CalibreAPIClient.test_connection")
    @patch("calibre_mcp.calibre_api.CalibreAPIClient.close")
    async def test_failed_quick_test(self, mock_close, mock_test):
        """Test failed quick library test"""
        mock_test.side_effect = Exception("Connection failed")

        from calibre_mcp.calibre_api import quick_library_test

        result = await quick_library_test("http://localhost:8080")

        self.assertFalse(result)
        mock_close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
