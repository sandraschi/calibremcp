import sqlite3
import json
from pathlib import Path

def get_schema(db_path):
    """Extract schema information from SQLite database."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        # Get table info
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [dict(row) for row in cursor.fetchall()]
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        foreign_keys = [dict(row) for row in cursor.fetchall()]
        
        schema[table] = {
            'columns': columns,
            'foreign_keys': foreign_keys
        }
    
    conn.close()
    return schema

def main():
    db_path = Path("samples/metadata.db")
    schema = get_schema(db_path)
    
    # Print basic schema information
    print(f"Database: {db_path.absolute()}")
    print(f"Tables: {len(schema)}\n")
    
    for table_name, table_info in schema.items():
        print(f"Table: {table_name}")
        print("  Columns:")
        for col in table_info['columns']:
            print(f"    {col['name']} ({col['type']})")
        
        if table_info['foreign_keys']:
            print("\n  Foreign Keys:")
            for fk in table_info['foreign_keys']:
                print(f"    {fk['from']} -> {fk['table']}.{fk['to']}")
        
        print("\n" + "-" * 80 + "\n")
    
    # Save full schema to file
    output_file = Path("samples/db_schema_detailed.json")
    with open(output_file, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"\nFull schema saved to: {output_file.absolute()}")

if __name__ == "__main__":
    main()
