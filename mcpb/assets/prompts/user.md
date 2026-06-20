# calibremcp: Comprehensive User Guide and Workflow Manual

Welcome to the Calibre MCP ecosystem. This guide provides step-by-step instructions for managing your Calibre e-book library through natural language commands via your MCP client. Whether you are cataloging a new collection, performing deep literary research, cleaning up metadata, or reading books in-chat this guide covers every aspect of the system.

## 1. Quick Start: Your First Library Query

The fastest way to verify your setup is to list books in your Calibre library. The server automatically discovers Calibre libraries from standard locations.

"Show me my Calibre libraries and list the most recent books."

The server calls manage_libraries operation=list to discover all Calibre libraries. If found it returns library name, path, book count, and size. Then query_books operation=recent returns the most recently added books with title, author, series, and formats.

## 2. Tutorial 1: Library Discovery and Switching

Goal: Find all Calibre libraries on your system and switch between them.

Step 1: Use manage_libraries operation=list to discover all Calibre libraries. The server probes the CALIBRE_LIBRARY_PATH environment variable, the Windows Registry (Calibre stores the library path under HKCU/Software/Calibre/LibraryPath), and standard user directories. Step 2: Review the list of libraries with their names, paths, book counts, and available sizes. Step 3: Switch to a specific library with manage_libraries operation=switch library_name="My Fiction Library". Step 4: Verify by running manage_libraries operation=stats to see detailed metrics for the active library including author count, tag count, format distribution, and series count. Step 5: Search across all libraries simultaneously with manage_libraries operation=search query="Dune" which returns results from every discovered library.

## 3. Tutorial 2: Searching and Filtering Books

Goal: Find specific books using advanced search filters.

Step 1: Simple search by title: query_books operation=search title="Dune". This searches the title field for exact or partial matches. Step 2: Search by author: query_books operation=search author="Asimov". This matches against the author sort name. Step 3: Combined search: query_books operation=search author="Asimov" tag="science fiction" min_rating=4. This returns books by Asimov tagged as science fiction with a rating of 4 or higher. Step 4: Search by text across title, author, and comments: query_books operation=search text="foundation empire". The text parameter performs a cross-field search. Step 5: Filter by date: query_books operation=search pubdate_start="2000-01-01" pubdate_end="2010-12-31". Step 6: Filter by format: query_books operation=search formats="EPUB,PDF" which returns books available in both EPUB and PDF formats. Step 7: Sort and paginate: add limit=10 offset=20 to paginate through results.

Search parameters: author (string), authors (list for multiple), exclude_authors, series (string), exclude_series, text (cross-field), title, tag/tags, exclude_tags, publisher/publishers, rating (exact match), min_rating, max_rating, unrated (bool), pubdate_start/pubdate_end (ISO dates), added_after/added_before, min_size/max_size (bytes), formats (list of extensions), comment (text in comments), has_empty_comments, limit (default 50), offset. Results include id, title, author, series, series_index, tags, rating, formats, size, pubdate, timestamp.

## 4. Tutorial 3: Adding and Managing Books

Goal: Add a new book to the library and update its metadata.

Step 1: Add a book from file: manage_books operation=add file_path="C:/Downloads/book.epub" fetch_metadata=true. The server adds the file to the Calibre library, auto-fetches metadata from the file's embedded metadata or Calibre's built-in metadata download (if configured). Step 2: Optionally convert during add: add convert_to="PDF" to also generate a PDF version. Step 3: Get book details: manage_books operation=details book_id=42. Returns full metadata including title, authors, series, tags, rating, publisher, pubdate, comments, formats with file paths and sizes, cover path, and custom column values. Step 4: Update metadata: manage_books operation=update book_id=42 metadata={"rating": 5, "tags": ["science fiction", "classic"]}. Step 5: Add a description: manage_comments operation=create book_id=42 text="A groundbreaking work of science fiction exploring themes of civilization and power." Step 6: Set reading status: manage_books operation=update book_id=42 metadata={"status": "reading", "progress": 0.35}.

## 5. Tutorial 4: Tag Management and Organization

Goal: Clean up and organize your tag system.

