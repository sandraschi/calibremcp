# Tauri 2.0 Native Desktop App

> **End users:** download `Calibre MCP_*_x64-setup.exe` from [Releases](https://github.com/sandraschi/calibre-mcp/releases/latest) and double-click. This page is for **maintainers** building the installer.

Calibre MCP ships with a Tauri 2.0 native wrapper — **one** installer, **one** shortcut. Python backend embedded in the bundle.

## Build (maintainers)

```powershell
just build-native
```

```text
native/target/release/bundle/nsis/Calibre MCP_1.8.6_x64-setup.exe
```

## Architecture

| Layer | Port | Notes |
|-------|------|-------|
| Tauri operator | — | Single install shortcut |
| Embedded Python backend | **10720** | FastAPI via `uvicorn app.main:app` |

Production UI uses `API_BASE = http://127.0.0.1:10720` (see `webapp/frontend/common/api.ts`).

Book/series detail routes use client-side fetch after static export (`generateStaticParams` placeholder).

## Production pitfalls (fleet)

Installer-only failures (`Failed to fetch`, JSON parse on `<!DOCTYPE`, missing covers, backend spawn) are documented in **mcp-central-docs**:

`standards/TAURI_PRODUCTION_PITFALLS.md`

Quick audit after any Tauri frontend change:

```powershell
rg "fetch\([`'\"]/api/" D:\Dev\repos\calibre-mcp\webapp\frontend --glob "*.{ts,tsx}" -g "!app/api/**"
```

Maintainer installer shortcut: `scripts/update-tauri-starts-link.ps1` → `D:\Dev\Tauri starts\calibre-mcp-setup.lnk`

## Dev mode

```powershell
cd native
npm install
npx @tauri-apps/cli dev
```

Frontend dev: `http://localhost:10721` with Next rewrites to the backend.
