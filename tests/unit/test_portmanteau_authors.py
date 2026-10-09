"""
Unit tests for manage_authors portmanteau tool.

Tests all 5 operations: list, get, get_books, stats, by_letter
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.authors.manage_authors import manage_authors


@pytest.fixture
def mock_author_helpers():
    """Mock the author helper functions."""
    with (
        patch("calibre_mcp.tools.authors.manage_authors.list_authors_helper") as list_authors,
        patch("calibre_mcp.tools.authors.manage_authors.get_author_helper") as get_author,
        patch("calibre_mcp.tools.authors.manage_authors.get_author_books_helper") as get_books,
        patch("calibre_mcp.tools.authors.manage_authors.get_author_stats_helper") as stats,
        patch("calibre_mcp.tools.authors.manage_authors.get_authors_by_letter_helper") as by_letter,
    ):
        list_authors.return_value = {"items": [{"id": 1, "name": "Test Author"}], "total": 1}

        get_author.return_value = {"id": 1, "name": "Test Author", "book_count": 5}

        get_books.return_value = {
            "author": {"id": 1, "name": "Test Author"},
            "books": [{"id": 1, "title": "Book 1"}],
            "total": 1,
        }

        stats.return_value = {"total_authors": 100, "top_authors": []}

        by_letter.return_value = {"authors": [{"id": 1, "name": "Test Author"}], "letter": "T"}

        yield {
            "list": list_authors,
            "get": get_author,
            "get_books": get_books,
            "stats": stats,
            "by_letter": by_letter,
        }


@pytest.mark.asyncio
async def test_manage_authors_list(mock_author_helpers):
    """Test manage_authors list operation."""
    result = await manage_authors(operation="list", limit=10)

    assert "items" in result
    assert result["total"] == 1
    mock_author_helpers["list"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_authors_get(mock_author_helpers):
    """Test manage_authors get operation."""
    result = await manage_authors(operation="get", author_id=1)

    assert result["id"] == 1
    assert result["name"] == "Test Author"
    mock_author_helpers["get"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_authors_get_books(mock_author_helpers):
    """Test manage_authors get_books operation."""
    result = await manage_authors(operation="get_books", author_id=1)

    assert "books" in result
    assert result["total"] == 1
    mock_author_helpers["get_books"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_authors_stats(mock_author_helpers):
    """Test manage_authors stats operation."""
    result = await manage_authors(operation="stats")

    assert result["total_authors"] == 100
    mock_author_helpers["stats"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_authors_by_letter(mock_author_helpers):
    """Test manage_authors by_letter operation."""
    result = await manage_authors(operation="by_letter", letter="T")

    assert "authors" in result
    assert result["letter"] == "T"
    mock_author_helpers["by_letter"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_authors_invalid_operation():
    """Test manage_authors with invalid operation."""
    result = await manage_authors(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_authors_missing_required_params():
    """Test manage_authors with missing required parameters."""
    # Get operation requires author_id
    result = await manage_authors(operation="get")

    assert "error" in result
    assert "author_id is required" in result["error"]

    # Get_books operation requires author_id
    result = await manage_authors(operation="get_books")

    assert "error" in result
    assert "author_id is required" in result["error"]

    # By_letter operation requires letter
    result = await manage_authors(operation="by_letter")

    assert "error" in result
    assert "letter is required" in result["error"]