Step 1: Get tag statistics: manage_tags operation=statistics to see tag usage frequencies. Step 2: Find potentially duplicate tags: manage_tags operation=find_duplicates similarity_threshold=0.85. This uses fuzzy string matching to identify similar tags like "sci-fi" and "scifi" or "mystery" and "mysteries". Step 3: Merge duplicates: manage_tags operation=merge source_tag_ids=[12,15] target_tag_id=12 to consolidate tags. Step 4: Find unused tags: manage_tags operation=get_unused. These are tags assigned to zero books, often left over from bulk imports. Step 5: Delete unused tags: manage_tags operation=delete_unused force=true. Step 6: Rename a tag: manage_tags operation=update tag_id=5 new_name="Artificial Intelligence". This renames the tag across all books. Step 7: Create a new tag: manage_tags operation=create name="cyberpunk".

## 6. Tutorial 5: Series Management

Goal: Track book series and identify missing volumes.

Step 1: List series: manage_series operation=list. Returns all series with names and book counts. Step 2: Get series details: manage_series operation=get series_id=12. Step 3: Get books in a series: manage_series operation=get_books series_id=12. Returns books sorted by series_index showing which volumes you have. Step 4: Run series analysis: manage_analysis operation=series_analysis. This identifies incomplete series with missing volume numbers. For example if you have "Foundation" volumes 1, 2, and 4 the analysis reports volume 3 as missing. Step 5: Use manage_books operation=update to set series and series_index on any book that is missing them. Step 6: For series metadata cleanup, use manage_library_operations operation=fix_series_metadata to repair numbering gaps and naming inconsistencies.

## 7. Tutorial 6: Full-Text and Semantic Search

Goal: Find passages inside books using both keyword and semantic search.

Step 1: Full-text search: search_fulltext query="artificial intelligence" limit=10. This searches Calibre's FTS index for exact keyword matches within book content. Results include book title, author, and the surrounding text snippet. Step 2: Semantic search: rag_retrieve query="the ethics of creating conscious machines" top_k=5. This uses LanceDB vector embeddings to find semantically related passages even if the exact keywords are not present. Step 3: Check RAG status: calibre_rag operation=status to see indexed documents and chunk count. Step 4: If the RAG index is empty, build it: rag_index_build force_rebuild=true. This processes all EPUB/PDF books in the library extracting text, chunking, and generating embeddings. Step 5: Use calibre_metadata_search for semantic metadata search: calibre_metadata_search query="dystopian future societies" top_k=10. This searches across titles, author names, tags, and comments.

RAG embedding models: The server uses sentence-transformers (all-MiniLM-L6-v2 or similar) for generating embeddings locally. Alternatively configure Ollama for embeddings via OLLAMA_BASE_URL environment variable. The RAG index is persisted in the sidecar database directory.

## 8. Tutorial 7: Format Conversion and Export

Goal: Convert books between formats and export your library.

Step 1: List available formats for a book: manage_books operation=details book_id=42 includes a formats field showing all available file formats. Step 2: Convert a book: manage_files operation=convert conversion_requests=[{"book_id": 42, "source_format": "EPUB", "target_format": "PDF"}]. The server uses Calibre's ebook-convert tool. Step 3: Bulk conversion: manage_files operation=convert conversion_requests=[{"book_id": 42, "target_format": "MOBI"}, {"book_id": 43, "target_format": "MOBI"}]]. Step 4: Download a file path: manage_files operation=download book_id=42 format_preference="PDF". Returns the local file path for further use. Step 5: Export metadata as CSV: export_books operation=csv author="Tolkien" limit=50. Exports author, title, series, tags, rating, dates, formats. Step 6: Export full catalog as JSON: export_books operation=json pretty=true. The JSON export includes all metadata fields, custom columns, and format paths. Step 7: Generate a styled HTML catalog: export_books operation=html html_style="catalog" tag="science fiction". Produces a standalone HTML page with cover thumbnails and table of contents.

## 9. Tutorial 8: Author and Publisher Analysis

Goal: Analyze your library by author demographics and publisher distribution.

