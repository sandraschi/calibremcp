# CalibreMCP - Product Requirements Document

## Overview
CalibreMCP is a FastMCP 2.0 server that provides comprehensive e-book library management capabilities through Claude Desktop. This document outlines the requirements for the AI-powered tools and series management features.

## 1. Advanced Search Functionality

### 1.1 Core Search Capabilities
- **Purpose**: Provide powerful and flexible search across the entire library
- **Features**:
  - Full-text search across titles, authors, series, tags, and comments
  - Case-insensitive and partial matching
  - Support for special characters and Unicode
  - Configurable result limits and pagination

### 1.2 Filtering Options
- **Date Ranges**:
  - Publication date (pubdate)
  - Date added to library (timestamp)
- **File Properties**:
  - File size ranges (min/max)
  - File formats (EPUB, PDF, MOBI, etc.)
- **Content Metadata**:
  - Empty/non-empty comments
  - Star ratings (exact, minimum, unrated)
  - Publisher filtering (single or multiple)
  - Series information
  - Tag filtering

### 1.3 Search Performance
- Optimized database queries for fast response times
- Indexing of frequently searched fields
- Caching of common search results
- Support for large libraries (100,000+ books)

### 1.4 Full-text search (Calibre FTS) and phrase locations
- **Calibre index:** `full-text-search.db` (FTS5) beside `metadata.db`; content table `books_text` joined to `books_fts` on `books_text.id = books_fts.rowid` (virtual table has no `book` column — see `utils/fts_utils.py`).
- **Tool:** `search_fulltext` — phrase/word search in book body; optional **`resolve_locations=True`** returns character offsets in indexed text, PDF page (PyMuPDF), EPUB spine href, and Calibre **`ebook-viewer --open-at search:…`** hints for jumping to a quote (e.g. stage directions).
- **Complement semantic RAG:** use Calibre FTS / `search_fulltext` for exact phrases; use metadata RAG (`calibre_metadata_search`) or chunk RAG (`rag_retrieve`) for meaning-based queries. Prefer **both** when the user query mixes quote-finding and conceptual discovery.

## 2. AI-Powered Tools

### 1.1 Book Recommendation Engine
- **Purpose**: Provide personalized book recommendations
- **Features**:
  - Content-based filtering using TF-IDF vectorization
  - Cosine similarity for finding similar books
  - Support for user preferences (authors, genres, publishers)
  - Training on library data

### 1.2 Content Analysis
- **Purpose**: Extract insights from book content
- **Features**:
  - Named Entity Recognition (NER) using spaCy
  - Sentiment analysis
  - Theme extraction
  - Reading level assessment
  - Caching of analysis results

### 1.3 Reading Habit Analysis
- **Purpose**: Provide insights into reading patterns
- **Features**:
  - Reading session statistics
  - Preferred reading times
  - Reading speed analysis
  - Genre preferences over time
  - Completion rate tracking

## 2. Series Management

### 2.1 Series Analysis
- **Purpose**: Identify and fix issues in book series
- **Features**:
  - Detect missing books in series
  - Identify inconsistent naming
  - Find duplicate series
  - Generate series reports

### 2.2 Metadata Validation
- **Purpose**: Ensure consistency across the library
- **Features**:
  - Validate series indices
  - Check for missing metadata
  - Standardize naming conventions
  - Detect and merge duplicate entries

### 2.3 Series Merging
- **Purpose**: Combine related series
- **Features**:
  - Merge duplicate series
  - Preserve reading order
  - Handle conflicts
  - Dry-run mode

## 3. Search API Specification

### 3.1 Search Parameters
```typescript
interface SearchParams {
  // Basic search
  query?: string;           // Search term (title, author, series, tags, comments)
  
  // Date filters
  pubdate_start?: string;   // YYYY-MM-DD
  pubdate_end?: string;     // YYYY-MM-DD
  added_after?: string;     // YYYY-MM-DD
  added_before?: string;    // YYYY-MM-DD
  
  // Content filters
  has_empty_comments?: boolean;  // True for empty, False for non-empty
  rating?: number;         // Exact rating (1-5)
  min_rating?: number;     // Minimum rating (1-5)
  unrated?: boolean;       // True for unrated books only
  
  // Publisher filters
  publisher?: string;      // Single publisher (partial match)
  publishers?: string[];   // Multiple publishers (OR condition)
  has_publisher?: boolean; // True/False for has publisher
  
  // File properties
  min_size?: number;       // Minimum file size in bytes
  max_size?: number;       // Maximum file size in bytes
  formats?: string[];      // File formats to include
  
  // Pagination
  limit?: number;          // Results per page (default: 50, max: 1000)
  offset?: number;         // Pagination offset (default: 0)
}
```

