"""
Unit tests for analyze_library portmanteau tool.

Tests all 6 operations: tag_statistics, duplicates, series, health,
unread_priority, reading_stats
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.analysis.analyze_library import analyze_library


@pytest.fixture
def mock_analyze_helpers():
    """Mock the analyze library helper functions."""
    with (
        patch("calibre_mcp.tools.analysis.analyze_library.get_tag_statistics_helper") as tag_stats,
        patch("calibre_mcp.tools.analysis.analyze_library.find_duplicate_books_helper") as duplicates,
        patch("calibre_mcp.tools.analysis.analyze_library.get_series_analysis_helper") as series,
        patch("calibre_mcp.tools.analysis.analyze_library.analyze_library_health_helper") as health,
        patch("calibre_mcp.tools.analysis.analyze_library.unread_priority_list_helper") as unread,
        patch("calibre_mcp.tools.analysis.analyze_library.reading_statistics_helper") as reading,
    ):
        tag_stats.return_value = {"total_tags": 100, "unused_tags_count": 5}

        duplicates.return_value = {"duplicate_groups": []}

        series.return_value = {"incomplete_series": [], "reading_order_suggestions": []}

        health.return_value = {"status": "healthy", "issues": []}

        unread.return_value = {"prioritized_books": []}

        reading.return_value = {"total_books": 1000, "completion_rate": 0.75}

        yield {
            "tag_statistics": tag_stats,
            "duplicates": duplicates,
            "series": series,
            "health": health,
            "unread_priority": unread,
            "reading_stats": reading,
        }


@pytest.mark.asyncio
async def test_analyze_library_tag_statistics(mock_analyze_helpers):
    """Test analyze_library tag_statistics operation."""
    result = await analyze_library(operation="tag_statistics")

    assert result["total_tags"] == 100
    mock_analyze_helpers["tag_statistics"].assert_called_once()


@pytest.mark.asyncio
async def test_analyze_library_duplicates(mock_analyze_helpers):
    """Test analyze_library duplicates operation."""
    result = await analyze_library(operation="duplicates")

    assert "duplicate_groups" in result
    mock_analyze_helpers["duplicates"].assert_called_once()


@pytest.mark.asyncio
async def test_analyze_library_series(mock_analyze_helpers):
    """Test analyze_library series operation."""
    result = await analyze_library(operation="series")

    assert "incomplete_series" in result
    mock_analyze_helpers["series"].assert_called_once()


@pytest.mark.asyncio
async def test_analyze_library_health(mock_analyze_helpers):
    """Test analyze_library health operation."""
    result = await analyze_library(operation="health")

    assert result["status"] == "healthy"
    mock_analyze_helpers["health"].assert_called_once()


@pytest.mark.asyncio
async def test_analyze_library_unread_priority(mock_analyze_helpers):
    """Test analyze_library unread_priority operation."""
    result = await analyze_library(operation="unread_priority")

    assert "prioritized_books" in result
    mock_analyze_helpers["unread_priority"].assert_called_once()


@pytest.mark.asyncio
async def test_analyze_library_reading_stats(mock_analyze_helpers):
    """Test analyze_library reading_stats operation."""
    result = await analyze_library(operation="reading_stats")

    assert result["total_books"] == 1000
    mock_analyze_helpers["reading_stats"].assert_called_once()


@pytest.mark.asyncio
async def test_analyze_library_invalid_operation():
    """Test analyze_library with invalid operation."""
    result = await analyze_library(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]
