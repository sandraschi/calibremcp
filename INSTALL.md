# Installing calibre-mcp

## Option A — Desktop app (recommended)

**Download, double-click, done.** No Git, no Python, no `just`, no build step.

1. Go to [Releases](https://github.com/sandraschi/calibre-mcp/releases/latest)
2. Download **`Calibre MCP_*_x64-setup.exe`**
3. Double-click the installer → finish the wizard
4. Launch **Calibre MCP** from the Start menu
5. Point it at your Calibre library if prompted (`CALIBRE_LIBRARY_PATH` — see [docs/Configuration.md](docs/Configuration.md))

That's it. Backend **10720** starts with the app.

**Requirements:** Windows 10/11 and an existing Calibre library on disk. [WebView2](https://developer.microsoft.com/microsoft-edge/webview2/) if prompted.

---

## Other install paths

### Prerequisites (Options B–E only)

| Tool | Purpose |
|------|---------|
| Git, uv | Clone and run from source |
| Node.js | Webapp dev |
| just | Optional dev shortcuts |
| Calibre library | Book metadata + files |

Python **3.12+** for source installs.

---

## Option B — MCPB drag and drop

1. Go to [Releases](https://github.com/sandraschi/calibre-mcp/releases/latest)
2. Download `calibre-mcp*.mcpb` (or build with `just mcpb-pack`)
3. Claude Desktop → Settings → MCP Servers → Install from file

MCP tools only — no desktop UI.

---

## Option C — Fastest from source (webapp)

```powershell
git clone https://github.com/sandraschi/calibre-mcp
cd calibre-mcp
.\start.ps1
```

Or: `just sync` then `just start-webapp` — backend **10720**, frontend **10721**.

---

## Option D — MCP stdio only

```powershell
git clone https://github.com/sandraschi/calibre-mcp
cd calibre-mcp
uv sync
uv run python -m calibre_mcp
```

Or: `just mcp`

---

## Option E — Developer mode

```powershell
winget install Casey.Just
git clone https://github.com/sandraschi/calibre-mcp
cd calibre-mcp
just sync-dev
just start-webapp-dev
```

Other recipes: `just test`, `just lint`, `just mcpb-pack`. List all: `just --list`.

**Build the Windows installer** (maintainers only): `just build-native` → [docs/TAURI.md](docs/TAURI.md).

---

## Verify installation

1. Desktop app running — health shows backend on **10720**
2. `GET http://127.0.0.1:10720/health` → OK
3. MCP prompt: *Search my Calibre library for recent science fiction.*

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Desktop app won't start | Install [WebView2](https://developer.microsoft.com/microsoft-edge/webview2/) |
| Library not found | Set `CALIBRE_LIBRARY_PATH` to your `metadata.db` folder |
| Port 10720/10721 in use | Stop other service on that port |
| `just` not found | Use Option A (no just) or Option C without just |
| Dependencies out of sync | `just sync-dev` or `uv sync --all-extras` |

---

*Feature overview: [README.md](README.md)*
