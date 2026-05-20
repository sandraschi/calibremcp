# Local Testing Guide

How to run, test, and iterate on Calibre plugins without repeatedly packaging ZIPs.

---

## Option 1 — calibre-customize (install from folder, recommended)

Install a plugin directly from source directory, then launch Calibre:

```powershell
calibre-customize -b D:\Dev\repos\calibre-plugins\calibreops-bridge
calibre
```

After any code change: repeat those two lines. Calibre must be restarted to reload plugins.

To uninstall:
```powershell
calibre-customize -r "CalibreOps Bridge"
```

---

## Option 2 — CALIBRE_DEVELOP_FROM (source-mounted, for core hacking)

Set an environment variable pointing to the src folder.
Calibre then loads ALL Python code from your source tree rather than its bundled copy.
This is for hacking Calibre internals, not usually needed for plugin development.

```powershell
$env:CALIBRE_DEVELOP_FROM = "D:\Dev\repos\calibre-plugins"
calibre
```

---

## Option 3 — calibre-debug GUI launch (console attached)

Launches the Calibre GUI with stdout attached so `print()` statements are visible:

```powershell
calibre-debug -g
```

This is the primary debug launch method. All `print()` and traceback output appears in
the console. Use this whenever you need to see plugin output.

Combine with Option 1:
```powershell
calibre-customize -b D:\Dev\repos\calibre-plugins\calibreops-bridge; calibre-debug -g
```

---

## Option 4 — Calibre Python shell (interactive API exploration)

Calibre has a built-in Python shell that runs inside its embedded interpreter:

Preferences → Miscellaneous → Open Calibre Python shell

Use this to explore the `db` API against your live 13k-book library before
writing plugin code. Example session:

```python
db = self.current_db.new_api
ids = list(db.all_book_ids())[:5]
for i in ids:
    print(db.field_for('title', i), db.field_for('authors', i))
```

You can also launch it from command line:
```powershell
calibre-debug --exec-file D:\Dev\repos\calibre-plugins\scratch\explore.py
```

---

## Build script — packaging the ZIP

`build.py` in each plugin folder packages the ZIP for manual installation or distribution:

```python
# build.py
import zipfile, os, sys

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_NAME = 'calibreops_bridge'
OUTPUT = os.path.join(PLUGIN_DIR, '..', f'{PLUGIN_NAME}.zip')

EXCLUDE = {'.git', '__pycache__', '*.pyc', 'build.py', '*.zip'}

with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(PLUGIN_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for f in files:
            if any(f.endswith(x.lstrip('*')) for x in EXCLUDE if '*' in x):
                continue
            path = os.path.join(root, f)
            arcname = os.path.relpath(path, PLUGIN_DIR)
            zf.write(path, arcname)

print(f'Built: {OUTPUT}')
```

Run with Calibre's Python (not your system Python):
```powershell
calibre-debug D:\Dev\repos\calibre-plugins\calibreops-bridge\build.py
```

---

## Checking calibreops is reachable

Before testing integration, verify the calibreops MCP server is up:

```powershell
Invoke-RestMethod http://localhost:10720/health
```

Or from Calibre's Python shell:
```python
import urllib.request
urllib.request.urlopen('http://localhost:10720/health', timeout=5).read()
```

---

## Logging

Inside plugin code, use Calibre's logger rather than `print` for production:

```python
from calibre.utils.logging import default_log
default_log.info('calibreops_bridge: query sent')
default_log.error('calibreops_bridge: connection failed')
```

In debug mode (`calibre-debug -g`) both `print()` and the logger write to console.

---

## Common errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ImportError: No module named calibre_plugins.X` | Wrong import name or missing .txt marker file | Check `plugin-import-name-X.txt` filename matches import |
| Plugin not appearing in toolbar | `genesis()` not called or `action_spec` wrong | Check `action.py` and restart Calibre |
| `RuntimeError: main thread is not in main loop` | HTTP call on main Qt thread | Move to QThread or ThreadedJob |
| Dialog opens then immediately closes | `exec()` not called (called `show()` instead) | Use `dialog.exec()` for modal |
