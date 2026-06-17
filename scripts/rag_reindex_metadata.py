"""Rebuild Calibre metadata LanceDB index — use with just rag-gpu-metadata (venv python, not uv run)."""

from __future__ import annotations


def main() -> int:
    from calibre_mcp.rag.fastembed_gpu import embed_use_gpu, repo_root_from_here
    from calibre_mcp.rag.metadata_rag import build_metadata_index

    gpu = embed_use_gpu(repo_root_from_here())
    print(f"[rag] GPU mode: {gpu}")
    count = build_metadata_index(force_rebuild=True)
    print(f"[rag] Indexed {count} books.")
    return 0 if count >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
