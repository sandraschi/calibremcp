# ADN: Webapp Logs, Book Modal, Chat Session

**Date**: 2025-01-30  
**Scope**: Webapp fixes and enhancements

## Summary

Session addressed broken webapp features: logs page URL parse error, book modal missing metadata, chat page undefined variables. Added logs API with tail/filter/live tail. Documented MCP HTTP vs direct-import architecture.

## Decisions

### 1. MCP_USE_HTTP=false for Webapp

**Context:** Webapp backend mounts FastMCP at /mcp, but tools are only registered in `main()` which runs only in stdio mode. HTTP mount has no tools.

**Decision:** Set `MCP_USE_HTTP=false` in webapp backend. MCP client uses direct Python import of tool functions instead of HTTP calls. Webapp works; HTTP path remains unfixed.

**Rationale:** Fixing HTTP would require registering tools at module load; previous attempts caused circular import. Direct import is reliable and fast.

### 2. Direct BookService for get_book

**Context:** Book modal showed no metadata (rating, publisher, identifiers, comments). MCP tool path returned data but frontend expected flat structure; BookService._to_response had full fields.

**Decision:** Backend GET /api/books/{id} tries direct BookService.get_by_id first when database is initialized. Fallback to MCP manage_books if direct path fails.

**Rationale:** Guarantees full metadata; BookService._to_response already includes publisher, rating, identifiers. Avoids MCP serialization quirks.

### 3. Logs Page: Log File + Status

**Context:** Logs page showed "System status" only; failed with "Failed to parse URL" (relative URL in SSR).

**Decision:**
- Fix getSystemStatus to use getBaseUrl() for absolute URL
- Add backend /api/logs for log file (tail, filter, level)
- Logs page: toggle Log file / System status; log viewer with filter, level, tail, live tail (polling with exponential backoff)
- Backend writes to logs/webapp.log with rotation
- Log sources: logs/calibremcp.log (MCP stdio), logs/webapp.log (webapp)

### 4. Chat Personalities

**Context:** Chat page referenced `personality` and `PERSONALITIES` but they were undefined; page crashed.

**Decision:** Add PERSONALITIES constant and personality state. Default, Librarian, Casual preprompts.

## Implemented

| Item | Location |
|------|----------|
| Logs API | webapp/backend/app/api/logs.py |
| Logs page | webapp/frontend/app/logs/page.tsx |
| getSystemStatus fix | webapp/frontend/lib/api.ts |
| get_book direct path | webapp/backend/app/api/books.py |
| Chat personalities | webapp/frontend/app/chat/page.tsx |
| Books publisher param | webapp/backend/app/api/books.py |
| Webapp file logging | webapp/backend/app/main.py |

## Logging Architecture

- **MCP stdio** (`python -m calibre_mcp`): Writes to logs/calibremcp.log (RotatingFileHandler, 10MB, 5 backups)
- **Webapp backend**: Writes to logs/webapp.log (same rotation)
- **Logs page**: Reads either file; LOG_FILE env overrides path

## References

- STATUS_REPORT.md - Webapp status section
- webapp/README.md - Logs, Chat personalities
- docs/Troubleshooting.md - Logging section
