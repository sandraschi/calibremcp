# CalibreMCP API Reference

**Comprehensive reference for all MCP tools and endpoints**

---

## 🔧 MCP Tools

CalibreMCP uses **FastMCP 2.13+** with **portmanteau tools** - consolidated tools that handle multiple related operations through an `operation` parameter. This reduces tool count while maintaining full functionality.

### **Tool 1: `query_books`** ⭐ **PRIMARY BOOK ACCESS TOOL**

**Portmanteau tool** that consolidates all book querying operations: search, list, find, get books by various criteria.

#### **Verb Mapping for Claude**

**IMPORTANT:** Users may use different verbs (search, list, find, query, get) but they all map to the same operation.

ALL of these user requests should use `operation="search"`:
- "search books by [author]" → `query_books(operation="search", author="...")`
- "list books by [author]" → `query_books(operation="search", author="...")`
- "find books by [author]" → `query_books(operation="search", author="...")`
- "query books by [author]" → `query_books(operation="search", author="...")`
- "get books by [author]" → `query_books(operation="search", author="...")`
- "show me books by [author]" → `query_books(operation="search", author="...")`

**Rule:** If the user wants to access/retrieve/discover books with filters (author, tag, publisher, etc.), use `operation="search"` regardless of which verb they use.

#### **Signature**

```python
async def query_books(
    operation: str,  # "search", "list", "by_author", "by_series"
    # Search parameters (for operation="search")
    author: Optional[str] = None,
    authors: Optional[List[str]] = None,
    exclude_authors: Optional[List[str]] = None,
    text: Optional[str] = None,
    query: Optional[str] = None,  # Alias for text
    tag: Optional[str] = None,
    tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    series: Optional[str] = None,
    exclude_series: Optional[List[str]] = None,
    publisher: Optional[str] = None,
    publishers: Optional[List[str]] = None,
    has_publisher: Optional[bool] = None,
    rating: Optional[int] = None,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    unrated: Optional[bool] = None,
    pubdate_start: Optional[str] = None,
    pubdate_end: Optional[str] = None,
    added_after: Optional[str] = None,
    added_before: Optional[str] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    formats: Optional[List[str]] = None,
    comment: Optional[str] = None,
    has_empty_comments: Optional[bool] = None,
    format_table: bool = False,
    limit: int = 50,
    offset: int = 0,
    # For operation="by_author"
    author_id: Optional[int] = None,
    # For operation="by_series"
    series_id: Optional[int] = None,
    # For operation="list"
    sort: str = "title",
) -> Dict[str, Any]
```

#### **Operations**

1. **`operation="search"`** ⭐ **PRIMARY OPERATION**
   - Use for ALL user requests to access books with filters
   - Works with ANY verb: "search", "list", "find", "query", "get", "show me"
   - Supports comprehensive filtering (author, publisher, year, tags, rating, etc.)
   - Example: `query_books(operation="search", author="Conan Doyle")`

2. **`operation="list"`**
   - Only use when user explicitly wants ALL books without filters
   - Simple pagination with minimal filtering
   - Example: `query_books(operation="list", limit=20)`

3. **`operation="by_author"`**
   - Get books by numeric author_id (requires `author_id` parameter)
   - For author names, use `operation="search"` with `author` parameter instead
   - Example: `query_books(operation="by_author", author_id=42)`

4. **`operation="by_series"`**
   - Get books in a series by numeric series_id (requires `series_id` parameter)
   - For series names, use `operation="search"` with `series` parameter instead
   - Example: `query_books(operation="by_series", series_id=15)`

#### **Search Parameters** (for `operation="search"`)

**Author Filters:**
- `author`: Filter by author name (case-insensitive partial match)
- `authors`: Filter by multiple authors (OR logic)
- `exclude_authors`: Exclude books by these authors

**Text & Tags:**
- `text` / `query`: Search in title, author, tags, series, comments
- `tag`: Filter by single tag
- `tags`: Filter by multiple tags (OR logic)
- `exclude_tags`: Exclude books with these tags

**Series:**
- `series`: Filter by series name
- `exclude_series`: Exclude books in these series

**Rating:**
- `rating`: Exact rating (1-5)
- `min_rating`: Minimum rating (1-5)
- `max_rating`: Maximum rating (1-5)
- `unrated`: Filter for unrated books only

