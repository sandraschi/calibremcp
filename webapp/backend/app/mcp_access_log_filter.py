"""
Suppress repetitive access-log noise from frequent polling endpoints.

MCP hosts poll JSON-RPC frequently (e.g. prompts/list every few seconds).
The frontend polls /api/rag/metadata/build/status, /health, etc.
Each poll was generating uvicorn.access lines.

- Set CALIBRE_LOG_ACCESS_VERBOSE=1 to log every request (debug).
- Set CALIBRE_LOG_MCP_VERBOSE=1 to restore full MCP stack logs.
"""

from __future__ import annotations

import logging
import os
import re


def _access_verbose() -> bool:
    return os.environ.get("CALIBRE_LOG_ACCESS_VERBOSE", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _mcp_verbose() -> bool:
    return os.environ.get("CALIBRE_LOG_MCP_VERBOSE", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


class _DropSuccessfulAccess(logging.Filter):
    """Drop uvicorn access lines for successful (2xx/3xx) responses.

    Keeps 4xx and 5xx visible so errors aren't silently swallowed.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        # Keep 4xx and 5xx responses visible (errors)
        if re.search(r'" \d[45]\d\d?\b', msg):
            return True
        # Drop 2xx and 3xx — these are noise for console
        return False


def configure_quiet_mcp_http_logging() -> None:
    """Attach filters and levels so frequent polling does not spam logs."""
    if not _access_verbose():
        flt = _DropSuccessfulAccess()
        for name in ("uvicorn.access",):
            logging.getLogger(name).addFilter(flt)

    if _mcp_verbose():
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
