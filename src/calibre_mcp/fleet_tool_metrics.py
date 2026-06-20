"""Fleet MCP tool-call metrics — see mcp-central-docs/monitoring/templates/fleet_tool_metrics.py."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from fastmcp.server.middleware import Middleware
from fastmcp.server.middleware.middleware import CallNext, MiddlewareContext

if TYPE_CHECKING:
    from fastmcp import FastMCP

_PROM_AVAILABLE = False
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    _mcp_tool_calls_total = Counter(
        "mcp_tool_calls_total",
        "Total MCP tool calls",
        ["tool_name", "status"],
    )
    _mcp_tool_duration_seconds = Histogram(
        "mcp_tool_duration_seconds",
        "MCP tool execution duration in seconds",
        ["tool_name"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, float("inf")),
    )
    _mcp_errors_total = Counter(
        "mcp_errors_total",
        "MCP tool errors",
        ["tool_name", "error_type"],
    )
    _PROM_AVAILABLE = True
except ImportError:
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"  # type: ignore[misc, assignment]

    def generate_latest() -> bytes:  # type: ignore[misc]
        return b"# mcp_prometheus_client_available 0\n"


class McpToolMetricsMiddleware(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next: CallNext) -> Any:
        if not _PROM_AVAILABLE:
            return await call_next(context)

        tool_name = getattr(context.message, "name", "unknown") or "unknown"
        start = time.perf_counter()
        try:
            result = await call_next(context)
            elapsed = time.perf_counter() - start
            _mcp_tool_duration_seconds.labels(tool_name=tool_name).observe(elapsed)
            _mcp_tool_calls_total.labels(tool_name=tool_name, status="success").inc()
            return result
        except Exception as exc:
            elapsed = time.perf_counter() - start
            _mcp_tool_duration_seconds.labels(tool_name=tool_name).observe(elapsed)
            _mcp_tool_calls_total.labels(tool_name=tool_name, status="error").inc()
            _mcp_errors_total.labels(tool_name=tool_name, error_type=type(exc).__name__).inc()
            raise


def register_mcp_tool_metrics(mcp: FastMCP) -> bool:
    if not _PROM_AVAILABLE:
        return False
    mcp.add_middleware(McpToolMetricsMiddleware())
    return True


def prometheus_metrics_body_and_type() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
