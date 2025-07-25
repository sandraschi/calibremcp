"""
CalibreMCP Module Entry Point

Allows running the server with: python -m calibre_mcp
"""

# Hybrid imports for maximum compatibility
try:
    # Try relative imports first (when running as module)
    from .server import main
except ImportError:
    # Fall back to absolute imports (when running script directly)
    try:
        from calibre_mcp.server import main
    except ImportError:
        # Last resort - add current directory to path
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from server import main

if __name__ == "__main__":
    main()
