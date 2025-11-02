#!/usr/bin/env python3
"""
Script to inspect the Calibre metadata.db structure.
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any
import json


def get_db_schema(db_path: str) -> Dict[str, Any]:
    """Extract schema information from SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    schema = {}

    # Get schema for each table
    for table in tables:
        # Get table info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [dict(row) for row in cursor.fetchall()]

        # Get index info
        cursor.execute(f"PRAGMA index_list({table})")
        indexes = []
        for idx in cursor.fetchall():
            idx_info = dict(idx)
            cursor.execute(f"PRAGMA index_info({idx['name']})")
            idx_info["columns"] = [dict(row) for row in cursor.fetchall()]
            indexes.append(idx_info)

        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        foreign_keys = [dict(row) for row in cursor.fetchall()]

        schema[table] = {"columns": columns, "indexes": indexes, "foreign_keys": foreign_keys}

    conn.close()
    return schema


def main():
    # Try to find metadata.db in common locations
    possible_paths = [
        Path("L:/Multimedia Files/Written Word/Main Library/metadata.db"),
        Path.home() / "Calibre Library/metadata.db",
        Path("C:/Users/Public/Calibre Library/metadata.db"),
        Path("D:/Calibre Library/metadata.db"),
    ]

    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = path
            print(f"Found database at: {db_path}")
            break

    if not db_path:
        print("Could not find metadata.db. Please specify the path to your Calibre library.")
        return

    # Get schema information
    schema = get_db_schema(str(db_path))

    # Print basic information
    print("\n=== Database Schema ===")
    for table_name, table_info in schema.items():
        print(f"\nTable: {table_name}")
        print(f"Columns: {[col['name'] for col in table_info['columns']]}")

        if table_info["foreign_keys"]:
            print("Foreign Keys:")
            for fk in table_info["foreign_keys"]:
                print(f"  {fk['from']} -> {fk['table']}.{fk['to']}")

    # Save full schema to file
    output_file = Path("calibre_schema.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"\nFull schema saved to: {output_file.absolute()}")


if __name__ == "__main__":
    main()
