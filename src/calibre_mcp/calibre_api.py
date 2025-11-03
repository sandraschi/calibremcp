"""
Calibre API Client

HTTP client for communicating with Calibre server REST API.
Handles authentication, request retries, and response parsing.
"""

from typing import List, Dict, Any, Optional
import json

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .config import CalibreConfig
from .logging_config import get_logger, log_operation, log_error

logger = get_logger("calibremcp.api")


class CalibreAPIError(Exception):
    """Custom exception for Calibre API errors"""

    pass


class CalibreAPIClient:
    """
    Async HTTP client for Calibre server API.

    Handles authentication, retries, and provides high-level
    methods for common library operations.
    """

    def __init__(self, config: CalibreConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with proper configuration"""
        if self._client is None:
            # Create client with auth and timeout settings
            auth = self.config.get_auth()
            self._client = httpx.AsyncClient(
                auth=auth,
                timeout=self.config.timeout,
                headers={
                    "User-Agent": "CalibreMCP/1.0.0 (FastMCP 2.0)",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def initialize(self) -> None:
        """
        Initialize the HTTP client eagerly.

        This is optional - the client uses lazy initialization by default.
        Calling this method pre-creates the HTTP client for early validation.
        """
        await self._get_client()

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError)
        ),
        reraise=True,
    )
    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Calibre server with automatic retry logic using tenacity.

        This method uses tenacity to automatically retry transient network errors
        (timeouts, connection errors) with exponential backoff. Authentication and
        HTTP 4xx/5xx errors are not retried as they indicate permanent failures.

        Args:
            endpoint: API endpoint (relative to base URL)
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            json_data: JSON request body

        Returns:
            Parsed JSON response

        Raises:
            CalibreAPIError: On API or network errors after all retries exhausted
        """
        client = await self._get_client()
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        try:
            response = await client.request(method=method, url=url, params=params, json=json_data)

            # Check for HTTP errors (these are NOT retried - they indicate permanent failures)
            if response.status_code == 401:
                raise CalibreAPIError(
                    "Authentication failed - check username/password. "
                    "Verify CALIBRE_USERNAME and CALIBRE_PASSWORD environment variables."
                )
            elif response.status_code == 404:
                raise CalibreAPIError(
                    f"Calibre server endpoint not found: {endpoint}. "
                    "Check server URL and ensure Calibre Content Server is running."
                )
            elif response.status_code >= 400:
                raise CalibreAPIError(
                    f"HTTP error {response.status_code}: {response.text}. "
                    f"Endpoint: {endpoint}, Method: {method}"
                )

            # Parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                # Some endpoints return plain text
                return {"result": response.text}

        except httpx.TimeoutException as e:
            raise CalibreAPIError(
                f"Request timeout after {self.config.timeout}s to {endpoint}. "
                "Possible causes: "
                "1. Calibre server is slow or overloaded - increase CALIBRE_TIMEOUT "
                "2. Network connectivity issues - check connection "
                "3. Server URL incorrect - verify CALIBRE_SERVER_URL"
            ) from e
        except httpx.ConnectError as e:
            raise CalibreAPIError(
                f"Connection failed to {url}. "
                "Possible causes: "
                "1. Calibre Content Server not running - start with 'calibre-server' "
                "2. Incorrect server URL - check CALIBRE_SERVER_URL env var "
                "3. Firewall blocking connection - check firewall settings "
                "4. Wrong port number - default is 8080"
            ) from e
        except httpx.RequestError as e:
            raise CalibreAPIError(
                f"Request error for {endpoint}: {str(e)}. "
                "This is a network-level error that will be retried automatically."
            ) from e
        except CalibreAPIError:
            raise  # Re-raise API errors immediately (no retry for auth/HTTP errors)

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Calibre server and get basic info.

        Returns:
            Dictionary with server version, library info, and capabilities
        """
        try:
            # Get interface initialization data
            init_data = await self._make_request("interface-data/init")

            # Extract relevant information
            server_info = {
                "version": init_data.get("version", "Unknown"),
                "library_name": init_data.get("library_map", {}).get("", "Default Library"),
                "total_books": init_data.get("search_result", {}).get("total_num", 0),
                "capabilities": [
                    "search",
                    "metadata",
                    "covers",
                    "downloads",
                    "library_stats",
                    "book_details",
                ],
            }

            return server_info

        except CalibreAPIError:
            raise  # Let specific API errors bubble up unchanged
        except Exception as e:
            raise CalibreAPIError(f"Connection test failed: {str(e)}")

    async def search_library(
        self, query: Optional[str] = None, limit: int = 50, sort: str = "title"
    ) -> List[Dict[str, Any]]:
        """
        Search library with optional query and sorting.

        Args:
            query: Search query string
            limit: Maximum results to return
            sort: Sort field (title, author, rating, date)

        Returns:
            List of book dictionaries with metadata
        """
        try:
            # Build search parameters
            params = {"num": limit, "sort": sort, "search_restriction": "", "library_id": ""}

            # Add query if provided
            if query:
                params["query"] = query

            # Make search request
            response = await self._make_request("search", params=params)

            # Extract book IDs from search results
            book_ids = response.get("book_ids", [])

            if not book_ids:
                return []

            # Get metadata for found books
            metadata = await self._get_books_metadata(book_ids)

            return metadata

        except Exception as e:
            raise CalibreAPIError(f"Library search failed: {str(e)}")

    async def advanced_search(
        self, text: str, fields: List[str], operator: str = "AND"
    ) -> List[Dict[str, Any]]:
        """
        Advanced search with field targeting and boolean logic.

        Args:
            text: Text to search for
            fields: List of fields to search in
            operator: Boolean operator (AND/OR)

        Returns:
            List of matching books with metadata
        """
        try:
            # Build Calibre search query
            if operator.upper() == "OR":
                # OR search: title:text OR authors:text OR tags:text
                query_parts = [f"{field}:{text}" for field in fields]
                query = " OR ".join(query_parts)
            else:
                # AND search: combine all fields
                query_parts = [f"{field}:{text}" for field in fields]
                query = " AND ".join(query_parts)

            # Use library search with constructed query
            return await self.search_library(query=query)

        except Exception as e:
            raise CalibreAPIError(f"Advanced search failed: {str(e)}")

    async def get_book_details(self, book_id: int) -> Dict[str, Any]:
        """
        Get detailed information for a specific book.

        Args:
            book_id: Calibre book ID

        Returns:
            Dictionary with complete book metadata and file info
        """
        try:
            # Get book metadata
            response = await self._make_request(f"book/{book_id}")

            if not response:
                return {}

            # Extract and format book data
            book_data = {
                "id": book_id,
                "title": response.get("title", "Unknown"),
                "authors": response.get("authors", []),
                "series": response.get("series"),
                "series_index": response.get("series_index"),
                "rating": response.get("rating"),
                "tags": response.get("tags", []),
                "comments": response.get("comments"),
                "published": response.get("pubdate"),
                "languages": response.get("languages", ["en"]),
                "formats": list(response.get("formats", {}).keys()),
                "identifiers": response.get("identifiers", {}),
                "last_modified": response.get("last_modified"),
                "cover_url": f"{self.config.server_url}/get/cover/{book_id}",
                "download_links": self._generate_download_links(
                    book_id, response.get("formats", {})
                ),
            }

            return book_data

        except Exception as e:
            raise CalibreAPIError(f"Failed to get book details: {str(e)}")

    async def _get_books_metadata(self, book_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Get metadata for multiple books by ID.

        Args:
            book_ids: List of Calibre book IDs

        Returns:
            List of book metadata dictionaries
        """
        try:
            # Get metadata for all books at once
            params = {"ids": ",".join(map(str, book_ids))}

            log_operation(
                logger, "fetch_book_metadata", level="INFO", book_ids=book_ids, count=len(book_ids)
            )

            try:
                response = await self._make_request("books", params=params)
                if not response:
                    log_operation(
                        logger,
                        "empty_response",
                        level="WARNING",
                        endpoint="books",
                        book_ids=book_ids,
                    )
                    return []
            except Exception as e:
                log_error(logger, "fetch_book_metadata", e, book_ids=book_ids)
                return []

            books = []
            for book_id in book_ids:
                book_data = response.get(str(book_id))
                if not book_data:
                    log_operation(logger, "book_not_found", level="WARNING", book_id=book_id)
                    continue

                # Format book data consistently
                book = {
                    "id": book_id,
                    "title": book_data.get("title", "Unknown"),
                    "authors": book_data.get("authors", []),
                    "series": book_data.get("series"),
                    "series_index": book_data.get("series_index"),
                    "rating": book_data.get("rating"),
                    "tags": book_data.get("tags", []),
                    "languages": book_data.get("languages", ["en"]),
                    "formats": list(book_data.get("formats", {}).keys()),
                    "last_modified": book_data.get("last_modified"),
                    "cover_url": f"{self.config.server_url}/get/cover/{book_id}",
                }
                books.append(book)

            log_operation(
                logger,
                "metadata_retrieval_success",
                level="INFO",
                books_retrieved=len(books),
                total_requested=len(book_ids),
            )
            return books

        except Exception as e:
            log_error(logger, "get_books_metadata_unexpected", e, book_ids=book_ids)
            return []

    def _generate_download_links(self, book_id: int, formats: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate download URLs for all available book formats.

        Args:
            book_id: Calibre book ID
            formats: Format dictionary from book metadata

        Returns:
            Dictionary mapping format to download URL
        """
        download_links = {}

        for format_name in formats.keys():
            download_url = f"{self.config.server_url}/get/{format_name.upper()}/{book_id}"
            download_links[format_name.upper()] = download_url

        return download_links


async def quick_library_test(server_url: str = "http://localhost:8080") -> bool:
    """
    Quick test function to verify Calibre server connectivity.

    Args:
        server_url: Calibre server URL to test

    Returns:
        True if connection successful, False otherwise
    """
    try:
        config = CalibreConfig(server_url=server_url)
        client = CalibreAPIClient(config)

        await client.test_connection()
        await client.close()

        log_operation(
            logger, "server_test_success", level="INFO", server_url=server_url, status="accessible"
        )
        return True

    except Exception as e:
        log_error(logger, "server_test_failed", e, server_url=server_url)
        return False
