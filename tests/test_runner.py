"""
Test runner script for Calibre MCP tests.

Provides a convenient way to run tests with various options.
"""

import sys
import subprocess
from pathlib import Path


def run_tests(
    test_path: str = "tests/",
    coverage: bool = False,
    verbose: bool = False,
    marker: str = "",
    test_name: str = "",
    parallel: bool = False,
):
    """Run pytest with specified options."""
    pytest_args = ["python", "-m", "pytest"]
    
    if verbose:
        pytest_args.append("-vv")
    else:
        pytest_args.append("-v")
    
    if coverage:
        pytest_args.extend([
            "--cov=calibre_mcp",
            "--cov-report=html",
            "--cov-report=term",
        ])
    
    if marker:
        pytest_args.extend(["-m", marker])
    
    if test_name:
        pytest_args.extend(["-k", test_name])
    
    if parallel:
        pytest_args.extend(["-n", "auto"])
    
    pytest_args.append(test_path)
    
    print(f"Running: {' '.join(pytest_args)}")
    print()
    
    result = subprocess.run(pytest_args)
    return result.returncode


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Calibre MCP tests")
    parser.add_argument(
        "--path",
        default="tests/",
        help="Test path to run (default: tests/)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--marker",
        default="",
        help="Run tests with specific marker (e.g., 'unit', 'integration')"
    )
    parser.add_argument(
        "--test",
        default="",
        help="Run specific test by name pattern"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        test_path=args.path,
        coverage=args.coverage,
        verbose=args.verbose,
        marker=args.marker,
        test_name=args.test,
        parallel=args.parallel,
    )
    
    sys.exit(exit_code)
