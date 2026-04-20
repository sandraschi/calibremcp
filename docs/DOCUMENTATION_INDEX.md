# CalibreMCP — documentation index

**Central map for this repository** ([`README.md`](../README.md) is the primary entry).

---

## Quick navigation

| If you want to… | Start here |
|-----------------|------------|
| Install and configure the server | [`README.md`](../README.md), [`Configuration.md`](Configuration.md) |
| Use tools from an AI client | [`USAGE_GUIDE_CLAUDE.md`](USAGE_GUIDE_CLAUDE.md), [`COOKBOOK.md`](COOKBOOK.md), [`PROMPTS.md`](PROMPTS.md) |
| Understand portmanteau tools | [`TOOLS_CONSOLIDATION.md`](TOOLS_CONSOLIDATION.md), [`TOOL_DOCSTRING_STANDARD.md`](TOOL_DOCSTRING_STANDARD.md) |
| RAG, FTS, agentic flows | [`AGENTIC_AND_RAG.md`](AGENTIC_AND_RAG.md), [`CALIBRE_DEBUG_EXPORT_AND_RAG_PLAN.md`](CALIBRE_DEBUG_EXPORT_AND_RAG_PLAN.md), [`FULL_TEXT_RAG_DESIGN.md`](FULL_TEXT_RAG_DESIGN.md), [`SEARCH_QUERY_EXAMPLES.md`](SEARCH_QUERY_EXAMPLES.md) |
| MCP protocol details (schemas, skills, UTF-8) | [`mcp-technical/MCP_OUTPUT_SCHEMAS_AND_SKILLS.md`](mcp-technical/MCP_OUTPUT_SCHEMAS_AND_SKILLS.md), [`mcp-technical/README.md`](mcp-technical/README.md) |
| MCP Apps / Prefab (optional rich cards) | [`mcp-technical/MCP_APPS_PREFAB.md`](mcp-technical/MCP_APPS_PREFAB.md) |
| Calibre plugin & integrations | [`integrations/CALIBRE_INTEGRATION_GUIDE.md`](integrations/CALIBRE_INTEGRATION_GUIDE.md) |
| Webapp | [`WEBAPP_IMPLEMENTATION_GUIDE.md`](WEBAPP_IMPLEMENTATION_GUIDE.md), [`WEBAPP_RECOMMENDATION.md`](WEBAPP_RECOMMENDATION.md) |
| MCPB / distribution | [`mcpb-packaging/README.md`](mcpb-packaging/README.md) |
| Troubleshooting | [`Troubleshooting.md`](Troubleshooting.md), [`VERIFY_SERVER_LOAD.md`](VERIFY_SERVER_LOAD.md) |
| Contribute | [`CONTRIBUTING.md`](../CONTRIBUTING.md), [`development/README.md`](development/README.md) |

---

## Repository layout (docs)

High-level view of `docs/` — not every file is listed; use search or the sections below.

```
docs/
├── README.md (this index)
├── API.md, PRD.md, Configuration.md
├── AGENTIC_AND_RAG.md, CALIBRE_DEBUG_EXPORT_AND_RAG_PLAN.md, FULL_TEXT_RAG_DESIGN.md, COOKBOOK.md, PROMPTS.md
├── TOOLS_CONSOLIDATION.md, TOOL_DOCSTRING_STANDARD.md, TOOL_DOCSTRING_MIGRATION.md
├── SEARCH_QUERY_EXAMPLES.md, Troubleshooting.md, VERIFY_SERVER_LOAD.md
├── USAGE_GUIDE_CLAUDE.md, CALIBRE_LIBRARY_STRUCTURE.md, EXPORT_USAGE.md
├── WEBAPP_*.md, PLAN_FASTMCP_31_RAG_SKILLS.md, ORGANIZATION_SUMMARY.md
│
├── mcp-technical/          MCP server: FastMCP, debugging, output schemas, skills UTF-8, MCP Apps / Prefab
├── integrations/         Calibre GUI plugin and library integration
├── development/            Internal dev notes, migrations, compliance
├── mcpb-packaging/         MCPB bundle and PyPI-style publishing notes
├── glama-platform/         Glama.ai directory / quality (historical)
├── glama/                  Glama requirements / gold notes
├── github/                 CI, releases, security
├── repository-protection/  Branches, backups (generic workflow)
├── testing/                Megatest and test harness docs
├── adn-notes/              Design notes and session logs
├── research/               Spikes (e.g. FastMCP persistence)
└── serena/                 Serena tooling notes (optional)
```

