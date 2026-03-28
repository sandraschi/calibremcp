# MCP output schemas, bundled skills, and Windows UTF-8

This document describes how CalibreMCP exposes **structured tool outputs** (MCP `outputSchema`), loads **bundled skills** under `skill://`, and avoids **Windows encoding failures** when reading UTF-8 markdown.

## FastMCP and root `outputSchema`

FastMCP requires tool **output schemas to be a single JSON Schema object** (`type: object`). Root-level **`anyOf` / `oneOf` unions are rejected** at registration (“Output schemas must represent object types”).

Therefore:

- **`manage_authors`** uses one Pydantic model, **`ManageAuthorsMCPOutput`** (`src/calibre_mcp/tools/author_schemas.py`), with **optional** fields covering every successful branch (`list`, `get`, `get_books`, `stats`, `by_letter`) plus structured **error** fields (`success`, `error`, `error_code`, `suggestions`, …). **`model_config` allows extra properties** so future fields do not break clients.
- **`calibre_ocr`** uses **`CalibreOCROutput`** in `src/calibre_mcp/tools/ocr_output_schema.py` (same pattern: core fields + `extra="allow"` for provider-specific keys).

Static analyzers and catalogs (e.g. ToolBench) can use these schemas to reason about return shapes without inferring from call sites only.

## Legacy `author_tools` module

The module `src/calibre_mcp/tools/author_tools.py` **no longer defines** separate MCP tools (`list_authors`, `get_author`, …). Those `@mcp_tool`-decorated methods were removed so **static analysis does not count duplicate “ghost” tools** next to the real **`manage_authors`** portmanteau.

The module **re-exports** schema types (`MANAGE_AUTHORS_OUTPUT_SCHEMA`, `AuthorListResult`, …) for backwards compatibility with older references. **Always call** `manage_authors(operation="list"|"get"|…)` for author operations.

## Bundled skills and UTF-8 on Windows

FastMCP’s **`SkillProvider`** loads `SKILL.md` via **`Path.read_text()`** without an explicit encoding. On Windows the process default is often **cp1252**, which can raise **`UnicodeDecodeError`** on UTF-8 skill files.

**Mitigation:** before registering **`SkillsDirectoryProvider`**, `src/calibre_mcp/server.py` calls **`install_skills_utf8_read_patch([_skills_root])`** (`src/calibre_mcp/skills_encoding.py`). That installs a **narrow** monkey-patch: for paths **under the resolved bundled `calibre_mcp/skills/` directory** only, `read_text()` uses **`encoding="utf-8"`** and **`errors="replace"`**. Reads outside those roots are unchanged.

## Tests

`tests/test_tool_preload.py` imports each tool module listed for the webapp preload list. If an **optional** module is missing (e.g. `manage_specialized` when the file is not shipped), the test **skips** with `ModuleNotFoundError` instead of failing the suite.

## See also

- Portmanteau overview: [../TOOLS_CONSOLIDATION.md](../TOOLS_CONSOLIDATION.md)
- Prompts and skills UX: [../PROMPTS.md](../PROMPTS.md)
- FastMCP tool design: `mcp-central-docs` — `standards/TOOL_DESIGN_STANDARDS.md`
