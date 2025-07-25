"""
Minimal test to check basic imports
"""
print("Testing basic imports...")

try:
    import asyncio
    print("✅ asyncio")
    
    import os
    print("✅ os")
    
    import sqlite3
    print("✅ sqlite3")
    
    from typing import Optional, List, Dict, Any
    print("✅ typing")
    
    from datetime import datetime, timedelta
    print("✅ datetime")
    
    from pathlib import Path
    print("✅ pathlib")
    
    import httpx
    print("✅ httpx")
    
    from pydantic import BaseModel, Field
    print("✅ pydantic")
    
    from rich.console import Console
    print("✅ rich")
    
    from dotenv import load_dotenv
    print("✅ python-dotenv")
    
    try:
        from fastmcp import FastMCP
        print("✅ fastmcp")
    except ImportError as e:
        print(f"❌ fastmcp import failed: {e}")
        print("   This might be the issue!")
    
    print("\n🎉 Basic imports test completed!")
    
except Exception as e:
    print(f"❌ Error during import test: {e}")
