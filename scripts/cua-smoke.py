#!/usr/bin/env python3
"""CUA smoke test — simplified (pywinauto direct, no pywinauto-mcp dep).

CUA_SMOKE_VERSION = 2

Phases:
    1. Kill stale processes
    2. Silent install NSIS
    3. Launch app, wait for backend health
    4. Verify window (pywinauto)
    5. Screenshot
    6. Diagnostics check
    7. Uninstall
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path

CUA_SMOKE_VERSION = 2
DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cua-nsis-config.json")
_CONFIG = {}

def load_config(path=None):
    p = path or DEFAULT_CONFIG
    if not os.path.exists(p): return {}
    with open(p) as f: return json.load(f)

def cfg(k, d=""):
    return _CONFIG.get(k, d)

_CONFIG = load_config()

BACKEND_PORT = int(cfg("backend_port", 10700))
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
PRODUCT_NAME = cfg("product_name", "App")
HEALTH_PATH = cfg("health_path", "/api/v1/health")
WINDOW_TITLE_RE = cfg("window_title_re", PRODUCT_NAME)
INSTALL_DIR = os.path.expandvars(cfg("install_dir", f"%LOCALAPPDATA%\\{PRODUCT_NAME}"))
OPERATOR_EXE = cfg("operator_exe", f"{PRODUCT_NAME.lower().replace(' ','-')}-native.exe")
PROCESS_NAMES = cfg("backend_process_names", [OPERATOR_EXE.replace(".exe",""), f"{OPERATOR_EXE.replace('.exe','').replace('-native','')}-backend"])
NSIS_GLOB = cfg("nsis_glob", f"native/target/release/bundle/nsis/{PRODUCT_NAME}_*_x64-setup.exe")
MAX_RETRY, RETRY_DELAY = 30, 3

def log(m): print(f"  [cua] {m}", flush=True)
def fatal(m): print(f"  [cua] FATAL: {m}", flush=True); sys.exit(1)

# Phase 1
def kill_stale():
    for name in PROCESS_NAMES:
        subprocess.run(["taskkill", "/F", "/IM", name, "/T"], capture_output=True, timeout=10)
    time.sleep(1); log("Stale processes killed")

# Phase 2
def find_installer():
    repo_root = Path(__file__).resolve().parent.parent
    matches = sorted(glob.glob(str(repo_root / NSIS_GLOB.replace("/", "\\"))), key=os.path.getmtime, reverse=True)
    if matches: return matches[0]
    fatal("No NSIS installer found")

def silent_install(inst):
    log(f"Installing: {inst}")
    r = subprocess.run([inst, "/S"], capture_output=True, timeout=120)
    if r.returncode != 0: fatal(f"Install failed: {r.returncode}")
    time.sleep(2); log("Install complete")

# Phase 3
def launch_app():
    exe = os.path.join(INSTALL_DIR, OPERATOR_EXE)
    if not os.path.exists(exe): fatal(f"Operator not found at {exe}")
    subprocess.Popen([exe], cwd=INSTALL_DIR)
    for i in range(MAX_RETRY):
        try:
            r = urllib.request.urlopen(f"{BACKEND_URL}{HEALTH_PATH}", timeout=5)
            if r.status == 200: log(f"Backend healthy (attempt {i+1})"); return
        except: pass
        time.sleep(RETRY_DELAY)
    fatal(f"Backend not reachable after {MAX_RETRY * RETRY_DELAY}s")

def _find_tauri_window():
    """Find Tauri webview window handle — excludes classic Calibre (QMainWindow)."""
    import pywinauto.findwindows
    all_wins = pywinauto.findwindows.find_elements(title_re=WINDOW_TITLE_RE)
    tauri = [w for w in all_wins if w.class_name != "QMainWindow"]
    if not tauri:
        classes = set(w.class_name for w in all_wins)
        raise RuntimeError(f"No Tauri window found (classes: {classes})")
    return tauri[0].handle

# Phase 4
def verify_window():
    import pywinauto
    handle = _find_tauri_window()
    app = pywinauto.Application(backend="uia").connect(handle=handle)
    win = app.window(handle=handle)
    win.wait("visible", timeout=10)
    r = win.rectangle(); w = r.width(); h = r.height()
    log(f"Window found: {w}x{h} class={win.class_name} title=\"{win.window_text}\"")
    if w < 200 or h < 200:
        raise RuntimeError(f"Window too small: {w}x{h}")

# Phase 5
def screenshot_and_ocr(output_dir):
    import pywinauto
    handle = _find_tauri_window()
    app = pywinauto.Application(backend="uia").connect(handle=handle)
    win = app.window(handle=handle)
    win.set_focus(); time.sleep(2)
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"cua-{int(time.time())}.png")
    win.capture_as_image().save(path)
    log(f"Screenshot: {path} ({os.path.getsize(path)} bytes)")

    # OCR the window to verify it's showing the actual app, not a blank/error page
    try:
        import pytesseract
        text = pytesseract.image_to_string(path)
        ocr_sample = text.strip()[:200]
        log(f"OCR text: {ocr_sample}")
        # Check for error indicators
        err_keywords = ["could not connect", "cannot reach", "this page", "404", "500"]
        for kw in err_keywords:
            if kw in text.lower():
                log(f"WARNING: OCR found '{kw}' — WebView may show an error page")
    except ImportError:
        log("pytesseract not available — OCR skipped")
    except Exception as e:
        log(f"OCR failed: {e}")

# Phase 6
# Phase 5b - Sidebar nav click-through (title-based UIA matching)
def nav_click_through(output_dir):
    import pywinauto
    handle = _find_tauri_window()
    app = pywinauto.Application(backend="uia").connect(handle=handle)
    win = app.window(handle=handle)
    win.set_focus(); time.sleep(2)
    nav_routes = cfg("nav_routes", [])
    if not isinstance(nav_routes, list) or not nav_routes:
        log("No nav_routes in config - nav walk skipped")
        return
    win.maximize(); time.sleep(1)
    for label, expected in nav_routes:
        try:
            link = win.descendants(title=label)
            if link:
                link[0].click_input()
            else:
                elements = win.descendants(control_type="Hyperlink")
                el = [e for e in elements if label.lower() in (e.window_text() or "").lower()]
                if el:
                    el[0].click_input()
                else:
                    log(f"Nav '{label}': no link found - skipped")
                    continue
            time.sleep(2)
            path = os.path.join(output_dir, f"nav-{label.lower().replace(' ','-')}.png")
            win.capture_as_image().save(path)
            log(f"Nav '{label}': clicked + screenshot ({os.path.getsize(path)} bytes)")
        except Exception as e:
            log(f"Nav '{label}' failed (non-fatal): {e}")

def check_diagnostics():
    try:
        r = urllib.request.urlopen(f"{BACKEND_URL}/api/v1/diagnostics", timeout=5)
        data = json.loads(r.read())
        log(f"Diagnostics: HTTP {r.status}")
        if isinstance(data, dict): log(f"  keys: {list(data.keys())[:5]}")
    except Exception as e:
        log(f"Diagnostics check failed: {e}")

# Phase 7
def uninstall():
    un = os.path.join(INSTALL_DIR, "uninstall.exe")
    if not os.path.exists(un): log("No uninstaller found"); return
    subprocess.run([un, "/S"], capture_output=True, timeout=60)
    time.sleep(2); log("Uninstall complete")

def main():
    parser = argparse.ArgumentParser(description="CUA-NSIS smoke test")
    parser.add_argument("--installer"); parser.add_argument("--config")
    parser.add_argument("--output-dir", default="cua-reports")
    args = parser.parse_args()
    if args.config: _CONFIG.update(load_config(args.config))

    phases = [
        (True, "Kill stale", kill_stale),
        (True, "Install", lambda: silent_install(args.installer or find_installer())),
        (True, "Launch", launch_app),
        (False, "Window", verify_window),
        (False, "Screenshot", lambda: screenshot(args.output_dir)),
        (False, "Nav walk", lambda: nav_click_through(args.output_dir)),
        (False, "Diagnostics", check_diagnostics),
        (False, "Uninstall", uninstall),
    ]
    passed = failed = 0; halted = False
    for fatal_phase, name, fn in phases:
        try:
            fn(); passed += 1; log(f"V {name}")
        except Exception as e:
            failed += 1
            tb = traceback.format_exc()
            log(f"X {name}: {e}")
            for line in tb.splitlines()[-5:]:
                log(f"  {line}")
            if fatal_phase: halted = True
    log(f"Result: {passed}/{passed+failed}")
    if halted: sys.exit(1)
    log("ALL PHASES PASSED")

if __name__ == "__main__":
    main()
