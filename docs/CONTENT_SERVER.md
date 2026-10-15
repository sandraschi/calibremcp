# Calibre Content Server — our setup, integration & watchlist

The Calibre **Content Server** (the "webserver" inside the Calibre GUI) is a
first-class citizen in this repo: every tool-side write goes through it
whenever the GUI holds the library. This page documents our instance, how we
use it, and what we are watching in its UI.

> Calibre here: **9.16** desktop. Server URL, username, and password live in the
> repo `.env` (`CALIBRE_SERVER_URL`, `CALIBRE_USERNAME`, `CALIBRE_PASSWORD`) —
> never in docs or chat logs.

## Our instance

- **URL**: from `.env` (`http://localhost:8099` on this machine)
- **Source**: Calibre GUI → Preferences → **Sharing over the net** → enabled + autostart
- **Auth**: sharing account required for writes (reads work per the Sharing settings)
- **Libraries served**: all local libraries (Main, Comics, Manga, IT, Japanese, …) with a chip chooser on the home page

## What it looks like (verified 2026-10-15, Calibre 9.16)

Home page sections, top to bottom:

- **Sidebar**: Home · Search · Downloaded books · Browse (Authors, Series, Formats,
  Publisher, Rating, Tags, Published) · Virtual libraries (+ New virtual library) · Settings
- **Continue reading…** shelf with cover + author
- **Library chooser**: one chip per served library
- **Newly added…** cover shelf (our own imports show up here within seconds)
- Footer note: offline mode / downloadable books for mobile clients
- Top-right user avatar = per-user accounts with separate read state

It is a full reading/browsing client in its own right (cover grid, tag browser,
in-browser reader via `viewer.js`), not just an API.

## How calibre-mcp uses it

`src/calibre_mcp/tools/book_management/calibredb_runner.py` implements the
two-route pattern for every writer:

| Op | Direct route | Fallback route | Result field |
|---|---|---|---|
| add | `calibredb add … --library-path` | `calibredb --with-library <url> add …` | `"via": "direct" \| "content_server"` |
| update (`set_metadata`, cover) | same | same | logged, same shape |
| delete (`remove`) | same | same | logged |
| online metadata apply | same | same | error dict otherwise |

The fallback triggers only on lock markers ("another calibre program",
"database is locked", …). Reads never contend — search, browse, RAG, exports
work regardless of GUI/server state.

Manual recipes (same credentials as `.env`):

```powershell
# read-only probe: list two books through the server
& "C:\Program Files\Calibre2\calibredb.exe" --with-library http://127.0.0.1:8099 `
  --username <sharing-user> --password <sharing-pass> list --limit 2

# write through the server (what the fallback does)
& "C:\Program Files\Calibre2\calibredb.exe" --with-library http://127.0.0.1:8099 `
  --username <sharing-user> --password <sharing-pass> `
  add "C:\path\book.pdf" --title "Title" --authors "Author"
```

## Ideas we are watching (copy-back candidates)

Observed in the 9.x server UI; noted as inspiration for our own webapp
(status: watching, none adopted yet):

1. **Continue-reading shelf on home** — one glance resume; our Overview could do the same from read state.
2. **Downloaded-books / offline mode** — per-device offline packs with a reload-to-enable flow.
3. **In-sidebar virtual-library creator** — "New virtual library" where you browse, not buried in a tools page.
4. **Per-user accounts with separate state** — avatar menu; relevant if the webapp ever goes multi-user.
5. **Multi-library chip chooser on home** — faster than our Libraries page round-trip for switching context.
6. **Newly-added shelf** — our `recent` op already feeds this; surfacing it on Overview is trivial.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `via: direct` fails "library is locked", no fallback attempted | `CALIBRE_SERVER_URL` empty | Set it in `.env`, restart backend |
| Fallback fails "username/password incorrect" | Sharing credentials changed | Update `CALIBRE_USERNAME`/`CALIBRE_PASSWORD` in `.env`, restart backend |
| Server unreachable | GUI closed (no autostart) or Sharing disabled | Open Calibre once / re-enable Sharing over the net |
| New imports invisible in our webapp | Backend TTL cache (60 s) | Wait a minute or switch library to refresh |

See also: `docs/ONBOARDING.md` (Sharing setup), in-app Help → Guides.
