"""
Tests for search logging functionality.

Verifies that logging is working correctly and capturing the right information.
"""

import logging

import pytest

from calibre_mcp.db.database import get_database
from calibre_mcp.services.book_service import BookService
from calibre_mcp.tools.book_tools import search_books_helper


class TestSearchLogging:
    """Test logging in search operations."""

    @pytest.mark.asyncio
    async def test_search_logs_start(self, test_database, caplog):
        """Test that search logs start of operation."""
        with caplog.at_level(logging.INFO):
            await search_books_helper(text="Scarlet", limit=10)

        # Check for start log
        log_messages = [record.message for record in caplog.records]
        assert any("Starting book search" in msg or "search_books" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_search_logs_parameters(self, test_database, caplog):
        """Test that search logs all parameters."""
        with caplog.at_level(logging.INFO):
            await search_books_helper(text="test", author="test author", tag="test tag", limit=5, offset=0)

        # Check that parameters are logged
        log_records = [record for record in caplog.records if hasattr(record, "extra")]
        assert len(log_records) > 0

    @pytest.mark.asyncio
    async def test_search_logs_database_connection(self, test_database, caplog):
        """Test that search logs database connection attempts."""
        with caplog.at_level(logging.DEBUG):
            await search_books_helper(text="Scarlet", limit=10)

        # Check for database-related logs
        log_messages = [record.message for record in caplog.records]
        db_logs = [msg for msg in log_messages if "database" in msg.lower() or "db" in msg.lower()]
        assert len(db_logs) > 0

    @pytest.mark.asyncio
    async def test_search_logs_completion(self, test_database, caplog):
        """Test that search logs completion with results."""
        with caplog.at_level(logging.INFO):
            result = await search_books_helper(text="Scarlet", limit=10)

        # Check for completion log
        log_messages = [record.message for record in caplog.records]
        completion_logs = [msg for msg in log_messages if "complete" in msg.lower() or "completed" in msg.lower()]
        assert len(completion_logs) > 0

    @pytest.mark.asyncio
    async def test_search_logs_errors(self, test_database, caplog):
        """Test that search logs errors correctly."""
        with caplog.at_level(logging.ERROR):
            try:
                await search_books_helper(limit=0)  # Invalid limit
            except ValueError:
                pass

        # Check for error logs
        error_logs = [record for record in caplog.records if record.levelno >= logging.ERROR]
        assert len(error_logs) > 0

    @pytest.mark.asyncio
    async def test_search_logs_timing(self, test_database, caplog):
        """Test that search logs operation timing."""
        with caplog.at_level(logging.INFO):
            await search_books_helper(text="Scarlet", limit=10)

        # Check for timing information in structured logs
        log_records = [
            record for record in caplog.records if hasattr(record, "extra") and "duration" in str(record.extra)
        ]
        assert len(log_records) > 0

    def test_book_service_logs_query_start(self, test_database, caplog):
        """Test that BookService logs query start."""

        db = get_database()
        service = BookService(db)

        with caplog.at_level(logging.INFO):
            service.get_all(skip=0, limit=10)

        # Check for query start log
        log_messages = [record.message for record in caplog.records]
        assert any("get_all" in msg.lower() or "query" in msg.lower() for msg in log_messages)

    def test_book_service_logs_filters(self, test_database, caplog):
        """Test that BookService logs applied filters."""

        db = get_database()
        service = BookService(db)

        with caplog.at_level(logging.DEBUG):
            service.get_all(search="test", author_name="test author", tag_name="test tag", skip=0, limit=10)

        # Check for filter logs
        log_messages = [record.message for record in caplog.records]
        filter_logs = [msg for msg in log_messages if "filter" in msg.lower()]
        assert len(filter_logs) > 0

    def test_book_service_logs_fts_usage(self, test_database, caplog):
        """Test that BookService logs FTS vs LIKE search usage."""

        db = get_database()
        service = BookService(db)

        with caplog.at_level(logging.INFO):
            service.get_all(search="Scarlet", skip=0, limit=10)

        # Check for FTS or LIKE search logs
        log_messages = [record.message for record in caplog.records]
        search_method_logs = [
            msg for msg in log_messages if "fts" in msg.lower() or "like" in msg.lower() or "search" in msg.lower()
        ]
        assert len(search_method_logs) > 0

    def test_book_service_logs_query_results(self, test_database, caplog):
        """Test that BookService logs query results."""

        db = get_database()
        service = BookService(db)

        with caplog.at_level(logging.INFO):
            result = service.get_all(skip=0, limit=10)

        # Check for result logs
        log_messages = [record.message for record in caplog.records]
        result_logs = [
            msg
            for msg in log_messages
            if "total" in msg.lower() or "result" in msg.lower() or "complete" in msg.lower()
        ]
        assert len(result_logs) > 0

    def test_book_service_logs_errors(self, test_database, caplog):
        """Test that BookService logs errors correctly."""

        db = get_database()
        service = BookService(db)

        with caplog.at_level(logging.ERROR):
            try:
                service.get_all(limit=0)  # Invalid limit
            except ValueError:
                pass

        # Check for error logs
        error_logs = [record for record in caplog.records if record.levelno >= logging.ERROR]
        assert len(error_logs) > 0


class TestStructuredLogging:
    """Test structured logging format."""

    @pytest.mark.asyncio
    async def test_logs_have_correlation_id(self, test_database, caplog):
        """Test that logs include correlation IDs."""
        with caplog.at_level(logging.INFO):
            await search_books_helper(text="Scarlet", limit=10)

        # Check for correlation ID in structured logs
        log_records = [
            record for record in caplog.records if hasattr(record, "extra") and "correlation_id" in str(record.extra)
        ]
        assert len(log_records) > 0

    @pytest.mark.asyncio
    async def test_logs_have_service_field(self, test_database, caplog):
        """Test that logs include service field."""
        with caplog.at_level(logging.INFO):
            await search_books_helper(text="Scarlet", limit=10)

        # Check for service field in logs
        log_records = [
            record for record in caplog.records if hasattr(record, "extra") and "service" in str(record.extra)
        ]
        assert len(log_records) > 0

    @pytest.mark.asyncio
    async def test_logs_have_action_field(self, test_database, caplog):
        """Test that logs include action field."""
        with caplog.at_level(logging.INFO):
            await search_books_helper(text="Scarlet", limit=10)

        # Check for action field in logs
        log_records = [
            record for record in caplog.records if hasattr(record, "extra") and "action" in str(record.extra)
        ]
        assert len(log_records) > 0
