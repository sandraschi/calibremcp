# Moltbot Calibre Skill

AgentSkills-compatible skill for Moltbot/ClawdBot that enables Calibre e-book library management via `calibredb` CLI.

## Requirements

- [Calibre](https://calibre-ebook.com/) installed with `calibredb` on PATH
- Moltbot with `exec` tool enabled (default)

## Install

### From this repo (manual)

Copy the `calibre` folder into your Moltbot skills directory:

- Workspace: `<workspace>/skills/calibre/`
- Managed: `~/.clawdbot/skills/calibre/`

```powershell
Copy-Item -Recurse "moltbot-skill\calibre" "$env:USERPROFILE\.clawdbot\skills\calibre"
```

### From MoltHub (when available)

```bash
molthub install calibre
# or: clawdhub install calibre
```

## Usage

Once installed, the agent will use `exec` to run `calibredb` when you ask to:

- Search or list books
- Add e-books from paths
- Export books (formats, paths)
- Edit metadata (title, authors, tags)
- Remove books
- Generate catalogs

## Library path

- Single library: Uses Calibre default.
- Multiple libraries: Specify with `--with-library /path` or set `CALIBRE_LIBRARY_PATH`.

## Publish to MoltHub

When [molthub.com](https://molthub.com) launches:

1. Ensure skill folder is `calibre/` with valid `SKILL.md`
2. From repo root: `molthub publish calibre --slug calibre`
3. Or sync: `molthub sync` (scans and publishes)

## Related

- [CalibreMCP](https://github.com/sandraschi/calibre-mcp) – MCP server with AI tools, extended metadata, Anna's Archive import
- [Calibre manual – calibredb](https://manual.calibre-ebook.com/generated/en/calibredb.html)
