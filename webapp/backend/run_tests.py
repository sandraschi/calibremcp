"""Run endpoint tests."""

import subprocess
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
script_path = backend_dir / "test_endpoints_http.py"

print(f"Running endpoint tests from: {script_path}")
print("=" * 60)

try:
    result = subprocess.run(
        [sys.executable, str(script_path)], cwd=str(backend_dir), capture_output=False, text=True
    )
    sys.exit(result.returncode)
except Exception as e:
    print(f"Failed to run tests: {e}")
    sys.exit(1)
