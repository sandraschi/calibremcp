"""
Unit tests for export_books portmanteau tool.

Tests all 4 operations: csv, json, html, pandoc
"""

from unittest.mock import patch

import pytest

# Patch mcp.tool before importing to make it a no-op
with patch("calibre_mcp.server.mcp") as mock_mcp_instance:
    # Make mcp.tool() return the function unchanged
    mock_mcp_instance.tool = lambda *_a, **_kw: lambda f: f
    from calibre_mcp.tools.import_export.export_books_portmanteau import export_books


@pytest.fixture
def mock_export_helpers():
    """Mock the export helper functions."""
    with (
        patch("calibre_mcp.tools.import_export.export_books_portmanteau.export_csv_helper") as csv,
        patch("calibre_mcp.tools.import_export.export_books_portmanteau.export_json_helper") as json,
        patch("calibre_mcp.tools.import_export.export_books_portmanteau.export_html_helper") as html,
        patch("calibre_mcp.tools.import_export.export_books_portmanteau.export_pandoc_helper") as pandoc,
    ):
        csv.return_value = {"success": True, "file_path": "/path/to/export.csv", "books_exported": 10}

        json.return_value = {"success": True, "file_path": "/path/to/export.json", "books_exported": 10}

        html.return_value = {"success": True, "file_path": "/path/to/export.html", "books_exported": 10}

        pandoc.return_value = {
            "success": True,
            "file_path": "/path/to/export.docx",
            "books_exported": 10,
            "format": "docx",
        }

        yield {
            "csv": csv,
            "json": json,
            "html": html,
            "pandoc": pandoc,
        }


@pytest.mark.asyncio
async def test_export_books_csv(mock_export_helpers):
    """Test export_books csv operation."""
    result = await export_books(operation="csv", limit=10)

    assert result["success"] is True
    assert result["books_exported"] == 10
    mock_export_helpers["csv"].assert_called_once()


@pytest.mark.asyncio
async def test_export_books_json(mock_export_helpers):
    """Test export_books json operation."""
    result = await export_books(operation="json", limit=10)

    assert result["success"] is True
    assert result["books_exported"] == 10
    mock_export_helpers["json"].assert_called_once()


@pytest.mark.asyncio
async def test_export_books_html(mock_export_helpers):
    """Test export_books html operation."""
    result = await export_books(operation="html", limit=10)

    assert result["success"] is True
    assert result["books_exported"] == 10
    mock_export_helpers["html"].assert_called_once()


@pytest.mark.asyncio
async def test_export_books_pandoc(mock_export_helpers):
    """Test export_books pandoc operation."""
    result = await export_books(operation="pandoc", format_type="docx", limit=10)

    assert result["success"] is True
    assert result["format"] == "docx"
    mock_export_helpers["pandoc"].assert_called_once()


@pytest.mark.asyncio
async def test_export_books_invalid_operation():
    """Test export_books with invalid operation."""
    result = await export_books(operation="invalid")

    assert "error" in result
    assert "Invalid operation" in result["error"]
