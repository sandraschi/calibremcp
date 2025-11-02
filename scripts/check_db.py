#!/usr/bin/env python3
"""Simple script to check database connection and list tables."""

import sqlite3
from pathlib import Path


def main():
    db_path = Path("D:/Dev/repos/calibremcp/samples/metadata.db")
    print(f"Connecting to database: {db_path}")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        print("\nTables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")

            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("  Columns:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Rows: {count}")

        conn.close()
        print("\nDatabase check completed successfully.")

    except Exception as e:
        print(f"Error accessing database: {e}")


if __name__ == "__main__":
    main()
