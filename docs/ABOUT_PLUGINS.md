# About Plugins

calibre-mcp has two plugin projects that extend Calibre's GUI with MCP-powered features.

## Plugin 1: CalibreMCP Integration (this repo)

**Location:** `calibre_plugin/` in this repository  
**Status:** Production — metadata editor + VL search  
**Install:** `calibre-customize.exe -b D:\Dev\repos\calibre-mcp\calibre_plugin`

### What's implemented

| Feature | Description | Server needed? |
|---------|-------------|:---:|
| **Extended metadata panel** | Edit translator, first_published, and personal notes per book. Shortcut: `Ctrl+Shift+M` | No |
| **VL from Query** | Type a natural-language query → creates a Calibre Virtual Library of matching books | Yes (webapp) |
| **Bulk Enrich** | Placeholder dialog — checks backend connectivity. AI enrichment planned | N/A |

### Architecture

```
Calibre GUI
└── CalibreMCP Integration plugin
    ├── Extended metadata → calibre_mcp_data.db (direct SQLite)
    └── VL from Query     → http://localhost:10720/api/search (webapp)
```

Data is stored in `%APPDATA%\calibre-mcp\calibre_mcp_data.db` and shared with the MCP server — notes you add in the plugin appear when Claude queries your library.

Full docs: [calibre_plugin/README.md](../calibre_plugin/README.md)

---

## Plugin 2: calibreops-bridge (separate repo)

**Repo:** [`D:\Dev\repos\calibre-plugins`](https://github.com/sandraschi/calibre-plugins)  
**Status:** Phase 0 — skeleton built, UI work not started

### Planned features

| Feature | Description |
|---------|-------------|
| **RAG semantic search** | Search your library by meaning, not just keywords, from inside Calibre |
| **Synopsis generation** | AI-generated spoiler-aware book synopses |
| **Series analysis** | Reading order, completion status, gaps in series |
| **Metadata AI enrichment** | Auto-fill descriptions, tags, first_published via AI |

### Architecture (planned)

```
Calibre GUI
├── CalibreMCP Integration plugin  (metadata + VL)
└── calibreops-bridge plugin       (RAG + AI features)
    ├── SearchDialog → http://localhost:10720/api/rag/metadata/search
    ├── Synopsis     → http://localhost:10720/api/rag/synopsis/{book_id}
    └── Series       → http://localhost:10720/api/series/analysis
```

Both plugins share the same **calibre-mcp webapp backend** on port 10720 and can coexist in Calibre simultaneously.

### Implementation phases

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Plugin skeleton, config, HTTP client stubs | Done |
| 1 | SearchDialog + metadata RAG integration | Not started |
| 2 | Synopsis dialog + series analysis | Not started |
| 3 | Polish, packaging, icon | Not started |
| 4 | Merge into calibre_plugin/ or publish separately | Decision pending |

Full spec: `D:\Dev\repos\calibre-plugins\docs\CALIBREOPS_BRIDGE_SPEC.md`

---

## Future plugin roadmap

| Priority | Feature | Target plugin |
|----------|---------|---------------|
| High | Implement Bulk Enrich (AI metadata fill) | calibre_plugin (this repo) |
| High | Tag suggestions via AI | calibreops-bridge or merged |
| Medium | Custom column sync (translator ↔ `#translator`) | calibre_plugin |
| Medium | Right-click AI actions in Calibre GUI | calibreops-bridge |
| Low | Anna's Archive / Gutenberg integration directly in plugin UI | TBD |

---

## Why two plugins?

The `calibre_plugin/` in this repo handles **metadata editing and library operations** — things that work offline via direct SQLite. The `calibreops-bridge` handles **AI/RAG features** that require the webapp backend. They started as one design but were split to keep concerns separate during development. A merge decision is planned for Phase 4.

> **Next:** [About MCP Tools](ABOUT_MCP_TOOLS.md) | **Back:** [About Calibre Web](ABOUT_CALIBRE_WEB.md)
