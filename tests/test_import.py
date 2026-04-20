#!/usr/bin/env python3
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

try:
    pass

except Exception:
    import traceback

    traceback.print_exc()
