"""
Tests for error handling in search functionality.

Verifies that errors are handled gracefully and logged appropriately.
"""

import logging
from unittest.mock import patch

import pytest

from calibre_mcp.db.database import get_database
from calibre_mcp.services.book_service import BookService
from calibre_mcp.tools.book_tools import search_books_helper


class TestSearchErrorHandling:
    """Test error handling in search operations."""

    @pytest.mark.asyncio
    async def test_database_not_initialized_error(self, caplog):
        """Test error handling when database is not initialized."""
        # Close any existing database connection
        from calibre_mcp.db.database import close_database

        try:
            close_database()
        except:
            pass

        # Try to search without database
        with pytest.raises((ValueError, RuntimeError)):
            await search_books_helper(text="test", limit=10)

    @pytest.mark.asyncio
    async def test_invalid_limit_error_message(self, test_database):
        """Test that invalid limit provides helpful error message."""
        with pytest.raises(ValueError) as exc_info:
            await search_books_helper(limit=0)

        assert "Limit must be between" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_offset_error_message(self, test_database):
        """Test that invalid offset provides helpful error message."""
        with pytest.raises(ValueError) as exc_info:
            await search_books_helper(offset=-1)

        assert "Offset cannot be negative" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_database_connection_error(self, test_database):
        """Test error handling for database connection failures."""
        from calibre_mcp.db.database import close_database

        # Close database
        close_database()

        # Mock database initialization to fail
        with patch("calibre_mcp.tools.book_tools.get_database") as mock_get_db:
            mock_get_db.side_effect = RuntimeError("Database not initialized")

            with pytest.raises((ValueError, RuntimeError)):
                await search_books_helper(text="test", limit=10)

    @pytest.mark.asyncio
    async def test_query_execution_error(self, test_database):
        """Test error handling for query execution failures."""

        db = get_database()
        service = BookService(db)

        # Mock session to raise error
        with patch.object(service, "_get_db_session") as mock_session:
            mock_session.side_effect = Exception("Database query failed")

            with pytest.raises(Exception):  # noqa: B017 (asserts error propagation, any type)
                service.get_all(skip=0, limit=10)

    def test_invalid_sort_order_error(self, test_database):
        """Test error handling for invalid sort_order."""

        db = get_database()
        service = BookService(db)

        with pytest.raises(ValueError) as exc_info:
            service.get_all(sort_order="invalid", skip=0, limit=10)

        assert "sort_order must be" in str(exc_info.value)

    def test_invalid_sort_by_error(self, test_database):
        """Test error handling for invalid sort_by."""

        db = get_database()
        service = BookService(db)

        with pytest.raises(ValueError) as exc_info:
            service.get_all(sort_by="invalid_field", skip=0, limit=10)

        assert "sort_by must be one of" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fts_error_fallback(self, test_database, caplog):
        """Test that FTS errors fall back to LIKE search."""

        db = get_database()
        service = BookService(db)

        # Mock FTS query to fail
        with patch("calibre_mcp.services.book_service.query_fts") as mock_fts:
            mock_fts.side_effect = Exception("FTS query failed")

            with caplog.at_level(logging.WARNING):
                result = service.get_all(search="Scarlet", skip=0, limit=10)

            # Should still return results using LIKE fallback
            assert "items" in result
            # Should log FTS error
            assert any("fts" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_empty_result_error_handling(self, test_database):
        """Test that empty results don't cause errors."""
        result = await search_books_helper(text="NonexistentBookTitle12345", limit=10)

        # Should return empty result, not raise error
        assert "items" in result
        assert result["total"] == 0
        assert len(result["items"]) == 0

    @pytest.mark.asyncio
    async def test_malformed_query_handling(self, test_database):
        """Test handling of malformed queries."""
        # Test with None values
        result = await search_books_helper(text=None, author=None, limit=10)

        assert "items" in result
        assert result["total"] >= 0

    @pytest.mark.asyncio
    async def test_error_recovery(self, test_database):
        """Test that errors don't break subsequent queries."""
        # Cause an error
        with pytest.raises(ValueError):
            await search_books_helper(limit=0)

        # Subsequent query should work
        result = await search_books_helper(text="Scarlet", limit=10)
        assert "items" in result

    def test_service_error_propagation(self, test_database):
        """Test that service errors propagate correctly."""

        db = get_database()
        service = BookService(db)

        # Test with invalid parameters
        with pytest.raises(ValueError):
            service.get_all(limit=0)

        # Valid query should still work
        result = service.get_all(skip=0, limit=10)
        assert "items" in result


class TestSearchErrorMessages:
    """Test that error messages are helpful and informative."""

    @pytest.mark.asyncio
    async def test_database_error_message_helpful(self, caplog):
        """Test that database errors provide helpful messages."""
        from calibre_mcp.db.database import close_database

        try:
            close_database()
        except:
            pass

        with pytest.raises((ValueError, RuntimeError)) as exc_info:
            await search_books_helper(text="test", limit=10)

        error_msg = str(exc_info.value)
        # Should mention libraries or database
        assert any(keyword in error_msg.lower() for keyword in ["library", "database", "initialize"])

    @pytest.mark.asyncio
    async def test_validation_error_message_clear(self, test_database):
        """Test that validation errors have clear messages."""
        with pytest.raises(ValueError) as exc_info:
            await search_books_helper(limit=0)

        error_msg = str(exc_info.value)
        assert "limit" in error_msg.lower() or "between" in error_msg.lower()

    def test_service_error_message_detailed(self, test_database):
        """Test that service errors provide detailed information."""

        db = get_database()
        service = BookService(db)

        with pytest.raises(ValueError) as exc_info:
            service.get_all(sort_order="invalid", skip=0, limit=10)

        error_msg = str(exc_info.value)
        assert "sort_order" in error_msg.lower()
        assert "asc" in error_msg.lower() or "desc" in error_msg.lower()
