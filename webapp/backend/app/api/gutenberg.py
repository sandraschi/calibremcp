"""Project Gutenberg API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class GutenbergSearchRequest(BaseModel):
    """Request body for Gutenberg search."""

    query: str


class GutenbergImportRequest(BaseModel):
    """Request body for Gutenberg import."""

    book_id: int
    format: str | None = "application/epub+zip"


@router.post("/search")
async def search_gutenberg_api(body: GutenbergSearchRequest):
    """Search Project Gutenberg."""
    if not body.query or not body.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")

    try:
        from calibre_mcp.tools.import_export.gutenberg_client import search_gutenberg

        result = await search_gutenberg(body.query.strip())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_gutenberg_book_api(body: GutenbergImportRequest):
    """Download and import a book from Project Gutenberg."""
    try:
        from pathlib import Path

        from calibre_mcp.tools.book_management.add_book import add_book_helper
        from calibre_mcp.tools.import_export.gutenberg_client import download_gutenberg_book

        tmp_path = await download_gutenberg_book(body.book_id, preferred_format=body.format)
        if not tmp_path:
            raise HTTPException(status_code=404, detail="Could not download book from Gutenberg.")

        try:
            result = await add_book_helper(file_path=tmp_path)
            return result
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gutenberg import failed: {str(e)}")
