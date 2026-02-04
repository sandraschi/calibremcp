"""Shared cache for libraries list and API response caching."""

import time
from typing import Any

# TTL cache for expensive API responses (authors, tags)
_ttl_cache: dict[str, tuple[Any, float]] = {}
_TTL_SECONDS = 60


def _ttl_key(prefix: str, **kwargs: Any) -> str:
    parts = [str(k) + "=" + str(v) for k, v in sorted(kwargs.items()) if v is not None]
    return f"{prefix}:{':'.join(parts)}"


def get_ttl_cached(key: str) -> Any | None:
    now = time.monotonic()
    if key in _ttl_cache:
        val, expires = _ttl_cache[key]
        if now < expires:
            return val
        del _ttl_cache[key]
    return None


def set_ttl_cached(key: str, value: Any, ttl: int = _TTL_SECONDS) -> None:
    _ttl_cache[key] = (value, time.monotonic() + ttl)


def invalidate_ttl_cache() -> None:
    """Call when library switches."""
    global _ttl_cache
    _ttl_cache.clear()


_libraries_cache: dict = {
    "libraries": [],
    "current_library": None,
    "total_libraries": 0,
    "loaded": False,
}


def get_libraries_cache() -> dict:
    return _libraries_cache


def update_libraries_cache(libraries: list, current_library, total_libraries: int) -> None:
    global _libraries_cache
    _libraries_cache["libraries"] = libraries
    _libraries_cache["current_library"] = current_library
    _libraries_cache["total_libraries"] = total_libraries
    _libraries_cache["loaded"] = True


def update_current_library(current: str) -> None:
    global _libraries_cache
    _libraries_cache["current_library"] = current
    invalidate_ttl_cache()
