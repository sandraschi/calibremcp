# CalibreMCP — fleet justfile (mcp-central-docs PACKAGING_STANDARDS §5)
# https://github.com/sandraschi/mcp-central-docs/blob/master/standards/PACKAGING_STANDARDS.md

set windows-shell := ["pwsh", "-NoLogo", "-Command"]

default:
    @just --list

# Install deps from lockfile
sync:
    uv sync

test:
    uv run pytest

lint:
    uv run ruff check .
    uv run ruff format --check .

fmt:
    uv run ruff format .

# MCPB → dist/calibre-mcp.mcpb (requires npm global @anthropic-ai/mcpb)
mcpb-pack:
    pwsh -NoProfile -File scripts/build-mcpb-package.ps1 -NoSign
