# CalibreMCP Usage Guide for Claude

**Complete guide for using CalibreMCP tools effectively with Claude Desktop**

---

## 🎯 **Understanding Portmanteau Tools**

CalibreMCP uses **portmanteau tools** - consolidated tools that handle multiple related operations through an `operation` parameter. This reduces tool count while maintaining full functionality.

**All Portmanteau Tools (18 total):**

### Core Library Management
- **`manage_libraries`** - Library operations (list, switch, stats, search)
- **`manage_books`** - Book CRUD operations (add, get, details, update, delete)
- **`query_books`** - ALL book querying (search, list, recent, find, get, by_author, by_series)

### Content Management
- **`manage_tags`** - Tag management (list, get, create, update, delete, find_duplicates, merge, etc.)
- **`manage_authors`** - Author management (list, get, get_books, stats, by_letter)
- **`manage_comments`** - Comment CRUD operations (create, read, update, delete, append, replace)
- **`manage_metadata`** - Metadata operations (update, organize_tags, fix_issues)
- **`manage_files`** - File operations (convert, download, bulk)

### System & Analysis
- **`manage_system`** - System tools (help, status, tool_help, list_tools, hello_world, health_check)
- **`manage_analysis`** - Analysis operations (tag_statistics, duplicates, series, health, unread_priority, reading_stats)
- **`analyze_library`** - Library analysis (6 operations)

### Advanced Features
- **`manage_bulk_operations`** - Bulk operations (update_metadata, export, delete, convert)
- **`manage_content_sync`** - Content synchronization (register_device, update_device, get_device, start, status, cancel)
- **`manage_smart_collections`** - Smart collections (create, get, update, delete, list, query, plus specialized creates)

### User Management
- **`manage_users`** - User management (create_user, update_user, delete_user, list_users, get_user, login, verify_token)

### Import/Export
- **`export_books`** - Book export (csv, json, html, pandoc)

### Viewer & Specialized
- **`manage_viewer`** - Book viewer (open, get_page, get_metadata, get_state, update_state, close, open_file)
- **`manage_specialized`** - Specialized tools (japanese_organizer, it_curator, reading_recommendations)

---

## 📚 **Verb Mapping: How Claude Handles User Queries**

### **The Problem**

Users naturally use different verbs:
- "search books by X"
- "list books by X"
- "find books by X"
- "query books by X"
- "get books by X"
- "show me books by X"

### **The Solution**

**ALL these verbs map to the SAME operation:** `query_books(operation="search", ...)`

The `query_books` tool has explicit verb mapping guidance in its docstring that tells Claude:
- "search books by [author]" → `query_books(operation="search", author="...")`
- "list books by [author]" → `query_books(operation="search", author="...")`
- "find books by [author]" → `query_books(operation="search", author="...")`
- "query books by [author]" → `query_books(operation="search", author="...")`
- "get books by [author]" → `query_books(operation="search", author="...")`

**Rule:** If the user wants to access/retrieve/discover books with filters (author, tag, publisher, etc.), use `operation="search"` regardless of which verb they use.

---

## 🚀 **Quick Start: Common User Queries**

### **Example 1: "List books by Conan Doyle"**

```python
# Claude interprets: "list books by X" → query_books with operation="search"
result = await query_books(
    operation="search",
    author="Conan Doyle",
    format_table=True  # Nice table output for user
)

# Result includes:
# - result["total"]: Total number of books found
# - result["items"]: List of book dictionaries
# - result.get("table"): Optional formatted table string
```

### **Example 2: "Find books about Python published in 2023"**

```python
# Claude interprets: "find books" → query_books with operation="search"
result = await query_books(
    operation="search",
    text="python",  # Search in title, author, tags, comments
    pubdate_start="2023-01-01",
    pubdate_end="2023-12-31",
    format_table=True
)
```

### **Example 3: "Get all my mystery books by Agatha Christie"**

```python
# Claude interprets: "get books" → query_books with operation="search"
result = await query_books(
    operation="search",
    author="Agatha Christie",
    tag="mystery",
    format_table=True
)
```

### **Example 4: "Show me highly rated books added recently"**

