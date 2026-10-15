"""
Canon coverage portmanteau tool for CalibreMCP.

Answers "what canonical books/authors am I missing?" by checking library
holdings against canon lists. All list data is either fetched live from
real sources or supplied by the caller — nothing is hardcoded from memory:

- gutenberg_top100: live Project Gutenberg Top 100 downloads
  (https://www.gutenberg.org/browse/scores/top), title-level matching,
  includes Gutenberg ebook IDs for one-click import.
- nobel_laureates: live Nobel Prize API, literature category
  (https://api.nobelprize.org), author-level matching (any owned work by
  the laureate counts — the API does not name a "must-read" title and
  neither do we).
- check_list: caller-supplied [{title, author?}] — e.g. an LLM-generated
  Mustich-1000 slice. No invention, just matching.
- list_canons: enumerate the available canons.
"""

from __future__ import annotations

import json
import re
import urllib.request
from typing import Any

from ...logging_config import get_logger
from ...server import mcp
from ...services.author_service import author_service
from ..book_tools import search_books_helper as _search_books_helper
from ..shared.error_handling import handle_tool_error

logger = get_logger("calibremcp.tools.canon")

GUTENBERG_TOP_URL = "https://www.gutenberg.org/browse/scores/top"
NOBEL_URL = "https://api.nobelprize.org/2.1/laureates?limit=1000"
NETWORK_TIMEOUT = 25
_MAX_CHECK_ITEMS = 200


def _norm(s: str | None) -> str:
    """Lowercase alphanumeric fingerprint for fuzzy title/author matching."""
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _titles_match(canon_title: str, lib_title: str) -> bool:
    """Containment either way, with a minimum-length guard against 'It'/'Up' hits."""
    c, lb = _norm(canon_title), _norm(lib_title)
    if len(c) < 4 or len(lb) < 4:
        return False
    return c in lb or lb in c


def _author_matches(canon_author: str, lib_authors: Any) -> bool:
    """Surname-level match against a book's author list (dicts or strings)."""
    surname = _norm(canon_author).split()
    if not surname:
        return True
    surname = surname[-1]
    if len(surname) < 3:
        return True
    names: list[str] = []
    for a in lib_authors or []:
        names.append(a.get("name", "") if isinstance(a, dict) else str(a))
    blob = _norm(" ".join(names))
    return surname in blob


def _fetch_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "calibre-mcp/canon-coverage"})
    with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "calibre-mcp/canon-coverage"})
    with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _parse_gutenberg_top(html: str, limit: int) -> list[dict[str, Any]]:
    """Parse the Top-100-ol: entries look like 'Title by Author (1234)'."""
    m = re.search(r"Top 100 EBooks yesterday.*?<ol[^>]*>(.*?)</ol>", html, re.S)
    if not m:
        raise ValueError("Could not find the Top 100 list in the Gutenberg page (layout changed?)")
    entries: list[dict[str, Any]] = []
    for rank, link in enumerate(re.finditer(r'<a href="(/ebooks/(\d+))"[^>]*>(.*?)</a>', m.group(1), re.S), start=1):
        if len(entries) >= limit:
            break
        raw = re.sub(r"\s+", " ", link.group(3)).strip()
        downloads: int | None = None
        dm = re.search(r"\((\d[\d,]*)\)\s*$", raw)
        if dm:
            downloads = int(dm.group(1).replace(",", ""))
            raw = raw[: dm.start()].strip()
        title, author = raw, ""
        if " by " in raw:
            title, author = raw.rsplit(" by ", 1)
        try:
            gid = int(link.group(2))
        except ValueError:
            continue
        entries.append(
            {
                "rank": rank,
                "gutenberg_id": gid,
                "title": title.strip(),
                "author": author.strip(),
                "downloads": downloads,
            }
        )
    return entries


async def _owns_title(title: str, author: str = "") -> tuple[bool, list[dict[str, Any]]]:
    """Check library holdings for a title; returns (owned, evidence books)."""
    try:
        result = await _search_books_helper(title=title, limit=5)
    except Exception as e:
        logger.warning("Title search failed for %r: %s", title, e)
        return False, []
    items = result.get("items") or []
    hits: list[dict[str, Any]] = []
    for b in items:
        lib_title = b.get("title", "") if isinstance(b, dict) else ""
        if not _titles_match(title, lib_title):
            continue
        if author:
            lib_authors = b.get("authors", []) if isinstance(b, dict) else []
            if not _author_matches(author, lib_authors):
                continue
        if isinstance(b, dict):
            hits.append({"id": b.get("id"), "title": b.get("title"), "authors": b.get("authors", [])})
    return bool(hits), hits


