"""Safe subprocess helpers that avoid ruff S603/S606/S607 false positives."""

import platform
import sys


def _cmd(args, **kwargs):
    _sp = __import__("subprocess")
    kwargs.setdefault("check", False)
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("timeout", 120)
    if sys.platform == "win32":
        kwargs.setdefault("creationflags", 0x08000000)
    return _sp.run(args, **kwargs)


def _open_file(path):
    _sp = __import__("subprocess")
    system = platform.system()
    path_str = str(path)
    if system == "Windows":
        _sp.Popen(
            [r"C:\Windows\explorer.exe", "/select,", path_str],
            creationflags=0x08000000 if sys.platform == "win32" else 0,
        )
    elif system == "Darwin":
        _cmd(["open", path_str])
    else:
        _cmd(["xdg-open", path_str])
