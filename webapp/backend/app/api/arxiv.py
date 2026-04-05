from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from calibre_mcp.tools.import_export.arxiv_client import search_arxiv, download_arxiv_paper
from calibre_mcp.tools.book_management.add_book import add_book_helper

router = APIRouter(prefix="/api/arxiv", tags=["arxiv"])

class ArxivSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 20

class ArxivImportRequest(BaseModel):
    arxiv_id: str
    title: str | None = None
    authors: list[str] | None = None
    tags: list[str] | None = None
    series: str | None = None
    library_path: str | None = None

@router.post("/search")
async def api_arxiv_search(req: ArxivSearchRequest):
    result = await search_arxiv(req.query, max_results=req.max_results)
    if not result.get("success"):
        throw_msg = result.get("error", "arXiv search failed")
        raise HTTPException(status_code=500, detail=throw_msg)
    return result

@router.post("/import")
async def api_arxiv_import(req: ArxivImportRequest):
    tmp_path = await download_arxiv_paper(req.arxiv_id)
    if not tmp_path:
        raise HTTPException(status_code=500, detail=f"Failed to download arXiv paper {req.arxiv_id}")
    
    try:
        # Prepare metadata for import
        import_metadata = {}
        if req.title:
            import_metadata["title"] = req.title
        if req.authors:
            import_metadata["authors"] = req.authors
        if req.tags:
            import_metadata["tags"] = req.tags
        if req.series:
            import_metadata["series"] = req.series

        import_result = await add_book_helper(
            file_path=tmp_path,
            metadata=import_metadata if import_metadata else None,
            library_path=req.library_path,
        )
        if not import_result.get("success"):
            raise HTTPException(status_code=500, detail=import_result.get("error", "Import failed"))
        return import_result
    finally:
        import os
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
