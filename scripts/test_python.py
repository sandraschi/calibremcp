import sys
import os
import sqlite3

print("Python version:", sys.version)
print("Working directory:", os.getcwd())
print("SQLite version:", sqlite3.sqlite_version)

# Try to list files in the current directory
try:
    print("\nFiles in current directory:")
    for f in os.listdir():
        print(f"- {f}")
except Exception as e:
    print(f"Error listing directory: {e}")

# Try to access the database
db_path = os.path.join('samples', 'metadata.db')
try:
    if os.path.exists(db_path):
        print(f"\nDatabase exists at: {os.path.abspath(db_path)}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Found {len(tables)} tables in the database.")
        conn.close()
    else:
        print(f"\nDatabase not found at: {os.path.abspath(db_path)}")
except Exception as e:
    print(f"Error accessing database: {e}")
