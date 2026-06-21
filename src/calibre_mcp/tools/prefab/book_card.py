"""
MCP App (Prefab): book metadata card with optional cover image.

Hosts: Claude Desktop, Cursor (when MCP Apps + Prefab renderer supported). Others may show JSON fallback.
"""

from __future__ import annotations

import base64
import os
from typing import Any

from fastmcp import Context
from prefab_ui.app import PrefabApp
from prefab_ui.components import Badge, Card, CardContent, CardHeader, CardTitle, Image, Separator, Text

from calibre_mcp.logging_config import get_logger
from calibre_mcp.server import mcp
from calibre_mcp.services.base_service import NotFoundError
from calibre_mcp.services.book_service import book_service

logger = get_logger("calibremcp.tools.prefab.book_card")

_MAX_COVER_BYTES = 30_000  # 30 KB raw → ~40 KB base64; larger covers are omitted to stay within token limits


def _cover_data_uri(book_id: int) -> str | None:
    raw = book_service.get_book_cover(book_id)
    if not raw:
        return None
    if len(raw) > _MAX_COVER_BYTES:
        return None  # Cover too large — omit rather than embed a corrupt partial image
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


def _format_tags(data: dict[str, Any]) -> list[str]:
    tags = data.get("tags") or []
    if not tags:
        return []
    if isinstance(tags[0], dict):
        return [str(t.get("name", "")) for t in tags if t.get("name")]
    return [str(t) for t in tags]


def _comments_plain_text(raw: str, max_chars: int = 1200) -> str:
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
    def show_book_prefab_card(book_id: int, ctx: Context | None = None) -> PrefabApp:
        """
        Show a rich book card (MCP App) with title, authors, series, tags, comment excerpt, and cover.

        Works in clients that render MCP Apps / Prefab (e.g. Claude Desktop; Cursor when supported).
        Disable with ``CALIBRE_PREFAB_APPS=0`` (skips registration).

        Args:
            book_id: Calibre book id (from ``query_books`` or the library).

        Returns:
            PrefabApp card with book details.
        """
        try:
            data = book_service.get_by_id(int(book_id))
        except NotFoundError:
            with Card(css_class="max-w-md") as view:
                with CardHeader():
                    CardTitle("Book not found")
                with CardContent():
                    Text(f"No book with id {book_id}.")
            return PrefabApp(view=view, title="Not found")
        except Exception as e:
            logger.exception("show_book_prefab_card failed")
            with Card(css_class="max-w-md") as view:
                with CardHeader():
                    CardTitle("Error")
                with CardContent():
                    Text(f"Could not load book {book_id}: {e}")
            return PrefabApp(view=view, title="Error")

        title = (data.get("title") or "Untitled").strip()
        auth_s = _format_authors(data)
        series_s = _format_series(data)
        tags = _format_tags(data)
        synopsis = _comments_plain_text(str(data.get("comments") or ""))
        cover_uri = _cover_data_uri(int(book_id))

        with Card(css_class="max-w-lg") as view:
            with CardHeader():
                CardTitle(title)
                if auth_s:
                    Text(auth_s, css_class="text-sm text-muted-foreground")
            with CardContent():
                if cover_uri:
                    Image(
                        src=cover_uri,
                        alt=f"Cover: {title}",
                        width="200px",
                        css_class="rounded shadow object-contain mb-3",
                    )
                if series_s:
                    Text(f"Series: {series_s}", css_class="text-sm mb-1")
                if tags:
                    for tag in tags[:8]:
                        Badge(tag, variant="secondary")
                if synopsis:
                    Separator(spacing=3)
                    Text("Synopsis", css_class="text-sm font-semibold mt-2 mb-1")
                    for para in synopsis.split("\n"):
                        p = para.strip()
                        if p:
                            Text(p, css_class="text-sm leading-relaxed")

        return PrefabApp(view=view, title=title)

    import sys
    sys.modules[__name__].show_book_prefab_card = show_book_prefab_card
    logger.info("Registered show_book_prefab_card (MCP App / Prefab)")
