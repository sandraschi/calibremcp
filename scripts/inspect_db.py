#!/usr/bin/env python3
"""
Script to inspect the Calibre metadata.db structure.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any


def get_db_schema(db_path: str) -> dict[str, Any]:
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
            break

    if not db_path:
        return

    # Get schema information
    schema = get_db_schema(str(db_path))

    # Print basic information
    for _table_name, table_info in schema.items():

        if table_info["foreign_keys"]:
            for _fk in table_info["foreign_keys"]:
                pass

    # Save full schema to file
    output_file = Path("calibre_schema.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)



if __name__ == "__main__":
    main()
