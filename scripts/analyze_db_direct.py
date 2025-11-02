import os
import sqlite3
import json
from pathlib import Path


def analyze_database(db_path, output_file):
    """Analyze the database and save results to a file."""
    results = {
        "database_path": str(Path(db_path).absolute()),
        "exists": os.path.exists(db_path),
        "tables": [],
        "error": None,
    }

    if not results["exists"]:
        results["error"] = f"Database file not found: {db_path}"
        return results

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        results["tables"] = tables

        # For each table, get column info and row count
        for table in tables:
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [
                dict(zip(["cid", "name", "type", "notnull", "dflt_value", "pk"], row))
                for row in cursor.fetchall()
            ]

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            results[table] = {"columns": columns, "row_count": row_count}

            # Get sample data (first row)
            if row_count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    results[table]["sample"] = dict(zip([col["name"] for col in columns], sample))

        conn.close()

    except Exception as e:
        results["error"] = f"Error analyzing database: {str(e)}"

    # Save results to file
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    return results


def main():
    # Path to the database
    db_path = os.path.join("samples", "metadata.db")
    output_file = os.path.join("samples", "db_analysis.json")

    # Run analysis
    results = analyze_database(db_path, output_file)

    # Print basic info
    if results["error"]:
        print(f"Error: {results['error']}")
    else:
        print(f"Database analyzed successfully: {results['database_path']}")
        print(f"Found {len(results['tables'])} tables.")
        print(f"Results saved to: {os.path.abspath(output_file)}")


if __name__ == "__main__":
    main()
