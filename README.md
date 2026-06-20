# CalibreMCP

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://biomejs.dev"><img src="https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white" alt="Biome"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <a href="https://tauri.app"><img src="https://img.shields.io/badge/Tauri-2.0-ffc131?style=flat-square&logo=tauri&logoColor=white" alt="Tauri"></a>
  <a href="https://github.com/sandraschi/calibremcp/releases"><img src="https://img.shields.io/github/v/release/sandraschi/calibremcp?style=flat-square&logo=github" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"></a>
</p>


> 📖 **[Installation Guide](INSTALL.md)** — download the `.exe` from Releases, double-click, done

**FastMCP 3.2 MCP server for Calibre e-book library management — AI-assisted search, RAG, and agentic workflows for Sandra's 1000+ book library.**

## Quick Start

Download **`Calibre MCP_*_x64-setup.exe`** from [Releases](https://github.com/sandraschi/calibre-mcp/releases/latest) → double-click → launch **Calibre MCP**. [Install guide](INSTALL.md).

Developers from source:

```powershell
git clone https://github.com/sandraschi/calibre-mcp
cd calibre-mcp
just sync
just start-webapp
```
// claude_desktop_config.json
{
"mcpServers": {
"calibre-mcp": {
"command": "uv",
"args": ["run", "calibre-mcp"],
"env": {
"CALIBRE_LIBRARY_PATH": "L:/Multimedia Files/Written Word/Calibre-Bibliothek"
}
}
}
}
Then ask Claude: *"Find unread sci-fi books"*, *"Open a random Banks novel"*, or *"What's my library health?"*

## What is this?

calibre-mcp bridges your Calibre e-book library and AI assistants (Claude Desktop, Cursor, etc.) via the Model Context Protocol. It reads Calibre's `metadata.db` directly, indexes metadata for semantic search (LanceDB RAG), and exposes 21 portmanteau tools for natural-language library management.

## Read more

| Topic | Description |
|-------|-------------|
| [About Calibre](docs/ABOUT_CALIBRE.md) | What Calibre is, how it stores data, access methods |
| [About Calibre Web](docs/ABOUT_CALIBRE_WEB.md) | calibre-web vs Calibre Content Server, running both together |
| [About Plugins](docs/ABOUT_PLUGINS.md) | CalibreMCP Integration plugin, calibreops-bridge, roadmap |
| [About MCP Tools](docs/ABOUT_MCP_TOOLS.md) | 21 portmanteau tools, architecture, agentic flows |
| [About AI Workflows](docs/ABOUT_AI_WORKFLOWS.md) | RAG, FTS, skills, prompts, sampling, agentic chaining |

## Key links

- **[Documentation hub](docs/README.md)** — curated entry
- **[Documentation index](docs/DOCUMENTATION_INDEX.md)** — full map of ~100 docs
- **[Tauri desktop](docs/TAURI.md)** — maintainer build and production pitfalls
- **[Cookbook](docs/COOKBOOK.md)** — goal-oriented recipes
- **[API reference](docs/API.md)** — all MCP tools and endpoints
- **[Configuration](docs/Configuration.md)** — env vars and library setup
- **[Troubleshooting](docs/Troubleshooting.md)** — common issues and fixes
- **[Webapp README](webapp/README.md)** — Next.js dashboard on ports 10720/10721
- **[Plugin README](calibre_plugin/README.md)** — Calibre GUI plugin install and usage
- **[Plugin repo](https://github.com/sandraschi/calibre-plugins)** — calibreops-bridge (RAG/AI plugin)

## Installation

```powershell
# Development install
git clone https://github.com/sandraschi/calibre-mcp.git
cd calibre-mcp
uv sync

# Or via MCPB package
npx mcpb install calibre-mcp
```

## Features

- **FastMCP 3.2** — Universal connect (stdio + HTTP), sampling, agentic tool chaining
- **21 portmanteau tools** — Consolidated operations (search, manage, export, OCR, viewer)
- **Metadata RAG (LanceDB)** — Semantic search over title, authors, tags, comments
- **Full-text chunk RAG** — FTS-driven book content retrieval
- **Calibre FTS** — Phrase search with PDF page / EPUB spine locations
- **Calibre plugin** — Extended metadata editor + VL from query in Calibre GUI
- **Webapp** — Next.js dashboard with AI chat, Semantic Search, Skills, Smart Import
- **Skills & prompts** — Reusable agentic workflows (recommendations, library health, etc.)
- **Concurrency-safe** — Thread-safe DB operations for multi-client access
- **Windows-native** — Unicode-safe, runs reliably on Windows

*Austrian efficiency for digital libraries. Built with realistic AI-assisted development timelines.*
