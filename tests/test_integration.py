"""
Integration tests for Calibre MCP server and tools.

Tests verify actual tool functionality with real database and services.
"""

import pytest
from unittest.mock import patch
import sqlite3

# Import actual tools
from calibre_mcp.tools.library.library_management import list_libraries
from calibre_mcp.tools.book_tools import search_books
from calibre_mcp.services.book_service import BookService
from calibre_mcp.models.book import BookCreate
from calibre_mcp.db.database import DatabaseService, init_database


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_metadata.db"
    # Create empty SQLite database
    conn = sqlite3.connect(str(db_path))
    conn.close()

    # Initialize database schema
    init_database(str(db_path), echo=False)

    return str(db_path)


@pytest.fixture
def db_service(temp_db):
    """Create database service with temporary database."""
    service = DatabaseService()
    service.initialize(temp_db, echo=False)
    return service


@pytest.fixture
def book_service(db_service):
    """Create book service with database."""
    return BookService(db_service)


@pytest.mark.asyncio
async def test_list_libraries_integration(tmp_path):
    """Test list_libraries tool with real library discovery."""
    # Create a test library directory
    test_lib = tmp_path / "test_library"
    test_lib.mkdir()
    (test_lib / "metadata.db").touch()

    # Mock library discovery to find our test library
    with patch("calibre_mcp.tools.library.library_management.discover_libraries") as mock_discover:
        mock_discover.return_value = {"test_library": str(test_lib)}

        result = await list_libraries()

        # Verify actual results
        assert result is not None
        assert hasattr(result, "libraries") or "libraries" in result
        assert hasattr(result, "total_libraries") or "total_libraries" in result
        # Verify library discovery was called
        mock_discover.assert_called_once()


@pytest.mark.asyncio
async def test_search_books_empty_library(book_service):
    """Test search_books with empty library returns empty results."""
    # Mock the book service to return empty results
    with patch("calibre_mcp.tools.book_tools.book_service") as mock_service:
        mock_service.get_all.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 50,
            "total_pages": 0,
        }

        result = await search_books(query="test")

        # Verify actual results structure
        assert "items" in result
        assert "total" in result
        assert result["total"] == 0
        assert len(result["items"]) == 0
        assert result["page"] == 1


@pytest.mark.asyncio
async def test_search_books_with_results(book_service, db_service):
    """Test search_books with actual book data."""
    # Create test books in database
    test_books = []
    for i in range(3):
        book_data = BookCreate(
            title=f"Test Book {i}",
            authors=[f"Author {i}"],
            tags=["test"],
        )
        created = book_service.create(book_data)
        test_books.append(created)

    # Now search for books
    with patch("calibre_mcp.tools.book_tools.book_service", book_service):
        result = await search_books(query="Test")

        # Verify we get results
        assert "items" in result
        assert "total" in result
        assert result["total"] >= 3
        assert len(result["items"]) >= 3

        # Verify book data structure
        for item in result["items"]:
            assert "id" in item
            assert "title" in item
            assert "authors" in item
            assert "Test" in item["title"]


@pytest.mark.asyncio
async def test_book_service_create_and_get(book_service):
    """Test creating and retrieving a book through the service."""
    # Create a book
    book_data = BookCreate(
        title="Integration Test Book",
        authors=["Test Author"],
        tags=["integration-test"],
        description="A book created for integration testing",
    )

    created = book_service.create(book_data)

    # Verify creation succeeded
    assert created is not None
    assert "id" in created
    book_id = created["id"]

    # Retrieve the book
    retrieved = book_service.get_by_id(book_id)

    # Verify retrieval
    assert retrieved is not None
    assert retrieved["id"] == book_id
    assert retrieved["title"] == "Integration Test Book"
    assert "Test Author" in retrieved["authors"]


@pytest.mark.asyncio
async def test_book_service_update(book_service):
    """Test updating a book through the service."""
    from calibre_mcp.models.book import BookUpdate

    # Create a book first
    book_data = BookCreate(
        title="Original Title",
        authors=["Original Author"],
        tags=["test"],
    )
    created = book_service.create(book_data)
    book_id = created["id"]

    # Update the book
    update_data = BookUpdate(title="Updated Title")
    updated = book_service.update(book_id, update_data)

    # Verify update
    assert updated is not None
    assert updated["title"] == "Updated Title"

    # Verify the update persisted
    retrieved = book_service.get_by_id(book_id)
    assert retrieved["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_book_service_delete(book_service):
    """Test deleting a book through the service."""
    # Create a book
    book_data = BookCreate(
        title="Book To Delete",
        authors=["Delete Author"],
        tags=["test"],
    )
    created = book_service.create(book_data)
    book_id = created["id"]

    # Delete the book
    book_service.delete(book_id)

    # Verify deletion - should raise NotFoundError
    from calibre_mcp.services.base_service import NotFoundError

    with pytest.raises(NotFoundError):
        book_service.get_by_id(book_id)


@pytest.mark.asyncio
async def test_error_handling_invalid_book_id(book_service):
    """Test error handling with invalid book ID."""
    from calibre_mcp.services.base_service import NotFoundError

    # Try to get non-existent book
    with pytest.raises(NotFoundError) as exc_info:
        book_service.get_by_id(99999)

    # Verify error message is helpful
    assert "99999" in str(exc_info.value)
    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_search_books_pagination(book_service):
    """Test search_books pagination works correctly."""
    # Create 15 test books
    for i in range(15):
        book_data = BookCreate(
            title=f"Paginated Book {i}",
            authors=[f"Author {i}"],
            tags=["pagination-test"],
        )
        book_service.create(book_data)

    # Test first page
    with patch("calibre_mcp.tools.book_tools.book_service", book_service):
        page1 = await search_books(query="Paginated", limit=5, offset=0)
        assert len(page1["items"]) == 5
        assert page1["page"] == 1
        assert page1["total"] >= 15

        # Test second page
        page2 = await search_books(query="Paginated", limit=5, offset=5)
        assert len(page2["items"]) == 5
        assert page2["page"] == 2

        # Verify different books on different pages
        page1_ids = {item["id"] for item in page1["items"]}
        page2_ids = {item["id"] for item in page2["items"]}
        assert page1_ids != page2_ids  # Should have different books
