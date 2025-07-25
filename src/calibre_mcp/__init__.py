"""
CalibreMCP - FastMCP 2.0 Server for Calibre E-book Library Management

Austrian efficiency package for Sandra's comprehensive e-book library workflow.
Provides 4 core tools for browsing, searching, and managing Calibre libraries.
"""

__version__ = "1.0.0"
__author__ = "Sandra"
__description__ = "FastMCP 2.0 server for Calibre e-book library management"

# Core exports - hybrid imports for maximum compatibility
try:
    # Try relative imports first (when running as module)
    from .server import mcp
    from .config import CalibreConfig
    from .calibre_api import CalibreAPIClient, CalibreAPIError
except ImportError:
    # Fall back to absolute imports (when running script directly)
    try:
        from calibre_mcp.server import mcp
        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.calibre_api import CalibreAPIClient, CalibreAPIError
    except ImportError:
        # Last resort - add current directory to path
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from server import mcp
        from config import CalibreConfig
        from calibre_api import CalibreAPIClient, CalibreAPIError

__all__ = [
    "mcp",
    "CalibreConfig", 
    "CalibreAPIClient",
    "CalibreAPIError"
]
