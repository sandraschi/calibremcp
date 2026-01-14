# Endpoint Testing Guide

## Test Scripts

Two test scripts are available:

1. **`test_all_endpoints.py`** - Tests MCP tools directly (bypasses HTTP layer)
2. **`test_endpoints_http.py`** - Tests endpoints via HTTP requests (full stack)

## Running Tests

### Direct MCP Tool Tests
```bash
cd webapp/backend
python test_all_endpoints.py
```

### HTTP Endpoint Tests
```bash
cd webapp/backend
python test_endpoints_http.py
```

**Note:** Requires backend server running on `http://localhost:13000`

## Endpoints to Test

### Books API (`/api/books`)
- [ ] GET `/api/books` - List books with filters
- [ ] GET `/api/books/{book_id}` - Get book by ID
- [ ] GET `/api/books/{book_id}/details` - Get complete book details
- [ ] POST `/api/books` - Add new book
- [ ] PUT `/api/books/{book_id}` - Update book metadata
- [ ] DELETE `/api/books/{book_id}` - Delete book

### Search API (`/api/search`)
- [ ] GET `/api/search` - Advanced book search

### Libraries API (`/api/libraries`)
- [ ] GET `/api/libraries` - List all libraries
- [ ] GET `/api/libraries/stats` - Get library statistics
- [ ] POST `/api/libraries/switch` - Switch active library

### Viewer API (`/api/viewer`)
- [ ] POST `/api/viewer/open-random` - Open random book
- [ ] POST `/api/viewer/open` - Open book in viewer
- [ ] GET `/api/viewer/page` - Get specific page
- [ ] GET `/api/viewer/metadata` - Get viewer metadata
- [ ] GET `/api/viewer/state` - Get viewer state
- [ ] PUT `/api/viewer/state` - Update viewer state
- [ ] POST `/api/viewer/close` - Close viewer session
- [ ] POST `/api/viewer/open-file` - Open file with default app

### Metadata API (`/api/metadata`)
- [ ] GET `/api/metadata/show` - Show book metadata
- [ ] POST `/api/metadata/update` - Update metadata
- [ ] POST `/api/metadata/organize-tags` - Organize tags
- [ ] POST `/api/metadata/fix-issues` - Fix metadata issues

### Health & Info
- [ ] GET `/` - Root endpoint
- [ ] GET `/health` - Health check

## Known Issues to Verify

1. **MCP Import Path**: Verify `calibre_mcp.tools` imports correctly
2. **Tool Mapping**: Verify all tool names in `client.py` tool_map are correct
3. **Error Handling**: Verify errors are properly converted to HTTP responses
4. **Response Format**: Verify all endpoints return proper JSON

## Testing Checklist

- [ ] All endpoints return 200 status for valid requests
- [ ] Error responses are properly formatted
- [ ] MCP tools are called correctly
- [ ] Response data matches expected structure
- [ ] Edge cases handled (missing params, invalid IDs, etc.)