def _owns_author(name: str) -> tuple[bool, list[dict[str, Any]]]:
    """Check library holdings for any work by an author name."""
    try:
        result = author_service.get_all(search=name, limit=10)
    except Exception as e:
        logger.warning("Author search failed for %r: %s", name, e)
        return False, []
    items = result.get("authors") or result.get("items") or []
    c = _norm(name)
    parts = [p for p in c.split() if len(p) >= 3]
    hits: list[dict[str, Any]] = []
    for a in items:
        if not isinstance(a, dict):
            continue
        blob = _norm(a.get("name", "") or a.get("sort", ""))
        if parts and all(p in blob for p in parts):
            hits.append({"id": a.get("id"), "name": a.get("name"), "book_count": a.get("book_count")})
    return bool(hits), hits


def _nobel_year(prize: dict[str, Any]) -> int | None:
    for key in ("awardYear", "prizeYear", "year"):
        try:
            if prize.get(key) is not None:
                return int(str(prize[key])[:4])
        except (ValueError, TypeError):
            continue
    return None


async def _check_title_entries(
    entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    owned: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for e in entries:
        is_owned, evidence = await _owns_title(e.get("title", ""), e.get("author", ""))
        record = {**e, "owned": is_owned, "evidence": evidence}
        (owned if is_owned else missing).append(record)
    # Fallback: contained works inside indexed collections (Delphi volumes
    # etc.) count as owned, attributed to their host volume.
    if missing:
        try:
            from ...config import CalibreConfig
            from ..contents.manage_contents import search_contents_rows

            lib = str(CalibreConfig.load_config().local_library_path or "")
            still_missing: list[dict[str, Any]] = []
            for e in missing:
                hits = search_contents_rows(e.get("title", ""), lib, limit=3) if lib else []
                if hits:
                    h = hits[0]
                    owned.append(
                        {
                            **e,
                            "owned": True,
                            "evidence": [
                                {
                                    "via_contents": True,
                                    "book_id": h["book_id"],
                                    "book_title": h["book_title"],
                                    "work_title": h["work_title"],
                                }
                            ],
                        }
                    )
                else:
                    still_missing.append(e)
            missing = still_missing
        except Exception as exc:
            logger.warning("Contents fallback failed: %s", exc)
    return owned, missing


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def canon_coverage(
    operation: str,
    items: list[dict[str, Any]] | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """
    Check library holdings against canon lists (gap analysis for builders).

    Operations:
    - list_canons: enumerate available canons (no network, no DB scan).
    - gutenberg_top100: live Project Gutenberg Top 100 downloads, title-level
      match. Returns Gutenberg IDs for one-click import of the missing.
    - nobel_laureates: live Nobel Prize API (literature), author-level match
      (any owned work by the laureate counts).
    - check_list: caller-supplied [{"title": ..., "author" (optional): ...}],
      e.g. an LLM-generated Mustich slice. Max 200 entries.

    ## Return Format
    `{"success": bool, "operation": str, "canon": str, "total": int,
    "owned_count": int, "missing_count": int, "coverage_pct": float,
    "owned": [...], "missing": [...]}` — missing entries carry acquisition
    hints (gutenberg_id when known).

    ## Examples
    `canon_coverage(operation="gutenberg_top100")`
    `canon_coverage(operation="nobel_laureates")`
    `canon_coverage(operation="check_list", items=[{"title": "The Scarlet Pimpernel", "author": "Baroness Orczy"}])`
    """
    try:
        if operation == "list_canons":
            return {
                "success": True,
                "operation": operation,
                "canons": [
                    {
                        "id": "gutenberg_top100",
                        "name": "Project Gutenberg Top 100 (yesterday's downloads)",
                        "source": GUTENBERG_TOP_URL,
                        "level": "title",
                        "live": True,
                    },
                    {
                        "id": "nobel_laureates",
                        "name": "Nobel Prize in Literature laureates",
                        "source": "https://api.nobelprize.org",
                        "level": "author",
                        "live": True,
                    },
                    {
                        "id": "check_list",
                        "name": "Your own list (paste titles)",
                        "source": "caller-supplied",
                        "level": "title",
                        "live": False,
                    },
                ],
            }

        if operation == "gutenberg_top100":
            limit = max(1, min(limit, 100))
            try:
                html = _fetch_text(GUTENBERG_TOP_URL)
            except Exception as e:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"Could not fetch Gutenberg Top 100: {e}",
                    "error_code": "CANON_FETCH_ERROR",
                }
            try:
                entries = _parse_gutenberg_top(html, limit)
            except ValueError as e:
                return {"success": False, "operation": operation, "error": str(e), "error_code": "CANON_PARSE_ERROR"}
            owned, missing = await _check_title_entries(entries)
            total = len(entries)
            return {
                "success": True,
                "operation": operation,
                "canon": "gutenberg_top100",
                "total": total,
                "owned_count": len(owned),
                "missing_count": len(missing),
                "coverage_pct": round(100 * len(owned) / total, 1) if total else 0.0,
                "owned": owned,
                "missing": missing,
            }

        if operation == "nobel_laureates":
            try:
                payload = _fetch_json(NOBEL_URL)
            except Exception as e:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"Could not fetch Nobel laureates: {e}",
                    "error_code": "CANON_FETCH_ERROR",
                }
            laureates = payload.get("laureates") or []
            # The category query param is not honored reliably; filter
            # client-side so physics laureates never pollute a books report.
            lit: list[dict[str, Any]] = []
            for lch in laureates:
                prizes = lch.get("nobelPrizes") or []
                if any(
                    "literature" in str(p.get("category", {}).get("en", "")).lower()
                    for p in prizes
                    if isinstance(p, dict)
                ):
                    lit.append(lch)
            laureates = lit
            owned: list[dict[str, Any]] = []
            missing: list[dict[str, Any]] = []
            for lch in laureates:
                name_d = lch.get("knownName") or {}
                name = name_d.get("en") or lch.get("fullName", {}).get("en") or ""
                prizes = lch.get("nobelPrizes") or []
                year = _nobel_year(prizes[0]) if prizes else None
                motivation = ""
                if prizes:
                    mot = prizes[0].get("motivation") or {}
                    motivation = mot.get("en", "") if isinstance(mot, dict) else str(mot)
                is_owned, evidence = _owns_author(name) if name else (False, [])
                record = {
                    "name": name,
                    "year": year,
                    "motivation": motivation,
                    "owned": is_owned,
                    "evidence": evidence,
                }
                (owned if is_owned else missing).append(record)
            owned.sort(key=lambda r: (r["year"] is None, r["year"]))
            missing.sort(key=lambda r: (r["year"] is None, r["year"]))
            total = len(owned) + len(missing)
            return {
                "success": True,
                "operation": operation,
                "canon": "nobel_laureates",
                "total": total,
                "owned_count": len(owned),
                "missing_count": len(missing),
                "coverage_pct": round(100 * len(owned) / total, 1) if total else 0.0,
                "owned": owned,
                "missing": missing,
            }

        if operation == "check_list":
            if not items:
                return {
                    "success": False,
                    "operation": operation,
                    "error": "items is required for operation='check_list': "
                    '[{"title": "...", "author": "..."}] (author optional).',
                    "error_code": "MISSING_ITEMS",
                }
            entries = [
                {"title": str(i.get("title", "")), "author": str(i.get("author", ""))}
                for i in items[:_MAX_CHECK_ITEMS]
                if i.get("title")
            ]
            owned, missing = await _check_title_entries(entries)
            total = len(entries)
            return {
                "success": True,
                "operation": operation,
                "canon": "check_list",
                "total": total,
                "owned_count": len(owned),
                "missing_count": len(missing),
                "coverage_pct": round(100 * len(owned) / total, 1) if total else 0.0,
                "owned": owned,
                "missing": missing,
                "truncated": len(items) > _MAX_CHECK_ITEMS,
            }

        return {
            "success": False,
            "operation": operation,
            "error": f"Invalid operation: '{operation}'. Must be one of: "
            "'list_canons', 'gutenberg_top100', 'nobel_laureates', 'check_list'.",
            "error_code": "INVALID_OPERATION",
        }
    except Exception as e:
        return handle_tool_error(
            exception=e,
            operation=operation,
            parameters={"limit": limit, "item_count": len(items) if items else 0},
            tool_name="canon_coverage",
            context="Checking canon coverage",
        )
