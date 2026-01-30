"""
Extended metadata portmanteau for CalibreMCP.

Stores translator and first_published in CalibreMCP's SQLite DB.
Calibre's pubdate is edition date; first_published = original publication (e.g. Julius Caesar 1599).
metadata.db schema is never modified.
"""

from typing import Optional, Dict, Any

from ...server import mcp
from ...logging_config import get_logger
from ..shared.error_handling import handle_tool_error, format_error_response
from ...services.extended_metadata_service import extended_metadata_service

logger = get_logger("calibremcp.tools.extended_metadata")


@mcp.tool()
async def manage_extended_metadata(
    operation: str,
    book_id: Optional[int] = None,
    translator: Optional[str] = None,
    first_published: Optional[str] = None,
    library_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Manage extended metadata (translator, first_published) for books.

    Stored in CalibreMCP's SQLite DB. Calibre's metadata.db is not modified.
    - translator: Translator name (not in Calibre schema)
    - first_published: Original publication date (e.g. "1599", "44 BC").
      Calibre's pubdate is edition date; use this for true first publication.

    SUPPORTED OPERATIONS:
    - get: Get translator and first_published for a book
    - set_translator: Set translator name
    - set_first_published: Set first publication (year or free text)
    - upsert: Set both translator and first_published (partial updates OK)
    - delete: Remove extended metadata for a book

    Args:
        operation: One of "get", "set_translator", "set_first_published", "upsert", "delete"
        book_id: Book ID (required for all operations)
        translator: Translator name (for set_translator, upsert)
        first_published: First publication (e.g. "1599", "44 BC") (for set_first_published, upsert)
        library_path: Override library path (optional)

    Returns:
        Operation-specific result dict.
    """
    try:
        if book_id is None and operation != "get":
            return format_error_response(
                error_msg="book_id is required.",
                error_code="MISSING_BOOK_ID",
                error_type="ValueError",
                operation=operation,
                suggestions=["Provide book_id", "Use query_books to find book IDs"],
                related_tools=["query_books"],
            )

        if operation == "get":
            if book_id is None:
                return format_error_response(
                    error_msg="book_id is required for get.",
                    error_code="MISSING_BOOK_ID",
                    error_type="ValueError",
                    operation=operation,
                    related_tools=["query_books"],
                )
            return extended_metadata_service.get(
                book_id=int(book_id),
                library_path=library_path,
            )

        elif operation == "set_translator":
            if not translator or not str(translator).strip():
                return format_error_response(
                    error_msg="translator is required and cannot be empty.",
                    error_code="MISSING_TRANSLATOR",
                    error_type="ValueError",
                    operation=operation,
                )
            return extended_metadata_service.set_translator(
                book_id=int(book_id),
                translator=str(translator).strip(),
                library_path=library_path,
            )

        elif operation == "set_first_published":
            if not first_published or not str(first_published).strip():
                return format_error_response(
                    error_msg="first_published is required and cannot be empty.",
                    error_code="MISSING_FIRST_PUBLISHED",
                    error_type="ValueError",
                    operation=operation,
                    suggestions=['Use year like "1599" or "44 BC" for ancient texts'],
                )
            return extended_metadata_service.set_first_published(
                book_id=int(book_id),
                first_published=str(first_published).strip(),
                library_path=library_path,
            )

        elif operation == "upsert":
            if translator is None and first_published is None:
                return format_error_response(
                    error_msg="At least one of translator or first_published is required for upsert.",
                    error_code="MISSING_FIELDS",
                    error_type="ValueError",
                    operation=operation,
                )
            return extended_metadata_service.upsert(
                book_id=int(book_id),
                translator=translator,
                first_published=first_published,
                library_path=library_path,
            )

        elif operation == "delete":
            return extended_metadata_service.delete(
                book_id=int(book_id),
                library_path=library_path,
            )

        else:
            return format_error_response(
                error_msg=f"Invalid operation: '{operation}'. Use: get, set_translator, set_first_published, upsert, delete.",
                error_code="INVALID_OPERATION",
                error_type="ValueError",
                operation=operation,
                suggestions=[
                    "get: Get translator and first_published",
                    "set_translator: Set translator name",
                    "set_first_published: Set original publication (e.g. 1599)",
                    "upsert: Set both (partial OK)",
                    "delete: Remove extended metadata",
                ],
                related_tools=["manage_extended_metadata", "query_books"],
            )

    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={
                "book_id": book_id,
                "translator": translator,
                "first_published": first_published,
            },
            tool_name="manage_extended_metadata",
            context="Managing extended metadata (translator, first_published)",
        )
