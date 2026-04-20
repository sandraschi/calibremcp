"""
Ollama client for CalibreMCP plugin.
Direct HTTP calls to local Ollama instance — no external dependencies.
Used for LLM synthesis in research/analysis dialogs without needing
Claude Desktop or any sampling-capable MCP client.
"""

import json
import urllib.request
from collections.abc import Iterator


def _get_ollama_url() -> str:
    from calibre_plugins.calibre_mcp_integration.config import prefs
    return prefs.get("ollama_url", "http://127.0.0.1:11434").rstrip("/")


def _get_ollama_model() -> str:
    from calibre_plugins.calibre_mcp_integration.config import prefs
    return prefs.get("ollama_model", "gemma3:12b")


def is_available() -> bool:
    """Check if Ollama is running and reachable."""
    try:
        req = urllib.request.Request(_get_ollama_url() + "/api/tags")
        with urllib.request.urlopen(req, timeout=2):
            return True
    except Exception:
        return False


def list_models() -> list[str]:
    """Return list of locally available model names."""
    try:
        req = urllib.request.Request(_get_ollama_url() + "/api/tags")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def generate(prompt: str, system: str = "", model: str = "",
             timeout: int = 120) -> str:
    """Single-shot generate — waits for full response, returns text.

    Uses /api/generate with stream=false.
    Falls back gracefully if Ollama is not running.
    """
    url = _get_ollama_url() + "/api/generate"
    payload = {
        "model": model or _get_ollama_model(),
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 3000},
    }
    if system:
        payload["system"] = system

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            result = json.loads(r.read().decode())
            return result.get("response", "").strip()
    except urllib.error.URLError:
        return ""
    except Exception as e:
        return f"[Ollama error: {e}]"


def generate_streaming(prompt: str, system: str = "",
                        model: str = "") -> Iterator[str]:
    """Streaming generate — yields text tokens as they arrive.

    Usage:
        for token in generate_streaming(prompt):
            text_widget.insertPlainText(token)
            QApplication.processEvents()
    """
    url = _get_ollama_url() + "/api/generate"
    payload = {
        "model": model or _get_ollama_model(),
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": 0.3, "num_predict": 3000},
    }
    if system:
        payload["system"] = system

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            for line in r:
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line.decode())
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done"):
                        break
                except json.JSONDecodeError:
                    continue
    except Exception:
        return
