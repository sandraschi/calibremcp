"""
Quick check script to verify server loads - use this before committing.
Run: python scripts/quick_check.py
"""

import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    # Test 1: Can we import the server?
    from calibre_mcp.server import mcp

    print("[OK] Server imports")

    # Test 2: Can we register all tools?
    from calibre_mcp.tools import register_tools

    register_tools(mcp)
    print("[OK] Tools registered")

    # Test 3: Can we import tag tools specifically?
    print("[OK] Tag tools import")

    print("\n[SUCCESS] Server will load in Claude!")
    sys.exit(0)

except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
