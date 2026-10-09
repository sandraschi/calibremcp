# Onboarding: calibre-mcp

Get from zero to a working AI librarian in ~10 minutes.

## What you need

1. **Calibre (the wrappee)** — the desktop e-book manager. Install first:
   `winget install calibre.calibre`. calibre-mcp reads your library's
   `metadata.db` directly; without Calibre there is nothing to manage.
2. **A Calibre library on disk** — e.g. `L:/Multimedia Files/Written Word/Calibre-Bibliothek`.
   Note the path; you will point `CALIBRE_LIBRARY_PATH` at it.
3. **No online account needed** — local-first. Cloud LLMs (OpenAI/Anthropic) are
   optional; Ollama on `localhost:11434` works offline.

## Money / cost pitfalls

- Everything local (Calibre + Ollama + LanceDB) is **free**.
- You only pay if you configure a cloud LLM key in Settings → LLM.
  Keys live in the server-side keystore (0600), never in the browser.

## Sanity check (60 seconds)

```powershell
uv sync
uv run python -m calibre_mcp   # stdio server; Ctrl+C to stop
```

Then in Claude Desktop (`calibre-mcp` server configured):

- `query_books(operation="search", query="Banks")` → book hits
- `manage_system(operation="status")` → server status

Webapp alternative: `.\webapp\start.ps1`, then open `http://127.0.0.1:10721`
and confirm the backend dot is green (`/api/health` → `{"status":"ok"}`).

## If it does not work

- Empty results → `CALIBRE_LIBRARY_PATH` points at the wrong folder
  (must contain `metadata.db`). See `docs/Configuration.md`.
- Backend dot red → port 10720 busy; `start.ps1` clears zombies on launch.
- More: `docs/Troubleshooting.md`.