**Publisher:**
- `publisher`: Filter by publisher name
- `publishers`: Filter by multiple publishers
- `has_publisher`: Filter books with/without publisher

**Date Filters:**
- `pubdate_start`: Publication date start (YYYY-MM-DD)
- `pubdate_end`: Publication date end (YYYY-MM-DD)
- `added_after`: Date added after (YYYY-MM-DD)
- `added_before`: Date added before (YYYY-MM-DD)

**File Filters:**
- `min_size`: Minimum file size in bytes
- `max_size`: Maximum file size in bytes
- `formats`: List of formats to include (e.g., ["EPUB", "PDF"])

**Other:**
- `comment`: Search in book comments only
- `has_empty_comments`: Filter books with empty/non-empty comments
- `format_table`: Format results as pretty text table (boolean)

**Pagination:**
- `limit`: Maximum results to return (default: 50)
- `offset`: Results offset for pagination (default: 0)

#### **Usage Examples**

```python
# User says: "list books by conan doyle"
result = await query_books(
    operation="search",
    author="Conan Doyle",
    format_table=True
)

# Advanced search: author + publisher + year
result = await query_books(
    operation="search",
    author="Conan Doyle",
    publisher="Penguin",
    pubdate_start="1900-01-01",
    pubdate_end="1930-12-31"
)

# Search with multiple filters (AND logic)
result = await query_books(
    operation="search",
    author="Agatha Christie",
    tags=["mystery", "crime"],
    min_rating=4,
    exclude_tags=["horror"]
)

# Search by publisher with year range
result = await query_books(
    operation="search",
    publishers=["O'Reilly Media", "No Starch Press"],
    pubdate_start="2023-01-01",
    pubdate_end="2024-12-31"
)

# Search recently added books with rating
result = await query_books(
    operation="search",
    added_after="2024-01-01",
    min_rating=4,
    format_table=True
)

# List all books (simple operation)
result = await query_books(operation="list", limit=20)

# Get books by author ID
result = await query_books(
    operation="by_author",
    author_id=42,
    limit=10
)

# Get books in a series
result = await query_books(
    operation="by_series",
    series_id=15
)
```

#### **Returns**

Dictionary containing operation-specific results:
- For `operation="search"`: Paginated search results with total count, books list, optional table
- For `operation="list"`: Simple book list with pagination
- For `operation="by_author"`: List of books by author ID
- For `operation="by_series"`: List of books in series order

---

### **Tool 2: `manage_books`** ⭐ **BOOK CRUD OPERATIONS**

**Portmanteau tool** that consolidates book management operations: add, get, update, delete.

#### **Signature**

```python
async def manage_books(
    operation: str,  # "add", "get", "update", "delete"
    book_id: Optional[str] = None,
    file_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    # ... additional parameters based on operation
) -> Dict[str, Any]
```

#### **Operations**

1. **`operation="add"`**: Add a new book to the library (requires `file_path`)
2. **`operation="get"`**: Retrieve detailed book information (requires `book_id`)
3. **`operation="update"`**: Update book metadata and properties (requires `book_id`)
4. **`operation="delete"`**: Delete a book from the library (requires `book_id`)

#### **Usage Examples**

```python
# Add a book
result = await manage_books(
    operation="add",
    file_path="/path/to/book.epub",
    metadata={"title": "My Book", "authors": ["Author Name"]}
)

# Get book details
result = await manage_books(
    operation="get",
    book_id="123",
    include_metadata=True,
    include_formats=True
)

# Update book metadata
result = await manage_books(
    operation="update",
    book_id="123",
    metadata={"rating": 5, "tags": ["favorite"]}
)

# Delete a book
result = await manage_books(
    operation="delete",
    book_id="123",
    delete_files=True
)
```

---

### **Tool 3: `manage_libraries`** ⭐ **LIBRARY MANAGEMENT**

**Portmanteau tool** for managing multiple Calibre libraries.

#### **Operations**

1. **`operation="list"`**: List all available libraries
2. **`operation="switch"`**: Switch to a different library (requires `library_name`)
3. **`operation="stats"`**: Get statistics for a library
4. **`operation="search"`**: Search across multiple libraries

