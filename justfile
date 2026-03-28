# CalibreMCP — fleet justfile (mcp-central-docs PACKAGING_STANDARDS §5)
# https://github.com/sandraschi/mcp-central-docs/blob/master/standards/PACKAGING_STANDARDS.md

set windows-shell := ["pwsh", "-NoLogo", "-Command"]

default:
    @just --list

stats:
    Set-Location '{{justfile_directory()}}'
    uv run python tools/repo_stats.py

# Install deps from lockfile (run after clone at repo root)
sync:
    uv sync

# Dev + optional extras (pytest, pre-commit, …)
sync-dev:
    uv sync --all-extras

# MCP server (stdio)
mcp:
    uv run python -m calibre_mcp

test:
    uv run pytest

# Unit tests only (fast)
test-unit:
    uv run pytest tests/unit -q

lint:
    uv run ruff check .
    uv run ruff format --check .

fmt:
    uv run ruff format .

# Auto-fix + format (local dev)
fix:
    uv run ruff format .
    uv run ruff check . --fix

# Lint + tests (CI-friendly)
check: lint test

# MCPB → dist/calibre-mcp.mcpb (requires npm global @anthropic-ai/mcpb)
mcpb-pack:
    pwsh -NoProfile -File scripts/build-mcpb-package.ps1 -NoSign
