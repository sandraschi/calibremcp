# -*- mode: python ; coding: utf-8 -*-

import sys
import sysconfig
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

_spec_root = Path(SPECPATH)
sys.path[:0] = [
    str(_spec_root / "webapp" / "backend"),
    str(_spec_root / "src"),
]
for _preload in ("app.main", "calibre_mcp.server", "calibre_mcp.__main__"):
    try:
        __import__(_preload)
    except Exception as _preload_exc:
        print(f"WARN: spec preload {_preload}: {_preload_exc}")


binaries = []

_sqlite3_bin = Path(sysconfig.get_config_var("prefix")) / "DLLs" / "_sqlite3.pyd"
if _sqlite3_bin.exists():
    binaries.append((str(_sqlite3_bin), "."))

_stdlib_dir = Path(sysconfig.get_config_var("prefix")) / "Lib"

datas = [

    ("src/calibre_mcp", "calibre_mcp"),

    ("webapp/backend/app", "app"),
    ("webapp/frontend/out", "webapp/frontend/out"),

]

for _mod in ("difflib.py", "statistics.py", "pydoc.py"):
    _mod_path = _stdlib_dir / _mod
    if _mod_path.exists():
        datas.append((str(_mod_path), "."))
_pydoc_data = _stdlib_dir / "pydoc_data"
if _pydoc_data.exists():
    datas.append((str(_pydoc_data), "pydoc_data"))



for pkg in (
    "fastmcp",
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic_core",
    "annotated_doc",
    "annotated_types",
    "starlette",
    "httpx",
    "httpcore",
    "anyio",
    "sniffio",
    "prefab_ui",
    "mcp",
    "h11",
    "httptools",
    "cachetools",
    "key_value",
    "py-key-value-aio",
    "beartype",
    "websockets",
    "watchfiles",
    "sqlalchemy",
    "greenlet",
    "aiohttp",
    "multidict",
    "yarl",
    "frozenlist",
    "aiosignal",
    "attrs",
    "propcache",
    "aiohappyeyeballs",
    "structlog",
    "tenacity",
    "python-dotenv",
    "lancedb",
    "fastembed",
    "ebooklib",
    "bs4",
    "lxml",
    "rich",
    "psutil",
    "keyring",
):

    try:

        datas += copy_metadata(pkg)

    except Exception:

        pass



hiddenimports = collect_submodules("calibre_mcp")

hiddenimports += collect_submodules("app")



for pkg in (
    "fastmcp",
    "mcp",
    "fastapi",
    "starlette",
    "pydantic",
    "pydantic_core",
    "annotated_doc",
    "annotated_types",
    "httpx",
    "httpcore",
    "anyio",
    "h11",
    "httptools",
    "cachetools",
    "key_value",
    "uvicorn",
    "beartype",
    "websockets",
    "watchfiles",
    "sqlalchemy",
    "greenlet",
    "aiohttp",
    "multidict",
    "yarl",
    "frozenlist",
    "aiosignal",
    "attrs",
    "propcache",
    "aiohappyeyeballs",
    "structlog",
    "prefab_ui",
    "lancedb",
    "tenacity",
    "beautifulsoup4",
    "bs4",
    "numpy",
    "ebooklib",
    "fitz",
    "pymupdf",
    "keyring",
    "psutil",
    "rich",
    "fastembed",
    "pyarrow",
    "jwt",
):

    try:

        pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)

        datas += pkg_datas

        binaries += pkg_binaries

        hiddenimports += pkg_hidden

    except Exception:

        pass



hiddenimports += [

    "fastmcp",

    "mcp",

    "fastapi",

    "starlette",

    "h11",

    "httptools",

    "beartype",

    "beartype.claw",

    "beartype.claw._ast",

    "beartype.claw._ast._clawaststar",

    "websockets",

    "websockets.legacy",

    "websockets.legacy.handshake",

    "cachetools",

    "key_value",

    "key_value.aio",

    "key_value.aio.stores",

    "key_value.aio.stores.memory",

    "uvicorn.logging",

    "uvicorn.loops",

    "uvicorn.loops.asyncio",

    "uvicorn.protocols",

    "uvicorn.protocols.http",

    "uvicorn.protocols.http.httptools_impl",

    "uvicorn.protocols.http.h11_impl",

    "uvicorn.lifespan",

    "uvicorn.lifespan.on",

    "app.main",

    "calibre_mcp.server",

    "sqlite3",

    "_sqlite3",

    "netrc",

    "difflib",

    "statistics",

    "pydoc",

    "jwt",

]



a = Analysis(

    ["run_server.py"],

    pathex=["src", "webapp/backend"],

    binaries=binaries,

    datas=datas,

    hiddenimports=hiddenimports,

    hookspath=[],
    
    hooksconfig={},

    runtime_hooks=['hooks/runtime-opentelemetry.py'],
    excludes=[

        "torch",

        "torchvision",

        "torchaudio",

        "tensorboard",

    ],

    noarchive=True,

    optimize=0,

)

# Strip .dist-info but preserve metadata for packages that need it at runtime
_keep_dist = ['fastmcp-', 'mcp-', 'prefab_ui-', 'opentelemetry-', 'email_validator-', 'annotated_doc-', 'annotated-doc-']
_saved = [e for e in a.datas if isinstance(e, tuple) and any(k in str(e[0]) for k in _keep_dist) and '.dist-info' in str(e[0])]
for _list in [a.datas, a.binaries, a.zipfiles, a.scripts]:
    _list[:] = [e for e in _list if not (isinstance(e, tuple) and '.dist-info' in str(e[0]))]
a.datas.extend(_saved)

pyz = PYZ(a.pure)



exe = EXE(

    pyz,

    a.scripts,

    a.binaries,

    a.datas,

    [],
    

    name="calibre-mcp-backend",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=False,

    upx_exclude=[],
    runtime_tmpdir=None,

    console=True,

    disable_windowed_traceback=False,

    argv_emulation=False,

    target_arch=None,

    codesign_identity=None,

    entitlements_file=None,

)