Step 1: List authors: manage_authors operation=list limit=100. Returns all authors with book counts. Step 2: Get author statistics: manage_authors operation=stats. Shows author count, books per author distribution, most prolific authors, and letter distribution. Step 3: Get books by a specific author: manage_authors operation=get_books author_id=15. Returns all books sorted by series then series_index. Step 4: For publisher analysis: manage_publishers operation=stats to see publisher distribution. Step 5: Filter books by publisher: manage_publishers operation=get_books publisher_name="Tor Books". Step 6: Use query_books with publisher field for targeted searches: query_books operation=search publisher="Penguin" tag="fiction".

## 10. Tutorial 9: Reading Statistics and Unread Priority

Goal: Understand your reading habits and prioritize your unread queue.

Step 1: Get reading statistics: reading_statistics(). Returns charts of books read per month/year, genre distribution, pages read, author diversity, and publishing era breakdown. Step 2: Get unread priority list: unread_priority_list(). Applies Austrian efficiency algorithm that scores unread books by rating (higher first), series completeness (finish near-complete series), age (older additions first), and genre diversity. Step 3: Use the prioritized list to decide what to read next. Step 4: Mark books as read: manage_books operation=update book_id=42 metadata={"status": "finished", "progress": 1.0}. Step 5: Track progress while reading: manage_books operation=update book_id=42 metadata={"status": "reading", "progress": 0.5}.

## 11. Tutorial 10: Deep Book Research

Goal: Get comprehensive information about a book including external reviews and thematic analysis.

Step 1: Get the book details: manage_books operation=details book_id=42 to confirm the correct book. Step 2: Run deep research: media_research_book book_id=42. This uses LLM sampling to fetch Wikipedia (book and author entries), SF Encyclopedia (for genre fiction), TVTropes (for fiction works), Anime News Network (for manga/light novels), and Open Library (if ISBN is present). It synthesizes everything with your local Calibre metadata (rating, tags, notes) and RAG passages into a structured report with sections: Overview, Context, Plot/Content, Critical Reception, Themes and Tropes, Adaptations, Related Works, Your Library. Step 3: Generate a synopsis: media_synopsis book_id=42 title="Dune". Uses full-text semantic chunks and LLM sampling to create a spoiler-aware summary. Step 4: Check critical reception: media_critical_reception author="Frank Herbert" title="Dune". Synthesizes professional reviews and academic analysis via web search. Step 5: For comparative analysis: media_deep_research topic="The depiction of artificial intelligence in 1970s science fiction". This searches across all books in your library with relevant RAG passages and produces a multi-book thematic analysis.

Deep research tools require a sampling-capable MCP client (Claude Desktop, Cursor). They use ctx.sample() to call the connected LLM for synthesis. Results are structured markdown documents that can be saved or exported.

## 12. Tool Reference Summary

Library discovery: manage_libraries. Book search: query_books. Book CRUD: manage_books. Metadata: manage_metadata. Tags: manage_tags. Series: manage_series. Authors: manage_authors. Publishers: manage_publishers. Files and conversion: manage_files. Comments: manage_comments. Viewer: manage_viewer. Analysis: manage_analysis. Full-text: search_fulltext. RAG: calibre_rag, rag_retrieve. Export: export_books. Research: media_research_book. System: manage_system.

## 13. Troubleshooting

Library not found: Set CALIBRE_LIBRARY_PATH to your Calibre library directory. The server also checks the Windows Registry. Run Calibre once to create the default library. Book search returns no results: Check that your search terms are not too specific. Use the text parameter for cross-field search. Format conversion fails: Ensure Calibre is installed (minimum v5.0). Check that ebook-convert is on PATH. RAG index empty: Run rag_index_build to create the vector index. This may take a while for large libraries with many books. Large libraries: Use pagination (limit and offset parameters) for all list operations. The server uses SQL LIMIT clauses for efficient queries. Write operations fail: The server uses read-write connections when modifying data. Ensure the Calibre database is not open in another application (Calibre GUI locks the database).

## 14. Tutorial 11: Custom Columns and Extended Metadata

Goal: Work with Calibre custom columns for personalized metadata.

