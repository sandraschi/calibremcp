"""
Dual transport for CalibreMCP (FastMCP 3.1+): stdio, HTTP streamable, optional SSE.

PORTMANTEAU PATTERN RATIONALE: One ``run_server`` / ``run_server_async`` entry so CLI and
embedders do not fork transport logic; aligns with fleet env vars (MCP_HOST, MCP_PORT).

Environment Variables:
    MCP_TRANSPORT: ``stdio`` | ``http`` | ``sse``. Default: stdio.
    MCP_HOST: Bind address for HTTP/SSE. Default: 127.0.0.1.
    MCP_PORT: Port for HTTP/SSE. Default: 10720 (fleet 10700+).
    MCP_PATH: HTTP path. Default: /mcp.

CLI:
    ``--stdio``, ``--http``, ``--sse`` (legacy), ``--host``, ``--port``, ``--path``, ``--debug``.

Usage:
    from calibre_mcp.transport import run_server_async

    await run_server_async(mcp, server_name="CalibreMCP")
"""

import argparse
import asyncio
import logging
import os
from typing import Literal

from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

TransportType = Literal["stdio", "http", "sse"]

# Environment variable standards
ENV_TRANSPORT = "MCP_TRANSPORT"  # stdio | http | sse
ENV_HOST = "MCP_HOST"  # default: 127.0.0.1
ENV_PORT = "MCP_PORT"  # default: 10720
ENV_PATH = "MCP_PATH"  # default: /mcp (HTTP only)


def get_transport_config() -> dict:
    """
    Get transport configuration from environment variables.

    Returns:
        Dictionary with transport, host, port, and path settings.
    """
    return {
        "transport": os.getenv(ENV_TRANSPORT, "stdio").lower(),
        "host": os.getenv(ENV_HOST, "127.0.0.1"),
        "port": int(os.getenv(ENV_PORT, "10720")),
        "path": os.getenv(ENV_PATH, "/mcp"),
    }


