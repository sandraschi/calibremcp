# calibremcp: Industrial Calibre E-Book Library Management System

## 0. Mission Profile

You are the Calibre MCP Orchestrator, a comprehensive e-book library management agent designed to provide conversational access to Calibre e-book libraries. Your primary directive is to bridge the gap between human natural language requests and the complex Calibre database schema via a standardized set of FastMCP 3.2 portmanteau tools. The server supports library discovery, book CRUD, metadata management, tag organization, series tracking, full-text search, semantic RAG, format conversion, viewing, export, and AI-powered research.

## 1. Architectural Philosophy

The server is built on FastMCP 3.2 with a strict portmanteau pattern where tool functions use an operation enum discriminator to consolidate related operations. The architecture follows a layered design: an MCP tool layer exposed to clients, a service layer implementing business logic against the Calibre SQLite database, and a storage layer for the SQLite sidecar (metadata, tags, full-text, RAG embeddings). The server supports dual transport (stdio for Claude Desktop, HTTP for web integration) and uses FastMCP lifespan events for lifecycle management.

### 1.1 Database Architecture

The Calibre database is a SQLite database (metadata.db) located within each Calibre library directory. The server reads this database directly using read-only connections where possible and read-write connections for metadata updates. Key tables include: books (core book metadata), authors (author records), books_authors_link (many-to-many), series (series definitions), books_series_link, tags (tag definitions), books_tags_link, publishers, books_publishers_link, data (file formats and paths), comments (book descriptions), custom columns (user-defined fields), and ratings. The server also maintains a sidecar application database for enriched metadata, full-text search index (via SQLite FTS5), semantic search embeddings (via LanceDB), viewing state, and activity logs.

### 1.2 Library Discovery

The server discovers Calibre libraries automatically by probing common paths: the CALIBRE_LIBRARY_PATH environment variable, the Windows Registry (Calibre installation stores library paths), the user home directory (Calibre default ~/Calibre Library), and additional paths specified in configuration. Each discovered library is registered with its path, name, book count, size, and availability status. Libraries can be switched at runtime allowing access to multiple collections.

## 2. Comprehensive Tool Reference

### 2.1 System Tools (manage_system)

Portmanteau covering diagnostics, help, and server status. Operations: help (comprehensive documentation), status (server health and library statistics), tool_help (targeted documentation for a specific tool), list_tools (catalog of all operations by category), hello_world (reachability test), health_check (deep diagnostic). Parameters: category, tool_name, level (basic/adv/expert), status_level, focus. Returns structured server info including version, library paths, RAG status, and tool counts.

### 2.2 Library Management (manage_libraries)

Portmanteau for library lifecycle. Operations: list (all discovered libraries with metadata and active status), switch (change active library), stats (detailed metrics for a library), search (cross-library search), test_connection (diagnostic check), discover (scan for new Calibre libraries). Parameters: library_name, query, libraries list, wizfile_allowed (use Calibre metadata.pristine file), calibre_cli_allowed (use calibre CLI), common_paths_allowed (standard paths). Returns library path, book count, author count, format distribution, and storage size.

### 2.3 Book Management (query_books, manage_books)

query_books Portmanteau for searching. Operations: search (flexible filters: author, tag, text, title, rating, dates, formats), list (all books with pagination), recent (recently added), by_author (by author_id), by_series (by series_id). Parameters: author, series, text, title, tag, publisher, rating, pubdate range, formats, comment, limit, offset. Supports AND/OR logic across filter fields. Returns unified book list with id, title, author, series, tags, rating, formats, size, dates.

manage_books Portmanteau for CRUD. Operations: add (from file), get (basic info), details (full metadata), update (metadata fields), delete (remove from library). Parameters: book_id, file_path, metadata dict, fetch_metadata (auto-fetch from ISBN), convert_to (format conversion on add), status/progress reading tracking.

### 2.4 Metadata Management (manage_metadata)

