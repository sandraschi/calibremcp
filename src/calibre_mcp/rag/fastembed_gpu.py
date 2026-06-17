"""Fleet-standard FastEmbed GPU bootstrap."""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE_CPU = 64
EMBED_BATCH_SIZE_GPU = 256


def _env_flag(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in ("1", "true", "yes", "on")


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[3]


def embed_use_gpu(repo_root: Path | None = None) -> bool:
    if _env_flag("RAG_GPU") or _env_flag("MCD_RAG_GPU"):
        return True
    root = repo_root or repo_root_from_here()
    if (root / ".venv" / "rag-gpu-mode").is_file():
        return True
    return False


def create_text_embedding(
    model_name: str,
    cache_dir: str,
    *,
    repo_root: Path | None = None,
    batch_cpu: int = EMBED_BATCH_SIZE_CPU,
    batch_gpu: int = EMBED_BATCH_SIZE_GPU,
):
    from fastembed import TextEmbedding

    root = repo_root or repo_root_from_here()
    if embed_use_gpu(root):
        try:
            model = TextEmbedding(
                model_name=model_name,
                cache_dir=cache_dir,
                providers=["CUDAExecutionProvider"],
            )
            providers = model.model.model.get_providers()
            if "CUDAExecutionProvider" in providers:
                logger.info("FastEmbed providers: %s", providers)
                return model, "cuda", batch_gpu
            logger.warning("CUDAExecutionProvider unavailable (%s); using CPU", providers)
        except Exception as exc:
            logger.warning("GPU embed init failed (%s); using CPU", exc)

    model = TextEmbedding(model_name=model_name, cache_dir=cache_dir)
    logger.info("FastEmbed providers: %s", model.model.model.get_providers())
    return model, "cpu", batch_cpu
