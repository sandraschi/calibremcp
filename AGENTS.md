# calibremcp — Agent Guide

## Overview
SOTA April 2026 industrialized FastMCP 3.2.0 server for conversational Calibre e-book library management with sampling, agentic workflows, skills, prompts, and LanceDB metadata RAG

## Entry Points

- `uv run schip-mcp-calibre` → `calibre_mcp.__main__:run`

## Standards
- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http`)
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `CLAUDE.md` — Claude Code context (if present)

## HTTP Daemon + Stdio Proxy

This server owns persistent state (Calibre metadata.db, LanceDB RAG index, book FTS cache). To prevent database contention when multiple stdio clients connect concurrently, use the HTTP Daemon + Stdio Proxy pattern:

1. Start the HTTP daemon (owns DB): `python -m calibre_mcp` (HTTP mode)
2. Stdio clients (Claude Desktop, opencode, Cursor) probe `http://127.0.0.1:10720/mcp` on startup
3. If the daemon is alive, the stdio instance becomes a lightweight proxy via `create_proxy()` — zero DB initialization
4. If unreachable, starts normally as a standalone server

**Env var** to override the probe URL: `CALIBREOPS_API_URL` (default: `http://127.0.0.1:10720/mcp`)
**Reference implementation:** `src/calibre_mcp/server.py`

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
