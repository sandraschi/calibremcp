"""LLM API endpoints for chat (Ollama, LM Studio, OpenAI-compatible)."""

import logging

import httpx
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

OLLAMA_DEFAULT = "http://127.0.0.1:11434"
LMSTUDIO_DEFAULT = "http://127.0.0.1:1234/v1"
OPENAI_DEFAULT = "https://api.openai.com/v1"


def _get_base_url(provider: str | None = None, base_url: str | None = None) -> str:
    if base_url and base_url.strip():
        return base_url.rstrip("/")
    p = (provider or settings.LLM_PROVIDER).lower()
    if p in ("ollama",):
        return settings.LLM_BASE_URL or OLLAMA_DEFAULT
    if p in ("lmstudio", "lm_studio"):
        return settings.LLM_BASE_URL or LMSTUDIO_DEFAULT
    return settings.LLM_BASE_URL or OPENAI_DEFAULT


@router.get("/models")
async def list_models(
    provider: str | None = None,
    base_url: str | None = None,
):
    """List available models (Ollama/LM Studio/OpenAI-compatible)."""
    url = _get_base_url(provider, base_url)
    if "ollama" in url or ":11434" in url:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{url}/api/tags")
                if r.status_code != 200:
                    return {"models": [], "error": r.text}
                data = r.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return {"models": models, "provider": "ollama"}
        except Exception as e:
            logger.warning("Ollama models fetch failed: %s", e)
            return {"models": [], "error": str(e)}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {}
            key = settings.LLM_API_KEY
            if key:
                headers["Authorization"] = f"Bearer {key}"
            ep = f"{url.rstrip('/')}/models"
            r = await client.get(ep, headers=headers or None)
            if r.status_code != 200:
                return {"models": [], "error": r.text}
            data = r.json()
            items = data.get("data", data.get("models", []))
            if isinstance(items, list):
                names = [m.get("id") or m.get("name") or m for m in items if isinstance(m, dict)]
            else:
                names = []
            return {"models": names, "provider": "openai-compatible"}
    except Exception as e:
        logger.warning("Models fetch failed: %s", e)
        return {"models": [], "error": str(e)}


@router.post("/chat")
async def chat(
    messages: list[dict[str, str]] = Body(...),
    model: str = Body("llama3.2", description="Model name"),
    stream: bool = Body(False),
    provider: str | None = Body(None),
    base_url: str | None = Body(None),
):
    """Chat completion. Supports streaming."""
    url = _get_base_url(provider, base_url)
    if "ollama" in url or ":11434" in url:
        req_url = f"{url}/api/chat"
        payload = {"model": model, "messages": messages, "stream": stream}
        if stream:

            async def _stream():
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream("POST", req_url, json=payload) as r:
                        async for chunk in r.aiter_text():
                            yield chunk

            return StreamingResponse(_stream(), media_type="text/event-stream")
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(req_url, json=payload)
            if r.status_code != 200:
                return {"error": r.text, "status": r.status_code}
            return r.json()
    req_url = f"{url}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if settings.LLM_API_KEY:
        headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"
    payload = {"model": model, "messages": messages, "stream": stream}
    if stream:

        async def _stream_openai():
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", req_url, json=payload, headers=headers) as r:
                    async for chunk in r.aiter_text():
                        yield chunk

        return StreamingResponse(_stream_openai(), media_type="text/event-stream")
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(req_url, json=payload, headers=headers)
        if r.status_code != 200:
            return {"error": r.text, "status": r.status_code}
        return r.json()
