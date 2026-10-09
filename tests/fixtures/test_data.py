"""Shared test data constants for Calibre MCP tests."""

# Sample book data
SAMPLE_BOOK = {
    "id": "test-book-1",
    "title": "Test Book",
    "authors": ["Test Author"],
    "description": "A test book description.",
    "tags": ["test", "fiction"],
    "series": "Test Series",
    "series_index": 1.0,
    "publisher": "Test Publisher",
    "published_date": "2023-01-01",
    "identifiers": {"isbn": "1234567890"},
    "languages": ["eng"],
    "rating": 4.5,
}

SAMPLE_BOOKS = [
    {
        "id": "book1",
        "title": "Test Book 1",
        "authors": ["Author 1"],
        "description": "Test description 1",
        "tags": ["test", "fiction"],
        "series": "Test Series 1",
        "series_index": 1.0,
        "publisher": "Test Publisher 1",
        "published_date": "2023-01-01",
        "identifiers": {"isbn": "1234567890"},
        "languages": ["eng"],
        "rating": 4.5,
    },
    {
        "id": "book2",
        "title": "Test Book 2",
        "authors": ["Author 2"],
        "description": "Test description 2",
        "tags": ["test", "non-fiction"],
        "series": "Test Series 1",
        "series_index": 2.0,
        "publisher": "Test Publisher 2",
        "published_date": "2023-02-01",
        "identifiers": {"isbn": "0987654321"},
        "languages": ["eng"],
        "rating": 4.0,
    },
]

# Test configuration
TEST_LIBRARY_PATH = "/tmp/calibre_test_library"
TEST_DB_URL = "sqlite:///:memory:"