#### **Usage Examples**

```python
# List all libraries
result = await manage_libraries(operation="list")

# Switch library
result = await manage_libraries(
    operation="switch",
    library_name="Main Library"
)

# Get library statistics
result = await manage_libraries(
    operation="stats",
    library_name="Main Library"
)

# Search across libraries
result = await manage_libraries(
    operation="search",
    query="python programming",
    libraries=["Main Library", "IT Library"]
)
```

---

### **Tool 4: `get_book_details`**

Get complete metadata and file information for a specific book (standalone tool, not portmanteau).

#### **Signature**

```python
async def get_book_details(book_id: int) -> BookDetailResponse
```

#### **Parameters**

- **`book_id`** (int): Calibre book ID to fetch details for

#### **Returns**

`BookDetailResponse` with complete book information:
- Basic metadata: title, authors, series, rating, tags
- Publication info: published date, languages, comments
- File information: available formats, download links
- System data: identifiers, last modified, cover URL

---

### **Tool 5: `test_calibre_connection`**

Test connection to Calibre server and get diagnostics.

#### **Signature**

```python
async def test_calibre_connection() -> ConnectionTestResponse
```

#### **Returns**

`ConnectionTestResponse` with:
- `connected`: Boolean connection status
- `server_version`: Calibre server version
- `library_name`: Primary library name
- `total_books`: Number of books in library
- `response_time_ms`: Connection response time
- `error_message`: Error details if connection failed
- `server_capabilities`: List of supported features

---

### **Additional Portmanteau Tools**

- **`manage_smart_collections`**: Create, update, delete, query smart collections
- **`manage_users`**: User management and authentication operations
- **Export tools**: `export_books_csv`, `export_books_json`, `export_books_html`, `export_books_pandoc`

---

## 📊 Response Models

### **BookSearchResult**

Individual book result from search operations.

```python
class BookSearchResult(BaseModel):
    book_id: int
    title: str
    authors: List[str]
    series: Optional[str] = None
    series_index: Optional[float] = None
    rating: Optional[int] = None  # 1-5 scale
    tags: List[str] = []
    languages: List[str] = ["en"]
    formats: List[str] = []  # ["EPUB", "PDF", "MOBI", etc.]
    last_modified: Optional[str] = None
    cover_url: Optional[str] = None
```

### **LibrarySearchResponse**

Response from `query_books` search operations.

```python
class LibrarySearchResponse(BaseModel):
    results: List[BookSearchResult]
    total_found: int
    query_used: Optional[str] = None
    search_time_ms: int
```

### **BookDetailResponse**

Complete book information from `get_book_details`.

```python
class BookDetailResponse(BaseModel):
    book_id: int
    title: str
    authors: List[str]
    series: Optional[str] = None
    series_index: Optional[float] = None
    rating: Optional[int] = None
    tags: List[str] = []
    comments: Optional[str] = None
    published: Optional[str] = None
    languages: List[str] = []
    formats: List[str] = []
    identifiers: Dict[str, str] = {}  # ISBN, Goodreads, etc.
    last_modified: Optional[str] = None
    cover_url: Optional[str] = None
    download_links: Dict[str, str] = {}  # Format -> URL mapping
```

### **ConnectionTestResponse**

Server connection test results.

```python
class ConnectionTestResponse(BaseModel):
    connected: bool
    server_version: Optional[str] = None
    library_name: Optional[str] = None
    total_books: Optional[int] = None
    response_time_ms: int
    error_message: Optional[str] = None
    server_capabilities: List[str] = []
```

---

## 🎯 **Default Library Auto-Loading**

**IMPORTANT:** The default library is automatically loaded on server startup. Users don't need to manually load or switch libraries before querying books.

Priority order for auto-loading:
1. Persisted library (from FastMCP 2.13 storage)
2. `config.local_library_path` (if set)
3. Active library from Calibre's config files
4. First discovered library (fallback)

---

## 🔍 Calibre Server REST API

CalibreMCP communicates with Calibre's built-in REST API server.

### **Base URL Structure**

```
http://localhost:8080/ajax/...
```

### **Core Endpoints Used**

