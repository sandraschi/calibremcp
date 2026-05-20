# Calibre Plugin Development Guide

Reference doc for developing Calibre plugins in this workspace.
Current Calibre version target: 9.x (Apr 2026). Python 3.12 embedded.

---

## Language & Runtime

Calibre embeds its own Python interpreter — currently Python 3.12 (bundled with Calibre 9.x).
You do NOT use the system Python or any venv. You cannot `pip install` into it.

Third-party pure-Python libraries can be bundled inside the plugin ZIP itself.
C extensions are not possible unless pre-compiled against Calibre's exact Python build.

UI toolkit: PyQt6 (via Calibre's own bindings, accessed through `calibre.gui2`).
Do not import PyQt6 directly — always go through `calibre.gui2` so you get Calibre's patched Qt.

---

## Plugin Types

| Type | Base class | Use case |
|------|-----------|---------|
| Interface action | `calibre.customize.InterfaceActionBase` | Toolbar button / menu item — most common |
| Metadata source | `calibre.ebooks.metadata.sources.base.Source` | Fetch metadata from external source |
| File type | `calibre.customize.FileTypePlugin` | Hook into import/export of a format |
| Catalog | `calibre.library.catalogs.epub_mobi.CatalogPlugin` | Generate catalogs |
| Editor tool | `calibre.gui2.tweak_book.plugin.Tool` | Add tools to the EPUB editor |
| Store | `calibre.gui2.store.StoreBase` | Ebook store integration |

For "do something with the library via a button", use `InterfaceActionBase`.

---

## ZIP Structure

A Calibre plugin is a ZIP file. The contents must follow this layout:

```
plugin-import-name-YOUR_UNIQUE_NAME.txt   ← empty file; filename sets the import name
__init__.py                                ← plugin class + metadata
action.py                                  ← InterfaceAction subclass (actual logic)
config.py                                  ← JSONConfig-based preferences (optional)
images/
    icon.png                               ← toolbar icon (32x32 or 48x48 PNG)
translations/                              ← optional; .mo files for i18n
```

The import name (from the .txt filename) must be a valid Python identifier and globally unique.
It is used in all internal imports:

```python
from calibre_plugins.calibreops_bridge.client import CalibreopsClient
```

---

## `__init__.py` — Metadata

```python
from calibre.customize import InterfaceActionBase

class CalibreOpsBridgePlugin(InterfaceActionBase):
    name                    = 'CalibreOps Bridge'
    description             = 'Surface calibreops MCP semantic search in Calibre'
    supported_platforms     = ['windows', 'osx', 'linux']
    author                  = 'sandraschi'
    version                 = (0, 1, 0)
    minimum_calibre_version = (6, 0, 0)
    actual_plugin           = 'calibre_plugins.calibreops_bridge.action:CalibreOpsBridgeAction'
    can_be_disabled         = True
```

---

## `action.py` — InterfaceAction subclass

```python
from calibre.gui2.actions import InterfaceAction

class CalibreOpsBridgeAction(InterfaceAction):
    name = 'CalibreOps Bridge'
    action_spec = ('CalibreOps', None, 'Search library via calibreops', None)

    def genesis(self):
        # Called once when plugin is loaded
        self.qaction.triggered.connect(self.show_search_dialog)

    def show_search_dialog(self):
        from calibre_plugins.calibreops_bridge.ui.search_dialog import SearchDialog
        d = SearchDialog(self.gui, self.qaction.icon())
        d.exec()
```

---

## Resources

Load bundled files (images, text) with:

```python
from calibre.customize.ui import plugin_for_input_format
from calibre_plugins.calibreops_bridge import CalibreOpsBridgePlugin
data = get_resources('images/calibreops.png')
```

Or via `__init__.py`:
```python
from calibre.customize import get_resources
icon_data = get_resources('images/calibreops.png')
```

---

## Database Access

Inside an InterfaceAction, `self.db` is the current library's DB proxy:

```python
db = self.db.new_api                        # new-style API
ids = db.all_book_ids()
title = db.field_for('title', book_id)
authors = db.field_for('authors', book_id)
formats = db.formats(book_id)
```

The full API: https://manual.calibre-ebook.com/db_api.html

---

## Preferences

Use `JSONConfig` — Calibre's built-in JSON-backed config:

```python
from calibre.utils.config import JSONConfig
prefs = JSONConfig('plugins/calibreops_bridge')
prefs.defaults['server_url'] = 'http://localhost:10720'
prefs.defaults['timeout']    = 10
```

Config is stored in Calibre's config directory automatically.
Expose a preferences dialog via `config.py` with a `ConfigWidget` subclass.

---

## Qt Dialogs

Always use Calibre's Qt wrappers:

```python
from calibre.gui2 import QDialog, Application
from calibre.gui2.widgets import LineEdit
# NOT: from PyQt6.QtWidgets import QDialog
```

Use `QDialog.exec()` for modal dialogs.

---

## Signals & Threading

Long-running operations (HTTP calls to calibreops) must run off the main thread.
Use Calibre's `ThreadedJob` or plain `QThread`:

```python
from calibre.gui2.threaded_jobs import ThreadedJob

def run_search(job):
    job.result = my_http_call(job.query)

job = ThreadedJob('calibreops_search', 'Searching via calibreops...', run_search, ...)
self.gui.job_manager.run_threaded_job(job)
```

Or use a simple `QThread` subclass for lighter tasks.

---

## HTTP / External calls

Use Python's stdlib `urllib.request` — it is always available.
For JSON APIs this is sufficient and avoids bundling dependencies.

```python
import urllib.request, json

def query_calibreops(endpoint, payload):
    url = f'http://localhost:10720{endpoint}'
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data,
          headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())
```

If you need `httpx` or `requests`, bundle them as pure-Python sources inside the ZIP.