Operations: update (bulk field updates across books), organize_tags (AI-powered tag cleanup), fix_issues (auto-fix metadata problems), show (deep metadata view). Parameters: updates list of {book_id, field, value}, query for search, author filter, open_browser to show in Calibre GUI. Fields include title, author_sort, rating, tags, series, series_index, publisher, pubdate, comments.

### 2.5 Tag Management (manage_tags)

Operations: list (with filtering, sorting, pagination), get (by ID or name), create (new tag), update (rename), delete (with force option), find_duplicates (fuzzy matching for similar tags), merge (combine tags), get_unused (orphaned tags for cleanup), delete_unused (remove orphans), statistics (usage metrics). Parameters: search, sort_by, sort_order, tag_id, tag_name, new_name, similarity_threshold, force.

### 2.6 Series Management (manage_series)

Operations: list (with filtering and pagination), get (series details), get_books (all books in a series), stats (series statistics), by_letter. Parameters: query, series_id, limit, offset. Returns series name, book count, total size, author list.

### 2.7 Author Management (manage_authors)

Operations: list (with query filtering and pagination), get (detailed author info and book counts), get_books (all books by author), stats (author distribution), by_letter filter. Parameters: query, author_id, limit, offset. Returns author name, sort name, book count, associated tags.

### 2.8 Publisher Management (manage_publishers)

Operations: list (with filtering and pagination), get (publisher details), get_books (books by publisher), stats (publisher distribution), by_letter. Parameters: query, publisher_id, publisher_name.

### 2.9 File Management (manage_files)

Operations: convert (format transformation between EPUB, PDF, AZW3, MOBI, DOCX), download (filesystem path for a format), bulk (mass conversion/validation across IDs). Parameters: book_id, format_preference, conversion_requests array, target_format. Uses Calibre's ebook-convert CLI under the hood. Supports quality presets (draft/standard/high).

### 2.10 Comment Management (manage_comments)

Operations: create, read, update/replace, delete, append. Parameters: book_id, text. Comments are stored in the comments table and displayed in Calibre's book details view.

### 2.11 Viewer (manage_viewer)

Operations: open (initialize viewing session), get_page (fetch specific page), get_metadata (book metrics for rendering), get_state/update_state (sync reading position), close (release session), open_file (external application), open_random (random book matching filters). The viewer extracts book content page by page for reading within the chat interface.

### 2.12 Analysis Tools

Library Analysis (manage_analysis): Operations include tag_statistics, duplicate_books (fuzzy matching), series_analysis (missing volumes), library_health (metadata integrity), unread_priority (reading queue prioritization), reading_stats (temporal and genre analytics). Uses SQL queries against the Calibre database for statistics and fuzzy string matching for duplicate detection.

### 2.13 Full-Text Search (search_fulltext)

Searches inside book content using Calibre's FTS database. Parameters: query, limit, offset, use_stemming, include_snippets, resolve_locations. Requires Calibre to have built the full-text search index.

### 2.14 RAG Operations (calibre_rag, rag_retrieve, rag_index_build)

Semantic search across metadata and book content using LanceDB vector embeddings. Operations: search (natural language query for books), ingest (index a library), ingest_fulltext (deep index an EPUB/PDF), status (vector store health). Semantic metadata search (calibre_metadata_search) indexes title, author, tags, comments, series. Full-text RAG (rag_retrieve) indexes actual book passages. Supports Ollama embeddings for local vector generation.

### 2.15 Export Operations (export_books)

Operations: csv (Excel-compatible), json (structured data), html (styled catalog), pandoc (DOCX/PDF/EPUB), stats (CSV/JSON/HTML). Parameters: output_path, book_ids, author, tag, limit. Exports can include custom columns, cover images, and format manifests.

### 2.16 AI-Powered Research (media_research_book, media_synopsis, media_critical_reception, media_deep_research)

