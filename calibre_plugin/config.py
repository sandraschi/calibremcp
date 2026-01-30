"""
Configuration for CalibreMCP Integration plugin.
"""

from calibre.utils.config import JSONConfig

prefs = JSONConfig("plugins/calibre_mcp_integration")

prefs.defaults["mcp_user_data_dir"] = ""
prefs.defaults["mcp_http_url"] = "http://127.0.0.1:13000"  # Calibre webapp backend
prefs.defaults["sync_translator_column"] = ""
prefs.defaults["sync_first_published_column"] = ""
prefs.defaults["sync_user_comment_column"] = ""


def get_mcp_user_data_dir():
    """Return MCP user data dir - config override or platform default."""
    override = prefs.get("mcp_user_data_dir", "")
    if override:
        from pathlib import Path

        return str(Path(override).expanduser().resolve())

    import os
    from pathlib import Path

    env_dir = os.getenv("CALIBRE_MCP_USER_DATA_DIR")
    if env_dir:
        return str(Path(env_dir))
    if os.name == "nt":
        appdata = os.getenv("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        return str(Path(appdata) / "calibre-mcp")
    home = Path.home()
    import platform

    if platform.system() == "Darwin":
        return str(home / "Library" / "Application Support" / "calibre-mcp")
    return str(home / ".local" / "share" / "calibre-mcp")
