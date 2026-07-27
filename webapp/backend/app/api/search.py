"""Search API endpoints — keyword, advanced filters, semantic RAG, full-text."""

from __future__ import annotations

import re
from typing import Any, Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

SearchMode = Literal["auto", "keyword", "advanced", "semantic", "fulltext"]

_NATURAL_LANGUAGE_RE = re.compile(
    r"\b(books?|novels?|about|like|similar|recommend|genre|tagged|author|published|reading)\b",
    re.IGNORECASE,
)

_ADVANCED_FILTER_KEYS = (
    "author",
    "authors",
    "exclude_authors",
    "tag",
    "tags",
    "exclude_tags",
    "series",
    "exclude_series",
    "publisher",
    "publishers",
    "title",
    "min_rating",
    "max_rating",
    "rating",
    "unrated",
    "pubdate_start",
    "pubdate_end",
    "added_after",
    "added_before",
    "min_year",
    "max_year",
    "formats",
    "comment",
    "has_empty_comments",
    "has_publisher",
    "min_size",
    "max_size",
)


class AdvancedSearchRequest(BaseModel):
    query: str | None = None
    text: str | None = None
    title: str | None = None
    author: str | None = None
    authors: list[str] | None = None
    exclude_authors: list[str] | None = None
    tag: str | None = None
    tags: list[str] | None = None
    exclude_tags: list[str] | None = None
    series: str | None = None
    exclude_series: list[str] | None = None
    publisher: str | None = None
    publishers: list[str] | None = None
    has_publisher: bool | None = None
    rating: int | None = Field(default=None, ge=1, le=5)
    min_rating: int | None = Field(default=None, ge=1, le=5)
    max_rating: int | None = Field(default=None, ge=1, le=5)
    unrated: bool | None = None
    pubdate_start: str | None = None
    pubdate_end: str | None = None
    min_year: int | None = None
    max_year: int | None = None
    added_after: str | None = None
    added_before: str | None = None
    formats: list[str] | None = None
    comment: str | None = None
    has_empty_comments: bool | None = None
    min_size: int | None = None
    max_size: int | None = None
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


class SmartSearchRequest(AdvancedSearchRequest):
    mode: SearchMode = "auto"
    include_snippets: bool = True


def _has_advanced_filters(filters: dict[str, Any]) -> bool:
    for key in _ADVANCED_FILTER_KEYS:
        value = filters.get(key)
        if value not in (None, "", []):
            return True
    return False


def _year_to_pubdate(filters: dict[str, Any]) -> dict[str, Any]:
    """Map min_year/max_year to pubdate_start/pubdate_end when not already set."""
    out = dict(filters)
    if out.get("min_year") and not out.get("pubdate_start"):
        out["pubdate_start"] = f"{out['min_year']}-01-01"
    if out.get("max_year") and not out.get("pubdate_end"):
        out["pubdate_end"] = f"{out['max_year']}-12-31"
    out.pop("min_year", None)
    out.pop("max_year", None)
    return out


def _normalize_book_items(result: dict[str, Any]) -> dict[str, Any]:
    """Normalize query_books / fulltext payloads for fleet consumers."""
    if not isinstance(result, dict):
        return {"items": [], "total": 0, "success": False}

    items = result.get("items") or result.get("results") or result.get("books") or []
    total = result.get("total")
    if total is None:
        total = result.get("total_found") or result.get("total_count") or len(items)

    normalized_items: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        book_id = item.get("id")
        tags = item.get("tags") or []
        if tags and isinstance(tags[0], dict):
            tags = [t.get("name", "") for t in tags if t.get("name")]
        authors = item.get("authors") or []
        if authors and isinstance(authors[0], dict):
            authors = [a.get("name", "") for a in authors if a.get("name")]
        normalized_items.append(
            {
                **item,
                "id": f"calibre:{book_id}" if book_id is not None else item.get("id"),
                "book_id": book_id,
                "authors": authors,
                "tags": tags,
                "source": "calibre",
                "loadable": book_id is not None,
                "cover_url": f"/api/books/{book_id}/cover" if book_id is not None else None,
                "poster_url": f"/api/books/{book_id}/cover" if book_id is not None else None,
                "artwork_url": f"/api/books/{book_id}/cover" if book_id is not None else None,
            }
        )

    return {
        **result,
        "items": normalized_items,
        "data": normalized_items,
        "total": total,
        "count": total,
        "success": result.get("success", True),
    }


