# calibre-mcp — Build Log

> **Purpose:** Track build failures, regressions, and fixes during NSIS/PyInstaller builds.
> This is NOT a changelog (functional changes) — it records build-process issues
> so we can recover faster when a pattern repeats.

## 2026-06-23 v1.8.6

### PyInstaller runt (14 MB instead of 186 MB)

**Symptom:** Backend exe produced at 14 MB. All third-party packages missing from the bundle.
**Root cause:** `.venv` was deleted during cleanup and recreated with `uv sync`. The new venv did not include `pyinstaller` as a dependency. `uv run pyinstaller` fell back to the global uv tools PyInstaller, which runs in its own venv (no access to project packages).
**Fix:** `uv pip install pyinstaller` to install PyInstaller in the project venv.
**Detection:** Check backend exe size before NSIS build — should be ~180-190 MB.

### Circular import: StorageBackend

**Symptom:** `cannot import name 'StorageBackend' from partially initialized module 'calibre_mcp.storage'`
**Root cause:** `storage/__init__.py` imported `from .local import LocalStorage` at line 9, before `StorageBackend` class was defined at line 13. `local.py` then tried `from . import StorageBackend` which didn't exist yet.
**Fix:** Moved `from .local import LocalStorage` and `from .remote import RemoteStorage` after the `StorageBackend` class definition.
**Lesson:** `noarchive=True` changes the import order vs PYZ — circular imports that were masked by PYZ ordering surface as real crashes.

### Mismatched webpack JS hashes (blank UI)

**Symptom:** UI rendered unstyled (black text on white, "Loading…" spinner). JS bundle returned `index.html` instead of the actual JS file.
**Root cause:** The `out/` directory accumulated stale JS chunks from multiple partial rebuilds. The HTML referenced `webpack-foo.js` but the file on disk was `webpack-bar.js`.
**Fix:** `Remove-Item out/ -Recurse -Force` then clean rebuild via `build-tauri-frontend.ps1`.
**Detection:** Check that each `<script src>` in `out/index.html` matches a real file in `out/_next/static/chunks/`.

### pathlib.Path.replace() broke on Python 3.12

**Symptom:** `TypeError: Path.replace() takes 2 positional arguments but 3 were given` on startup → "Failed to fetch books (500)" in UI.
**Root cause:** Python 3.12 repurposed `Path.replace()` from string replacement to file rename. Code used `pathlib.Path(path).resolve().replace("\\", "/")` instead of `str(pathlib.Path(path).resolve()).replace("\\", "/")`.
**Fix:** Wrapped with `str()` before calling `.replace()`.
**Fleet audit:** 2 occurrences in `src/calibre_mcp/db/database.py` (lines 73, 80). Other fleet repos use the safe `str(pathobj).replace(...)` pattern.

### Fleet-wide: Missing pyvenv.cfg

**Symptom:** `No pyvenv.cfg file` when running `uv run python`.
**Root cause:** The `.venv` directory had packages installed but was missing `pyvenv.cfg` (the marker file that identifies a venv). Caused by deleting the .venv and running `uv sync` which doesn't recreate pyvenv.cfg.
**Fix:** `Remove-Item .venv -Recurse -Force; uv sync` — full recreation.
