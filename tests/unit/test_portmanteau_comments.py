"""
Unit tests for manage_comments portmanteau tool.

Tests all 6 operations: create, read, update, delete, append, replace
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.comments.manage_comments import manage_comments


@pytest.fixture
def mock_comment_helpers():
    """Mock the comment helper functions."""
    with (
        patch("calibre_mcp.tools.comments.manage_comments.create_comment_helper") as create,
        patch("calibre_mcp.tools.comments.manage_comments.read_comment_helper") as read,
        patch("calibre_mcp.tools.comments.manage_comments.update_comment_helper") as update,
        patch("calibre_mcp.tools.comments.manage_comments.delete_comment_helper") as delete,
        patch("calibre_mcp.tools.comments.manage_comments.append_comment_helper") as append,
    ):
        create.return_value = {
            "success": True,
            "book_id": 123,
            "comment": {"book_id": 123, "text": "Test comment"},
            "message": "Comment created successfully",
        }

        read.return_value = {
            "success": True,
            "book_id": 123,
            "comment": {"book_id": 123, "text": "Existing comment"},
        }

        update.return_value = {
            "success": True,
            "book_id": 123,
            "comment": {"book_id": 123, "text": "Updated comment"},
            "message": "Comment updated successfully",
        }

        delete.return_value = {
            "success": True,
            "book_id": 123,
            "message": "Comment deleted successfully",
        }

        append.return_value = {
            "success": True,
            "book_id": 123,
            "comment": {"book_id": 123, "text": "Existing comment\n\nAppended text"},
            "message": "Comment appended successfully",
        }

        yield {
            "create": create,
            "read": read,
            "update": update,
            "delete": delete,
            "append": append,
        }


@pytest.mark.asyncio
async def test_manage_comments_create(mock_comment_helpers):
    """Test manage_comments create operation."""
    result = await manage_comments(operation="create", book_id="123", text="Test comment")

    assert result["success"] is True
    assert result["book_id"] == 123
    assert result["comment"]["text"] == "Test comment"
    mock_comment_helpers["create"].assert_called_once_with(123, "Test comment")


@pytest.mark.asyncio
async def test_manage_comments_read(mock_comment_helpers):
    """Test manage_comments read operation."""
    result = await manage_comments(operation="read", book_id="123")

    assert result["success"] is True
    assert result["book_id"] == 123
    assert result["comment"]["text"] == "Existing comment"
    mock_comment_helpers["read"].assert_called_once_with(123)


@pytest.mark.asyncio
async def test_manage_comments_update(mock_comment_helpers):
    """Test manage_comments update operation."""
    result = await manage_comments(operation="update", book_id="123", text="Updated comment")

    assert result["success"] is True
    assert result["book_id"] == 123
    assert result["comment"]["text"] == "Updated comment"
    mock_comment_helpers["update"].assert_called_once_with(123, "Updated comment")


@pytest.mark.asyncio
async def test_manage_comments_replace(mock_comment_helpers):
    """Test manage_comments replace operation (alias for update)."""
    result = await manage_comments(operation="replace", book_id="123", text="Replaced comment")

    assert result["success"] is True
    assert result["book_id"] == 123
    assert result["comment"]["text"] == "Updated comment"
    mock_comment_helpers["update"].assert_called_once_with(123, "Replaced comment")


@pytest.mark.asyncio
async def test_manage_comments_delete(mock_comment_helpers):
    """Test manage_comments delete operation."""
    result = await manage_comments(operation="delete", book_id="123")

    assert result["success"] is True
    assert result["book_id"] == 123
    mock_comment_helpers["delete"].assert_called_once_with(123)


@pytest.mark.asyncio
async def test_manage_comments_append(mock_comment_helpers):
    """Test manage_comments append operation."""
    result = await manage_comments(operation="append", book_id="123", text="Appended text")

    assert result["success"] is True
    assert result["book_id"] == 123
    assert "Appended text" in result["comment"]["text"]
    mock_comment_helpers["append"].assert_called_once_with(123, "Appended text")


@pytest.mark.asyncio
async def test_manage_comments_invalid_operation():
    """Test manage_comments with invalid operation."""
    result = await manage_comments(operation="invalid", book_id="123")

    assert result.get("success") is False
    assert "error" in result
    assert "Invalid operation" in result["error"]


@pytest.mark.asyncio
async def test_manage_comments_missing_book_id():
    """Test manage_comments with missing book_id."""
    result = await manage_comments(operation="read")

    assert result.get("success") is False
    assert "error" in result
    assert "book_id is required" in result["error"]


@pytest.mark.asyncio
async def test_manage_comments_missing_text():
    """Test manage_comments with missing text for operations that require it."""
    # Test create operation
    result = await manage_comments(operation="create", book_id="123")

    assert result.get("success") is False
    assert "error" in result
    assert "text is required" in result["error"]

    # Test update operation
    result = await manage_comments(operation="update", book_id="123")

    assert result.get("success") is False
    assert "error" in result
    assert "text is required" in result["error"]

    # Test append operation
    result = await manage_comments(operation="append", book_id="123")

    assert result.get("success") is False
    assert "error" in result
    assert "text is required" in result["error"]


@pytest.mark.asyncio
async def test_manage_comments_empty_text():
    """Test manage_comments with empty text."""
    result = await manage_comments(operation="create", book_id="123", text="   ")

    assert result.get("success") is False
    assert "error" in result
    assert "text is required" in result["error"]


@pytest.mark.asyncio
async def test_manage_comments_invalid_book_id():
    """Test manage_comments with invalid book_id format."""
    result = await manage_comments(operation="read", book_id="invalid")

    assert result.get("success") is False
    assert "error" in result
    assert "Invalid book_id format" in result["error"]


@pytest.mark.asyncio
async def test_manage_comments_read_no_comment(mock_comment_helpers):
    """Test manage_comments read operation when no comment exists."""
    mock_comment_helpers["read"].return_value = {
        "success": True,
        "book_id": 123,
        "comment": None,
        "message": "No comment found for this book",
    }

    result = await manage_comments(operation="read", book_id="123")

    assert result["success"] is True
    assert result["comment"] is None
    assert "No comment found" in result["message"]


@pytest.mark.asyncio
async def test_manage_comments_error_handling(mock_comment_helpers):
    """Test error handling in manage_comments."""
    from calibre_mcp.calibre_api import CalibreAPIError

    mock_comment_helpers["read"].side_effect = CalibreAPIError("Book not found")

    result = await manage_comments(operation="read", book_id="123")

    assert result.get("success") is False
    assert "error" in result
    assert "error_code" in result
