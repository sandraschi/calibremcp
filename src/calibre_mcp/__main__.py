"""
CalibreMCP Module Entry Point
"""

import asyncio
import contextlib
import io
import logging
import os
import sys
import warnings

from .server import main

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

_is_stdio_transport = not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True

if _is_stdio_transport:
    _original_stderr = sys.stderr
    with contextlib.suppress(Exception):
        _fd = os.open(os.devnull, os.O_WRONLY | os.O_TEXT)
        sys.stderr = io.TextIOWrapper(io.FileIO(_fd, mode="w"), encoding="utf-8")

    logging.getLogger("mcp").setLevel(logging.WARNING)
    logging.getLogger("mcp.server").setLevel(logging.WARNING)
    logging.getLogger("mcp.server.lowlevel").setLevel(logging.WARNING)
    logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # Restore stderr if we redirected it
        if "_original_stderr" in locals() and sys.stderr != _original_stderr:
            with contextlib.suppress(Exception):
                sys.stderr.close()
            sys.stderr = _original_stderr


def run():
    """Sync entry point for console_scripts."""
    try:
        asyncio.run(main())
    finally:
        if "_original_stderr" in dir() and sys.stderr != _original_stderr:
            with contextlib.suppress(Exception):
                sys.stderr.close()
            sys.stderr = _original_stderr
