"""Export API endpoints."""

from fastapi import APIRouter, Body

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.post("/csv")
async def export_to_csv(
    output_path: str | None = Body(None),
    book_ids: list[int] | None = Body(None),
    author: str | None = Body(None),
    tag: str | None = Body(None),
    limit: int = Body(1000, ge=1),
    include_fields: list[str] | None = Body(None),
    open_file: bool = Body(True),
):
    """Export books to CSV format."""
    try:
        result = await mcp_client.call_tool(
            "export_books",
            {
                "operation": "csv",
                "output_path": output_path,
                "book_ids": book_ids,
                "author": author,
                "tag": tag,
                "limit": limit,
                "include_fields": include_fields,
                "open_file": open_file,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/json")
async def export_to_json(
    output_path: str | None = Body(None),
    book_ids: list[int] | None = Body(None),
    author: str | None = Body(None),
    tag: str | None = Body(None),
    limit: int = Body(1000, ge=1),
    pretty: bool = Body(True),
    open_file: bool = Body(True),
):
    """Export books to JSON format."""
    try:
        result = await mcp_client.call_tool(
            "export_books",
            {
                "operation": "json",
                "output_path": output_path,
                "book_ids": book_ids,
                "author": author,
                "tag": tag,
                "limit": limit,
                "pretty": pretty,
                "open_file": open_file,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/html")
async def export_to_html(
    output_path: str | None = Body(None),
    book_ids: list[int] | None = Body(None),
    author: str | None = Body(None),
    tag: str | None = Body(None),
    limit: int = Body(1000, ge=1),
    open_file: bool = Body(True),
):
    """Export books to HTML format."""
    try:
        result = await mcp_client.call_tool(
            "export_books",
            {
                "operation": "html",
                "output_path": output_path,
                "book_ids": book_ids,
                "author": author,
                "tag": tag,
                "limit": limit,
                "open_file": open_file,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/pandoc")
async def export_with_pandoc(
    format_type: str = Body("docx", regex="^(docx|pdf|epub|html|latex|odt|rtf|txt)$"),
    output_path: str | None = Body(None),
    book_ids: list[int] | None = Body(None),
    author: str | None = Body(None),
    tag: str | None = Body(None),
    limit: int = Body(100, ge=1),
    open_file: bool = Body(True),
):
    """Export books using Pandoc."""
    try:
        result = await mcp_client.call_tool(
            "export_books",
            {
                "operation": "pandoc",
                "format_type": format_type,
                "output_path": output_path,
                "book_ids": book_ids,
                "author": author,
                "tag": tag,
                "limit": limit,
                "open_file": open_file,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