### 3.2 Response Format
```typescript
interface SearchResponse {
  items: Book[];           // Array of matching books
  total: number;           // Total number of matches
  page: number;            // Current page number
  per_page: number;        // Number of items per page
  total_pages: number;     // Total number of pages
}
```

## 4. Technical Requirements

### 4.1 Dependencies
- Python 3.11+
- spaCy with English model
- scikit-learn
- numpy
- pydantic
- fastmcp>=2.0

### 4.2 Performance
- Sub-second response times for typical searches
- Support for libraries with 100,000+ books
- Asynchronous processing for long-running operations
- Caching of search results and analysis
- Background processing for resource-intensive tasks
- Database indexing for frequently filtered fields

### 3.3 Security
- Input validation
- Proper error handling
- No sensitive data exposure in logs
- Safe file operations

## 4. User Interface

### 4.1 Claude Desktop Integration
- Tool registration
- Parameter validation
- Clear error messages
- Progress reporting

### 4.2 Command Line Interface
- Scriptable operations
- Progress indicators
- Configurable output formats (JSON, YAML, CSV)
- Logging options

## 5. Testing Requirements

### 5.1 Unit Tests
- Core functionality
- Edge cases
- Error conditions

### 5.2 Integration Tests
- End-to-end workflows
- Library operations
- Performance testing

### 5.3 Test Data
- Sample libraries
- Edge cases
- Performance test sets

## 6. Documentation

### 6.1 User Guide
- Installation
- Configuration
- Usage examples
- Troubleshooting

### 6.2 API Documentation
- Tool signatures
- Parameter descriptions
- Return values
- Error codes

### 6.3 Developer Guide
- Architecture
- Extending functionality
- Contributing guidelines

### 6.4 Webapp Startup Compliance (mcp-central-docs)
- **Port Reservoir**: Backend 10720, Frontend 10721 (reserved 10700-10800)
- **Zombie Kill**: start.ps1 uses kill-port before bind; PowerShell fallback for netstat
- **SSR Env**: `NEXT_PUBLIC_APP_URL` must match frontend port so getBaseUrl() hits self
- **Docs**: webapp/SETUP.md, webapp/README.md

## 7. Future Enhancements

### 7.1 Advanced AI Features
- Personalized reading recommendations
- Automatic genre classification
- Series detection
- Duplicate detection

### 7.2 Integration
- Goodreads integration
- Export/import functionality
- Cloud storage support
- Mobile app

## 8. Success Metrics
- Reduced time spent on library management
- Increased metadata accuracy
- Improved book discovery
- User satisfaction scores

## 9. Changelog

### v1.0.0 - Initial Release
- Basic library access
- Core metadata management
- Format conversion

### v1.1.0 - AI Tools
- Book recommendations
- Content analysis
- Reading habit insights

### v1.2.0 - Series Management
- Series analysis
- Metadata validation
- Series merging

### v1.3.0 - Neural Media RAG & FastMCP 3.1 Readiness
- DeepIngestor full-text embedding
- FastMCP 3.1 agentic workflows and tool loading fixes
- Enhanced 3-column webapp book modal and SOTA UI refinements

## 10. MCP Apps (Prefab) — rich cards (2026)

- **Purpose:** Optional Prefab tools for capable MCP hosts (e.g. Claude Desktop): **`show_book_prefab_card(book_id)`** — **title, authors, series, tags, cover, plain synopsis**; **`show_libraries_prefab_card()`** — **Our Calibre** overview (all discovered libraries, book counts, size, active flag, paths).
- **Install:** **`uv sync --extra apps`** (pulls **`prefab-ui`**). **`CALIBRE_PREFAB_APPS=0`** disables tool registration.
- **Implementation:** FastMCP **`@mcp.tool(app=True)`**, **`ToolResult`** + **`PrefabApp`**; Calibre **comments** may contain HTML — strip for display; **one `Text` node per line/paragraph** where layout matters.
- **Fallback:** Hosts without App rendering receive **`content`** text; server must not require Prefab for core library operations.
- **Documentation:** `docs/mcp-technical/MCP_APPS_PREFAB.md`; fleet standard [mcp-apps-prefab-ui.md](https://github.com/sandraschi/mcp-central-docs/blob/master/fastmcp/mcp-apps-prefab-ui.md) (MCP Central Docs).

## 11. License
MIT License
