"""
Restart Claude Desktop and verify MCP server loads successfully.

This script:
1. Pre-checks if server will load (optional but recommended)
2. Stops Claude Desktop
3. Restarts Claude Desktop
4. Monitors logs for successful MCP server startup
5. Reports success/failure

Note: Restarting Claude requires stopping the process (works without UAC).
Starting Claude may require UAC if installed in Program Files.
"""

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta


def find_claude_process():
    """Find Claude Desktop process."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Claude.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and "Claude.exe" in result.stdout:
            return True
        return False
    except Exception as e:
        print(f"[WARN] Could not check Claude process: {e}")
        return None


def stop_claude():
    """Stop Claude Desktop using taskkill.

    Uses Windows taskkill command to forcefully terminate Claude.exe.
    No UAC required - works without elevation.
    """
    print("\n[1/4] Stopping Claude Desktop (using taskkill)...")
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "Claude.exe"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("[OK] Claude Desktop stopped")
            time.sleep(2)  # Wait for process to fully terminate
            return True
        elif "not found" in result.stdout.lower() or "not running" in result.stdout.lower():
            print("[INFO] Claude Desktop was not running")
            return True
        else:
            print(f"[WARN] Unexpected response: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("[WARN] Timeout stopping Claude (process may be hung)")
        return False
    except Exception as e:
        print(f"[FAIL] Error stopping Claude: {e}")
        return False


def start_claude():
    """Start Claude Desktop."""
    print("\n[2/4] Starting Claude Desktop...")

    # Common Claude Desktop install locations
    possible_paths = [
        Path.home() / "AppData/Local/Programs/claude-desktop/Claude.exe",
        Path("C:/Program Files/Claude/Claude.exe"),
        Path("C:/Program Files (x86)/Claude/Claude.exe"),
    ]

    # Check if Claude is in PATH (less common but possible)
    try:
        result = subprocess.run(["where", "Claude"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            claude_path = Path(result.stdout.strip().split("\n")[0])
            if claude_path.exists():
                possible_paths.insert(0, claude_path)
    except Exception:
        pass

    # Try to find Claude
    claude_path = None
    for path in possible_paths:
        if path.exists():
            claude_path = path
            break

    if not claude_path:
        print("[FAIL] Could not find Claude Desktop executable")
        print("\nPlease start Claude Desktop manually, then run:")
        print("  python scripts/check_logs.py --errors-only")
        print("\nOr specify Claude path with --claude-path option")
        return False

    try:
        # Start Claude Desktop
        subprocess.Popen([str(claude_path)], shell=True)
        print(f"[OK] Started Claude Desktop from: {claude_path}")
        print("[INFO] Waiting for Claude to initialize...")
        time.sleep(5)  # Give Claude time to start and connect to MCP
        return True
    except Exception as e:
        print(f"[FAIL] Error starting Claude: {e}")
        print(f"[INFO] Try starting Claude manually from: {claude_path}")
        return False


def monitor_logs_for_startup(
    timeout_seconds=30, check_recent=True, log_file_size_before_check=None
):
    """Monitor logs for successful MCP server startup.

    Args:
        timeout_seconds: Timeout for watching new logs
        check_recent: If True, check recent logs (for --no-restart mode)
        log_file_size_before_check: Size of log file before script ran (to avoid checking our own logs)
    """
    print("\n[3/4] Monitoring logs for MCP server startup...")

    log_file = Path("logs/calibremcp.log")
    if not log_file.exists():
        print(f"[WARN] Log file not found: {log_file}")
        print("[INFO] Server may not have started yet, or logs are elsewhere")
        return False

    # If we have a size limit, only read up to that point (avoid checking logs created by pre-check)
    max_bytes = log_file_size_before_check if log_file_size_before_check else None

    # Look for success indicators
    success_indicators = [
        "registered",
        "tools registered",
        "server_startup",
        "database initialized",
    ]

    error_indicators = [
        "error",
        "exception",
        "traceback",
        "importerror",
        "modulenotfounderror",
        "failed",
        "server_startup_error",
    ]

    # First, check recent logs if requested (for --no-restart mode)
    if check_recent:
        print("[INFO] Checking LAST startup attempt in logs...")
        try:
            # Read log file up to the size before we started (to avoid our own pre-check logs)
            if max_bytes and log_file.stat().st_size > max_bytes:
                with open(log_file, "rb") as f:
                    content = f.read(max_bytes).decode("utf-8", errors="ignore")
                    # Get last complete line
                    if content and not content.endswith("\n"):
                        content = content.rsplit("\n", 1)[0] + "\n"
                    all_lines = content.splitlines(True)
            else:
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    all_lines = f.readlines()

                # Find the last "server_startup" log entry (most recent attempt)
                # Need to parse JSON to check the operation field
                last_startup_line_idx = None
                for i in range(len(all_lines) - 1, -1, -1):
                    line = all_lines[i]
                    try:
                        import json

                        log_entry = json.loads(line)
                        operation = log_entry.get("operation", "").lower()
                        # Find last server_startup (not server_startup_error)
                        if operation == "server_startup":
                            last_startup_line_idx = i
                            break
                    except (json.JSONDecodeError, AttributeError):
                        # Not JSON, skip
                        continue

                if last_startup_line_idx is None:
                    print("[WARN] No server_startup log entry found")
                    print("[INFO] Server may not have attempted to start, or logs are incomplete")
                    return False

                # Now check logs AFTER the last startup to see if it succeeded or failed
                # Look for success/error indicators in logs after the startup
                lines_after_startup = all_lines[last_startup_line_idx:]

                found_success = False
                found_error = False
                success_time = None

                # Check each line after startup for success or error
                for line in lines_after_startup:
                    try:
                        import json

                        log_entry = json.loads(line)
                        timestamp = log_entry.get("timestamp", "")
                        operation = log_entry.get("operation", "").lower()
                        message = log_entry.get("message", "").lower()

                        # Check for server_startup_error (most definitive failure)
                        if "server_startup_error" in operation:
                            found_error = True
                            print("[FAIL] Last startup attempt FAILED:")
                            print(f"  Time: {timestamp}")
                            print(f"  Error: {log_entry.get('message', 'Unknown error')[:200]}...")
                            return False

                        # Check for successful tool registration (happens after successful startup)
                        # Message format: "Registered 4 BaseTool classes (functions auto-registered on import)"
                        # Logger is "calibre_mcp.tools"
                        logger_name = log_entry.get("logger", "").lower()

                        # Success indicator: "Registered X BaseTool classes" from calibre_mcp.tools logger
                        # Check message pattern first (message is already lowercased)
                        if "registered" in message and "basetool classes" in message:
                            # Make sure it's from the tools module
                            if "calibre_mcp.tools" in logger_name or "tools" in logger_name:
                                found_success = True
                                success_time = timestamp
                                break  # Found success, stop looking

                    except (json.JSONDecodeError, AttributeError):
                        # Not JSON or missing fields, skip
                        continue

                if found_success:
                    print("[SUCCESS] Last startup attempt succeeded!")
                    if success_time:
                        print(f"  Success time: {success_time}")
                    return True
                elif found_error:
                    # Already printed above
                    return False
                else:
                    print("[WARN] Last startup found but could not determine success/failure")
                    print("[INFO] Check logs manually: python scripts/check_logs.py --tail 30")
                    return False

        except Exception as e:
            print(f"[WARN] Error checking recent logs: {e}")

    # If no recent success/error found, monitor for new entries
    start_time = datetime.now()
    timeout = timedelta(seconds=timeout_seconds)

    last_position = log_file.stat().st_size if log_file.exists() else 0

    print(f"[INFO] Watching log file: {log_file}")
    print(f"[INFO] Timeout: {timeout_seconds} seconds")

    while datetime.now() - start_time < timeout:
        try:
            # Check for new log entries
            if log_file.exists():
                current_size = log_file.stat().st_size
                if current_size > last_position:
                    # Read new log entries
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = current_size

                        # Check for success or error
                        for line in new_lines:
                            line_lower = line.lower()

                            # Check for errors first
                            if any(
                                indicator.lower() in line_lower for indicator in error_indicators
                            ):
                                if "error" in line_lower and "server_startup" in line_lower:
                                    print("\n[FAIL] Error detected in new logs:")
                                    print(f"  {line.strip()[:200]}...")
                                    return False

                            # Check for success
                            if any(
                                indicator.lower() in line_lower for indicator in success_indicators
                            ):
                                if "registered" in line_lower and "tools" in line_lower:
                                    print(
                                        "\n[SUCCESS] MCP server started successfully (new log entry)!"
                                    )
                                    print(f"  {line.strip()[:200]}...")
                                    return True
        except Exception as e:
            print(f"[WARN] Error reading log: {e}")

        time.sleep(1)

    print(f"\n[WARN] Timeout after {timeout_seconds} seconds")
    print("[INFO] Check logs manually: python scripts/check_logs.py --errors-only")
    return False


def pre_check_server():
    """Pre-check if server will load before restarting Claude.

    Returns:
        tuple: (success: bool, log_file_size_before: int | None)
    """
    print("\n[0/4] Pre-checking server load...")

    # Get log file size BEFORE we run pre-check
    log_file = Path("logs/calibremcp.log")
    log_size_before = log_file.stat().st_size if log_file.exists() else None

    try:
        import sys

        src_path = Path(__file__).parent.parent / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        from calibre_mcp.server import mcp
        from calibre_mcp.tools import register_tools

        register_tools(mcp)
        print("[OK] Pre-check passed - server should load successfully")
        return True, log_size_before
    except Exception as e:
        print(f"[FAIL] Pre-check failed: {e}")
        print("[WARN] Server may not load in Claude. Fix issues first!")
        response = input("\nContinue anyway? (y/N): ")
        return response.lower() == "y", log_size_before


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Restart Claude Desktop and verify MCP server loads"
    )
    parser.add_argument(
        "--skip-precheck", action="store_true", help="Skip pre-check (not recommended)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout for log monitoring in seconds (default: 30)",
    )
    parser.add_argument(
        "--claude-path", type=str, help="Path to Claude.exe (auto-detected if not specified)"
    )
    parser.add_argument(
        "--no-restart", action="store_true", help="Only monitor logs (do not restart Claude)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Claude Desktop Restart & MCP Server Check")
    print("=" * 60)

    # Pre-check (and get log file size before we started)
    log_file_size_before = None
    if not args.skip_precheck:
        precheck_passed, log_file_size_before = pre_check_server()
        if not precheck_passed:
            print("\n[STOP] Pre-check failed. Fix issues before restarting Claude.")
            return 1

    # Restart Claude (unless --no-restart)
    if not args.no_restart:
        if not stop_claude():
            print("\n[STOP] Failed to stop Claude. Check manually.")
            return 1

        if not start_claude():
            print("\n[STOP] Failed to start Claude. Start manually and check logs.")
            return 1
    else:
        print("\n[INFO] Skipping restart (--no-restart specified)")
        print("[INFO] Assuming Claude is already running")
        time.sleep(2)  # Give it a moment to connect

    # Monitor logs (check recent if --no-restart, wait for new if restarting)
    success = monitor_logs_for_startup(
        timeout_seconds=args.timeout,
        check_recent=args.no_restart,
        log_file_size_before_check=log_file_size_before,
    )

    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] MCP server loaded successfully in Claude!")
        return 0
    else:
        print("[FAILURE] Could not verify MCP server startup")
        print("\nNext steps:")
        print("  1. Check logs: python scripts/check_logs.py --errors-only")
        print("  2. Verify Claude Desktop MCP configuration")
        print("  3. Check Claude Desktop console for errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