```python
from datetime import datetime, timedelta

# Calculate dates
last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")

result = await query_books(
    operation="search",
    added_after=last_month,
    min_rating=4,
    format_table=True
)
```

---

## 📖 **Complete Workflows**

### **Workflow 1: Reading a Book**

#### User says: "I want to read A Tale of Two Cities"

```python
# Step 1: Search for the book
result = await query_books(
    operation="search",
    text="A Tale of Two Cities",
    format_table=True
)

# Step 2: Check results
if result.get("total", 0) > 0:
    book = result["items"][0]
    book_id = book["id"]
    
    # Step 3: Get full book details
    book_details = await manage_books(
        operation="get",
        book_id=str(book_id),
        include_metadata=True,
        include_formats=True
    )
    
    # Step 4: Display to user
    print(f"Found: {book_details['title']}")
    print(f"Authors: {', '.join(book_details.get('authors', []))}")
    if book_details.get('formats'):
        print(f"Available formats: {', '.join(book_details['formats'])}")
else:
    print("Book not found in library")
```

### **Workflow 2: Viewing Book Metadata**

#### User says: "Show me details for book ID 123"

```python
# Get complete book information
book = await manage_books(
    operation="get",
    book_id="123",
    include_metadata=True,
    include_formats=True,
    include_cover=False
)

# Display formatted metadata
print(f"Title: {book['title']}")
print(f"Authors: {', '.join(book.get('authors', []))}")
if book.get('rating'):
    print(f"Rating: {'⭐' * book['rating']}")
if book.get('tags'):
    print(f"Tags: {', '.join(book['tags'])}")
if book.get('comments'):
    print(f"Description: {book['comments'][:200]}...")
```

### **Workflow 3: Advanced Search**

#### User says: "Find programming books from O'Reilly published after 2020 with 4+ stars"

```python
result = await query_books(
    operation="search",
    text="programming",  # Search term
    publisher="O'Reilly Media",
    pubdate_start="2020-01-01",
    min_rating=4,
    format_table=True,
    limit=20
)

# Display results
if result.get("table"):
    print(result["table"])
else:
    print(f"Found {result.get('total', 0)} books:")
    for book in result.get("items", [])[:10]:
        print(f"  - {book['title']} by {', '.join(book.get('authors', []))}")
```

---

## 🔍 **Search Parameter Reference**

### **Author Filters**

```python
# Single author
query_books(operation="search", author="Conan Doyle")

# Multiple authors (OR logic - books by ANY of them)
query_books(operation="search", authors=["Shakespeare", "Homer"])

# Exclude authors
query_books(operation="search", author="Stephen King", exclude_authors=["Richard Bachman"])
```

### **Tag Filters**

```python
# Single tag
query_books(operation="search", tag="mystery")

# Multiple tags (OR logic - books with ANY tag)
query_books(operation="search", tags=["mystery", "crime", "thriller"])

# Exclude tags
query_books(operation="search", author="Conan Doyle", exclude_tags=["detective"])
```

### **Rating Filters**

```python
# Exact rating
query_books(operation="search", rating=5)

# Minimum rating
query_books(operation="search", min_rating=4)

# Rating range
query_books(operation="search", min_rating=3, max_rating=5)

# Unrated books only
query_books(operation="search", unrated=True)
```

### **Publisher Filters**

```python
# Single publisher
query_books(operation="search", publisher="O'Reilly Media")

# Multiple publishers
query_books(operation="search", publishers=["O'Reilly Media", "No Starch Press"])

# Has/doesn't have publisher
query_books(operation="search", has_publisher=True)
```

### **Date Filters**

```python
# Publication date range
query_books(
    operation="search",
    pubdate_start="2020-01-01",
    pubdate_end="2024-12-31"
)

# Added date range
from datetime import datetime, timedelta
last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")

query_books(
    operation="search",
    added_after=last_week,
    added_before=today
)
```

### **File Filters**

```python
# File size range (in bytes)
query_books(
    operation="search",
    min_size=1048576,   # 1 MB
    max_size=10485760   # 10 MB
)

# Format filtering
query_books(
    operation="search",
    formats=["EPUB", "PDF"]
)
```

