## Calibre MCP v1.9.0 (2026-09-11)

### Highlights
- **Embedded Web Reader Overlay**: Direct in-app e-book reading inside `BookModal` using Calibre Content Server's native `viewer.js` engine (`http://goliath:8099/`) with full-screen iframe, title header, pop-out to new tab, and exit controls.
- **Dedicated WebApp Views**:
  - `/library-health`: Database integrity checks (`PRAGMA integrity_check`), missing covers/formats audit, actionable recommendations, and re-scan controls.
  - `/duplicates`: Duplicate candidate clusters grouped by title similarity, author match, and ISBN collisions with side-by-side cover and format comparison.
  - `/reading`: Reading Queue prioritized by rating, author prominence, and series continuity + Reading Analytics (completion metrics, categories breakdown).
  - `/collections`: Virtual shelves browser with 1-click presets ("5-Star Masterpieces", "Unread Sci-Fi", "Epic Series Starters", "Quick Reads") and custom rule builder.
- **Hybrid Search (Reciprocal Rank Fusion)**: Added `hybrid_search` operation to `calibre_rag` portmanteau tool, combining Calibre FTS5 lexical rankings (`full-text-search.db`) and LanceDB semantic vector embeddings (`lancedb_calibre`) using RRF with $k=60$.
- **Incremental LanceDB RAG Sync**: Added `upsert_book_metadata(book_id)` and `remove_book_metadata(book_id)` hooked into `manage_books` (`add`, `update`, `delete`) to keep LanceDB vectors synchronized with the library without full rebuilds.
- **Physical Bookcase Cataloging**: Camera/photo cataloging of physical bookshelves via local vision OCR and Open Library enrichment (`bookcase_catalog` tool).
- **Dual WebApp Ecosystem**: Full architectural integration between Calibre Content Server (`:8099`) and CalibreMCP (`:10721` / `:10720`).
- **Production Artifacts**: Dual-packaged release featuring standalone NSIS installer (`Calibre MCP_1.9.0_x64-setup.exe`) and Claude Desktop bundle (`calibre-mcp-v1.9.0.mcpb`).
