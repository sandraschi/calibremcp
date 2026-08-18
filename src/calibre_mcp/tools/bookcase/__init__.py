"""
Bookcase cataloging MCP tool.

Photograph a physical bookcase, let a local vision model read the spines, match
each title to OpenLibrary metadata, and emit a catalog (JSON in-chat or CSV on
disk). Local-first - no cloud vision, no API keys.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from ...logging_config import get_logger
from ...server import mcp
from ...services.bookcase_catalog import catalog as _catalog
from ...services.bookcase_catalog import write_csv as _write_csv

logger = get_logger("calibremcp.tools.bookcase")


@mcp.tool()
async def bookcase_catalog(
    operation: Annotated[
        Literal["analyze", "csv"],
        Field(description="Operation: analyze (catalog in-chat) or csv (write to disk)."),
    ],
    image_paths: Annotated[
        list[str],
        Field(description="Absolute paths to bookcase photo(s) (JPEG/PNG)."),
    ],
    output_path: Annotated[
        str | None,
        Field(description="Destination CSV path (csv operation only)."),
    ] = None,
) -> dict:
    """
    Catalog a physical bookcase from photos.

    Reads the visible book spines with a local vision LLM (Ollama, default
    qwen3.8:27b), then matches each title against OpenLibrary to resolve
    ISBN / year / publisher. Returns the catalog inline (analyze) or writes a
    CSV (csv).

    [RATIONALE] Consolidates the spine-reading + metadata-matching pipeline so
    cataloging a shelf is one tool call instead of a manual photo-by-photo
    workflow.

    ## Return Format
    {"success": bool, "total_identified": int, "matched_count": int,
     "unmatched_count": int, "items": [{spine_title, spine_author, confidence,
     matched, title, author, year, publisher, isbn, ol_key}], "errors": [str]}

    ## Examples
    bookcase_catalog(operation="analyze", image_paths=["D:/shelf1.jpg", "D:/shelf2.jpg"])
    bookcase_catalog(operation="csv", image_paths=["D:/shelf1.jpg"], output_path="D:/catalog.csv")

    ## Notes
    - Requires Ollama running with a vision model (qwen3.8:27b) - set
      BOOKCASE_OLLAMA_URL / BOOKCASE_VISION_MODEL to override.
    - Spine-text accuracy is ~70-90% on clear photos; review the unmatched list.
    """
    try:
        if operation == "analyze":
            return await _catalog(image_paths)

        if operation == "csv":
            result = await _catalog(image_paths)
            if not result.get("success"):
                return result
            if not output_path:
                return {"success": False, "error": "output_path required for csv operation"}
            _write_csv(result.get("items", []), output_path)
            result["csv_path"] = output_path
            return result

        return {"success": False, "error": f"Unknown operation: {operation}"}
    except Exception as e:
        logger.error("bookcase_catalog '%s' failed: %s", operation, e, exc_info=True)
        return {"success": False, "error": f"bookcase_catalog failed: {e}"}
