set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'
    C:\Users\sandr\AppData\Local\Programs\Python\Python313\Scripts\ruff.exe check .
    & "C:\Users\sandr\.local\bin\biome.exe" check --config-path="{{justfile_directory()}}\webapp\frontend" "{{justfile_directory()}}\webapp\frontend\app" "{{justfile_directory()}}\webapp\frontend\components" "{{justfile_directory()}}\webapp\frontend\common" "{{justfile_directory()}}\webapp\frontend\e2e"

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}\webapp\frontend'
    npx @biomejs/biome check --write .

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

# Build webapp frontend for production
build-webapp:
    Set-Location '{{justfile_directory()}}\webapp\frontend'
    npm run build

# Start webapp in production mode (builds first if needed)
start-webapp:
    pwsh -NoProfile -File '{{justfile_directory()}}\webapp\start.ps1'

# Start webapp in dev mode (slow, recompiles on request)
start-webapp-dev:
    pwsh -NoProfile -File '{{justfile_directory()}}\webapp\start.ps1' -Dev

# Rebuild + start webapp (force rebuild)
rebuild-webapp:
    pwsh -NoProfile -File '{{justfile_directory()}}\webapp\start.ps1' -Rebuild

# MCP server (stdio)
mcp:
    uv run python -m calibre_mcp

# ── RAG (LanceDB metadata index) ─────────────────────────────────────────────

# Rebuild metadata LanceDB index (CPU)
rag-metadata:
    @pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-metadata.ps1

# Rebuild metadata LanceDB index on GPU (after rag-gpu-install)
rag-gpu-metadata:
    @pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-gpu-metadata.ps1

# One-time: install fastembed-gpu + onnxruntime-gpu + NVIDIA CUDA 12 runtimes (~1.5 GB)
rag-gpu-install:
    @pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-gpu-install.ps1

# Revert to CPU onnxruntime stack
rag-cpu-install:
    @pwsh.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-cpu-install.ps1

test:
    uv run pytest

e2e:
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\playwright-audit.ps1" -RepoPath "{{justfile_directory()}}"

# Unit tests only (fast)
test-unit:
    uv run pytest tests/unit -q

fmt:
    uv run ruff format .

# Auto-fix + format (local dev)
# Lint + tests (CI-friendly)
check: lint test

# ── Native (Tauri) ─────────────────────────────────────────────────────────────

# Build embedded Python backend → native/resources/
build-sidecar:
    pwsh -NoProfile -ExecutionPolicy Bypass -File '{{justfile_directory()}}\native\build-sidecar.ps1'

# Primary end-user deliverable: Next static export + embedded backend + NSIS
build-native install-desktop:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

build-native-debug:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx @tauri-apps/cli build --debug

