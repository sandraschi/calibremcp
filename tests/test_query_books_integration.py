"""
Integration tests for query_books using the test database fixture.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calibre_mcp.services.book_service import book_service


def test_search_by_author(test_database):
    """Test searching books by author using test database."""
    results = book_service.get_all(search="Conan Doyle", limit=10)

    assert results["total"] >= 2, "Should find at least 2 Conan Doyle books"
    assert len(results["items"]) >= 2

    # Verify book titles
    titles = [book["title"] for book in results["items"]]
    assert "A Study in Scarlet" in titles
    assert "The Sign of the Four" in titles


def test_search_by_tag(test_database):
    """Test searching books by tag."""
    results = book_service.get_all(search="mystery", limit=10)

    assert results["total"] >= 2, "Should find at least 2 mystery books"

    # Verify both Sherlock Holmes books are included
    titles = [book["title"] for book in results["items"]]
    assert "A Study in Scarlet" in titles or "The Sign of the Four" in titles


def test_get_book_by_id(test_database):
    """Test getting a specific book by ID."""
    book = book_service.get_by_id(1)

    assert book is not None
    assert book["id"] == 1
    assert book["title"] == "A Study in Scarlet"
    assert len(book["authors"]) > 0
    assert book["authors"][0]["name"] == "Arthur Conan Doyle"


def test_book_formats_included(test_database):
    """Test that book formats are included in results."""
    book = book_service.get_by_id(1)

    assert "formats" in book
    assert len(book["formats"]) >= 1

    # Check format structure
    fmt = book["formats"][0]
    assert "format" in fmt
    assert "filename" in fmt
    assert "path" in fmt
    assert "size" in fmt


def test_filter_by_series(test_database):
    """Test filtering books by series."""
    results = book_service.get_all(series_name="Sherlock Holmes", limit=10)

    assert results["total"] >= 2
    titles = [book["title"] for book in results["items"]]
    assert "A Study in Scarlet" in titles
    assert "The Sign of the Four" in titles


def test_pagination(test_database):
    """Test pagination of results."""
    # Get first page
    page1 = book_service.get_all(limit=2, skip=0)
    assert len(page1["items"]) == 2

    # Get second page
    page2 = book_service.get_all(limit=2, skip=2)
    assert len(page2["items"]) >= 1

    # Verify different books
    page1_ids = {book["id"] for book in page1["items"]}
    page2_ids = {book["id"] for book in page2["items"]}
    assert page1_ids.isdisjoint(page2_ids)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
