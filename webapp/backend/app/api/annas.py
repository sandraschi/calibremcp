"""Anna's Archive search API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class AnnasSearchRequest(BaseModel):
    """Request body for Anna's search."""

    query: str
    max_results: int = 20
    mirrors: list[str] | None = None


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
