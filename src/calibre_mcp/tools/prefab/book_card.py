"""
MCP App (Prefab): book metadata card with optional cover image.

Hosts: Claude Desktop, Cursor (when MCP Apps + Prefab renderer supported). Others may show JSON fallback.
"""

from __future__ import annotations

import base64
import os
from typing import Any

from fastmcp import Context
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Image, Text

from calibre_mcp.logging_config import get_logger
from calibre_mcp.server import mcp
from calibre_mcp.services.base_service import NotFoundError
from calibre_mcp.services.book_service import book_service

logger = get_logger("calibremcp.tools.prefab.book_card")

_MAX_COVER_BYTES = 512_000


def show_book_prefab_card(book_id: int, ctx: Context | None = None) -> Any:
    """Placeholder until ``register_book_card_tool`` replaces this with the real MCP App tool."""
    return {
        "success": False,
        "error": "prefab_unavailable",
        "message": "Prefab book card is not active (CALIBRE_PREFAB_APPS=0).",
    }


def _cover_data_uri(book_id: int) -> str | None:
    raw = book_service.get_book_cover(book_id)
    if not raw:
        return None
    if len(raw) > _MAX_COVER_BYTES:
        raw = raw[:_MAX_COVER_BYTES]
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    elif raw[:2] == b"\xff\xd8":
        mime = "image/jpeg"
    elif len(raw) >= 12 and raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        mime = "image/webp"
    else:
        mime = "image/jpeg"
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _format_authors(data: dict[str, Any]) -> str:
    authors = data.get("authors") or []
    if not authors:
        return ""
    if isinstance(authors[0], dict):
        return ", ".join(str(a.get("name", "")) for a in authors if a.get("name"))
    return ", ".join(str(a) for a in authors)


def _format_series(data: dict[str, Any]) -> str:
    series = data.get("series")
    if series is None:
        return ""
    if isinstance(series, dict):
        return str(series.get("name") or "")
    return str(series)


def _format_tags(data: dict[str, Any]) -> str:
    tags = data.get("tags") or []
    if not tags:
        return ""
    if isinstance(tags[0], dict):
        return ", ".join(str(t.get("name", "")) for t in tags if t.get("name"))
    return ", ".join(str(t) for t in tags)


def _comments_plain_text(raw: str, max_chars: int = 1200) -> str:
    """Calibre stores rich comments as HTML; Prefab ``Text`` is plain — strip tags and normalize."""
    if not raw or not str(raw).strip():
        return ""
    s = str(raw).strip()
    if "<" in s and ">" in s:
        from bs4 import BeautifulSoup

        s = BeautifulSoup(s, "html.parser").get_text(separator="\n", strip=True)
    lines: list[str] = []
    for line in s.splitlines():
        line = " ".join(line.split())
        if line:
            lines.append(line)
    out = "\n".join(lines)
    if len(out) > max_chars:
        out = out[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return out


def register_book_card_tool() -> None:
    """Register ``show_book_prefab_card`` on the global FastMCP instance."""
    if os.environ.get("CALIBRE_PREFAB_APPS", "1").strip().lower() in ("0", "false", "no", "off"):
        logger.info("Prefab book card disabled (CALIBRE_PREFAB_APPS=0)")
        return

    @mcp.tool(app=True)
    def show_book_prefab_card(book_id: int, ctx: Context | None = None) -> Any:
        """
        Show a rich book card (MCP App) with title, authors, series, tags, comment excerpt, and cover.

        Works in clients that render MCP Apps / Prefab (e.g. Claude Desktop; Cursor when supported).
        Disable with ``CALIBRE_PREFAB_APPS=0`` (skips registration).

        Args:
            book_id: Calibre book id (from ``query_books`` or the library).

        Returns:
            ToolResult with Prefab UI plus a short text summary for the model.
        """
        try:
            data = book_service.get_by_id(int(book_id))
        except NotFoundError:
            with Card(css_class="max-w-md") as view:
                with CardHeader():
                    CardTitle("Book not found")
                with CardContent():
                    Text(f"No book with id {book_id}.")
            return ToolResult(
                content=f"Book id {book_id} not found.",
                structured_content=PrefabApp(view=view, title="Not found"),
            )
        except Exception as e:
            logger.exception("show_book_prefab_card failed")
            return {
                "success": False,
                "error": str(e),
                "message": f"Could not load book {book_id}.",
            }

        title = (data.get("title") or "Untitled").strip()
        auth_s = _format_authors(data)
        series_s = _format_series(data)
        tag_s = _format_tags(data)
        synopsis = _comments_plain_text(str(data.get("comments") or ""))

        cover_uri = _cover_data_uri(int(book_id))

        with Card(css_class="max-w-lg") as view:
            with CardHeader():
                CardTitle(title)
            with CardContent():
                if cover_uri:
                    Image(
                        src=cover_uri,
                        alt=f"Cover: {title}",
                        width="200px",
                        css_class="rounded shadow object-contain",
                    )
                # One Text per line — Prefab/HTML collapses \n inside a single Text node.
                Text(f"Authors: {auth_s or '—'}")
                if series_s:
                    Text(f"Series: {series_s}")
                if tag_s:
                    Text(f"Tags: {tag_s}")
                if synopsis:
                    Text("Synopsis", css_class="text-sm font-semibold opacity-90 mt-2")
                    for para in synopsis.split("\n"):
                        p = para.strip()
                        if p:
                            Text(p, css_class="text-sm leading-relaxed")

        summary_parts = [f"Book card: {title}", auth_s or "—"]
        if series_s:
            summary_parts.append(f"series: {series_s}")
        summary = " — ".join(summary_parts)

        return ToolResult(
            content=summary,
            structured_content=PrefabApp(view=view, title=title),
        )

    import sys

    sys.modules[__name__].show_book_prefab_card = show_book_prefab_card
    logger.info("Registered show_book_prefab_card (MCP App / Prefab)")
