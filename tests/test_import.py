#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

print("Starting server import test...")
try:
    import calibre_mcp.server

    print("Server import completed successfully")
    print(f"MCP instance exists: {hasattr(calibre_mcp.server, 'mcp')}")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback

    traceback.print_exc()
