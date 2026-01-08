#!/usr/bin/env python3
"""
Master Test Runner - Runs all portmanteau test batteries

Run with: python tests/portmanteau/run_all_tests.py
"""

import sys
import asyncio
import subprocess
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def run_test_file(test_file: Path) -> tuple[str, bool, str]:
    """Run a single test file and return results."""
    print(f"\n{'=' * 80}")
    print(f"Running: {test_file.name}")
    print('=' * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        success = result.returncode == 0
        return test_file.name, success, result.stdout[-200:] if result.stdout else ""
    except subprocess.TimeoutExpired:
        return test_file.name, False, "Test timed out after 5 minutes"
    except Exception as e:
        return test_file.name, False, str(e)

def main():
    """Run all portmanteau test batteries."""
    
    print("CALIBRE MCP PORTMANTEAU TEST BATTERY RUNNER")
    print("=" * 80)
    print("Running all portmanteau test batteries...")
    print("=" * 80)
    
    # Find all test files
    test_dir = Path(__file__).parent
    test_files = sorted(test_dir.glob("test_*.py"))
    
    # Exclude this file
    test_files = [f for f in test_files if f.name != "run_all_tests.py"]
    
    if not test_files:
        print("[ERROR] No test files found!")
        return False
    
    print(f"\nFound {len(test_files)} test batteries to run:\n")
    for tf in test_files:
        print(f"  - {tf.name}")
    
    # Run all tests
    results = []
    for test_file in test_files:
        name, success, output = run_test_file(test_file)
        results.append((name, success, output))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for name, success, output in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {name}")
        if success:
            passed += 1
        else:
            failed += 1
            if output:
                print(f"  Last output: {output[:100]}...")
    
    print("\n" + "=" * 80)
    print(f"OVERALL: {passed}/{len(results)} test batteries passed")
    print("=" * 80)
    
    if failed == 0:
        print("\nALL TEST BATTERIES PASSED!")
        return True
    else:
        print(f"\n{failed} TEST BATTERY(IES) FAILED.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
