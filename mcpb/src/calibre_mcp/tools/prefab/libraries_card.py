"""
MCP App (Prefab): \"Our Calibre\" card — all discovered libraries and basic stats.

CALIBRE_PREFAB_APPS=0 skips registration (same as the book card).
"""

from __future__ import annotations

import os
from typing import Any

from fastmcp import Context
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Card, CardContent, CardHeader, CardTitle, Text

from calibre_mcp.logging_config import get_logger
from calibre_mcp.server import mcp

logger = get_logger("calibremcp.tools.prefab.libraries_card")


async def show_libraries_prefab_card(ctx: Context | None = None) -> Any:
    """Placeholder until ``register_libraries_card_tool`` replaces this with the real MCP App tool."""
    return {
        "success": False,
        "error": "prefab_unavailable",
        "message": "Prefab libraries card is not active (CALIBRE_PREFAB_APPS=0).",
    }


def _truncate_path(path: str, max_len: int = 80) -> str:
    p = path.strip()
    if len(p) <= max_len:
        return p
    head = max_len // 2 - 2
    tail = max_len - head - 3
    return f"{p[:head]}…{p[-tail:]}" if tail > 0 else p[:max_len] + "…"


def register_libraries_card_tool() -> None:
    """Register ``show_libraries_prefab_card`` on the global FastMCP instance."""
    if os.environ.get("CALIBRE_PREFAB_APPS", "1").strip().lower() in ("0", "false", "no", "off"):
        logger.info("Prefab libraries card disabled (CALIBRE_PREFAB_APPS=0)")
        return

    @mcp.tool(app=True)
    async def show_libraries_prefab_card(ctx: Context | None = None) -> Any:
        """
        Show an \"Our Calibre\" card (MCP App): all discovered libraries with book counts, size, active flag, paths.

        Uses the same discovery as ``manage_libraries(operation='list')``.
        Disable with ``CALIBRE_PREFAB_APPS=0`` (skips registration).

        Returns:
            ToolResult with Prefab UI plus a short text summary for the model.
        """
        from calibre_mcp.tools.library.library_management import list_libraries_helper

        try:
            listed = await list_libraries_helper()
        except Exception as e:
            logger.exception("show_libraries_prefab_card: list_libraries_helper failed")
            return {
                "success": False,
                "error": str(e),
                "message": "Could not list Calibre libraries.",
            }

        data = listed.model_dump()
        libraries: list[dict[str, Any]] = data.get("libraries") or []
        current = (data.get("current_library") or "").strip()
        total = int(data.get("total_libraries") or 0)

        if not libraries:
            with Card(css_class="max-w-lg") as view:
                with CardHeader():
                    CardTitle("Our Calibre")
                with CardContent():
                    Text("No Calibre libraries discovered.")
                    Text(
                        "Configure CALIBRE_LIBRARY_PATH or use manage_libraries(operation='discover').",
                        css_class="text-sm opacity-90",
                    )
            return ToolResult(
                content="Our Calibre: no libraries discovered.",
                structured_content=PrefabApp(view=view, title="Our Calibre"),
            )

        with Card(css_class="max-w-lg") as view:
            with CardHeader():
                CardTitle("Our Calibre")
            with CardContent():
                Text(
                    f"{total} librar{'y' if total == 1 else 'ies'}"
                    + (f" · active: {current}" if current else ""),
                    css_class="text-sm opacity-90 mb-2",
                )
                for i, lib in enumerate(libraries):
                    name = str(lib.get("name") or "—")
                    books = int(lib.get("book_count") or 0)
                    size_mb = lib.get("size_mb")
                    try:
                        size_s = f"{float(size_mb):.1f} MB" if size_mb is not None else "—"
                    except (TypeError, ValueError):
                        size_s = "—"
                    active = bool(lib.get("is_active"))
                    path_s = _truncate_path(str(lib.get("path") or ""))

                    label = f"{name}" + ("  ·  active" if active else "")
                    head_cls = "font-semibold mt-3" if i else "font-semibold"
                    Text(label, css_class=head_cls)
                    Text(f"Books: {books}  ·  Size: {size_s}", css_class="text-sm")
                    if path_s:
                        Text(path_s, css_class="text-xs opacity-80")

        lines = [
            f"Our Calibre: {total} libraries",
        ]
        if current:
            lines.append(f"active: {current}")
        for lib in libraries:
            nm = str(lib.get("name") or "")
            bc = int(lib.get("book_count") or 0)
            mark = " *" if lib.get("is_active") else ""
            lines.append(f"- {nm}{mark}: {bc} books")
        summary = "\n".join(lines)

        return ToolResult(
            content=summary,
            structured_content=PrefabApp(view=view, title="Our Calibre"),
        )

    import sys

    sys.modules[__name__].show_libraries_prefab_card = show_libraries_prefab_card
    logger.info("Registered show_libraries_prefab_card (MCP App / Prefab)")
