"""
Book export portmanteau tool for CalibreMCP.

Consolidates all book export operations into a single unified interface.
"""

from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ..shared.error_handling import format_error_response, handle_tool_error

# Import helper functions (NOT registered as MCP tools)
from .export_helpers import (
    export_csv_helper,
    export_html_helper,
    export_json_helper,
    export_pandoc_helper,
    export_stats_csv_helper,
    export_stats_html_helper,
    export_stats_json_helper,
)

logger = get_logger("calibremcp.tools.export")


@mcp.tool()
async def export_books(
    operation: str,
    # Common parameters
    output_path: str | None = None,
    book_ids: list[int] | None = None,
    author: str | None = None,
    tag: str | None = None,
    limit: int = 1000,
    open_file: bool = True,
    # Detail level for csv/json/html (minimal, standard, full)
    detail_level: str | None = None,
    # CSV-specific parameters
    include_fields: list[str] | None = None,
    # JSON-specific parameters
    pretty: bool = True,
    # HTML-specific parameters
    html_style: str = "catalog",
    # Pandoc-specific parameters
    format_type: str = "docx",
    # Stats-specific parameters
    stats_format: str = "json",
) -> dict[str, Any]:
    """
    Export book metadata and library statistics to various professional formats.

    Operations:
    - csv: Excel-compatible metadata export with custom fields.
    - json: Complete metadata dump for data exchange or backup.
    - html: Standalone styled catalog, gallery, or dashboard views.
    - pandoc: Professional document conversion (DOCX, PDF, EPUB, RTF, etc.).
    - stats: Library-wide analytics exported to CSV, JSON, or HTML.

    Example:
    - export_books(operation="csv", author="Agatha Christie")
    - export_books(operation="pandoc", format_type="docx", tag="mystery")
    """
    try:
        if operation == "csv":
            try:
                return await export_csv_helper(
                    output_path=output_path,
                    book_ids=book_ids,
                    author=author,
                    tag=tag,
                    limit=limit,
                    include_fields=include_fields,
                    detail_level=detail_level,
                    open_file=open_file,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"author": author, "tag": tag, "book_ids": book_ids},
                    tool_name="export_books",
                    context="Exporting books to CSV format",
                )

        elif operation == "json":
            try:
                return await export_json_helper(
                    output_path=output_path,
                    book_ids=book_ids,
                    author=author,
                    tag=tag,
                    limit=limit,
                    pretty=pretty,
                    detail_level=detail_level,
                    open_file=open_file,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"author": author, "tag": tag, "book_ids": book_ids},
                    tool_name="export_books",
                    context="Exporting books to JSON format",
                )

        elif operation == "html":
            try:
                return await export_html_helper(
                    output_path=output_path,
                    book_ids=book_ids,
                    author=author,
                    tag=tag,
                    limit=limit,
                    open_file=open_file,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"author": author, "tag": tag, "book_ids": book_ids},
                    tool_name="export_books",
                    context="Exporting books to HTML format",
                )

        elif operation == "stats":
            try:
                if stats_format == "csv":
                    return await export_stats_csv_helper(
                        output_path=output_path,
                        open_file=open_file,
                    )
                if stats_format == "html":
                    return await export_stats_html_helper(
                        output_path=output_path,
                        open_file=open_file,
                    )
                return await export_stats_json_helper(
                    output_path=output_path,
                    pretty=pretty,
                    open_file=open_file,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"stats_format": stats_format},
                    tool_name="export_books",
                    context="Exporting library statistics",
                )

        elif operation == "pandoc":
            try:
                return await export_pandoc_helper(
                    output_path=output_path,
                    format_type=format_type,
                    book_ids=book_ids,
                    author=author,
                    tag=tag,
                    limit=limit,
                    open_file=open_file,
                )
            except Exception as e:
                return handle_tool_error(
                    exception=e,
                    operation=operation,
                    parameters={"format_type": format_type, "author": author, "tag": tag},
                    tool_name="export_books",
                    context=f"Exporting books using Pandoc to {format_type} format",
                )

        else:
            return format_error_response(
                error_msg=(
                    f"Invalid operation: '{operation}'. Must be one of: "
                    "'csv', 'json', 'html', 'pandoc', 'stats'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='csv' to export books to CSV",
                    "Use operation='json' to export books to JSON",
                    "Use operation='html' to export books to HTML (html_style: catalog, gallery, dashboard)",
                    "Use operation='pandoc' to export using Pandoc (DOCX, PDF, EPUB, etc.)",
                    "Use operation='stats' to export library statistics (stats_format: csv, json, html)",
                ],
                related_tools=["export_books"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "operation": operation,
                "author": author,
                "tag": tag,
                "format_type": format_type if operation == "pandoc" else None,
            },
            tool_name="export_books",
            context="Book export operation",
        )
