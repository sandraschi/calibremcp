"""Book API endpoints."""

from pathlib import Path

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import FileResponse

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()


@router.get("/{book_id}/cover")
async def get_book_cover(book_id: int):
    """Serve cover image for a book."""
    try:
        from calibre_mcp.db.database import DatabaseService
        from calibre_mcp.db.models import Book

        db = DatabaseService()
        if db._engine is None:
            raise HTTPException(status_code=503, detail="Database not initialized")

        db_path = db._current_db_path
        if not db_path:
            raise HTTPException(status_code=503, detail="No library loaded")

        library_path = Path(db_path).parent.resolve()
        with db.session_scope() as session:
            book = session.query(Book).filter(Book.id == book_id).first()
            if not book or not book.path:
                raise HTTPException(status_code=404, detail="Book not found")

            book_path = book.path.strip("/").strip("\\").replace("\\", "/")
            folder = (library_path / book_path).resolve()
            cover_path = None
            for name in ("cover.jpg", "cover.jpeg", "cover.png"):
                candidate = folder / name
                if candidate.exists():
                    cover_path = candidate
                    break
            if not cover_path:
                raise HTTPException(status_code=404, detail="No cover")

        media_type = "image/png" if str(cover_path).lower().endswith(".png") else "image/jpeg"
        return FileResponse(str(cover_path), media_type=media_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_books(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    author: str | None = None,
    tag: str | None = None,
    publisher: str | None = None,
    text: str | None = None,
):
    """List books with optional filters. Unfiltered browse cached 30s."""
    from ..cache import _ttl_key, get_libraries_cache, get_ttl_cached, set_ttl_cached

    lib = get_libraries_cache().get("current_library") or ""
    unfiltered = not (author or tag or publisher or text)
    if unfiltered:
        key = _ttl_key("books", lib=lib, limit=limit, offset=offset)
        cached = get_ttl_cached(key)
        if cached is not None:
            return cached
    try:
        result = await mcp_client.call_tool(
            "query_books",
            {
                "operation": "search",
                "limit": limit,
                "offset": offset,
                "author": author,
                "tag": tag,
                "publisher": publisher,
                "text": text,
            },
        )
        # Normalize for frontend: expect { items, total }; tool may return results/total_found
        if isinstance(result, dict) and "items" not in result and "results" in result:
            result = {**result, "items": result["results"], "total": result.get("total_found", len(result["results"]))}
        if unfiltered:
            set_ttl_cached(key, result, ttl=30)
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{book_id}")
async def get_book(book_id: int):
    """Get book details by ID. Uses direct BookService when available for full metadata."""
    try:
        # Prefer direct BookService for full metadata (rating, publisher, identifiers)
        try:
            from calibre_mcp.db.database import DatabaseService
            from calibre_mcp.services.book_service import BookService

            db = DatabaseService()
            if db._engine is not None and db._current_db_path:
                svc = BookService(db)
                book_dict = svc.get_by_id(book_id)
                # Normalize to match frontend Book shape
                authors = book_dict.get("authors", [])
                if authors and isinstance(authors[0], dict):
                    authors = [a.get("name", "") for a in authors]
                return {
                    "id": book_dict.get("id"),
                    "title": book_dict.get("title"),
                    "authors": authors,
                    "rating": book_dict.get("rating"),
                    "tags": [
                        t.get("name", t) if isinstance(t, dict) else t
                        for t in book_dict.get("tags", [])
                    ],
                    "formats": book_dict.get("formats", []),
                    "publisher": book_dict.get("publisher"),
                    "pubdate": book_dict.get("pubdate"),
                    "timestamp": book_dict.get("timestamp"),
                    "last_modified": book_dict.get("last_modified"),
                    "series": book_dict.get("series", {}).get("name")
                    if isinstance(book_dict.get("series"), dict)
                    else book_dict.get("series"),
                    "series_index": book_dict.get("series_index"),
                    "identifiers": book_dict.get("identifiers", {}),
                    "comments": book_dict.get("comments"),
                    "description": book_dict.get("comments"),
                    "path": book_dict.get("path"),
                    "uuid": book_dict.get("uuid"),
                    "has_cover": book_dict.get("has_cover"),
                }
        except Exception:
            pass
        # Fallback to MCP tool
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "get",
                "book_id": str(book_id),
                "include_metadata": True,
                "include_formats": True,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.get("/{book_id}/details")
async def get_book_details(book_id: int):
    """Get complete metadata and file information for a book."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "details",
                "book_id": str(book_id),
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.post("/")
async def add_book(data: dict = Body(...)):
    """Add a new book to the library."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "add",
                "file_path": data.get("file_path"),
                "metadata": data.get("metadata"),
                "fetch_metadata": data.get("fetch_metadata", True),
                "convert_to": data.get("convert_to"),
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.put("/{book_id}")
async def update_book(book_id: int, data: dict = Body(...)):
    """Update a book's metadata and properties."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "update",
                "book_id": str(book_id),
                "metadata": data.get("metadata"),
                "status": data.get("status"),
                "progress": data.get("progress"),
                "cover_path": data.get("cover_path"),
                "update_timestamp": data.get("update_timestamp", True),
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)


@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    delete_files: bool = Query(True, description="Delete files from disk"),
    force: bool = Query(False, description="Skip dependency checks"),
):
    """Delete a book from the library."""
    try:
        result = await mcp_client.call_tool(
            "manage_books",
            {
                "operation": "delete",
                "book_id": str(book_id),
                "delete_files": delete_files,
                "force": force,
            },
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
