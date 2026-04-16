# API Endpoints Documentation

Complete list of all available API endpoints for the Calibre Webapp backend.

## Books API (`/api/books`)

### GET `/api/books`
List books with optional filters.

**Query Parameters:**
- `limit` (int, default: 50): Maximum number of results (1-1000)
- `offset` (int, default: 0): Results offset for pagination
- `author` (string, optional): Filter by author name
- `tag` (string, optional): Filter by tag name
- `publisher` (string, optional): Filter by publisher name
- `text` (string, optional): Search text

**Response:** BookListResponse with items, total, page, per_page

### GET `/api/books/{book_id}`
Get book details by ID. Uses direct BookService when available for full metadata (rating, publisher, identifiers, comments).

**Path Parameters:**
- `book_id` (int): Book ID

**Response:** Book object with metadata and formats

### GET `/api/books/{book_id}/details`
Get complete metadata and file information for a book.

**Path Parameters:**
- `book_id` (int): Book ID

**Response:** BookDetailResponse with complete metadata and file paths

### POST `/api/books`
Add a new book to the library.

**Request Body:**
```json
{
  "file_path": "string (required)",
  "metadata": "object (optional)",
  "fetch_metadata": "boolean (default: true)",
  "convert_to": "string (optional)"
}
```

**Response:** Created book information

### PUT `/api/books/{book_id}`
Update a book's metadata and properties.

**Path Parameters:**
- `book_id` (int): Book ID

**Request Body:**
```json
{
  "metadata": "object (optional)",
  "status": "string (optional)",
  "progress": "float (optional, 0.0-1.0)",
  "cover_path": "string (optional)",
  "update_timestamp": "boolean (default: true)"
}
```

**Response:** Update confirmation with updated fields

### DELETE `/api/books/{book_id}`
Delete a book from the library.

**Path Parameters:**
- `book_id` (int): Book ID

**Query Parameters:**
- `delete_files` (boolean, default: true): Delete files from disk
- `force` (boolean, default: false): Skip dependency checks

**Response:** Deletion confirmation

## Search API (`/api/search`)

### GET `/api/search`
Advanced book search.

**Query Parameters:**
- `query` (string, optional): Search query text
- `author` (string, optional): Filter by author
- `tag` (string, optional): Filter by tag
- `min_rating` (int, optional): Minimum rating (1-5)
- `limit` (int, default: 50): Maximum results (1-1000)
- `offset` (int, default: 0): Results offset

**Response:** BookListResponse with search results

## Libraries API (`/api/libraries`)

### GET `/api/libraries`
List all available libraries.

**Response:** LibraryListResponse with libraries array, current_library, total_libraries

### GET `/api/libraries/stats`
Get statistics for a library.

**Query Parameters:**
- `library_name` (string, optional): Library name (uses current if omitted)

**Response:** LibraryStats with total_books, total_authors, format_distribution, etc.

### POST `/api/libraries/switch`
Switch to a different library.

**Request Body:**
```json
{
  "library_name": "string (required)"
}
```

**Response:** Success status with new library information

## Viewer API (`/api/viewer`)

### POST `/api/viewer/open-random`
Open a random book matching criteria.

**Query Parameters:**
- `author` (string, optional): Author name filter
- `tag` (string, optional): Tag name filter
- `series` (string, optional): Series name filter
- `format_preference` (string, default: "EPUB"): Preferred file format

**Response:** Selected book information and file path

### POST `/api/viewer/open`
Open a book in the viewer.

**Request Body:**
```json
{
  "book_id": "int (required)",
  "file_path": "string (required)"
}
```

**Response:** Viewer metadata, state, and first page

### GET `/api/viewer/page`
Get a specific page from a book.

**Query Parameters:**
- `book_id` (int, required): Book ID
- `file_path` (string, required): Path to book file
- `page_number` (int, default: 0): Zero-based page number

**Response:** Page content and metadata

