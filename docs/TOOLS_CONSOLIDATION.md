# Calibre MCP Tool Consolidation

**Target:** 15 core tools (down from 27)  
**Timestamp:** 2025-01-31

## Summary

Tools consolidated to 15 core + optional beta tools. Mock/placeholder tools removed from default load. Experimental tools moved behind `CALIBRE_BETA_TOOLS=true`.

## Core Tools (15)

| # | Tool | Operations |
|---|------|------------|
| 1 | manage_libraries | list, switch, stats, search, test_connection, discover |
| 2 | manage_books | add, get, details, update, delete |
| 3 | manage_metadata | update, organize_tags, fix_issues, show |
| 4 | manage_tags | list, create, update, delete, merge |
| 5 | manage_comments | create, read, update, delete, append |
| 6 | manage_series | list, create, update, delete |
| 7 | manage_publishers | list, create, update, delete |
| 8 | manage_authors | list, create, update, delete |
| 9 | manage_files | read, write, convert, extract |
| 10 | manage_analysis | analyze, stats, health |
| 11 | manage_library_operations | analyze_series, fix_series_metadata, merge_series, list_books |
| 12 | manage_system | status, help, config |
| 13 | export_books | export, import |
| 14 | manage_viewer | open, close |
| 15 | calibre_ocr | OCR operations |

## Merged (No Longer Standalone)

- **test_calibre_connection** -> manage_libraries(operation="test_connection")
- **library_discovery** -> manage_libraries(operation="discover")

## Beta Tools (CALIBRE_BETA_TOOLS=true)

Load experimental/niche tools:

- manage_import
- manage_descriptions
- manage_user_comments
- manage_extended_metadata
- manage_times
- manage_content_sync (device sync)
- manage_ai_operations (requires Ollama)
- manage_bulk_operations
- manage_organization
- manage_users (auth)
- manage_specialized (placeholder - returns "not implemented")
- agentic_calibre_workflow
- intelligent_library_processing

## Removed (Mocks)

- manage_specialized: Placeholder only, returns "not implemented". Moved to beta.
- agentic tools: Return capability descriptions but do not execute LLM orchestration. Moved to beta.

## Enabling Beta Tools

```powershell
$env:CALIBRE_BETA_TOOLS = "true"
# Then start the MCP server
```

Or in `.env`:
```
CALIBRE_BETA_TOOLS=true
```

## Future Consolidation (Optional)

To reduce further (e.g. for adn-beta or minimal install):

- Merge manage_comments, manage_descriptions into manage_metadata (add comment_*, description_* operations)
- Merge manage_times, manage_extended_metadata into manage_metadata
- Merge manage_user_comments into manage_comments or manage_metadata
