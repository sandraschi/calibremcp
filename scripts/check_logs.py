"""
Quick log checker - shows recent server logs to diagnose startup issues.
Usage: python scripts/check_logs.py [--tail N] [--errors-only]
"""

import sys
from pathlib import Path


def check_logs(tail: int = 50, errors_only: bool = False):
    """Check recent server logs."""
    log_file = Path("logs/calibremcp.log")

    if not log_file.exists():
        print(f"[INFO] Log file not found: {log_file}")
        print("[INFO] Server may not have run yet, or logs are in a different location.")
        return 0

    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        if errors_only:
            # Filter for errors and warnings
            relevant_lines = [
                line
                for line in lines[-tail * 2 :]  # Check more lines to find errors
                if any(
                    keyword in line.lower()
                    for keyword in ["error", "exception", "traceback", "failed", "warning"]
                )
            ]
            if not relevant_lines:
                print("[OK] No errors or warnings in recent logs")
                return 0
            print(f"\n{'=' * 80}")
            print(f"ERRORS/WARNINGS in last {tail} lines:")
            print("=" * 80)
            for line in relevant_lines[-tail:]:
                print(line.rstrip())
        else:
            print(f"\n{'=' * 80}")
            print(f"Last {min(tail, len(lines))} lines from {log_file}:")
            print("=" * 80)
            for line in lines[-tail:]:
                print(line.rstrip())

        # Check for common issues
        recent_text = "".join(lines[-tail:])
        issues = []

        if "ImportError" in recent_text:
            issues.append("ImportError detected - check imports")
        if "ModuleNotFoundError" in recent_text:
            issues.append("ModuleNotFoundError detected - check dependencies")
        if "AttributeError" in recent_text:
            issues.append("AttributeError detected - check code changes")
        if "NameError" in recent_text:
            issues.append("NameError detected - check variable names")
        if "Traceback" in recent_text:
            issues.append("Exception traceback found - check stack trace")

        if issues:
            print(f"\n{'=' * 80}")
            print("POTENTIAL ISSUES DETECTED:")
            print("=" * 80)
            for issue in issues:
                print(f"  - {issue}")
            return 1
        else:
            print("\n[OK] No obvious errors in recent logs")
            return 0

    except Exception as e:
        print(f"[ERROR] Failed to read log file: {e}")
        return 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Check CalibreMCP server logs")
    parser.add_argument(
        "--tail", "-n", type=int, default=50, help="Number of lines to show (default: 50)"
    )
    parser.add_argument(
        "--errors-only", "-e", action="store_true", help="Show only errors and warnings"
    )

    args = parser.parse_args()

    return check_logs(tail=args.tail, errors_only=args.errors_only)


if __name__ == "__main__":
    sys.exit(main())