### GET `/api/viewer/metadata`
Get comprehensive metadata for a book.

**Query Parameters:**
- `book_id` (int, required): Book ID
- `file_path` (string, required): Path to book file

**Response:** ViewerMetadata with page count, dimensions, format

### GET `/api/viewer/state`
Get the current viewer state.

**Query Parameters:**
- `book_id` (int, required): Book ID
- `file_path` (string, required): Path to book file

**Response:** ViewerState with current_page, zoom, layout, etc.

### PUT `/api/viewer/state`
Update viewer state (save reading progress).

**Request Body:**
```json
{
  "book_id": "int (required)",
  "file_path": "string (required)",
  "current_page": "int (optional)",
  "reading_direction": "string (optional: ltr|rtl|vertical)",
  "page_layout": "string (optional: single|double|auto)",
  "zoom_mode": "string (optional: fit-width|fit-height|fit-both|original|custom)",
  "zoom_level": "float (optional, 0.1-5.0)"
}
```

**Response:** Updated ViewerState

### POST `/api/viewer/close`
Close a viewer session.

**Request Body:**
```json
{
  "book_id": "int (required)",
  "file_path": "string (required)"
}
```

**Response:** Success status

### POST `/api/viewer/open-file`
Open a book file with the system's default application.

**Request Body:**
```json
{
  "book_id": "int (required)",
  "file_path": "string (required)"
}
```

**Response:** Success status and file path

## Metadata API (`/api/metadata`)

### GET `/api/metadata/show`
Show comprehensive book metadata.

**Query Parameters:**
- `query` (string, optional): Book title or partial title
- `author` (string, optional): Author name filter
- `open_browser` (boolean, default: false): Open HTML popup in browser

**Response:** Detailed metadata dictionary

### POST `/api/metadata/update`
Update metadata for single or multiple books.

**Request Body:**
```json
{
  "updates": [
    {
      "book_id": "int (required)",
      "field": "string (required)",
      "value": "any (required)"
    }
  ]
}
```

**Response:** Update results with success/failure counts

### POST `/api/metadata/organize-tags`
AI-powered tag organization and cleanup suggestions.

**Response:** Tag statistics and organization suggestions

### POST `/api/metadata/fix-issues`
Automatically fix common metadata problems.

**Response:** Results of automatic fixes

## Logs API (`/api/logs`)

### GET `/api/logs`
Tail log file with optional filtering.

**Query Parameters:**
- `tail` (int, default: 500): Last N lines (1-10000)
- `filter` (string, optional): Substring filter for log lines
- `level` (string, optional): Log level filter (DEBUG, INFO, WARNING, ERROR)

**Response:**
```json
{
  "lines": ["log line 1", "..."],
  "total": 1234,
  "file": "/path/to/logs/webapp.log",
  "error": "optional error message"
}
```

**Log sources:** `logs/calibremcp.log` (MCP stdio), `logs/webapp.log` (webapp backend); override via `LOG_FILE` env.

## Health & Info

### GET `/`
Root endpoint with API information.

**Response:** API message, version, docs URL

### GET `/health`
Health check endpoint.

**Response:** `{"status": "healthy"}`

### GET `/debug/import`
Debug endpoint to test calibre_mcp import.

**Response:** Python path, PYTHONPATH, import status, and calibre_mcp file location

### GET `/docs`
Swagger UI documentation (interactive API explorer)

### GET `/redoc`
ReDoc documentation (alternative API docs)

## RAG API (`/api/rag`)

### GET `/api/rag/metadata/build/status`
Poll progress of a running metadata index build.

**Response:** `{status, current, total, percentage, message}`

### POST `/api/rag/metadata/build`
Start build or rebuild of the LanceDB metadata index (title, authors, tags, comments).

**Query Parameters:**
- `force_rebuild` (boolean, default: false)

**Response:** `{status, message, books_indexed}`

### POST `/api/rag/content/build`
Start build or rebuild of the LanceDB full-text content index (full book text).
Significantly slower than metadata build on large libraries.

