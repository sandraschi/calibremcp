# calibre-plugins

Calibre plugin workspace for sandraschi's fleet.

## Structure

```
calibre-plugins/
├── docs/                        # All dev reference docs
│   ├── PLUGIN_DEV_GUIDE.md      # How Calibre plugins work — language, structure, build
│   ├── LOCAL_TESTING.md         # Dev loop, debug setup, calibre-debug, hot-reload
│   ├── PUBLISHING.md            # MobileRead thread format, ZIP packaging, versioning
│   └── CALIBREOPS_BRIDGE_SPEC.md # Architecture spec for the calibreops integration plugin
│
├── calibreops-bridge/           # Plugin: calibreops MCP integration
│   ├── plugin-import-name-calibreops_bridge.txt
│   ├── __init__.py
│   ├── action.py
│   ├── config.py
│   ├── ui/
│   │   ├── search_dialog.py
│   │   ├── rag_panel.py
│   │   └── result_widget.py
│   ├── client/
│   │   └── calibreops_client.py  # HTTP client for calibreops MCP server
│   ├── images/
│   │   └── calibreops.png
│   └── build.py                  # Packages plugin ZIP for installation
│
└── README.md
```

## Plugins

| Plugin | Status | Purpose |
|--------|--------|---------|
| calibreops-bridge | Planning | Surface calibreops RAG/semantic search in Calibre GUI |

## Dev environment

- Calibre installed at default path; `calibre-debug` on PATH
- `CALIBRE_DEVELOP_FROM` env var for source-mounted dev mode
- calibreops backend: http://localhost:10720
- See `docs/LOCAL_TESTING.md` for the full dev loop