### **Combining Filters**

All filters use AND logic when combined:

```python
# Books by Agatha Christie, tagged "mystery", rated 4+, published after 1960
result = await query_books(
    operation="search",
    author="Agatha Christie",
    tag="mystery",
    min_rating=4,
    pubdate_start="1960-01-01",
    format_table=True
)
```

---

## 🏠 **Library Management**

### **Auto-Loading Default Library**

**IMPORTANT:** The default library is automatically loaded on server startup. No manual library loading needed!

Priority order:
1. Persisted library (from FastMCP 2.13 storage)
2. `config.local_library_path` (if set)
3. Active library from Calibre's config files
4. First discovered library (fallback)

### **Switching Libraries**

```python
# List available libraries
libraries = await manage_libraries(operation="list")
print(f"Available libraries: {[lib['name'] for lib in libraries['libraries']]}")

# Switch to a different library
result = await manage_libraries(
    operation="switch",
    library_name="Main Library"
)

if result["success"]:
    print(f"Switched to: {result['library_name']}")
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
```

### **Cross-Library Search**

```python
# Search across multiple libraries
result = await manage_libraries(
    operation="search",
    query="python programming",
    libraries=["Main Library", "IT Library"]
)

for book in result["results"]:
    print(f"{book['title']} (in {book['library_name']})")
```

---

## ⚠️ **Common Patterns & Pitfalls**

### **✅ DO: Use operation="search" for filtered queries**

```python
# User says: "list books by conan doyle"
# ✅ CORRECT
result = await query_books(operation="search", author="Conan Doyle")

# ❌ WRONG
result = await query_books(operation="list", author="Conan Doyle")  # 'list' doesn't support author filter
```

### **✅ DO: Use format_table=True for user-friendly output**

```python
# ✅ Good for displaying to users
result = await query_books(
    operation="search",
    author="Conan Doyle",
    format_table=True
)
print(result.get("table", "No results"))
```

### **✅ DO: Use operation="list" only for ALL books**

```python
# ✅ Correct use of "list" operation
result = await query_books(operation="list", limit=50)  # Get 50 books, no filters

# ❌ Wrong - use "search" instead
result = await query_books(operation="list", author="X")  # 'list' doesn't support filters
```

### **✅ DO: Handle pagination**

```python
# First page
result1 = await query_books(operation="search", author="Conan Doyle", limit=50, offset=0)

# Next page
result2 = await query_books(operation="search", author="Conan Doyle", limit=50, offset=50)

total = result1.get("total", 0)
if total > 50:
    print(f"Showing page 1 of {total // 50 + 1}")
```

### **❌ DON'T: Use by_author or by_series with names**

```python
# ❌ WRONG - by_author requires numeric ID
result = await query_books(operation="by_author", author="Conan Doyle")  # Will fail

# ✅ CORRECT - use search operation with author name
result = await query_books(operation="search", author="Conan Doyle")

# ✅ CORRECT - use by_author only when you have numeric ID
result = await query_books(operation="by_author", author_id=42)
```

---

## 🎨 **Best Practices**

1. **Always use `operation="search"` for user queries with filters**
   - Works with ANY verb: search, list, find, query, get, show me
   - Supports all filter types: author, tag, publisher, year, rating, etc.

2. **Use `format_table=True` for displaying results to users**
   - Creates human-readable table format
   - Includes book titles, authors, ratings, descriptions

3. **Limit results for better UX**
   - Default limit is 50 (good for most cases)
   - Use pagination (offset parameter) for large result sets

4. **Combine filters for precise searches**
   - All filters use AND logic
   - More specific = better results

5. **Handle errors gracefully**
   - Check `result.get("success")` for portmanteau tools
   - Provide actionable error messages to users

---

## 📚 **Additional Resources**

- **API Reference**: See [API.md](API.md) for complete tool documentation
- **Tool Docstrings**: All tools have comprehensive inline documentation
- **Verb Mapping**: See `query_books` docstring for complete verb mapping guide

---

*This guide helps Claude successfully use CalibreMCP tools on the first try. All tools include comprehensive docstrings with examples, error handling, and verb mapping guidance.*