---

## Core reference (repo root `docs/`)

| Document | Purpose |
|----------|---------|
| [`API.md`](API.md) | HTTP/API and tool surface overview |
| [`PRD.md`](PRD.md) | Product requirements |
| [`Configuration.md`](Configuration.md) | Environment and library paths |
| [`TOOLS_CONSOLIDATION.md`](TOOLS_CONSOLIDATION.md) | Portmanteau tool list and consolidation |
| [`TOOL_DOCSTRING_STANDARD.md`](TOOL_DOCSTRING_STANDARD.md) | Docstring conventions for tools |
| [`COOKBOOK.md`](COOKBOOK.md) | Goal-oriented recipes |
| [`PROMPTS.md`](PROMPTS.md) | Registered MCP prompts |
| [`AGENTIC_AND_RAG.md`](AGENTIC_AND_RAG.md) | FTS vs RAG, LanceDB layout, agentic tools |
| [`FULL_TEXT_RAG_DESIGN.md`](FULL_TEXT_RAG_DESIGN.md) | Full-book chunk RAG design |
| [`SEARCH_QUERY_EXAMPLES.md`](SEARCH_QUERY_EXAMPLES.md) | Query examples |
| [`Troubleshooting.md`](Troubleshooting.md) | Common failures |
| [`ORGANIZATION_SUMMARY.md`](ORGANIZATION_SUMMARY.md) | How docs evolved (meta) |

---

## MCP technical (`docs/mcp-technical/`)

| Document | Purpose |
|----------|---------|
| [`README.md`](mcp-technical/README.md) | Index of technical topics |
| [`MCP_OUTPUT_SCHEMAS_AND_SKILLS.md`](mcp-technical/MCP_OUTPUT_SCHEMAS_AND_SKILLS.md) | `outputSchema`, `manage_authors` / `calibre_ocr`, bundled skills, Windows UTF-8 |
| [`CLAUDE_DESKTOP_DEBUGGING.md`](mcp-technical/CLAUDE_DESKTOP_DEBUGGING.md) | Claude Desktop / stdio issues |
| [`MCP_PRODUCTION_CHECKLIST.md`](mcp-technical/MCP_PRODUCTION_CHECKLIST.md) | Production checklist |
| [`TROUBLESHOOTING_FASTMCP_2.12.md`](mcp-technical/TROUBLESHOOTING_FASTMCP_2.12.md) | FastMCP troubleshooting |
| [`CONTAINERIZATION_GUIDELINES.md`](mcp-technical/CONTAINERIZATION_GUIDELINES.md) | Docker patterns |
| [`MONITORING_STACK_DEPLOYMENT.md`](mcp-technical/MONITORING_STACK_DEPLOYMENT.md) | Observability |
| [`FASTMCP_2.13_PERSISTENT_STORAGE_PATTERN.md`](mcp-technical/FASTMCP_2.13_PERSISTENT_STORAGE_PATTERN.md) | Persistence pattern |
| [`PORTMANTEAU_TOOL_MIGRATION_PLAN.md`](mcp-technical/PORTMANTEAU_TOOL_MIGRATION_PLAN.md) | Migration history |

---

## Calibre integrations (`docs/integrations/`)

| Document | Purpose |
|----------|---------|
| [`CALIBRE_INTEGRATION_GUIDE.md`](integrations/CALIBRE_INTEGRATION_GUIDE.md) | Library access, API, database |
| [`CALIBRE_PLUGIN_DESIGN.md`](integrations/CALIBRE_PLUGIN_DESIGN.md) | Plugin architecture |
| [`CALIBRE_PLUGIN_IMPLEMENTATION_NOTES.md`](integrations/CALIBRE_PLUGIN_IMPLEMENTATION_NOTES.md) | Implementation checklist |

