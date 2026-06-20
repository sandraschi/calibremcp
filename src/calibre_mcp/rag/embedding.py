"""
Embedding for RAG: Ollama (nomic-embed-text) with FastEmbed fallback.

Ollama preferred when available; FastEmbed for headless/server without Ollama.
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_FASTEMBED_CACHE: dict[str, Any] = {}


def _get_fastembed(model: str, cache_dir: str | None = None) -> Any:
    """Return a cached TextEmbedding instance (lazy singleton per model name)."""
    key = f"{model}:{cache_dir or ''}"
    if key not in _FASTEMBED_CACHE:
        from calibre_mcp.rag.fastembed_gpu import create_text_embedding, repo_root_from_here

        model_obj, device, _batch = create_text_embedding(
            model,
            cache_dir or "",
            repo_root=repo_root_from_here(),
        )
        _FASTEMBED_CACHE[key] = model_obj
        logger.info("[rag] FastEmbed device: %s", device)
    return _FASTEMBED_CACHE[key]


OLLAMA_EMBED_DEFAULT = "http://127.0.0.1:11434"
OLLAMA_EMBED_MODEL = "nomic-embed-text"


def _embed_via_ollama(texts: list[str], base_url: str, model: str) -> list[list[float]]:
    import httpx

    out: list[list[float]] = []
    for t in texts:
        try:
            r = httpx.post(
                f"{base_url.rstrip('/')}/api/embeddings",
                json={"model": model, "prompt": t},
                timeout=60.0,
            )
            if r.status_code != 200:
                raise RuntimeError(f"Ollama embed {r.status_code}: {r.text[:200]}")
            data = r.json()
            emb = data.get("embedding")
            if not emb:
                raise RuntimeError("No embedding in Ollama response")
            out.append(emb)
        except Exception as e:
            logger.warning("Ollama embed failed for chunk: %s", e)
            raise
    return out


def _embed_via_fastembed(
    texts: list[str], model: str, cache_dir: str | None = None
) -> list[list[float]]:
    import importlib.util

    if importlib.util.find_spec("fastembed") is None:
        raise ImportError("Install RAG extras: pip install calibre-mcp[rag]")
    embedder = _get_fastembed(model, cache_dir)
    embeddings = list(embedder.embed(texts))
    return [list(e) for e in embeddings]


def embed_texts(
    texts: list[str],
    *,
    use_ollama: bool = True,
    ollama_base_url: str = OLLAMA_EMBED_DEFAULT,
    ollama_model: str = OLLAMA_EMBED_MODEL,
    fastembed_model: str = "BAAI/bge-small-en-v1.5",
    cache_dir: str | Path | None = None,
) -> list[list[float]]:
    """
    Embed a list of texts. Tries Ollama first if use_ollama else FastEmbed.
    """
    if not texts:
        return []
    if use_ollama:
        try:
            return _embed_via_ollama(texts, ollama_base_url, ollama_model)
        except Exception as e:
            logger.info("Ollama embed unavailable (%s), falling back to FastEmbed", e)
    return _embed_via_fastembed(
        texts, fastembed_model, cache_dir=str(cache_dir) if cache_dir else None
    )
