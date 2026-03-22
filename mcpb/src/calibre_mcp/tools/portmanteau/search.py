import logging

from calibre_mcp.rag.lancedb_vector_store import LanceVectorStore
from calibre_mcp.rag.storage_paths import portmanteau_lancedb_dir
from calibre_mcp.server import mcp

logger = logging.getLogger(__name__)


def _get_vector_store(
    table_name: str = "calibre_media",
    *,
    metadata_db_path: str | None = None,
) -> LanceVectorStore:
    """LanceDB store under ``{library}/lancedb_calibre`` (separate from FTS ``lancedb/`` and metadata ``lancedb_metadata/``)."""
    from calibre_mcp.db.database import get_database

    if metadata_db_path:
        base = portmanteau_lancedb_dir(metadata_db_path)
    else:
        db = get_database()
        path = db.get_current_path()
        if not path:
            raise RuntimeError(
                "No Calibre library loaded. Use manage_libraries(operation='switch') first, "
                "or pass db_path for ingest."
            )
        base = portmanteau_lancedb_dir(path)
    return LanceVectorStore(db_path=str(base), table_name=table_name)


@mcp.tool()
async def calibre_rag(
    operation: str,
    query: str | None = None,
    limit: int = 5,
    db_path: str | None = None,
    search_type: str = "metadata",
    book_id: str | None = None,
    title: str | None = None,
    file_path: str | None = None,
) -> dict:
    """
    Unified Portmanteau for Semantic Search and RAG Operations on the Calibre Library.

    Operations:
        - "search": Perform a semantic search across library items using a natural language query.
        - "ingest": Index a specified library (db_path required) into the LanceDB Vector Store.
        - "ingest_fulltext": Deep index a specific EPUB/PDF (book_id, title, file_path required).
        - "status": Get vector store status and row counts.

    Args:
        operation: 'search', 'ingest', 'ingest_fulltext', or 'status'
        query: Natural language semantic query (required for 'search')
        limit: Max results to return (default: 5)
        db_path: Absolute path to metadata.db (required for 'ingest' operation)
        search_type: 'metadata' or 'fulltext' (default: 'metadata')
        book_id: Book ID (required for 'ingest_fulltext')
        title: Title of the book (required for 'ingest_fulltext')
        file_path: Path to EPUB/PDF file (required for 'ingest_fulltext')
    """
    try:
        table_name = "calibre_fulltext" if search_type == "fulltext" else "calibre_media"
        store = _get_vector_store(table_name=table_name, metadata_db_path=db_path)

        if operation == "status":
            stats = store.get_table_metadata()
            return {
                "success": True,
                "operation": "status",
                "message": f"Vector Store Status: {stats['row_count']} document(s) indexed.",
                "data": stats,
            }

        if operation == "search":
            if not query:
                return {
                    "success": False,
                    "error": "query parameter is required for semantic search",
                }

            logger.info("Performing semantic search for: %s", query)
            results = store.search(query=query, limit=limit)

            formatted_results = []
            for res in results:
                meta = res.get("metadata", {})
                if search_type == "fulltext":
                    formatted_results.append(
                        {
                            "title": meta.get("title", "Unknown Title"),
                            "location": meta.get("location", ""),
                            "book_id": meta.get("book_id"),
                            "score": res.get("_distance", 0),
                            "content_preview": res.get("content", "")[:300] + "..."
                            if res.get("content")
                            else "",
                        }
                    )
                else:
                    formatted_results.append(
                        {
                            "title": meta.get("title", "Unknown Title"),
                            "authors": meta.get("authors", "Unknown Author"),
                            "series": meta.get("series", ""),
                            "book_id": meta.get("book_id"),
                            "score": res.get("_distance", 0),
                        }
                    )

            return {
                "success": True,
                "operation": "search",
                "query": query,
                "message": f"Found {len(formatted_results)} semantically relevant books",
                "results": formatted_results,
            }

        if operation == "ingest":
            if not db_path:
                return {
                    "success": False,
                    "error": "db_path parameter (absolute path to Calibre metadata.db) is required for ingestion",
                }

            from calibre_mcp.services.rag_ingestor import CalibreIngestor

            ingestor = CalibreIngestor(db_path=db_path, vector_store=store)

            result = await ingestor.ingest_library()
            return {
                "success": result["status"] == "success",
                "operation": "ingest",
                "message": f"Ingestion completed with status: {result['status']}",
                "data": result,
            }

        if operation == "ingest_fulltext":
            if not all([book_id, title, file_path]):
                return {
                    "success": False,
                    "error": "book_id, title, and file_path are required for ingest_fulltext",
                }

            from calibre_mcp.services.deep_ingestor import DeepIngestor

            ingestor = DeepIngestor(vector_store=store)
            result = await ingestor.ingest_book_fulltext(
                book_id=str(book_id), title=title, file_path=file_path
            )
            return {
                "success": result.get("status") == "success",
                "operation": "ingest_fulltext",
                "message": result.get("message", f"Status: {result.get('status')}"),
                "data": result,
            }

        return {
            "success": False,
            "error": f"Invalid operation: '{operation}'",
            "suggestions": ["search", "ingest", "status"],
        }

    except Exception as e:
        logger.error("Error in calibre_rag tool: %s", e, exc_info=True)
        return {"success": False, "error": str(e)}
