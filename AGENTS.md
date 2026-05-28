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