async def _keyword_search(
    *,
    query: str | None,
    author: str | None = None,
    tag: str | None = None,
    min_rating: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    result = await mcp_client.call_tool(
        "query_books",
        {
            "operation": "search",
            "text": query,
            "author": author,
            "tag": tag,
            "min_rating": min_rating,
            "limit": limit,
            "offset": offset,
        },
    )
    payload = _normalize_book_items(result if isinstance(result, dict) else {})
    payload["engine"] = "calibre_keyword"
    payload["message"] = f"Calibre keyword search: {payload.get('total', 0)} result(s)"
    return payload


async def _advanced_search(req: AdvancedSearchRequest) -> dict[str, Any]:
    args = _year_to_pubdate(req.model_dump(exclude_none=True))
    text = args.pop("query", None) or args.pop("text", None)
    args["operation"] = "search"
    if text:
        args["text"] = text
    result = await mcp_client.call_tool("query_books", args)
    payload = _normalize_book_items(result if isinstance(result, dict) else {})
    payload["engine"] = "calibre_advanced"
    payload["message"] = f"Calibre advanced search: {payload.get('total', 0)} result(s)"
    return payload


async def _semantic_search(query: str, *, limit: int = 20) -> dict[str, Any]:
    result = await mcp_client.call_tool(
        "calibre_metadata_search",
        {"query": query, "top_k": min(limit, 50)},
    )
    if not isinstance(result, dict):
        return {"items": [], "data": [], "total": 0, "engine": "calibre_semantic", "success": False}

    hits = result.get("results") or result.get("hits") or []
    items: list[dict[str, Any]] = []
    for hit in hits:
        meta = hit.get("metadata") if isinstance(hit, dict) else {}
        if not isinstance(meta, dict):
            meta = hit if isinstance(hit, dict) else {}
        book_id = meta.get("book_id") or meta.get("id")
        items.append(
            {
                "id": f"calibre:{book_id}" if book_id is not None else None,
                "book_id": book_id,
                "title": meta.get("title") or meta.get("name") or "Unknown",
                "authors": meta.get("authors") or [],
                "tags": meta.get("tags") or [],
                "summary": meta.get("comments") or meta.get("summary") or hit.get("content") or "",
                "score": hit.get("score"),
                "source": "calibre",
                "loadable": book_id is not None,
            }
        )

    return {
        "items": items,
        "data": items,
        "total": len(items),
        "count": len(items),
        "engine": "calibre_semantic",
        "message": f"Calibre semantic search: {len(items)} result(s)",
        "success": result.get("success", True),
    }


async def _fulltext_search(
    query: str,
    *,
    limit: int = 50,
    offset: int = 0,
    include_snippets: bool = True,
) -> dict[str, Any]:
    result = await mcp_client.call_tool(
        "search_fulltext",
        {
            "query": query.strip(),
            "limit": limit,
            "offset": offset,
            "include_snippets": include_snippets,
            "enrich": True,
        },
    )
    if not isinstance(result, dict):
        return {"items": [], "data": [], "total": 0, "engine": "calibre_fulltext", "success": False}

    books = result.get("books") or []
    snippets = result.get("snippets") or {}
    for book in books:
        bid = book.get("id")
        if bid is not None and bid in snippets:
            book["snippet"] = snippets[bid]

    payload = _normalize_book_items({"items": books, "total": result.get("total") or len(books)})
    payload["engine"] = "calibre_fulltext"
    payload["message"] = f"Calibre full-text search: {payload.get('total', 0)} result(s)"
    return payload


@router.get("/")
async def search_books(
    query: str | None = Query(None, description="Search query text"),
    author: str | None = None,
    tag: str | None = None,
    min_rating: int | None = Query(None, ge=1, le=5),
    fulltext: bool = Query(False, description="Search inside book content (Calibre FTS)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Book search: metadata (default) or full-text inside book content."""
    try:
        if fulltext and query and query.strip():
            return await _fulltext_search(query, limit=limit, offset=offset)
        return await _keyword_search(
            query=query,
            author=author,
            tag=tag,
            min_rating=min_rating,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise handle_mcp_error(e) from e


@router.post("/advanced")
async def advanced_search(req: AdvancedSearchRequest):
    """Multi-filter Calibre search (author, tags, series, publisher, dates, ratings, formats)."""
    try:
        return await _advanced_search(req)
    except Exception as e:
        raise handle_mcp_error(e) from e


@router.post("/smart")
async def smart_search(req: SmartSearchRequest):
    """Intelligent search: auto-selects keyword, advanced filters, semantic metadata, or full-text."""
    try:
        query = (req.query or req.text or "").strip()
        filters = req.model_dump(exclude_none=True)
        has_filters = _has_advanced_filters(filters)

        if not query and not has_filters:
            return {
                "items": [],
                "data": [],
                "total": 0,
                "count": 0,
                "engine": None,
                "message": "query or filters required",
                "success": True,
            }

        mode = req.mode
        if mode == "semantic":
            if not query:
                return await _advanced_search(req)
            return await _semantic_search(query, limit=req.limit)
        if mode == "fulltext":
            if not query:
                return await _advanced_search(req)
            return await _fulltext_search(
                query,
                limit=req.limit,
                offset=req.offset,
                include_snippets=req.include_snippets,
            )
        if mode == "advanced" or (mode == "auto" and has_filters):
            return await _advanced_search(req)
        if mode == "keyword":
            return await _keyword_search(
                query=query or None,
                author=req.author,
                tag=req.tag,
                min_rating=req.min_rating,
                limit=req.limit,
                offset=req.offset,
            )

        # auto without explicit filters
        if query and _NATURAL_LANGUAGE_RE.search(query):
            semantic = await _semantic_search(query, limit=min(req.limit, 30))
            if semantic.get("total", 0) > 0:
                semantic["message"] = (
                    f"{semantic['message']} (auto: natural-language query → semantic index)"
                )
                return semantic

        return await _keyword_search(
            query=query or None,
            author=req.author,
            tag=req.tag,
            min_rating=req.min_rating,
            limit=req.limit,
            offset=req.offset,
        )
    except Exception as e:
        raise handle_mcp_error(e) from e
