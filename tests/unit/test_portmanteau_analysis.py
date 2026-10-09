"""
Unit tests for manage_analysis portmanteau tool.

Tests all 6 operations: tag_statistics, duplicate_books, series_analysis,
library_health, unread_priority, reading_stats
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.analysis.manage_analysis import manage_analysis


@pytest.fixture
def mock_analysis_helpers():
    """Mock the analysis helper functions."""
    with (
        patch("calibre_mcp.tools.analysis.manage_analysis.get_tag_statistics_helper") as tag_stats,
        patch("calibre_mcp.tools.analysis.manage_analysis.find_duplicate_books_helper") as duplicates,
        patch("calibre_mcp.tools.analysis.manage_analysis.get_series_analysis_helper") as series,
        patch("calibre_mcp.tools.analysis.manage_analysis.analyze_library_health_helper") as health,
        patch("calibre_mcp.tools.analysis.manage_analysis.unread_priority_list_helper") as unread,
        patch("calibre_mcp.tools.analysis.manage_analysis.reading_statistics_helper") as reading,
    ):
        tag_stats.return_value = {"total_tags": 100, "unused_tags_count": 5}

        duplicates.return_value = {"duplicate_groups": []}

        series.return_value = {"incomplete_series": [], "reading_order_suggestions": []}

        health.return_value = {"status": "healthy", "issues": []}

        unread.return_value = {"prioritized_books": []}

        reading.return_value = {"total_books": 1000, "completion_rate": 0.75}

        yield {
            "tag_statistics": tag_stats,
            "duplicate_books": duplicates,
            "series_analysis": series,
            "library_health": health,
            "unread_priority": unread,
            "reading_stats": reading,
        }


@pytest.mark.asyncio
async def test_manage_analysis_tag_statistics(mock_analysis_helpers):
    """Test manage_analysis tag_statistics operation."""
    result = await manage_analysis(operation="tag_statistics")

    assert result["total_tags"] == 100
    mock_analysis_helpers["tag_statistics"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_analysis_duplicate_books(mock_analysis_helpers):
    """Test manage_analysis duplicate_books operation."""
    result = await manage_analysis(operation="duplicate_books")

    assert "duplicate_groups" in result
    mock_analysis_helpers["duplicate_books"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_analysis_series_analysis(mock_analysis_helpers):
    """Test manage_analysis series_analysis operation."""
    result = await manage_analysis(operation="series_analysis")

    assert "incomplete_series" in result
    mock_analysis_helpers["series_analysis"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_analysis_library_health(mock_analysis_helpers):
    """Test manage_analysis library_health operation."""
    result = await manage_analysis(operation="library_health")

    assert result["status"] == "healthy"
    mock_analysis_helpers["library_health"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_analysis_unread_priority(mock_analysis_helpers):
    """Test manage_analysis unread_priority operation."""
    result = await manage_analysis(operation="unread_priority")

    assert "prioritized_books" in result
    mock_analysis_helpers["unread_priority"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_analysis_reading_stats(mock_analysis_helpers):
    """Test manage_analysis reading_stats operation."""
    result = await manage_analysis(operation="reading_stats")

    assert result["total_books"] == 1000
    mock_analysis_helpers["reading_stats"].assert_called_once()


@pytest.mark.asyncio
async def test_manage_analysis_invalid_operation():
    """Test manage_analysis with invalid operation."""
    result = await manage_analysis(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]
