"""
Book export portmanteau tool for CalibreMCP.

Consolidates all book export operations into a single unified interface.
"""

from typing import Optional, List, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response

# Import helper functions (NOT registered as MCP tools)
from .export_helpers import (
    export_csv_helper,
    export_json_helper,
    export_html_helper,
    export_pandoc_helper,
)

logger = get_logger("calibremcp.tools.export")


@mcp.tool()
async def export_books(
    operation: str,
    # Common parameters
    output_path: Optional[str] = None,
    book_ids: Optional[List[int]] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 1000,
    open_file: bool = True,
    # CSV-specific parameters
    include_fields: Optional[List[str]] = None,
    # JSON-specific parameters
    pretty: bool = True,
    # Pandoc-specific parameters
    format_type: str = "docx",
) -> Dict[str, Any]:
    """
    Comprehensive book export tool for CalibreMCP.

    PORTMANTEAU PATTERN RATIONALE:
    Instead of creating 4 separate tools (one per export format), this tool consolidates related
    export operations into a single interface. This design:
    - Prevents tool explosion (4 tools → 1 tool) while maintaining full functionality
    - Improves discoverability by grouping related operations together
    - Reduces cognitive load when working with export tasks
    - Enables consistent export interface across all formats
    - Follows FastMCP 2.13+ best practices for feature-rich MCP servers

    SUPPORTED OPERATIONS:
    - csv: Export books to CSV format (Excel-compatible)
    - json: Export books to JSON format (data exchange/backup)
    - html: Export books to beautiful HTML format (web viewing)
    - pandoc: Export books using Pandoc (DOCX, PDF, EPUB, LaTeX, RTF, etc.)

    OPERATIONS DETAIL:

    csv: Export to CSV format
    - Creates Excel-compatible CSV files with UTF-8 BOM encoding
    - Supports custom field selection via include_fields parameter
    - Automatically formats lists (authors, tags, formats) as comma-separated strings
    - Saves to Desktop/calibre_exports/ by default
    - Parameters: output_path, book_ids, author, tag, limit, include_fields, open_file

    json: Export to JSON format
    - Exports complete book metadata as JSON
    - Supports pretty-printed (indented) or compact format
    - Useful for data exchange, backup, or import into other systems
    - Preserves all book data structures (lists, dicts, etc.)
    - Parameters: output_path, book_ids, author, tag, limit, pretty, open_file

    html: Export to HTML format
    - Creates beautiful standalone HTML file with embedded CSS
    - Professional styling optimized for readability
    - Includes export information, book catalog, and summary
    - Can be viewed in any web browser or printed
    - Parameters: output_path, book_ids, author, tag, limit, open_file

    pandoc: Export using Pandoc
    - Converts book metadata to Markdown then uses Pandoc for format conversion
    - Supports: docx (default), pdf, epub, html, latex, odt, rtf, txt
    - Requires Pandoc to be installed and available in PATH
    - PDF export additionally requires LaTeX (MiKTeX or TeX Live)
    - Recommended for professional document generation
    - Parameters: output_path, format_type, book_ids, author, tag, limit, open_file

    Prerequisites:
        - Library must be accessible (auto-loaded on server startup)
        - For 'pandoc' operation: Pandoc must be installed (check with: pandoc --version)
        - For PDF export: LaTeX must be installed (MiKTeX on Windows, TeX Live on Linux/Mac)

    Parameters:
        operation: The export operation to perform. Must be one of: "csv", "json", "html", "pandoc"

        # Common parameters (all operations)
        output_path: Path where to save the exported file. If None, saves to Desktop/calibre_exports/
                    with intelligent filename based on filters.
                    Example: "C:/Users/Name/Desktop/calibre_exports/books_export.csv"

        book_ids: Optional list of specific book IDs to export.
                 If None, exports all matching books (up to limit).
                 Example: [1, 2, 3]

        author: Filter books by author name (optional)
                Example: "Conan Doyle"

        tag: Filter books by tag name (optional)
             Example: "mystery"

        limit: Maximum number of books to export
               - CSV/JSON/HTML: default 1000, use -1 for no limit
               - Pandoc: default 100 (processing can be slow for large exports)

        open_file: If True, opens the exported file with default application after export
                  (default: True). Works on Windows, macOS, and Linux.

        # CSV-specific parameters
        include_fields: List of fields to include in CSV. If None, includes all common fields.
                       Available: id, title, authors, tags, series, rating, pubdate,
                       publisher, isbn, comments, formats, has_cover, timestamp
                       Example: ["title", "authors", "rating", "tags"]

        # JSON-specific parameters
        pretty: If True, format JSON with indentation (default: True)
                If False, use compact JSON format

        # Pandoc-specific parameters
        format_type: Output format for pandoc operation (default: "docx")
                    Supported: docx, epub, html, latex, odt, pdf, rtf, txt
                    Note: PDF export requires LaTeX

    Returns:
        Dictionary containing operation-specific results:

        For all operations:
            {
                "success": bool - Whether export succeeded
                "file_path": str - Path to exported file (if successful)
                "books_exported": int - Number of books exported
                "export_date": str - ISO timestamp of export
                "opened": bool - Whether file was opened (if open_file=True)
            }

        For operation="csv":
            {
                ... (above fields) ...
                "fields_included": List[str] - Fields included in CSV
            }

        For operation="pandoc":
            {
                ... (above fields) ...
                "format": str - Format that was exported
                "pandoc_available": bool - Whether Pandoc was available
                "error": Optional[str] - Error message if success=False
            }

    Usage:
        # Export all books to CSV
        result = await export_books(operation="csv")

        # Export books by author to JSON
        result = await export_books(operation="json", author="Conan Doyle")

        # Export mystery books to HTML
        result = await export_books(operation="html", tag="mystery")

        # Export to DOCX using Pandoc
        result = await export_books(operation="pandoc", format_type="docx", author="Conan Doyle")

    Examples:
        # Export books by Conan Doyle to CSV
        result = await export_books(
            operation="csv",
            author="Conan Doyle",
            include_fields=["title", "authors", "rating", "tags"]
        )

        # Export mystery books to JSON (compact format)
        result = await export_books(
            operation="json",
            tag="mystery",
            pretty=False
        )

        # Export to beautiful HTML
        result = await export_books(
            operation="html",
            author="Agatha Christie",
            limit=50
        )

        # Export to DOCX (most common Pandoc use case)
        result = await export_books(
            operation="pandoc",
            format_type="docx",
            author="Conan Doyle"
        )

        # Export to PDF (requires Pandoc + LaTeX)
        result = await export_books(
            operation="pandoc",
            format_type="pdf",
            book_ids=[1, 2, 3],
            limit=10
        )

        # Export specific books to custom path
        result = await export_books(
            operation="csv",
            book_ids=[1, 2, 3],
            output_path="C:/Exports/my_books.csv"
        )

    Errors:
        Common errors and solutions:
        - Invalid operation: Use one of "csv", "json", "html", "pandoc"
        - Pandoc not found (pandoc operation): Install Pandoc and ensure it's in PATH
        - LaTeX not found (PDF export): Install MiKTeX (Windows) or TeX Live (Linux/Mac)
        - No books found: Verify filters (author, tag) or book_ids are correct
        - File write error: Check file permissions and disk space

    See Also:
        - query_books(): For finding books to export
        - manage_books(): For book management operations
        - manage_libraries(): For library management
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
                    "'csv', 'json', 'html', 'pandoc'"
                ),
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "Use operation='csv' to export to CSV format (Excel-compatible)",
                    "Use operation='json' to export to JSON format (data exchange)",
                    "Use operation='html' to export to HTML format (web viewing)",
                    "Use operation='pandoc' to export using Pandoc (DOCX, PDF, EPUB, etc.)",
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