- **`GET /ajax/interface-data/init`** - Server initialization and library info
- **`GET /ajax/search`** - Library search with query parameters
- **`GET /ajax/books`** - Bulk book metadata retrieval
- **`GET /ajax/book/{id}`** - Individual book details

### **Media Endpoints**

- **`GET /get/cover/{id}`** - Book cover image
- **`GET /get/{format}/{id}`** - Download book in specific format
- **`GET /get/thumb/{id}`** - Thumbnail cover image

### **Authentication**

Supports HTTP Basic Authentication when enabled in Calibre server:

```python
# Configuration
username: "your_username"
password: "your_password"
```

---

## 📝 Query Syntax

### **Search Query Patterns**

CalibreMCP supports Calibre's native search syntax through the `query_books` tool.

#### **Field-Specific Searches**

```python
# Use query_books with operation="search"
query_books(operation="search", author="Conan Doyle")  # Author filter
query_books(operation="search", tag="science")         # Tag filter
query_books(operation="search", series="Foundation")   # Series filter
query_books(operation="search", publisher="O'Reilly")  # Publisher filter
query_books(operation="search", min_rating=4)          # Rating filter
```

#### **Boolean Operations**

Filters in `query_books` use AND logic when combined:
- `author="X"` AND `tag="Y"` AND `min_rating=4` = All conditions must match
- `tags=["X", "Y"]` = Books with tag X OR tag Y

#### **Advanced Patterns**

```python
# Date range filtering
query_books(
    operation="search",
    pubdate_start="2020-01-01",
    pubdate_end="2024-12-31"
)

# File size filtering
query_books(
    operation="search",
    min_size=1048576,  # 1 MB
    max_size=10485760  # 10 MB
)

# Format filtering
query_books(
    operation="search",
    formats=["EPUB", "PDF"]
)
```

### **Sort Options** (for `operation="list"`)

- **`title`** - Alphabetical by title
- **`authors`** - Alphabetical by author surname
- **`rating`** - Highest rated first
- **`date`** - Most recently added first
- **`pubdate`** - Most recently published first
- **`series`** - Series order

---

## ⚡ Performance Guidelines

### **Optimal Query Patterns**

- **Use specific filters** (author, tag) instead of broad text searches
- **Limit results** to 50 or fewer for responsive UI
- **Use `format_table=True`** for human-readable output
- **Cache frequent queries** on client side

### **Rate Limiting**

- **Default**: 60 requests per minute
- **Burst limit**: 10 concurrent requests
- **Timeout**: 30 seconds per request

### **Memory Considerations**

- **Cover images**: ~100KB each
- **Book metadata**: ~2KB each
- **Search results**: Cache for 5 minutes
- **Total cache**: Limited to 50MB

---

## 🚨 Error Codes

### **HTTP Status Codes**

- **200** - Success
- **401** - Authentication failed
- **404** - Calibre server not found / Book not found
- **500** - Calibre server internal error
- **timeout** - Request timeout (>30s)

### **CalibreAPIError Types**

- **`Connection failed`** - Network connectivity issue
- **`Authentication failed`** - Invalid username/password
- **`Server not found`** - Wrong URL or server not running
- **`Request timeout`** - Server overloaded or slow response
- **`JSON decode error`** - Malformed server response

### **Graceful Degradation**

All MCP tools return valid responses even on errors:
- Empty result lists for search failures
- Error dictionaries with `success: false` and actionable error messages
- Detailed suggestions for fixing issues

---

## 🔧 Development Tools

### **MCP Inspector Testing**

```bash
# Start MCP Inspector for interactive testing
python -m calibre_mcp.server
# Navigate to: http://127.0.0.1:6274
```

### **Direct API Testing**

```python
from calibre_mcp.calibre_api import quick_library_test
import asyncio

# Quick connection test
result = asyncio.run(quick_library_test("http://localhost:8080"))
print(f"Connection successful: {result}")
```

### **Configuration Testing**

```python
from calibre_mcp.config import CalibreConfig

config = CalibreConfig.load_config()
print(f"Server: {config.server_url}")
print(f"Auth configured: {config.has_auth}")
```

---

*Built with Austrian efficiency for comprehensive e-book library management. Uses FastMCP 2.13+ portmanteau tool pattern for optimal Claude Desktop integration.*
