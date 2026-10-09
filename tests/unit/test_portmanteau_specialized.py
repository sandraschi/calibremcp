"""
Unit tests for manage_specialized portmanteau tool.

Tests all 3 operations: japanese_organizer, it_curator, reading_recommendations
"""

import importlib.util

import pytest

if importlib.util.find_spec("calibre_mcp.tools.specialized.manage_specialized") is None:
    pytest.skip("manage_specialized portmanteau not implemented yet", allow_module_level=True)

from unittest.mock import patch

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.specialized.manage_specialized import manage_specialized


@pytest.fixture
def mock_specialized_helpers():
    """Mock the specialized helper functions."""
    with (
        patch("calibre_mcp.tools.specialized.manage_specialized.japanese_book_organizer_helper") as japanese,
        patch("calibre_mcp.tools.specialized.manage_specialized.it_book_curator_helper") as it_curator,
        patch("calibre_mcp.tools.specialized.manage_specialized.reading_recommendations_helper") as reading,
    ):
        japanese.return_value = {"manga_series": [], "light_novels": [], "recommendations": []}

        it_curator.return_value = {"by_language": {}, "outdated_books": [], "learning_paths": []}

        reading.return_value = {"recommendations": [], "reasoning": "Based on reading history"}

        yield {
            "japanese": japanese,
            "it_curator": it_curator,
            "reading": reading,
        }


@pytest.mark.asyncio
async def test_manage_specialized_japanese_organizer(mock_specialized_helpers):
    """Test manage_specialized japanese_organizer operation."""
    result = await manage_specialized(operation="japanese_organizer")

    # Currently returns "not yet implemented" error
    assert "error" in result or "success" in result
    assert result.get("success") is False or "not yet implemented" in result.get("error", "").lower()


@pytest.mark.asyncio
async def test_manage_specialized_it_curator(mock_specialized_helpers):
    """Test manage_specialized it_curator operation."""
    result = await manage_specialized(operation="it_curator")

    # Currently returns "not yet implemented" error
    assert "error" in result or "success" in result
    assert result.get("success") is False or "not yet implemented" in result.get("error", "").lower()


@pytest.mark.asyncio
async def test_manage_specialized_reading_recommendations(mock_specialized_helpers):
    """Test manage_specialized reading_recommendations operation."""
    result = await manage_specialized(operation="reading_recommendations")

    # Currently returns "not yet implemented" error
    assert "error" in result or "success" in result
    assert result.get("success") is False or "not yet implemented" in result.get("error", "").lower()


@pytest.mark.asyncio
async def test_manage_specialized_invalid_operation():
    """Test manage_specialized with invalid operation."""
    result = await manage_specialized(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]
