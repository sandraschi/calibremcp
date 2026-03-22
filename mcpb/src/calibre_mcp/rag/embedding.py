"""
Embedding for RAG: Ollama (nomic-embed-text) with FastEmbed fallback.

Ollama preferred when available; FastEmbed for headless/server without Ollama.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

OLLAMA_EMBED_DEFAULT = "http://127.0.0.1:11434"
OLLAMA_EMBED_MODEL = "nomic-embed-text"


def _embed_via_ollama(texts: List[str], base_url: str, model: str) -> List[List[float]]:
    import httpx

    out: List[List[float]] = []
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


def _embed_via_fastembed(texts: List[str], model: str) -> List[List[float]]:
    try:
        from fastembed import TextEmbedding
    except ImportError:
        raise ImportError("Install RAG extras: pip install calibre-mcp[rag]")
    embedder = TextEmbedding(model_name=model)
    embeddings = list(embedder.embed(texts))
    return [list(e) for e in embeddings]


def embed_texts(
    texts: List[str],
    *,
    use_ollama: bool = True,
    ollama_base_url: str = OLLAMA_EMBED_DEFAULT,
    ollama_model: str = OLLAMA_EMBED_MODEL,
    fastembed_model: str = "BAAI/bge-small-en-v1.5",
) -> List[List[float]]:
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
    return _embed_via_fastembed(texts, fastembed_model)
