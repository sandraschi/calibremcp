#!/usr/bin/env python3
"""
Calibre MCP Startup Diagnostic Script

This script helps identify what's causing startup hangs by testing each component individually.
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diagnose")

def test_phase(phase_name, test_func):
    """Test a phase with timing and error handling."""
    logger.info(f"🔍 TESTING PHASE: {phase_name}")
    start_time = time.time()

    try:
        result = test_func()
        elapsed = time.time() - start_time
        logger.info(f"✅ {phase_name} completed in {elapsed:.2f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ PHASE FAILED after {elapsed:.2f}s: {e}", exc_info=True)
        return False

def test_basic_imports():
    """Test basic Python imports."""
    logger.info("Testing basic Python imports...")

    # Test standard library
    import asyncio
    import logging
    import pathlib
    import typing

    logger.info("✅ Standard library imports OK")

    # Test external dependencies
    import fastmcp
    import pydantic
    import dotenv

    logger.info("✅ External dependencies OK")
    return True

def test_calibre_mcp_base():
    """Test basic Calibre MCP imports."""
    logger.info("Testing Calibre MCP base imports...")

    # Test basic server import
    from calibre_mcp.server import mcp
    logger.info(f"✅ MCP instance created: {type(mcp).__name__}")

    return True

def test_logging_config():
    """Test logging configuration."""
    logger.info("Testing logging configuration...")

    from calibre_mcp.logging_config import get_logger, setup_logging
    logger.info("✅ Logging config imports OK")

    # Test logger creation
    test_logger = get_logger("diagnose.test")
    test_logger.info("✅ Logger creation OK")

    return True

def test_tool_imports():
    """Test individual tool imports."""
    logger.info("Testing tool imports...")

    tool_modules = [
        'calibre_mcp.tools.core',
        'calibre_mcp.tools.library',
        'calibre_mcp.tools.book_management',
        'calibre_mcp.tools.metadata',
        'calibre_mcp.tools.tags',
        'calibre_mcp.tools.comments',
        'calibre_mcp.tools.analysis',
        'calibre_mcp.tools.system',
        'calibre_mcp.tools.specialized',
        'calibre_mcp.tools.user_management',
        'calibre_mcp.tools.import_export',
        'calibre_mcp.tools.viewer',
        'calibre_mcp.tools.advanced_features',
        'calibre_mcp.tools.files',
        'calibre_mcp.tools.authors',
    ]

    failed_modules = []

    for module_name in tool_modules:
        try:
            logger.info(f"Testing {module_name}...")
            start_time = time.time()
            __import__(module_name)
            elapsed = time.time() - start_time
            logger.info(f"✅ {module_name} imported in {elapsed:.2f}s")
        except Exception as e:
            logger.error(f"❌ Failed to import {module_name}: {e}")
            failed_modules.append(module_name)

    if failed_modules:
        logger.error(f"❌ {len(failed_modules)} tool modules failed to import: {failed_modules}")
        return False

    logger.info("✅ All tool modules imported successfully")
    return True

def test_agentic_workflow():
    """Test agentic workflow tool specifically."""
    logger.info("Testing agentic workflow tool...")

    from calibre_mcp.tools.agentic_workflow import build_success_response, AgenticWorkflowTool
    logger.info("✅ Agentic workflow imports OK")

    # Test response builder
    resp = build_success_response("test", "Test summary", {"result": "ok"})
    logger.info("✅ Response builder works")

    # Test tool creation
    tool = AgenticWorkflowTool()
    logger.info(f"✅ Tool created, available: {tool.is_available()}")

    return True

def test_full_server_startup():
    """Test full server startup."""
    logger.info("Testing full server startup...")

    import subprocess
    import os

    # Run server with timeout
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(src_path)

        proc = subprocess.Popen(
            [sys.executable, 'run_server.py'],
            cwd=str(repo_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait up to 15 seconds for startup
        try:
            stdout, stderr = proc.communicate(timeout=15)
            returncode = proc.returncode

            if returncode == 0:
                logger.info("✅ Server started and exited cleanly")
                return True
            else:
                logger.error(f"❌ Server exited with code {returncode}")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.info("⚠️ Server is still running (expected for MCP server)")
            proc.terminate()
            proc.wait()
            return True

    except Exception as e:
        logger.error(f"❌ Server startup test failed: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    logger.info("🚀 Starting Calibre MCP Startup Diagnostics")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Working directory: {Path.cwd()}")
    logger.info(f"Source path: {src_path}")

    tests = [
        ("Basic Python Imports", test_basic_imports),
        ("Calibre MCP Base", test_calibre_mcp_base),
        ("Logging Configuration", test_logging_config),
        ("Tool Imports", test_tool_imports),
        ("Agentic Workflow", test_agentic_workflow),
        ("Full Server Startup", test_full_server_startup),
    ]

    results = []
    for test_name, test_func in tests:
        result = test_phase(test_name, test_func)
        results.append((test_name, result))

    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 DIAGNOSTIC SUMMARY")
    logger.info("="*60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info("15")
        if result:
            passed += 1
        else:
            failed += 1

    logger.info(f"\n📈 Results: {passed} passed, {failed} failed")

    if failed == 0:
        logger.info("🎉 All tests passed! Server should start normally.")
    else:
        logger.info("⚠️ Some tests failed. Check the logs above for hanging components.")
        logger.info("💡 The hanging component is likely causing the startup delay.")

if __name__ == "__main__":
    main()