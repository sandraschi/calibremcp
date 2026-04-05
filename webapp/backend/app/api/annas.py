"""Anna's Archive search API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AnnasSearchRequest(BaseModel):
    """Request body for Anna's search."""

    query: str
    max_results: int = 20
    mirrors: list[str] | None = None


class AnnasDownloadRequest(BaseModel):
    """Request body for Anna's download."""

    md5: str
    target_format: str | None = None
    title: str | None = None
    authors: list[str] | None = None
    tags: list[str] | None = None
    series: str | None = None
    library_path: str | None = None


@router.post("/search")
async def search_annas_archive(body: AnnasSearchRequest):
    """Search Anna's Archive by book title or author."""
    if not body.query or not body.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    try:
        from calibre_mcp.tools.import_export.annas_client import search_annas

        result = await search_annas(
            query=body.query.strip(),
            max_results=min(body.max_results, 50),
            mirrors=body.mirrors if body.mirrors else None,
        )
        return result
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Anna's client not available: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def download_annas_book_api(body: AnnasDownloadRequest):
    """Download and import a book from Anna's Archive."""
    if not body.md5 or not body.md5.strip():
        raise HTTPException(status_code=400, detail="MD5 is required")

    try:
        from pathlib import Path

        from calibre_mcp.tools.book_management.add_book import add_book_helper
        from calibre_mcp.tools.import_export.annas_client import (
            AnnasLinkRestrictionError,
            AnnasNoLinksError,
            download_annas_book,
        )

        try:
            tmp_path = await download_annas_book(body.md5.strip(), target_format=body.target_format)
            if not tmp_path:
                raise HTTPException(status_code=404, detail="Download failed. All mirrors were unreachable.")
        except AnnasLinkRestrictionError as e:
            # Special case: manual interaction needed
            return {
                "success": False,
                "error_code": "MANUAL_INTERACTION_REQUIRED",
                "message": str(e),
                "detail_url": f"https://annas-archive.gl/md5/{body.md5.strip()}" # Fallback link
            }
        except AnnasNoLinksError as e:
            raise HTTPException(status_code=404, detail=str(e))

        try:
            # Prepare metadata for import
            import_metadata = {}
            if body.title:
                import_metadata["title"] = body.title
            if body.authors:
                import_metadata["authors"] = body.authors
            if body.tags:
                import_metadata["tags"] = body.tags
            if body.series:
                import_metadata["series"] = body.series

            result = await add_book_helper(
                file_path=tmp_path,
                metadata=import_metadata if import_metadata else None,
                library_path=body.library_path,
            )
            return result
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download/Import failed: {str(e)}")
