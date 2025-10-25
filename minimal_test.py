"""
Minimal test to check basic imports
"""
print("Testing basic imports...")

try:
    print("asyncio")
    
    print("os")
    
    print("sqlite3")
    
    print("typing")
    
    print("datetime")
    
    print("pathlib")
    
    print("httpx")
    
    print("pydantic")
    
    print("rich")
    
    print("python-dotenv")
    
    try:
        from fastmcp import FastMCP
        print("fastmcp")
    except ImportError as e:
        print(f"fastmcp import failed: {e}")
        print("   This might be the issue!")
    
    print("\nBasic imports test completed!")
    
except Exception as e:
    print(f"Error during import test: {e}")
