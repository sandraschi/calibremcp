# CalibreMCP API Reference

**Comprehensive reference for all MCP tools and endpoints**

---

## 🔧 MCP Tools

CalibreMCP provides 4 FastMCP 2.0 tools for comprehensive Calibre library management through Claude Desktop.

### **Tool 1: `list_books`**

Browse/search library with flexible filtering and sorting.

#### **Signature**

```python
async def list_books(
    query: Optional[str] = None,
    limit: int = 50,
    sort: str = "title"
) -> LibrarySearchResponse
```

#### **Parameters**

- **`query`** (optional): Search query (title, author, tags, series)
- **`limit`** (int): Maximum results to return (1-200, default 50)
- **`sort`** (str): Sort order - title, author, rating, date, series

#### **Returns**

`LibrarySearchResponse` with:

- **`results`**: List of `BookSearchResult` objects
- **`total_found`**: Total books matching criteria
- **`query_used`**: Search query that was executed
- **`search_time_ms`**: Time taken for search in milliseconds

#### **Usage Examples**

```python
# Browse recent books
await list_books(sort="date", limit=20)

# Search for programming books  
await list_books("programming python", limit=30, sort="rating")

# List all books (no query)
await list_books(limit=100)
```

#### **Error Handling**

- Returns empty results on connection failure
- Validates limit to 1-200 range
- Graceful degradation on search errors

---

### **Tool 2: `get_book_details`**

Get complete metadata and file information for a specific book.

#### **Signature**

```python
async def get_book_details(book_id: int) -> BookDetailResponse
```

#### **Parameters**

- **`book_id`** (int): Calibre book ID to fetch details for

#### **Returns**

`BookDetailResponse` with complete book information:

- **Basic metadata**: title, authors, series, rating, tags
- **Publication info**: published date, languages, comments
- **File information**: available formats, download links
- **System data**: identifiers, last modified, cover URL

#### **Usage Examples**

```python
# Get complete book information
await get_book_details(12345)

# Check available formats
details = await get_book_details(123)
if "EPUB" in details.formats:
    print(f"EPUB available: {details.download_links['EPUB']}")
```

#### **Error Handling**

- Returns "Book not found" for invalid IDs
- Graceful handling of missing metadata fields
- Comprehensive error messages in title field

---

### **Tool 3: `search_books`**

Advanced search with field targeting and boolean operations.

#### **Signature**

```python
async def search_books(
    text: str,
    fields: Optional[List[str]] = None,
    operator: str = "AND"
) -> LibrarySearchResponse
```

#### **Parameters**

- **`text`** (str): Search text to look for
- **`fields`** (optional): List of fields to search in
  - Available: `["title", "authors", "tags", "series", "comments"]`
  - Default: `["title", "authors", "tags", "comments"]`
- **`operator`** (str): Boolean operator - "AND" or "OR"

#### **Returns**

`LibrarySearchResponse` with filtered results and relevance scoring.

#### **Usage Examples**

```python
# Search titles and tags with OR logic
await search_books("artificial intelligence", ["title", "tags"], "OR")

# Search all fields with AND logic (default)
await search_books("python programming")

# Search only in series names
await search_books("Foundation", ["series"])
```

#### **Search Logic**

- **AND**: All fields must contain the text
- **OR**: Any field can contain the text
- **Field targeting**: Limits search to specific metadata fields
- **Relevance scoring**: Results ordered by match quality

---

### **Tool 4: `test_calibre_connection`**

Test connection to Calibre server and get diagnostics.

#### **Signature**

```python
async def test_calibre_connection() -> ConnectionTestResponse
```

#### **Parameters**

None

#### **Returns**

`ConnectionTestResponse` with:

- **`connected`**: Boolean connection status
- **`server_version`**: Calibre server version
- **`library_name`**: Primary library name
- **`total_books`**: Number of books in library
- **`response_time_ms`**: Connection response time
- **`error_message`**: Error details if connection failed
- **`server_capabilities`**: List of supported features

#### **Usage Examples**

```python
# Test connection and get server info
result = await test_calibre_connection()
if result.connected:
    print(f"Connected to {result.library_name} with {result.total_books} books")
else:
    print(f"Connection failed: {result.error_message}")
```

#### **Diagnostic Information**

- Server version and capabilities
- Library statistics and accessibility
- Performance metrics
- Detailed error messages for troubleshooting

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

Response from `list_books` and `search_books` operations.

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

CalibreMCP supports Calibre's native search syntax:

#### **Field-Specific Searches**

```
title:python          # Search in title field
authors:asimov        # Search in authors field
tag:science           # Search in tags field
series:"Foundation"   # Exact phrase matching
rating:>=4            # Numeric comparisons
formats:epub          # Filter by available formats
```

#### **Boolean Operations**

```
python AND programming        # Both terms required
fiction OR fantasy           # Either term acceptable
programming NOT beginner     # Exclude term
```

#### **Advanced Patterns**

```
date:>2020-01-01             # Published after date
size:>10MB                   # File size filtering
language:eng                 # Language filtering
```

### **Sort Options**

- **`title`** - Alphabetical by title
- **`authors`** - Alphabetical by author surname
- **`rating`** - Highest rated first
- **`date`** - Most recently added first
- **`pubdate`** - Most recently published first
- **`series`** - Series order
- **`size`** - Largest files first

---

## ⚡ Performance Guidelines

### **Optimal Query Patterns**

- **Field-specific searches** perform faster than full-text
- **Limit results** to 50 or fewer for responsive UI
- **Use specific tags** instead of broad content searches
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
- "Error: ..." titles for book detail failures
- `connected: false` for connection test failures

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

*Built with Austrian efficiency for Sandra's comprehensive e-book workflow.*
