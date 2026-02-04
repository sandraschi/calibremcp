"""Log file API for tail, filter, level."""

import os
from pathlib import Path

from fastapi import APIRouter, Query

router = APIRouter()


# Log file path: env LOG_FILE, or logs/calibremcp.log relative to project root
def _log_path() -> Path | None:
    if os.environ.get("LOG_FILE"):
        p = Path(os.environ["LOG_FILE"])
        if p.is_absolute():
            return p if p.exists() else None
    # Project root: backend/app/api -> 5 levels up
    root = Path(__file__).resolve().parent.parent.parent.parent.parent
    candidates = [
        root / "logs" / "calibremcp.log",
        root / "logs" / "webapp.log",
        root / "log" / "calibremcp.log",
        Path("logs") / "calibremcp.log",
        Path("logs") / "webapp.log",
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return None


@router.get("")
async def get_logs(
    tail: int = Query(500, ge=1, le=10000, description="Last N lines"),
    filter: str | None = Query(None, description="Substring filter"),
    level: str | None = Query(None, description="Log level filter (DEBUG,INFO,WARNING,ERROR)"),
):
    """Return tail of log file with optional filter and level filter. Uses rotation-safe read."""
    log_path = _log_path()
    if not log_path:
        return {"lines": [], "total": 0, "error": "No log file found"}
    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        return {"lines": [], "total": 0, "error": str(e)}

    # Apply filters
    if filter:
        fl = filter.lower()
        lines = [ln for ln in lines if fl in ln.lower()]
    if level:
        lv = level.upper()
        lines = [ln for ln in lines if f'"level":"{lv}"' in ln or f'"level": "{lv}"' in ln]

    total = len(lines)
    lines = lines[-tail:] if tail < total else lines
    return {"lines": lines, "total": total, "file": str(log_path)}
