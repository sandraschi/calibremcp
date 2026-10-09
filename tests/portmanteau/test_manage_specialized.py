#!/usr/bin/env python3
"""
Test Battery for manage_specialized Portmanteau Tool

Tests all operations: japanese_organizer, it_curator, reading_recommendations
Run with: python tests/portmanteau/test_manage_specialized.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


async def run_test_battery():
    """Run comprehensive test battery for manage_specialized portmanteau."""

    print("MANAGE_SPECIALIZED PORTMANTEAU TEST BATTERY")
    print("=" * 60)
    print("Testing: japanese_organizer, it_curator, reading_recommendations")
    print("=" * 60)

    test_results = []

    try:
        # Import tool
        print("\n[IMPORT] Importing manage_specialized tool...")
        from calibre_mcp.tools.specialized.manage_specialized import manage_specialized

        from calibre_mcp.config import CalibreConfig
        from calibre_mcp.db.database import init_database

        print("[OK] Tool imported successfully")

        # Initialize with a library
        print("\n[DB] Initializing database...")
        config = CalibreConfig()
        libraries = config.discover_libraries()

        if not libraries:
            print("[ERROR] No libraries found")
            return False

        first_lib_name = next(iter(libraries.keys()))
        first_lib_path = libraries[first_lib_name].path
        init_database(str(first_lib_path / "metadata.db"), echo=False)
        print(f"[OK] Database initialized with library: {first_lib_name}")

        # Test 1: Japanese Organizer
        print("\n[TEST1] JAPANESE ORGANIZER")
        try:
            result = await manage_specialized(operation="japanese_organizer")
            if result.get("success") or "manga_series" in result or "light_novels" in result:
                manga_count = len(result.get("manga_series", []))
                ln_count = len(result.get("light_novels", []))
                test_results.append(("Japanese Organizer", True, f"Found {manga_count} manga, {ln_count} light novels"))
                print(f"[OK] Japanese organizer: {manga_count} manga series, {ln_count} light novels")
            else:
                test_results.append(("Japanese Organizer", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Japanese Organizer", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 2: IT Curator
        print("\n[TEST2] IT CURATOR")
        try:
            result = await manage_specialized(operation="it_curator")
            if result.get("success") or "by_language" in result or "learning_paths" in result:
                languages = len(result.get("by_language", {}))
                test_results.append(("IT Curator", True, f"Organized by {languages} programming languages"))
                print(f"[OK] IT curator: organized by {languages} programming languages")
            else:
                test_results.append(("IT Curator", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("IT Curator", False, str(e)))
            print(f"[FAIL] {e}")

        # Test 3: Reading Recommendations
        print("\n[TEST3] READING RECOMMENDATIONS")
        try:
            result = await manage_specialized(operation="reading_recommendations")
            if result.get("success") or "recommendations" in result:
                rec_count = len(result.get("recommendations", []))
                test_results.append(("Reading Recommendations", True, f"Generated {rec_count} recommendations"))
                print(f"[OK] Reading recommendations: {rec_count} recommendations")
            else:
                test_results.append(("Reading Recommendations", False, result.get("error", "Unknown error")))
                print(f"[FAIL] {result.get('error', 'Unknown error')}")
        except Exception as e:
            test_results.append(("Reading Recommendations", False, str(e)))
            print(f"[FAIL] {e}")

    except Exception as e:
        print(f"\n[CRITICAL] ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Print results summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(test_results)

    for test_name, success, details in test_results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}: {details}")
        if success:
            passed += 1

    print(f"\nOVERALL: {passed}/{total} tests passed")

    if passed == total:
        print("ALL TESTS PASSED!")
        return True
    else:
        print("SOME TESTS FAILED.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_test_battery())
    sys.exit(0 if success else 1)