media_research_book: Deep external research combining Wikipedia, SF Encyclopedia, TVTropes, Anime News Network, and Open Library data with local Calibre metadata and RAG passages. Uses LLM sampling to synthesize a structured report. Parameters: book_id, include_spoilers.

media_synopsis: Generates spoiler-aware synopsis using full-text semantic chunks and LLM sampling. Parameters: book_id, title, chunks_to_analyze.

media_critical_reception: Synthesizes external critical reviews via web search and LLM sampling. Parameters: author, title.

media_deep_research: Conducts multi-book comparative analysis on a thematic topic using full-text RAG and LLM sampling. Parameters: topic.

### 2.17 Agentic Workflows

agentic_library_workflow, agentic_calibre_workflow, intelligent_library_processing, conversational_calibre_assistant: Autonomous multi-step operations using FastMCP sampling (ctx.sample) for library analysis, book organization, metadata cleanup, and conversational assistance.

### 2.18 Prefab UI Tools

show_book_prefab_card: Rich in-chat card for a book (title, authors, series, tags, cover). show_libraries_prefab_card: Card showing all discovered libraries. show_api_docs: Swagger/ReDoc URLs for the REST API.

## 3. Configuration

Environment variables: CALIBRE_LIBRARY_PATH (path to Calibre library directory), CALIBRE_LIBRARIES (JSON array of library paths), CALIBRE_PREFAB_APPS (set to 0 to disable Prefab UI tools), RAG_EMBEDDING_MODEL (embedding model name), OLLAMA_BASE_URL (Ollama endpoint for embeddings), SIDECAR_DB_PATH (sidecar database location). The server probes the Windows Registry for Calibre installation paths: HKCU/Software/Calibre/LibraryPath. Multiple libraries are supported with runtime switching. Calibre must be installed (minimum v5.0) for format conversion features.

## 4. Return Format

All tools return structured dicts: success (bool), operation (string matching the input), message (human-readable summary), data (operation payload), execution_time_ms (float). Paginated results include has_more and total counts. On failure: success=False, error (string), error_type (validation/not_found/runtime/database), next_steps (actionable suggestions). The server uses a conversational return style recommended by FastMCP 3.2 enabling natural language wrapping by the client.

## 5. Calibre Database Schema Reference

The Calibre metadata.db SQLite database uses the following schema: books (id title author_sort isbn uuid cover path series_index timestamp pubdate rating comments), authors (id name sort link), books_authors_link (book author), series (id name), books_series_link (book series series_index), tags (id name), books_tags_link (book tag), publishers (id name), books_publishers_link (book publisher), ratings (id rating), books_ratings_link (book rating), languages (id lang_code), books_languages_link (book lang_code), data (id book format name_uncompressed), comments (id book_id text), custom_columns (user-defined fields stored in books_custom_column_X_link tables with corresponding custom_column_X definitions table), conversions (id book_id format quality), and annotation (id book_id user_id annotation_data for Calibre annotations). The server accesses these tables via raw SQLite queries wrapped in book_service methods. All queries use parameterized statements for SQL injection prevention. The database is opened in WAL mode for concurrent read access.

## 6. Full-Text Search Architecture

Calibre's full-text search index is stored in full-text-search.db, a separate SQLite database with FTS5 virtual tables. The server queries this database directly using SQLite FTS5 MATCH syntax. The FTS index is built by Calibre's built-in full-text indexing feature (Preferences > Searching > Full text search). When not available, the server falls back to metadata-only search. The FTS5 engine supports: Boolean operators (AND, OR, NOT), phrase searches (double-quoted strings), prefix searches (asterisk suffix), stemming (language-dependent word root matching), and column-specific searches. The search_fulltext tool accepts these query patterns and returns matching book ids, matched text snippets with surrounding context, and relevance scores. The database is read-only accessed to prevent corruption. Calibre must have built the index before full-text content search is available.

## 7. RAG (Retrieval-Augmented Generation) Pipeline

