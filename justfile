set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the SOTA Industrial Dashboard
default:
    @$lines = Get-Content '{{justfile()}}'; \
    Write-Host ' [SOTA] Industrial Operations Dashboard v1.3.2' -ForegroundColor White -BackgroundColor Cyan; \
    Write-Host '' ; \
    $currentCategory = ''; \
    foreach ($line in $lines) { \
        if ($line -match '^# ── ([^─]+) ─') { \
            $currentCategory = $matches[1].Trim(); \
            Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
            Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
        } elseif ($line -match '^# ([^─].+)') { \
            $desc = $matches[1].Trim(); \
            $idx = [array]::IndexOf($lines, $line); \
            if ($idx -lt $lines.Count - 1) { \
                $nextLine = $lines[$idx + 1]; \
                if ($nextLine -match '^([a-z0-9-]+):') { \
                    $recipe = $matches[1]; \
                    $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                    Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
                    Write-Host "$pad$desc" -ForegroundColor Gray; \
                } \
            } \
        } \
    } \
    Write-Host "`n  [System State: PROD/HARDENED]" -ForegroundColor DarkGray; \
    Write-Host ''

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# CalibreMCP — fleet justfile (mcp-central-docs PACKAGING_STANDARDS §5)
# https://github.com/sandraschi/mcp-central-docs/blob/master/standards/PACKAGING_STANDARDS.md

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

fmt:
    uv run ruff format .

# Auto-fix + format (local dev)
# Lint + tests (CI-friendly)
check: lint test

# MCPB → dist/calibre-mcp.mcpb (requires npm global @anthropic-ai/mcpb)
mcpb-pack:
    pwsh -NoProfile -File scripts/build-mcpb-package.ps1 -NoSign
