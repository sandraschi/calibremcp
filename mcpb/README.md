# CalibreMCP — MCPB bundle root

This directory is the **pack root** for **`mcpb pack`** (Claude Desktop `.mcpb`).

## Fleet standard

Layout and process follow **[MCP Central Docs — MCPB_PACKAGING_STANDARDS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/MCPB_PACKAGING_STANDARDS.md)** and **[PACKAGING_STANDARDS.md §5](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/PACKAGING_STANDARDS.md#5-python-mcp-repo-uv-justfile-llmstxt-glama-mcpb-pack)**:

- `manifest.json` (v0.2), `assets/` (icon + `assets/prompts/`), self-contained `src/calibre_mcp/`
- **No** `pyproject.toml` / lockfiles inside the bundle — install dependencies from the **repository** with **`uv sync`** (or `pip install -e .`) after clone; see root `README.md`
- **Do not** use `mcpb init` / `mcpb create` (forbidden by fleet standard)
- **`glama.json`** remains at **repository root** only — excluded from this pack via `.mcpbignore`

## Build

From repository root (PowerShell):

```powershell
.\scripts\build-mcpb-package.ps1 -NoSign
```

Output: `dist\calibre-mcp.mcpb`

Or: `just mcpb-pack` (requires [just](https://github.com/casey/just)). **Requires** the global CLI: `npm install -g @anthropic-ai/mcpb` (then `mcpb` on your PATH).