Step 1: Query a book to see available custom columns: manage_books operation=details book_id=42. Custom columns appear in the response with their lookup names. Step 2: Update a custom column: manage_metadata operation=update updates=[{"book_id": 42, "field": "#myrating", "value": "5/5"}]. Custom column field names start with #. Step 3: Search using custom column filters. While direct search on custom columns requires knowing the column name, the query interface can filter on standard fields. Step 4: Use extended metadata tools: manage_extended_metadata for managing custom column definitions.

## 15. Tutorial 12: Agentic Library Workflows

Goal: Use autonomous AI-powered workflows for complex library tasks.

Step 1: Try the conversational assistant: conversational_calibre_assistant with a question like "What are the most underrated books in my library?" Step 2: Use intelligent library processing: intelligent_library_processing with a task like "Organize my library tags and fix any metadata issues." The AI analyzes the library state and executes appropriate tool calls. Step 3: Use agentic workflows: agentic_calibre_workflow with a goal like "Find all incomplete series, identify the missing books, and create a reading plan." The workflow uses FastMCP sampling to reason about the library and generate a plan. Step 4: These workflows are non-deterministic and use LLM sampling -- results vary based on the connected LLM capabilities.

## 16. FAQ

Q: Can I access multiple Calibre libraries simultaneously? A: Yes. Use manage_libraries operation=list to discover all libraries, then manage_libraries operation=switch library_name to switch between them. Cross-library search is supported via manage_libraries operation=search.

Q: Does the server modify my Calibre database directly? A: Read operations never modify data. Write operations (metadata updates, tag management, book deletion) modify the Calibre metadata.db directly. Always back up your Calibre library before performing destructive operations using the filesystem (copy the library folder).

Q: Why are some books not found in full-text search? A: Calibre must build the FTS index separately (Preferences > Searching > Full text search > Build index). Books added after index creation need the index refreshed.

Q: Can I read books directly in the chat? A: Yes, using the manage_viewer tool. It extracts book pages and returns content for reading within the MCP client interface. The viewer supports EPUB and MOBI formats.

Q: How do I import a large number of books? A: Copy the files to your Calibre library directory or use Calibre's "Add books" function. The manage_books tool supports adding single files. For bulk imports use Calibre's built-in import which the server does not replicate.

## 17. REST API Reference Summary

All REST endpoints are available at http://localhost:PORT (configurable via MCP_PORT). Key endpoints: GET /health server health, GET /api/v1/status server status, GET /api/v1/tools tool listing, POST /api/v1/control/{tool_name} dispatch tool calls. The webapp provides the full SOTA dashboard with Library browser, Tag management UI, Book viewer, Metadata editor, Export tools, RAG search interface, and API documentation. The FastAPI backend exposes auto-generated Swagger UI at /docs and ReDoc at /redoc for API exploration.

## 18. Tutorial 13: Library Health Check and Repair

Goal: Run a comprehensive health check on your Calibre library and fix common issues.

Step 1: Run library health analysis: manage_analysis operation=library_health. This checks for: missing files (books with no associated format files on disk), database integrity (SQLite integrity_check), orphaned database entries (authors with no books, tags with no books, series with no books), duplicate entries (same book added twice with different IDs). Step 2: Review the health report which lists each issue found with severity (warning, error, critical). Step 3: Fix missing files: if books have no format files on disk, the book records are orphaned. Use manage_books operation=delete to remove them and then re-add the books from source files. Step 4: Merge duplicates: use find_duplicate_books which returns potential duplicate pairs with similarity scores. Use manage_books operation=delete on the duplicate after confirming it is truly a duplicate. Step 5: Clean up orphaned tags: use manage_tags operation=delete_unused to remove tags with zero book associations. Step 6: Clean up orphaned series: series with no books can be identified through the series analysis and removed manually. Step 7: Rebuild the RAG index after major library changes: rag_index_build.

## 19. Tutorial 14: Custom Metadata Workflows

Goal: Use custom columns and extended metadata fields for personalized library organization.