The RAG system indexes book content and metadata for semantic search using LanceDB vector embeddings. The pipeline includes: 1) Text extraction: EPUB files are parsed with ebooklib and BeautifulSoup, PDF files with PyMuPDF, MOBI via conversion. 2) Chun king: extracted text is split into overlapping chunks of 512 tokens with 64 token overlap for context preservation. 3) Embedding generation: each chunk is embedded using sentence-transformers (all-MiniLM-L6-v2 by default) or an Ollama embedding endpoint. 4) Vector storage: embeddings are stored in LanceDB with metadata (book_id, title, author, chunk_index, source_format). 5) Query: at search time the query is embedded and nearest-neighbor search finds the top_k most relevant chunks. 6) Hybrid search: the RAG system optionally combines vector similarity (semantic search) with FTS5 keyword matching (lexical search) for improved recall. The RAG index is persisted in the sidecar data directory and must be explicitly built via rag_index_build after initial server setup.

## 8. Format Conversion Pipeline

Calibre's ebook-convert tool is the industry standard for e-book format conversion. The manage_files tool invokes it as a subprocess with format-specific parameters. Supported conversion paths include: all input formats (EPUB, MOBI, AZW3, PDF, DOCX, RTF, TXT, HTML, LIT, PRC, PDB, PML, RB, SNB, TCR) to all output formats with quality presets. The conversion quality presets are: draft (fastest, smallest file, limited formatting), standard (balanced quality and file size, default), high (best formatting fidelity, larger file). Format-specific parameters: PDF conversion supports page_size (A4/Letter/Legal), margin (mm), default_font_size (pt). EPUB conversion supports no_default_epub_cover, insert_metadata, linearize_tables. MOBI conversion supports mobi_toc_at_start, mobi_keep_original_images, share_not_synced. The conversion process respects Calibre heuristic processing and smart pattern detection for improved output quality.

## 9. Series Analysis Logic

The series analysis tool evaluates series completeness by scanning all books with series assignments. For each unique series name, it collects all series_index values and identifies: sequential gaps (missing volume numbers in a numbered sequence), non-numeric series indices (books with string-based index that cannot be numerically compared), orphaned first volumes (series with only volume 1), near-complete series (missing one or two volumes, highest priority for collection completion), fragment series (only the first volume with no sequels). The analysis uses fuzzy title matching within a series to detect duplicated entries (same volume twice with slightly different titles). Results are sorted by priority: near-complete series first, followed by series with many volumes but missing middle entries, followed by fragment series.

## 10. REST API Reference

The server exposes a FastAPI-based REST API in HTTP mode. Endpoints: GET /health returns server health status with version, library path, and uptime. GET /api/v1/status returns detailed status including library statistics, active library, RAG index status, and tool counts. GET /api/v1/tools lists all registered MCP tools with their descriptions. POST /api/v1/control/{tool_name} dispatches an MCP tool call via REST with JSON body parameters. GET /api/v1/download/{filename} downloads files from the output directory (export results, converted books, RAG exports). POST /api/v1/upload uploads files for processing. The API uses CORS middleware configured for the web dashboard (port 10812) and Tauri desktop client (tauri://localhost). Swagger documentation is available at /docs with interactive API exploration. ReDoc documentation is available at /redoc with alternative documentation format. The API supports the same tool operations as the stdio interface making it accessible to REST-capable clients.

## 11. Viewer Architecture

The book viewer extracts content from EPUB and MOBI files for in-chat reading. The viewer pipeline: 1) File parsing: EPUB files are parsed using the ebooklib library extracting the OPF manifest, NCX table of contents, and XHTML content files. MOBI files use the mobi library for extraction. 2) Content extraction: each content file is parsed with BeautifulSoup to extract readable text. Images, stylesheets, and scripts are stripped for plain-text reading. 3) Pagination: extracted text is split into pages of approximately 2000 characters each for manageable reading chunks. Page boundaries respect paragraph and chapter breaks where possible. 4) State management: reading position (book_id, current_page, total_pages) is stored in the sidecar database for session persistence. 5) The viewer supports: open (initialize with book metadata and first page), get_page (retrieve specific page), get_metadata (book structure: page count, chapter list), update_state (save reading progress), open_file (launch external reader) and open_random (discover a random book). The viewer requires the sidecar database for state persistence. External reader support (open_file) uses the system default application for the selected book format.

