#!/usr/bin/env python3
"""Simple script to check database connection and list tables."""

import sqlite3
from pathlib import Path


def main():
    db_path = Path("D:/Dev/repos/calibremcp/samples/metadata.db")

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]

            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for _col in columns:
                pass

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            cursor.fetchone()[0]

        conn.close()

    except Exception:
        pass


if __name__ == "__main__":
    main()
