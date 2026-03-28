"""Optional MCP Apps (Prefab UI) for rich chat surfaces — install ``calibre-mcp[apps]``."""

from __future__ import annotations

from calibre_mcp.logging_config import get_logger

logger = get_logger("calibremcp.tools.prefab")


def register_prefab_tools() -> None:
    """Load Prefab + register MCP App tools when deps and env allow."""
    from .book_card import register_book_card_tool
    from .libraries_card import register_libraries_card_tool

    register_book_card_tool()
    register_libraries_card_tool()