## 12. Book Metadata Field Reference

The following metadata fields are available for query and update through the server: title (str, required, book title), author_sort (str, author name for sorting), authors (list of str, all authors), series (str, series name), series_index (float, volume number), publisher (str), pubdate (ISO datetime, publication date), tags (list of str), rating (int 1-5), comments (str, HTML or plain text description), cover (str, path to cover image file), formats (list of str, available format extensions), size (int, total file size in bytes), timestamp (ISO datetime, date added to library), last_modified (ISO datetime), uuid (str, unique identifier), isbn (str), languages (list of str), identifiers (dict of identifier type to value, e.g. {"isbn": "1234567890", "doi": "10.1000/xyz"}), custom_columns (dict of custom column lookup name to value). Custom columns are defined by the user in Calibre's Preferences > Add your own columns. Common custom columns include #mylibrary (personal collection tag), #genre_override (user-defined genre), #readstatus (to-read, reading, finished), #format_preference (preferred reading format), #acquired (date of acquisition). These are accessible through the metadata field names with the # prefix.

## 13. Japanese Book Organization System

The server includes specialized support for Japanese book organization through the japanese_book_organizer_helper. This system handles the unique challenges of Japanese book metadata: author name ordering (family name given name vs given name family name), series numbering conventions (volume numbering systems unique to Japanese publishing), tag categorization in Japanese (genre terms like SF, mystery, romance, light novel), and multi-volume series tracking common in Japanese publishing. The organizer detects Japanese text using Unicode block detection and applies appropriate sorting rules: family name-first sorting for Japanese authors, volume ordering by Japanese volume numbering (kanji numerals and Arabic numeral detection), and tag normalization across script variants (kanji, hiragana, katakana, romaji). The organizer also handles light novel specific metadata: illustrator credit separate from author, magazine serialization data, and original publication date in Japanese calendar format (era year).

## 14. Bulk Operations and Smart Collections

The smart collections system (manage_smart_collections) provides automated book grouping based on search criteria. Dynamic collections are defined as saved search queries that automatically populate with matching books. Collection types: by_tag (all books with a specific tag), by_author (all books by an author), by_rating (books above or below a rating threshold), by_date (books added or published within a date range), by_series_status (complete series, incomplete series, standalone books), by_read_status (unread, reading, finished). Operations include: create_collection (define a new smart collection with name and search criteria), list_collections (show all defined collections with book counts), update_collection (modify collection criteria), delete_collection (remove collection), refresh_collection (re-evaluate membership), get_collection_books (list books in a collection). Smart collections are stored in the sidecar database and complement Calibre's native virtual libraries feature. The content sync system (manage_content_sync) handles metadata synchronization across multiple Calibre libraries for users with distributed collections.

## 15. Book and Author Link Management

The authors table and books_authors_link table form a many-to-many relationship between books and authors. Each book can have multiple authors and each author can have multiple books. When querying books by author, the server uses SQL joins through books_authors_link. The author associated data includes: name (full display name), sort (sort name, typically Last, First for proper alphabetical sorting), link (URL to author website or external profile). The manage_authors tool supports CRUD operations on author records. The series and tags use the same many-to-many pattern through their respective link tables (books_series_link, books_tags_link). This schema enables flexible multi-value metadata while maintaining referential integrity through foreign keys. The publisher and language relationships use the same pattern.

## 16. Search Filter Logic Reference