Implementation code: [`calibre_plugin/`](../calibre_plugin/) (repository root).

---

## Packaging (`docs/mcpb-packaging/`)

| Document | Purpose |
|----------|---------|
| [`README.md`](mcpb-packaging/README.md) | MCPB hub |
| [`MCPB_PACKAGING_STANDARDS.md`](mcpb-packaging/MCPB_PACKAGING_STANDARDS.md) | Standards alignment |
| [`PYPI_PUBLISHING_GUIDE.md`](mcpb-packaging/PYPI_PUBLISHING_GUIDE.md) | PyPI publishing |

Build script (root): [`scripts/build-mcpb-package.ps1`](../scripts/build-mcpb-package.ps1).

---

## Development (`docs/development/`)

Hub: [`development/README.md`](development/README.md).

Notable entries: `PYDANTIC_V2_MIGRATION.md`, `REMAINING_TOOL_MIGRATION.md`, `FASTMCP_213_COMPLIANCE.md`, `PORTMANTEAU_REFACTORING_SUMMARY.md`, `MCP_SYNC_DEBUGGING_GUIDE.md`, `PYTHON_DEPENDENCY_HELL_FIX.md`, and other phase/migration notes.

---

## GitHub & CI (`docs/github/`)

[`README.md`](github/README.md), [`WORKFLOWS.md`](github/WORKFLOWS.md), [`RELEASE_CHECKLIST.md`](github/RELEASE_CHECKLIST.md), [`SECURITY_HARDENING.md`](github/SECURITY_HARDENING.md).

---

## Glama (`docs/glama-platform/`, `docs/glama/`)

Directory listings, Gold status notes, rescan and integration guides — see [`glama-platform/README.md`](glama-platform/README.md).

---

## Repository protection (`docs/repository-protection/`)

Generic Git workflow: [`README.md`](repository-protection/README.md), branch protection, backups.

---

## Testing (`docs/testing/`)

Megatest and universal MCP test harness documentation (see [`testing/UNIVERSAL_MCP_MEGATEST_GUIDE.md`](testing/UNIVERSAL_MCP_MEGATEST_GUIDE.md)).

---

## Optional / archive

- **`docs/adn-notes/`** — ADRs and session notes  
- **`docs/research/`** — Research spikes  
- **`docs/serena/`** — Serena copy/install notes  
- **`Full_Documentation.md`**, **`COMPLETE_DOCUMENTATION_STRUCTURE.md`** — Large dumps; prefer topical docs above  

---

## Suggested reading paths

**1. New user (30 min)**  
[`README.md`](../README.md) → [`COOKBOOK.md`](COOKBOOK.md) → [`Configuration.md`](Configuration.md)

**2. MCP integrator (1 h)**  
[`TOOLS_CONSOLIDATION.md`](TOOLS_CONSOLIDATION.md) → [`mcp-technical/MCP_OUTPUT_SCHEMAS_AND_SKILLS.md`](mcp-technical/MCP_OUTPUT_SCHEMAS_AND_SKILLS.md) → [`API.md`](API.md)

**3. RAG / search developer**  
[`AGENTIC_AND_RAG.md`](AGENTIC_AND_RAG.md) → [`FULL_TEXT_RAG_DESIGN.md`](FULL_TEXT_RAG_DESIGN.md) → [`SEARCH_QUERY_EXAMPLES.md`](SEARCH_QUERY_EXAMPLES.md)

**4. Contributor**  
[`CONTRIBUTING.md`](../CONTRIBUTING.md) → [`development/README.md`](development/README.md) → [`github/WORKFLOWS.md`](github/WORKFLOWS.md)

---

## Getting help

- **Issues:** [github.com/sandra/calibre-mcp/issues](https://github.com/sandra/calibre-mcp/issues)  
- **Docs wrong or stale:** open an issue or PR against this file or the specific doc.

---

*Index for CalibreMCP. Update this file when adding major doc areas.*
