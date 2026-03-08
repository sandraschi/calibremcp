import sys
import logging

logger = logging.getLogger(__name__)

# Provide docs_mcp path if it's external, depending on environment setup.
# FastMCP tools can load this dynamically if added to PYTHONPATH, but to be robust:
sys.path.append(r"d:\Dev\repos\mcp-central-docs\src")

try:
    from docs_mcp.backend.rag_core import BaseVectorStore
except ImportError:
    BaseVectorStore = None
    logger.warning("mcp-central-docs is not available. calibre_rag tool may fail.")

from calibre_mcp.server import mcp


def _get_vector_store(table_name: str = "calibre_media") -> "BaseVectorStore":
    """Lazily load the vector store for semantic search."""
    if BaseVectorStore is None:
        raise RuntimeError(
            "Vector Store dependency 'docs_mcp' not found. Cannot perform RAG operations."
        )

    # Store at local LanceDB path
    return BaseVectorStore(db_path="data/lancedb_calibre", table_name=table_name)


@mcp.tool()
async def calibre_rag(
    operation: str,
    query: str = None,
    limit: int = 5,
    db_path: str = None,
    search_type: str = "metadata",
    book_id: str = None,
    title: str = None,
    file_path: str = None,
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
        store = _get_vector_store(table_name=table_name)

        if operation == "status":
            stats = store.get_table_metadata()
            return {
                "success": True,
                "operation": "status",
                "message": f"Vector Store Status: {stats['row_count']} document(s) indexed.",
                "data": stats,
            }

        elif operation == "search":
            if not query:
                return {
                    "success": False,
                    "error": "query parameter is required for semantic search",
                }

            logger.info(f"Performing semantic search for: {query}")
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

        elif operation == "ingest":
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

        elif operation == "ingest_fulltext":
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

        else:
            return {
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "suggestions": ["search", "ingest", "status"],
            }

    except Exception as e:
        logger.error(f"Error in calibre_rag tool: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