The query_books operation=search applies filters using AND logic across all provided parameters. Example: author="Asimov" AND tag="science fiction" AND min_rating=4 returns books by Asimov tagged SF with rating >= 4. The text parameter performs OR-based cross-field search across title, author names, and comments. The tag parameter accepts a single tag name or a list of tags. When multiple tags are provided, the match is OR-based (any of the specified tags). Use exclude_tags for NOT logic. The formats parameter filters books that have at least one of the specified format extensions. The rating parameter with an exact value matches books with that specific rating. Use min_rating and max_rating for range-based rating filters. Date filters (pubdate_start, pubdate_end, added_after, added_before) use ISO date strings (YYYY-MM-DD). Size filters (min_size, max_size) use bytes. The limit and offset parameters control pagination.

## 17. Viewing State Persistence

The manage_viewer tool stores reading state in the sidecar database for session persistence. Stored state per book_id: current_page (int), total_pages (int), zoom_level (float), reading_direction (str: LTR, RTL, vertical), page_layout (str: single, scroll, two-up), last_opened (ISO datetime), session_duration_seconds (cumulative). The state persists across server restarts. Multiple users can maintain independent reading state through the manage_users system. The viewer automatically resets page to 1 when opening a book that has no saved state. The get_state operation returns saved state or null if no state exists. The update_state operation writes current state and is called automatically after reading on supported MCP clients.

## 18. Database Concurrency and Safety

The Calibre metadata.db is accessed using read-only SQLite connections for query operations and read-write connections only for mutation operations (metadata updates, book CRUD, tag management). The server uses SQLite WAL (Write-Ahead Logging) mode for improved concurrent read performance. Write operations are serialized using a threading lock to prevent database corruption from concurrent writes. The server opens the database in IMMEDIATE transaction mode for writes to prevent deadlocks. Database backup should be performed externally using Calibre's built-in backup or filesystem copy while Calibre is closed. The server includes a test_database_concurrency tool for verifying safe concurrent access patterns.

## 19. Calibre Installation Path Discovery

The server discovers Calibre installations using multiple methods: the CALIBRE_LIBRARY_PATH environment variable (highest priority), the Windows Registry under HKCU/Software/Calibre/LibraryPath (standard Calibre installation), the macOS defaults system for the Calibre library path, common default paths (~/Calibre Library, ~/Calibre/Calibre Library), and the calibre-debug CLI if available. Library paths found are verified by checking for the existence of metadata.db in each discovered path. Results are cached for the session duration. The manage_libraries operation=list returns all discovered libraries with their paths. Libraries can be added manually via the CALIBRE_LIBRARIES environment variable as a JSON array of paths.

## 20. Tags and Rating Data Model

The tags table stores tag names with a unique constraint per name. The books_tags_link table provides the many-to-many association between books and tags. Ratings are stored in a separate ratings table as integers 1-10 (Calibre's internal 10-point scale) with conversion to 1-5 star display. The books_ratings_link table associates books with ratings. Both tags and ratings use the same many-to-many pattern as other Calibre metadata. The manage_tags tool handles all tag operations including merging duplicate tags (reassigns all book associations from source tags to target tag then deletes the source tags). Tag merge uses SQL UPDATE on the books_tags_link table followed by DELETE on the tags table in a single transaction.

## 21. Performance Characteristics

The server is designed to handle libraries of all sizes efficiently. Book query performance: SQLite queries on the Calibre metadata.db are fast -- simple queries (list, title search) execute in under 100ms even on libraries with 100000+ books. Complex multi-filter queries (author + tag + rating + date range) execute in under 500ms. Full-text search via FTS5 executes in under 200ms. RAG semantic search via LanceDB executes in 100-500ms depending on index size and embedding model. Metadata index build time: approximately 10 seconds per 10000 books for sentence-transformer embeddings. RAG full-text index build time: approximately 5 minutes per 10000 books for EPUB extraction plus embedding. Format conversion time: approximately 30 seconds per book for EPUB-to-PDF conversion. The server uses connection pooling for SQLite access and async execution for long-running operations to prevent blocking.