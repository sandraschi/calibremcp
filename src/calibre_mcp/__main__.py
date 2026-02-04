"""
CalibreMCP Module Entry Point

Allows running the server with: python -m calibre_mcp
"""

# CRITICAL: Suppress ALL warnings and redirect stderr BEFORE ANY imports
# MCP stdio protocol requires clean stdout/stderr for JSON-RPC communication
import os
import sys
import warnings

# Suppress all warnings immediately
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")

# For MCP stdio transport, redirect stderr to devnull to prevent warning output
# This is necessary because warnings are printed to stderr, breaking JSON-RPC protocol
# Check if we're running as MCP server (stdio transport - stdin is not a TTY)
_is_stdio_transport = not sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else True

if _is_stdio_transport:
    # Running as MCP server (stdio transport) - redirect stderr to devnull
    # Save original stderr for actual errors if needed
    _original_stderr = sys.stderr
    try:
        # Redirect stderr to devnull to suppress ALL stderr output (including warnings)
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    except Exception:
        # If we can't redirect, at least suppress warnings
        pass

    # Also suppress FastMCP internal logging that interferes with MCP protocol
    import logging

    logging.getLogger("mcp").setLevel(logging.WARNING)
    logging.getLogger("mcp.server").setLevel(logging.WARNING)
    logging.getLogger("mcp.server.lowlevel").setLevel(logging.WARNING)
    logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)

# Standard imports
import asyncio

from .server import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # Restore stderr if we redirected it
        if "_original_stderr" in locals() and sys.stderr != _original_stderr:
            try:
                sys.stderr.close()
            except Exception:
                pass
            sys.stderr = _original_stderr
