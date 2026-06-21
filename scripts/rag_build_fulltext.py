"""Build Calibre full-text RAG index (LanceDB, fastembed) — run directly, not via MCP.

Usage:
    cd C:/Users/hackb/calibremcp
    .venv/Scripts/python scripts/rag_build_fulltext.py           # resume if interrupted
    .venv/Scripts/python scripts/rag_build_fulltext.py --force   # wipe and rebuild from scratch

Resumes automatically from where it left off if interrupted.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import lancedb

LIBRARY_PATH = Path(r"C:\Users\hackb\OneDrive\Calibre Library\metadata.db")
BATCH_SIZE = 128
TABLE_NAME = "books_rag"


def get_indexed_ids(db_path: str) -> set[str]:
    """Return all chunk IDs already written to the index."""
    try:
        db = lancedb.connect(db_path)
        if TABLE_NAME not in db.table_names():
            return set()
        tbl = db.open_table(TABLE_NAME)
        ids = tbl.to_arrow(columns=["id"]).column("id").to_pylist()
        return set(ids)
    except Exception as e:
        print(f"[rag] Warning: could not read existing index ({e}), starting fresh")
        return set()


def main() -> int:
    force = "--force" in sys.argv or "-f" in sys.argv

    from calibre_mcp.rag.chunking import chunk_books_text
    from calibre_mcp.rag.fastembed_gpu import embed_use_gpu, repo_root_from_here
    from calibre_mcp.rag.lancedb_vector_store import LanceVectorStore
    from calibre_mcp.rag.storage_paths import fts_chunks_lancedb_dir
    from calibre_mcp.utils.fts_utils import find_fts_database

    gpu = embed_use_gpu(repo_root_from_here())
    print(f"[rag] GPU mode: {gpu}")

    if not LIBRARY_PATH.exists():
        print(f"[rag] ERROR: metadata.db not found at {LIBRARY_PATH}")
        return 1

    fts = find_fts_database(LIBRARY_PATH)
    if not fts:
        print("[rag] ERROR: full-text-search.db not found. Enable FTS in Calibre and index books first.")
        return 1

    print(f"[rag] FTS database: {fts} ({fts.stat().st_size // 1024 // 1024} MB)")

    db_path = str(fts_chunks_lancedb_dir(LIBRARY_PATH))

    if force:
        print("[rag] --force: dropping existing table and rebuilding from scratch")
        db = lancedb.connect(db_path)
        if TABLE_NAME in db.table_names():
            db.drop_table(TABLE_NAME)
        already_indexed: set[str] = set()
    else:
        already_indexed = get_indexed_ids(db_path)
        if already_indexed:
            print(f"[rag] Resuming: {len(already_indexed):,} chunks already indexed, skipping them")
        else:
            print("[rag] No existing index found, starting fresh")

    store = LanceVectorStore(db_path=db_path, table_name=TABLE_NAME)

    t0 = time.time()
    batch: list[dict] = []
    total_new = 0
    total_skipped = 0

    def flush() -> None:
        nonlocal total_new
        if not batch:
            return
        store.add_documents(batch, overwrite=False)
        total_new += len(batch)
        elapsed = time.time() - t0
        print(f"[rag]   {total_new:,} new chunks indexed ({elapsed:.0f}s elapsed)...")
        batch.clear()

    for chunk in chunk_books_text(LIBRARY_PATH):
        chunk_id = f"b{chunk['book_id']}_f{chunk['format']}_i{chunk['chunk_index']}"
        if chunk_id in already_indexed:
            total_skipped += 1
            continue
        batch.append({
            "id": chunk_id,
            "content": chunk["text"],
            "metadata": {
                "book_id": chunk["book_id"],
                "format": chunk["format"],
                "chunk_index": chunk["chunk_index"],
            },
        })
        if len(batch) >= BATCH_SIZE:
            flush()

    flush()

    elapsed = time.time() - t0
    print(f"[rag] Done: {total_new:,} new chunks indexed in {elapsed:.0f}s.")
    if total_skipped:
        print(f"[rag] Skipped {total_skipped:,} chunks already in index.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
