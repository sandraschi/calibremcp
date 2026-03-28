"""
Suppress repetitive access-log noise for mounted FastMCP at /mcp.

MCP hosts poll JSON-RPC frequently (e.g. prompts/list every few seconds). Each poll
was generating uvicorn.access lines and filling webapp.log.

Set CALIBRE_LOG_MCP_HTTP_ACCESS=1 to log every /mcp request again (debug).
"""

from __future__ import annotations

import logging
import os


def _mcp_access_verbose() -> bool:
    return os.environ.get("CALIBRE_LOG_MCP_HTTP_ACCESS", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _mcp_library_verbose() -> bool:
    return os.environ.get("CALIBRE_MCP_DEBUG_LOG", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


class _DropSuccessfulMcpMountAccess(logging.Filter):
    """Drop uvicorn access lines for successful (2xx) calls to the mounted /mcp app."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if "/mcp" not in msg:
            return True
        # Keep errors and non-success status codes visible
        if " 200 " in msg or " 204 " in msg or msg.rstrip().endswith(" 200"):
            return False
        return True


def configure_quiet_mcp_http_logging() -> None:
    """Attach filters and levels so MCP polling does not spam logs."""
    if _mcp_access_verbose():
        return

    flt = _DropSuccessfulMcpMountAccess()
    for name in ("uvicorn.access",):
        logging.getLogger(name).addFilter(flt)

    if _mcp_library_verbose():
        return

    # Third-party MCP stack: INFO logs on every JSON-RPC message in some versions
    for name in (
        "mcp",
        "mcp.server",
        "mcp.server.streamable_http",
        "mcp.server.lowlevel",
        "fastmcp",
        "fastmcp.server",
        "fastmcp.middleware",
        "fastmcp.middleware.logging",
        "fastmcp.middleware.timing",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)
