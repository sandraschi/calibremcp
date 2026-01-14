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
- `text` (string, optional): Search text

**Response:** BookListResponse with items, total, page, per_page

### GET `/api/books/{book_id}`
Get book details by ID.

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

## Additional Endpoints

The backend also exposes endpoints for all MCP tools:

- `/api/authors` - Author management
- `/api/tags` - Tag management
- `/api/comments` - Comment CRUD operations
- `/api/files` - File operations (convert, download, bulk)
- `/api/analysis` - Library analysis and statistics
- `/api/specialized` - Specialized operations (Japanese organizer, IT curator, reading recommendations)
- `/api/bulk` - Bulk operations (update metadata, export, delete, convert)
- `/api/export` - Book export (CSV, JSON, HTML, Pandoc formats)
- `/api/collections` - Smart collections management
- `/api/system` - System management and help

See Swagger UI at `/docs` for complete endpoint documentation.
