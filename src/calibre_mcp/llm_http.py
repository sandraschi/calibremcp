"""
OpenAI-compatible chat completions over HTTP (Ollama, LM Studio, cloud).

Used by ``transport`` when CalibreMCP runs with ``--http`` so ``/api/v1/chat`` works
without the separate webapp backend. Env mirrors the webapp: ``LLM_PROVIDER``,
``LLM_BASE_URL``, ``LLM_API_KEY``.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from fastapi.responses import StreamingResponse

OLLAMA_DEFAULT = "http://127.0.0.1:11434"
LMSTUDIO_DEFAULT = "http://127.0.0.1:1234/v1"
OPENAI_DEFAULT = "https://api.openai.com/v1"

DEFAULT_SYSTEM = (
    "You are the CalibreMCP library assistant. Help with ebooks, Calibre metadata, "
    "search strategies, and reading suggestions. Be concise and accurate."
)


def get_llm_base_url(provider: str | None = None, base_url: str | None = None) -> str:
    if base_url and base_url.strip():
        return base_url.rstrip("/")
    p = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower()
    env_base = (os.getenv("LLM_BASE_URL") or "").strip()
    if env_base:
        return env_base.rstrip("/")
    if p in ("ollama",):
        return OLLAMA_DEFAULT
    if p in ("lmstudio", "lm_studio"):
        return LMSTUDIO_DEFAULT
    return OPENAI_DEFAULT


def get_llm_api_key() -> str:
    return (os.getenv("LLM_API_KEY") or "").strip()


def extract_assistant_text(data: dict[str, Any]) -> str:
    msg = data.get("message")
    if isinstance(msg, dict):
        c = msg.get("content")
        if c is not None:
            return str(c)
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        inner = choices[0]
        if isinstance(inner, dict):
            m = inner.get("message")
            if isinstance(m, dict):
                c = m.get("content")
                if c is not None:
                    return str(c)
    return ""


async def chat_complete(
    messages: list[dict[str, str]],
    *,
    model: str = "llama3.2",
    stream: bool = False,
    provider: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any] | StreamingResponse:
    """
    Forward chat to Ollama ``/api/chat`` or OpenAI-compatible ``/chat/completions``.

    Returns:
        Parsed JSON dict on success (non-stream), or StreamingResponse for stream=True.
    """
    url = get_llm_base_url(provider, base_url)
    is_ollama = "ollama" in url.lower() or ":11434" in url

    if is_ollama:
        req_url = f"{url}/api/chat"
        payload: dict[str, Any] = {"model": model, "messages": messages, "stream": stream}
        if stream:

            async def _stream_ollama():
                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream("POST", req_url, json=payload) as r:
                        async for chunk in r.aiter_text():
                            yield chunk

            return StreamingResponse(_stream_ollama(), media_type="text/event-stream")

        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(req_url, json=payload)
            if r.status_code != 200:
                return {
                    "success": False,
                    "error": "llm_request_failed",
                    "detail": r.text[:2000],
                    "status": r.status_code,
                }
            try:
                data = r.json()
            except Exception as e:
                return {"success": False, "error": "invalid_json", "detail": str(e)}
            text = extract_assistant_text(data)
            return {
                "success": True,
                "response": text,
                "raw": data,
                "provider": "ollama",
            }

    req_url = f"{url.rstrip('/')}/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    key = get_llm_api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    payload = {"model": model, "messages": messages, "stream": stream}

    if stream:

        async def _stream_openai():
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", req_url, json=payload, headers=headers) as r:
                    async for chunk in r.aiter_text():
                        yield chunk

        return StreamingResponse(_stream_openai(), media_type="text/event-stream")

    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(req_url, json=payload, headers=headers)
        if r.status_code != 200:
            return {
                "success": False,
                "error": "llm_request_failed",
                "detail": r.text[:2000],
                "status": r.status_code,
            }
        try:
            data = r.json()
        except Exception as e:
            return {"success": False, "error": "invalid_json", "detail": str(e)}
        text = extract_assistant_text(data)
        return {
            "success": True,
            "response": text,
            "raw": data,
            "provider": "openai-compatible",
        }