Step 1: Understand custom columns. Calibre allows user-defined custom columns that appear in the book details and can be searched and filtered. The manage_extended_metadata tool handles custom column lifecycle. Step 2: Query existing custom columns using manage_extended_metadata. They appear with a # prefix in field names. Step 3: Update custom column values: manage_metadata operation=update with updates containing the #field_name and value. Common custom columns include: #genre (user-defined sub-genre), #reading_status (enum: to-read, reading, finished, abandoned), #shelf_location (physical shelf identifier), #acquired_date (date of acquisition), #price_paid (purchase price), #personal_rating (1-10 scale), #recommended_by (string reference). Step 4: Search using custom columns through query_books with the appropriate field mapping. Step 5: Export books with custom columns: use export_books operation=json or csv which includes all custom column data. Step 6: For extensive custom column workflows, use manage_metadata operation=organize_tags to see the relationship between tags and custom columns.

## 20. Calibre File Format Support

Calibre supports an extensive range of input and output formats through the conversion engine. Supported input formats for reading directly: EPUB (standard for most modern e-books), MOBI (Amazon Kindle format), AZW3 (Kindle KF8 format), PDF (Adobe Portable Document Format), DOCX (Microsoft Word), RTF (Rich Text Format), TXT (plain text), HTML (web page), LIT (Microsoft Reader), PRC (Palm Resource), PDB (Palm Database), PML (Palm Markup Language), RB (RocketBook), SNB (Shanda Bambook), TCR (Psion Series 3), OEB (Open E-book), CBZ/CBR (comic book archives). Supported output formats via conversion: EPUB, MOBI, AZW3, PDF, DOCX, RTF, TXT, HTML, LRF (Sony Reader), PDB, PML, RB, SNB, TCR. The conversion quality depends on the source format quality -- PDF source text extraction is limited by PDF structure while EPUB sources provide the best conversion results. Format metadata: each book can have multiple formats stored simultaneously. The data table tracks each format file with book_id, format (uppercase extension), and name (filename without extension). The manage_files tool provides format conversion and download access.

## 21. Integration with Fleet Ecosystem

calibremcp integrates with the broader fleet ecosystem through the shared monitoring stack and REST API. The server exposes Prometheus metrics for unified monitoring (tool call counts, execution durations, error rates, library size statistics). The fleet monitoring stack collects these metrics for dashboard visualization. The show_api_docs tool exposes Swagger and ReDoc URLs for web-based API discovery. The server registers in the fleet discovery system via the REST API for cross-referencing by other servers. The Prefab UI tools (show_book_prefab_card, show_libraries_prefab_card) provide in-chat rich cards in supporting MCP clients. The webapp on port 10812 provides full SOTA dashboard with library browsing, tag management, book viewer, metadata editor, export tools, RAG search, and API documentation. The FastAPI backend serves both the MCP interface and the web dashboard under the same port with CORS middleware for cross-origin access.

## 22. Metadata Update Field Reference

