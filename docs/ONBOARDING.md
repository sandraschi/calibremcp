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

## One-time: enable Sharing (imports with the GUI open)

Calibre only allows one direct writer on `metadata.db`. When the GUI is open,
calibre-mcp imports/updates/deletes go through your Calibre **Content Server**
automatically — but the server must exist:

1. Calibre → Preferences → **Sharing over the net** → enable, autostart.
   Note the port (default 8080) and the sharing username/password (if required).
2. Put them in the repo `.env`:
   `CALIBRE_SERVER_URL=http://localhost:<port>`,
   `CALIBRE_USERNAME=…`, `CALIBRE_PASSWORD=…`.
3. Restart the backend (`webapp\start.ps1`) so it picks up the values.

Without this, imports fail with "library is locked" whenever Calibre is open.
With it, results report `"via": "content_server"` and everything just works.

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

## First import walkthrough (5 minutes)

1. Open the webapp → **Import** page (or stay in chat with `manage_books`).
2. Paste a PDF/EPUB path → Add. Override title/authors/tags if detection is off.
3. Check it landed: **Books** sorted by newest, or
   `query_books(operation="recent", limit=1)`.
4. Try an arXiv import: paste an ID like `2610.13455` on the Import → arXiv tab.
5. Browse **Authors / Series / Tags / Publishers**: flip Cards/List, sort by
   Book count to see your heavy hitters. Views are URL-driven — bookmark them.

## Ports (all localhost)

| What | Port |
|---|---|
| Backend REST + MCP (`/mcp`) | 10720 |
| Frontend webapp | 10721 |
| Calibre Content Server (Sharing) | 8080 default (yours may differ) |

## If it does not work

- Empty results → `CALIBRE_LIBRARY_PATH` points at the wrong folder
  (must contain `metadata.db`). See `docs/Configuration.md`.
- "Library is locked" on import → Sharing not enabled / creds wrong in `.env`
  (see above). Restart the backend after fixing `.env`.
- "Username/password incorrect" → update `CALIBRE_USERNAME`/`CALIBRE_PASSWORD`,
  restart backend.
- Backend dot red → port 10720 busy; `start.ps1` clears zombies on launch.
- More: `docs/Troubleshooting.md`, in-app **Help → Guides** tab.
