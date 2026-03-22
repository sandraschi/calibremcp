# MCP prompt catalog (CalibreMCP)

Registered in `src/calibre_mcp/prompts.py` via FastMCP `@mcp.prompt()`. Clients list prompts over MCP and inject the returned body into the chat.

**How to use this doc:** pick a **prompt name** (first column), then use **suggested tools** so the model does not guess. For full prompt text, see the source file or your client’s prompt picker.

| Prompt name | Intent (short) | Suggested tools / notes |
|-------------|----------------|-------------------------|
| `reading_recommendations` | Next read from habits, series, ratings | `query_books`, `manage_analysis`, `manage_libraries` |
| `library_organization` | Duplicates, messy metadata, structure | `manage_library_operations`, `query_books`, `manage_analysis` |
| `book_discovery` | Unread / similar / overlooked in collection | `query_books`, `calibre_metadata_search` (after index) |
| `series_management` | Incomplete series, order, gaps | `query_books` (series filters), `manage_metadata` |
| `metadata_cleanup` | Missing fields, inconsistent authors/tags | `manage_metadata`, bulk-style filters via `query_books` |
| `tag_organization` | Merge duplicates, unused tags, hierarchy | `query_books`, tag operations via portmanteau metadata tools |
| `duplicate_detection` | Same title/author/ISBN candidates | `manage_analysis`, `query_books` |
| `reading_statistics` | Genres, authors, ratings, trends | `manage_analysis`, `query_books` stats-style queries |
| `japanese_books` | Manga / LN / 学習 — series order | `query_books`, series + tag filters |
| `it_books` | Tech stack, outdated titles, learning path | `query_books`, `calibre_metadata_search` |
| `format_conversion` | EPUB/PDF/AZW gaps per device | `manage_books`, format-related operations |
| `library_search` | Advanced filters (date, size, rating, publisher) | `query_books` with combined parameters |
| `unread_priority` | Ranked TBR queue | `query_books` (unread, rating, tags) |
| `library_health` | Missing files, orphans, integrity feel | `manage_analysis`, `manage_library_operations` |
| `author_analysis` | Depth by author, gaps | `query_books`, author filters |
| `bulk_operations` | Many books one action | Appropriate `manage_*` + `query_books` lists |
| `reading_goals` | Pace, series completion | `query_books`, `manage_analysis` |
| `book_comparison` | Same topic / edition / series choice | `query_books`, `calibre_metadata_search`, optional `rag_retrieve` |
| `library_export` | Series/author/tag export batches | `manage_books` export paths per tool docs |
| `smart_collections` | Dynamic groupings (tags, dates, status) | `query_books`; Calibre-side saved searches if applicable |
| `calibre_semantic_search` | **Meaning** over metadata (not body FTS) | `calibre_metadata_index_build` (once), then `calibre_metadata_search` |
| `calibre_mcp_guide` | Skills + chaining overview | Read `skill://calibre-expert/SKILL.md`; then `agentic_library_workflow` or direct tools |

## Pairing prompts with sampling

If the host supports **SEP-1577** (`ctx.sample`), prefer **`agentic_library_workflow`** for multi-step natural-language goals after choosing the closest prompt above. Otherwise chain **`manage_libraries` → `query_books` / `calibre_metadata_search` / `search_fulltext` → `manage_viewer`** explicitly.

## See also

- [COOKBOOK.md](./COOKBOOK.md) — goal-oriented recipes  
- [AGENTIC_AND_RAG.md](./AGENTIC_AND_RAG.md) — FTS vs RAG, indexes, HTTP chat  
- [README.md](../README.md) — configuration and usage examples  
