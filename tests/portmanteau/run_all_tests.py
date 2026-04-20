#!/usr/bin/env python3
"""
Master Test Runner - Runs all portmanteau test batteries

Run with: python tests/portmanteau/run_all_tests.py
"""

import subprocess
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def run_test_file(test_file: Path) -> tuple[str, bool, str]:
    """Run a single test file and return results."""

    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per test
        )

        # Print output
        if result.stdout:
            pass
        if result.stderr:
            pass

        success = result.returncode == 0
        return test_file.name, success, result.stdout[-200:] if result.stdout else ""
    except subprocess.TimeoutExpired:
        return test_file.name, False, "Test timed out after 5 minutes"
    except Exception as e:
        return test_file.name, False, str(e)


def main():
    """Run all portmanteau test batteries."""


    # Find all test files
    test_dir = Path(__file__).parent
    test_files = sorted(test_dir.glob("test_*.py"))

    # Exclude this file
    test_files = [f for f in test_files if f.name != "run_all_tests.py"]

    if not test_files:
        return False

    for _tf in test_files:
        pass

    # Run all tests
    results = []
    for test_file in test_files:
        name, success, output = run_test_file(test_file)
        results.append((name, success, output))

    # Print summary

    passed = 0
    failed = 0

    for name, success, output in results:
        if success:
            passed += 1
        else:
            failed += 1
            if output:
                pass


    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