The manage_metadata and manage_books update operations accept these field names: title (str, book title), author_sort (str, sort name for author), rating (int 1-5, book rating), tags (list of str, replaces all tags), series (str, series name), series_index (float, volume number in series), publisher (str, publisher name), pubdate (str ISO date, publication date), comments (str, book description text), cover (str, filesystem path to new cover image), status (str: to-read, reading, finished, abandoned), progress (float 0.0-1.0, reading progress), custom column (#fieldname, where fieldname is the custom column lookup name). When updating tags, the provided list replaces all existing tags. To add a tag without removing others, use manage_tags instead. Custom column values are type-dependent: text columns accept strings, rating columns accept integers, date columns accept ISO date strings, enum columns accept one of the defined values, series-like columns accept a string name and optional index.

## 23. Library Health Check Parameters

The manage_analysis operation=library_health checks: missing format files (books in the database with no corresponding files in the library directory), database consistency (SQLite integrity_check), orphan records (authors/tags/series/publishers with zero book associations), duplicate titles (books with identical or near-identical titles by the same author), empty comments (books with no description text), stale metadata (books with missing ISBN, no publisher, or no pubdate), large books (formats over 50MB that may be corrupt), and custom column issues (invalid values or unlinked custom column definitions). Each issue category has a severity level. Critical issues prevent normal library operation (missing format files, database corruption). Warnings suggest cleanup but do not block operations (empty comments, missing metadata). Info items are awareness-level observations (large format files, many unused tags). The fix_issues operation repairs automatically fixable problems (unused tag removal, orphaned author cleanup, database vacuum).

## 24. User and Comments Management

manage_users: Multi-user Calibre library management. Operations include: list (show all registered users), create (add user with username, password, and permissions), update (change user details or permissions), delete (remove user), get_user_library (show per-user library state for reading progress tracking). Users have independent reading progress, tags, and notes on shared libraries. manage_user_comments: Personal notes separate from Calibre's shared comments. Operations include: set_note (add/update private note for a book), get_notes (list all notes by user), search_notes (full-text search across notes), delete_note (remove a note). User comments are stored in the sidecar database and are not visible in the Calibre GUI. manage_times: Track reading time and sessions. Operations include: start_session (begin reading timer for a book), end_session (end timer and log duration), get_stats (total reading time, average session length, pages per hour reported).

## 25. Working with External Sources

The ai operations (media_research_book, media_synopsis, media_critical_reception, media_deep_research) use external data sources to enrich book information. Wikipedia: fetches book and author entries for overview and context. The server uses the Wikipedia API (en.wikipedia.org/w/api.php) with action=query and prop=extracts to get article summaries. SF Encyclopedia: specialized reference for science fiction, fantasy, and horror works. Queried via web scraping of the SFE website at sf-encyclopedia.com. TVTropes: trope analysis for fiction works including but not limited to SFF. Uses the TVTropes API for page content extraction. Open Library: ISBN-based metadata retrieval via openlibrary.org/api/books API returning cover URLs, descriptions, and subject classifications. The server orchestrates these external calls with timeout handling and rate limiting. Results are synthesized via LLM sampling (ctx.sample()) into structured markdown reports. If sampling is unavailable, the external data is returned as raw structured data without synthesis. The external research tools require network access and may take 10-30 seconds to complete depending on the number of sources queried and the response time of external APIs.

## 26. Advanced Publisher and Series Analysis

For in-depth library analytics: 1) Use manage_publishers operation=stats to see publisher distribution across your library. The report shows which publishers appear most frequently, average rating by publisher, and top genres per publisher. 2) Use manage_series operation=stats to see series distribution: most prolific series authors, average series length, completion rate (percentage of volumes owned vs total volumes). 3) Use manage_authors operation=stats for author analytics: most represented authors, average rating per author, genre specialization per author, publication decade distribution. 4) Cross-reference these stats to identify collection strengths and gaps: do you have complete collections from your favorite authors? Are there publishers whose entire catalog you collect? Which series are waiting for the next volume? 5) Export the combined analysis as HTML for a visually rich library catalog using export_books operation=html with include_stats=true. The HTML catalog includes cover thumbnails, reading progress indicators, and series completion status.

## 27. Batch Operations for Large Libraries

The bulk operations system (manage_bulk_operations) enables efficient processing of large book collections. Operations include: bulk_tag_assign (apply a tag to all books matching a search query), bulk_metadata_update (update a specific field across multiple books), bulk_convert (convert format for all books in a series or by an author), bulk_export (export a subset of the library matching criteria). The bulk operations use efficient SQL queries for selection and batch processing for conversion to minimize database overhead. For very large operations (over 10000 books), the server processes in batches of 500 with progress tracking. The bulk operations respect the same permission model as individual operations. For destructive bulk operations (delete, overwrite), a confirmation step is included to prevent accidental data loss.

## 28. Viewing and Reading Books In-Chat

The manage_viewer tool enables reading books directly through the chat interface. The viewer extracts text from EPUB and MOBI files: 1) Use manage_viewer operation=open book_id=42 to initialize the viewer. Returns book metadata (title, author, total pages, chapter list). 2) Use manage_viewer operation=get_page book_id=42 page_number=1 to retrieve the first page of content. Returns page text, page number, total pages, chapter title. 3) Use manage_viewer operation=update_state to save reading position (current_page, zoom_level, reading_direction). 4) Use manage_viewer operation=get_state to resume reading from a saved position. 5) Use manage_viewer operation=open_file book_id=42 to open the book in the system default reader application (Calibre E-book Viewer, Adobe Digital Editions, etc.). 6) Use manage_viewer operation=open_random to discover a random book from your library. The viewer supports EPUB 2 and EPUB 3 format, MOBI/KF8 format, and plain text files. PDF files are not supported for in-chat reading due to the complexity of PDF text extraction.

