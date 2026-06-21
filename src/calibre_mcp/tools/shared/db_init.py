"""
Shared DB auto-initialization helper.

Ensures the DatabaseService singleton is connected to the active Calibre
library before any tool accesses it. Safe to call multiple times.
"""

from ...logging_config import get_logger

logger = get_logger("calibremcp.tools.shared.db_init")


def ensure_db_initialized() -> str | None:
    """
    Initialize DatabaseService if not yet done.

    Returns None on success, or an error string if no library can be found.
    """
    from ...db.database import db as database_singleton, init_database

    if database_singleton._engine is not None:
        return None  # already initialized

    from ...config import CalibreConfig
    from ...utils.library_utils import discover_calibre_libraries

    try:
        config = CalibreConfig()
        if config.auto_discover_libraries:
            config.discover_libraries()

        lib_path = config.local_library_path
        if not lib_path:
            discovered = discover_calibre_libraries()
            if discovered:
                lib_path = next(iter(discovered.values()))

        if not lib_path or not (lib_path / "metadata.db").exists():
            return "No Calibre library found. Set CALIBRE_BASE_PATH or CALIBRE_LIBRARY_PATH."

        init_database(str((lib_path / "metadata.db").absolute()), echo=False)
        logger.info("Auto-initialized database with library: %s", lib_path)
        return None

    except Exception as e:
        logger.error("Failed to auto-initialize database: %s", e, exc_info=True)
        return f"Database initialization failed: {e}"