def create_argument_parser(server_name: str) -> argparse.ArgumentParser:
    """
    Create standardized CLI argument parser for MCP servers.

    Args:
        server_name: Name of the MCP server for help text.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description=f"{server_name} - FastMCP 2.14.4+ Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Environment Variables:
  {ENV_TRANSPORT}    Transport mode: stdio, http, sse (default: stdio)
  {ENV_HOST}         Bind address (default: 127.0.0.1)
  {ENV_PORT}         Port number (default: 10720)
  {ENV_PATH}         HTTP endpoint path (default: /mcp)

Examples:
  # STDIO mode (Claude Desktop)
  python -m {server_name.replace("-", "_")} --stdio

  # HTTP mode (web apps)
  python -m {server_name.replace("-", "_")} --http --port 10720

  # Via environment
  MCP_TRANSPORT=http MCP_PORT=10720 python -m {server_name.replace("-", "_")}
""",
    )

    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument(
        "--stdio", action="store_true", help="Run in STDIO (JSON-RPC) mode (default)"
    )
    transport_group.add_argument(
        "--http", action="store_true", help="Run in HTTP Streamable mode (FastMCP 2.14.4+)"
    )
    transport_group.add_argument(
        "--sse", action="store_true", help="Run in SSE mode (deprecated, use --http)"
    )

    parser.add_argument(
        "--host", default=None, help=f"Host to bind to (default: ${ENV_HOST} or 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help=f"Port to listen on (default: ${ENV_PORT} or 10720)"
    )
    parser.add_argument(
        "--path", default=None, help=f"HTTP endpoint path (default: ${ENV_PATH} or /mcp)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser


def resolve_transport(args: argparse.Namespace) -> TransportType:
    """
    Resolve transport type from CLI args with environment fallback.

    Priority:
        1. CLI arguments (--http, --stdio, --sse)
        2. Environment variable (MCP_TRANSPORT)
        3. Default (stdio)

    Args:
        args: Parsed CLI arguments.

    Returns:
        Transport type string.
    """
    if args.http:
        return "http"
    if args.sse:
        logger.warning(
            "SSE transport is deprecated. Consider using --http instead. "
            "SSE support will be removed in a future version."
        )
        return "sse"
    if args.stdio:
        return "stdio"
    # Fall back to environment variable
    env_transport = os.getenv(ENV_TRANSPORT, "stdio").lower()
    if env_transport not in ("stdio", "http", "sse"):
        logger.warning(f"Invalid {ENV_TRANSPORT}='{env_transport}', defaulting to stdio")
        return "stdio"
    if env_transport == "sse":
        logger.warning(
            "SSE transport is deprecated. Consider using MCP_TRANSPORT=http instead."
        )
    return env_transport  # type: ignore


def resolve_config(args: argparse.Namespace) -> dict:
    """
    Resolve full transport configuration from CLI args and environment.

    CLI args take precedence over environment variables.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Dictionary with transport, host, port, path settings.
    """
    env_config = get_transport_config()

    return {
        "transport": resolve_transport(args),
        "host": args.host if args.host is not None else env_config["host"],
        "port": args.port if args.port is not None else env_config["port"],
        "path": args.path if args.path is not None else env_config["path"],
    }


def run_server(
    mcp_app, args: argparse.Namespace | None = None, server_name: str = "mcp-server"
) -> None:
    """
    Unified server runner for all transport modes.

    This is the main entry point for running an MCP server with proper
    transport configuration based on CLI arguments and environment variables.

    Args:
        mcp_app: FastMCP application instance.
        args: Parsed CLI arguments (optional, will parse if None).
        server_name: Server name for logging and help text.

    Raises:
        Exception: If server fails to start.
    """
    # Simply run the async version
    asyncio.run(run_server_async(mcp_app, args, server_name))


async def run_server_async(
    mcp_app, args: argparse.Namespace | None = None, server_name: str = "mcp-server"
) -> None:
    """
    Asynchronous unified server runner for all transport modes.

    Args:
        mcp_app: FastMCP application instance.
        args: Parsed CLI arguments (optional, will parse if None).
        server_name: Server name for logging and help text.
    """
    if args is None:
        parser = create_argument_parser(server_name)
        args = parser.parse_args()

    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug(f"Debug logging enabled for {server_name}")

    config = resolve_config(args)
    transport = config["transport"]

    logger.info(f"Starting {server_name} v{getattr(mcp_app, 'version', '?.?.?')}")
    logger.info(f"Transport: {transport.upper()}")

    try:
        if transport == "stdio":
            logger.info("Running in STDIO mode - Ready for Claude Desktop!")
            await mcp_app.run_stdio_async()

        elif transport == "http":
            host = config["host"]
            port = config["port"]
            path = config["path"]
            endpoint = f"http://{host}:{port}{path}"

            import subprocess

            from pydantic import BaseModel

            from calibre_mcp.llm_http import DEFAULT_SYSTEM, chat_complete

            class LaunchRequest(BaseModel):
                repo_path: str

            # SOTA Fleet Launch Protocol Injection
            @mcp_app.app.post("/api/fleet/launch")
            async def fleet_launch(launch_req: LaunchRequest):
                """SOTA Fleet Launch Protocol"""
                repo_path = launch_req.repo_path
                if not (
                    repo_path.lower().startswith("d:/dev/repos")
                    or repo_path.lower().startswith("c:/users/sandr")
                ):
                    return {"status": "error", "message": "Forbidden path"}

                if not os.path.exists(repo_path):
                    return {"status": "error", "message": "Path not found"}

                start_ps1 = os.path.join(repo_path, "start.ps1")
                if os.path.exists(start_ps1):
                    # Use absolute path for powershell to satisfy lints and ensure reliability
                    subprocess.Popen(
                        [
                            "powershell.exe",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-File",
                            "start.ps1",
                        ],
                        cwd=repo_path,
                    )
                    return {
                        "status": "success",
                        "message": f"Launched {os.path.basename(repo_path)}",
                    }

                return {"status": "error", "message": "start.ps1 not found"}

            class SearchQuery(BaseModel):
                query: str
                limit: int = 10
                search_type: str = "metadata"  # metadata or fulltext

            class ChatQuery(BaseModel):
                """Single-turn (message) or multi-turn (messages); same shape as webapp ``/api/llm/chat``."""

                message: str = ""
                context: str = ""
                messages: list[dict[str, str]] | None = None
                model: str = "llama3.2"
                stream: bool = False
                provider: str | None = None
                base_url: str | None = None

            @mcp_app.app.post("/api/v1/search")
            async def semantic_search(req: SearchQuery):
                from calibre_mcp.tools.portmanteau.search import calibre_rag

                try:
                    return await calibre_rag(
                        operation="search",
                        query=req.query,
                        limit=req.limit,
                        search_type=req.search_type,
                    )
                except Exception as e:
                    logger.exception(f"Search endpoint error: {e}")
                    return {"success": False, "error": str(e)}

            @mcp_app.app.post("/api/v1/chat")
            async def chat_with_media(req: ChatQuery):
                """Proxy to local Ollama or OpenAI-compatible API (``LLM_*`` env). Supports streaming."""
                msgs_in = req.messages if req.messages else []
                if msgs_in:
                    built: list[dict[str, str]] = [dict(m) for m in msgs_in]
                else:
                    text = (req.message or "").strip()
                    if not text:
                        return {
                            "success": False,
                            "error": "empty_message",
                            "message": "Provide `message` or non-empty `messages`.",
                        }
                    ctx = (req.context or "").strip()
                    if ctx:
                        built = [
                            {"role": "system", "content": ctx},
                            {"role": "user", "content": text},
                        ]
                    else:
                        built = [
                            {"role": "system", "content": DEFAULT_SYSTEM},
                            {"role": "user", "content": text},
                        ]

                out = await chat_complete(
                    built,
                    model=req.model,
                    stream=req.stream,
                    provider=req.provider,
                    base_url=req.base_url,
                )

                if isinstance(out, StreamingResponse):
                    return out
                if out.get("success") is False:
                    return out
                merged: dict = {
                    **out,
                    "context_used": bool((req.context or "").strip()),
                }
                raw = out.get("raw")
                if isinstance(raw, dict):
                    if "message" in raw:
                        merged["message"] = raw["message"]
                    if "choices" in raw:
                        merged["choices"] = raw["choices"]
                return merged

            logger.info(f"Running in HTTP Streamable mode: {endpoint}")
            await mcp_app.run_http_async(host=host, port=port, path=path)

        elif transport == "sse":
            host = config["host"]
            port = config["port"]
            logger.warning("SSE mode is deprecated. Migrate to HTTP Streamable (--http).")
            logger.info(f"Running in SSE mode: http://{host}:{port}")
            await mcp_app.run_sse_async(host=host, port=port)

    except asyncio.CancelledError:
        logger.info(f"{server_name} task cancelled")
    except Exception as e:
        logger.error(f"{server_name} failed: {e}", exc_info=True)
        raise


# Export public API
__all__ = [
    "TransportType",
    "ENV_TRANSPORT",
    "ENV_HOST",
    "ENV_PORT",
    "ENV_PATH",
    "get_transport_config",
    "create_argument_parser",
    "resolve_transport",
    "resolve_config",
    "run_server",
    "run_server_async",
]
