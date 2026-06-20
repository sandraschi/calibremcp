"""
Windows: FastMCP's SkillProvider uses Path.read_text() with the process default
encoding (often cp1252), which fails on UTF-8 SKILL.md files.

We patch pathlib.Path.read_text only for paths under configured skill roots so
markdown reads use UTF-8 with replacement for invalid bytes.
"""

from __future__ import annotations

import pathlib
from collections.abc import Sequence
from pathlib import Path
from typing import Any

_ORIGINAL_READ_TEXT = Path.read_text
_PATCH_INSTALLED = False
_ROOTS: list[Path] = []


def _normalize_roots(roots: Sequence[str | Path]) -> list[Path]:
    out: list[Path] = []
    for r in roots:
        try:
            out.append(Path(r).resolve())
        except OSError:
            out.append(Path(r))
    return out


def _under_any_root(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    for root in _ROOTS:
        try:
            if resolved.is_relative_to(root):
                return True
        except (ValueError, OSError):
            continue
    return False


def _patched_read_text(self: Path, *args: Any, **kwargs: Any) -> str:
    if args:
        return _ORIGINAL_READ_TEXT(self, *args, **kwargs)
    if kwargs.get("encoding") is None and _under_any_root(self):
        merged = dict(kwargs)
        merged.setdefault("encoding", "utf-8")
        merged.setdefault("errors", "replace")
        return _ORIGINAL_READ_TEXT(self, *args, **merged)
    return _ORIGINAL_READ_TEXT(self, *args, **kwargs)


def install_skills_utf8_read_patch(roots: Sequence[str | Path]) -> None:
    """Apply Path.read_text UTF-8 behavior for paths under the given skill roots."""
    global _PATCH_INSTALLED, _ROOTS
    _ROOTS = _normalize_roots(roots)
    if Path.read_text is not _patched_read_text:
        pathlib.Path.read_text = _patched_read_text  # type: ignore[method-assign]
        _PATCH_INSTALLED = True


def is_skills_utf8_patch_active() -> bool:
    return _PATCH_INSTALLED