## 29. Format Conversion Quality Tips

For best conversion results: EPUB to PDF: set page_size=A4, margin_size=15mm, default_font_size=11pt for a readable document layout. EPUB to MOBI: use mobi_toc_at_start=true for Kindle table of contents compatibility. PDF to EPUB: quality depends on source PDF structure. PDFs with embedded text (searchable PDFs) convert well; scanned PDFs (image-only) require OCR which is not supported. AZW3 to EPUB: use --linearize_tables for complex table layouts. DOCX to EPUB: ensure source uses styles (Heading 1, Normal, etc.) for proper chapter detection. HTML to EPUB: provide a TOC file for multi-page HTML sources. High quality preset uses --base-font-size=12 and --margin-size=15pt for comfortable reading. Draft quality preset produces smaller files at 72dpi rendering. The conversion engine supports custom heuristics for input format detection and can be configured via conversion_requests parameter with format-specific options.

## 30. Performance Optimization

For large libraries (over 50000 books): use pagination (limit and offset) on all query operations to reduce response time. Use specific search filters rather than broad queries to leverage SQLite indexes. Build the RAG index incrementally rather than all at once by using the sync operation periodically. If format conversion performance is critical, run multiple conversion requests in parallel (the server supports concurrent subprocess execution). For viewing large books, use get_page with specific page numbers rather than opening the entire book. The VACUUM operation via Calibre's maintenance tools improves database performance over time. The server uses SQL connection pooling and prepared statements for optimal database performance.

## 31. Database Backup and Recovery

Regular Calibre database backups are essential: 1) Use the operating system to copy the entire Calibre library directory periodically. 2) Use Calibre's built-in backup (Connect/Share > Start Content Server for wireless access, then export via OPDS). 3) Before major metadata operations, back up using filesystem copy. 4) If the metadata.db becomes corrupted, restore from your latest backup. 5) The server's manage_analysis operation=library_health checks database integrity via SQLite PRAGMA integrity_check. 6) If integrity_check fails, Calibre includes a metadata.db recovery tool: calibre-debug --restore-database --path=/path/to/library. 7) The database auto-recovery can recover most corruption issues but may lose recent changes. 8) The server cannot repair a corrupted database - restore from backup.

## 32. Fleet Integration and Cross-Referencing

The server supports integration with other Fleet MCP servers for combined operations. The REST API enables cross-server tool calling through POST /api/v1/control/{tool_name}. The web dashboard at port 10812 provides visual integration with the fleet discovery system. The fleet scanning endpoint (port 10813) discovers other active MCP servers for cross-referencing. The Prefab UI tools register with the fleet system for discovery by other servers. The server's Prometheus metrics (when enabled) feed into the unified monitoring stack.

## 33. Server Logs and Diagnostics

The server provides comprehensive logging for diagnostics. Use get_logs to retrieve recent activity. Use export_logs to save logs for external analysis. Log levels: DEBUG (verbose operation details, useful for troubleshooting), INFO (normal operation messages), WARNING (non-critical issues), ERROR (operation failures). The logs include timestamps, module names, function names, and operation details. The activity log captures all tool invocations with parameters and results. For deep diagnostic support, enable DEBUG logging via the LOG_LEVEL environment variable.

## 34. Command-Line Interface

The server supports CLI arguments: --stdio (run in stdio mode for Claude Desktop), --http (HTTP mode for web), --sse (SSE transport, deprecated), --host (bind address, default 127.0.0.1), --port (HTTP port, default 10813), --path (MCP endpoint path, default /mcp), --debug (enable debug logging). Environment variables: MCP_TRANSPORT overrides transport, MCP_HOST overrides bind address, MCP_PORT overrides port, MCP_PATH overrides endpoint path. The server also uses CALIBRE_LIBRARY_PATH, CALIBRE_LIBRARIES (JSON array), CALIBRE_PREFAB_APPS (disable Prefab), RAG_EMBEDDING_MODEL, OLLAMA_BASE_URL, SIDECAR_DB_PATH. The web dashboard starts automatically with the HTTP server.