**Query Parameters:**
- `force_rebuild` (boolean, default: false)

### GET `/api/rag/metadata/search`
Semantic search over book metadata using LanceDB.

**Query Parameters:**
- `q` (string, required): Natural-language query
- `top_k` (int, default: 10, max: 50)

**Response:** `{results: [{book_id, title, text, score}]}`

### GET `/api/rag/retrieve`
Semantic passage retrieval from full book content using LanceDB.
Requires content index to be built first.

**Query Parameters:**
- `q` (string, required): Natural-language query
- `top_k` (int, default: 10, max: 50)

**Response:** `{query, hits: [{book_id, title, chunk_idx, snippet, rank}]}`

### POST `/api/rag/search`
Combined portmanteau RAG search (metadata + content, auto-selects mode).

**Query Parameters:**
- `q` (string, required)
- `top_k` (int, default: 10)
- `mode` (string, default: "auto"): "metadata" | "content" | "auto"

### POST `/api/rag/synopsis/{book_id}`
Generate a RAG-synthesised spoiler-aware synopsis for a book.

**Path Parameters:**
- `book_id` (int): Book ID

**Query Parameters:**
- `spoilers` (boolean, default: false)

**Response:** `{book_id, title, synopsis, spoilers}`

### POST `/api/rag/research/{book_id}`
Deep external research on a single book. Fetches Wikipedia (book + author),
SF Encyclopedia (genre fiction), TVTropes (fiction), Anime News Network
(manga/light novels), and Open Library (if ISBN present). Combines with
local Calibre data — rating, tags, personal notes, RAG passages if indexed.
Synthesises via LLM sampling into a structured markdown research report.

**Requires sampling-capable MCP client context (Claude Desktop / Cursor).**
Response time: 10–30 seconds.

**Path Parameters:**
- `book_id` (int): Calibre book ID

**Query Parameters:**
- `include_spoilers` (boolean, default: false)

**Response:**
```json
{
  "success": true,
  "book_id": 1234,
  "title": "Use of Weapons",
  "authors": ["Iain M. Banks"],
  "report": "# Use of Weapons\n\n## Overview\n...",
  "sources_fetched": ["wikipedia_book", "wikipedia_author", "sf_encyclopedia", "tvtropes"],
  "sources_failed": ["goodreads"],
  "local_data": {"rating": 5, "personal_notes": true, "rag_passages": 3}
}
```

### POST `/api/rag/critical-reception/{book_id}`
Synthesise external critical reviews and academic reception (web + library).

### POST `/api/rag/deep-research`
Cross-book thematic analysis using full-text RAG.

**Query Parameters:**
- `topic` (string, required): Thematic topic
- `limit` (int, default: 5): Max books to include

### POST `/api/rag/metadata/export`
Export all library metadata as JSON for external RAG pipelines.

**Query Parameters:**
- `output_path` (string, optional): Override output file path

## Series API (`/api/series`)

### GET `/api/series`
List series with optional search. Cached 60s.

**Query Parameters:**
- `query` (string, optional)
- `limit` (int, default: 50)
- `offset` (int, default: 0)
- `letter` (string, optional): Filter by first letter

### GET `/api/series/stats`
Library-wide series statistics.

### GET `/api/series/analysis`
Reading order and completion analysis for a named series.

**Query Parameters:**
- `series_name` (string, required): Exact or partial series name

**Response:** `{series, books: [{index, title, owned, book_id}], missing, total_volumes, owned_count}`

### GET `/api/series/completion`
Library-wide series completion report.

**Query Parameters:**
- `min_books` (int, default: 2)
- `incomplete_only` (boolean, default: true)

### GET `/api/series/{series_id}`
Get series details by ID.

### GET `/api/series/{series_id}/books`
Get all books in a series.

**Query Parameters:**
- `limit` (int, default: 50)
- `offset` (int, default: 0)


