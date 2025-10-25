#!/usr/bin/env python3
"""
Analyze Calibre metadata.db structure and generate schema information.
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, Any

def get_table_schema(cursor, table_name: str) -> Dict[str, Any]:
    """Get schema information for a specific table."""
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [dict(row) for row in cursor.fetchall()]
    
    # Get index information
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = []
    for idx in cursor.fetchall():
        idx_info = dict(idx)
        cursor.execute(f"PRAGMA index_info({idx['name']})")
        idx_info['columns'] = [dict(row) for row in cursor.fetchall()]
        indexes.append(idx_info)
    
    # Get foreign key information
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = [dict(row) for row in cursor.fetchall()]
    
    # Get sample data (first 2 rows)
    sample_data = []
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
        sample_data = [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError:
        sample_data = []
    
    return {
        'columns': columns,
        'indexes': indexes,
        'foreign_keys': foreign_keys,
        'sample_data': sample_data
    }

def get_database_schema(db_path: Path) -> Dict[str, Any]:
    """Get complete schema information for the database."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        schema[table] = get_table_schema(cursor, table)
    
    conn.close()
    return {
        'tables': tables,
        'schema': schema,
        'database_path': str(db_path.absolute())
    }

def generate_schema_documentation(schema: Dict[str, Any]) -> str:
    """Generate markdown documentation from schema."""
    output = [
        "# Calibre Database Schema",
        f"Database: `{schema['database_path']}`",
        f"Tables: {len(schema['tables'])}\n"
    ]
    
    for table_name, table_info in schema['schema'].items():
        output.append(f"## Table: `{table_name}`\n")
        
        # Columns
        output.append("### Columns")
        output.append("| Name | Type | Not Null | Default | PK |")
        output.append("|------|------|----------|---------|----|")
        for col in table_info['columns']:
            output.append(
                f"| {col['name']} | {col['type']} | "
                f"{bool(col['notnull'])} | {col['dflt_value']} | "
                f"{bool(col['pk'])} |"
            )
        output.append("")
        
        # Foreign Keys
        if table_info['foreign_keys']:
            output.append("### Foreign Keys")
            output.append("| From | To Table | To Column | On Update | On Delete |")
            output.append("|------|----------|-----------|-----------|-----------|")
            for fk in table_info['foreign_keys']:
                output.append(
                    f"| {fk['from']} | {fk['table']} | {fk['to']} | "
                    f"{fk['on_update']} | {fk['on_delete']} |"
                )
            output.append("")
        
        # Indexes
        if table_info['indexes']:
            output.append("### Indexes")
            for idx in table_info['indexes']:
                cols = ", ".join([col['name'] for col in idx['columns']])
                output.append(f"- **{idx['name']}** ({cols}){' UNIQUE' if idx['unique'] else ''}")
            output.append("")
        
        # Sample Data
        if table_info['sample_data']:
            output.append("### Sample Data")
            if table_info['sample_data']:
                sample = table_info['sample_data'][0]
                output.append("```json")
                output.append(json.dumps(sample, indent=2))
                output.append("```")
            output.append("")
        
        output.append("---\n")
    
    return "\n".join(output)

def main():
    db_path = Path("D:/Dev/repos/calibremcp/samples/metadata.db")
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return
    
    print(f"Analyzing database: {db_path}")
    schema = get_database_schema(db_path)
    
    # Save raw schema as JSON
    json_path = db_path.parent / "database_schema.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2)
    print(f"Raw schema saved to: {json_path}")
    
    # Generate and save markdown documentation
    md_path = db_path.parent / "DATABASE_SCHEMA.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(generate_schema_documentation(schema))
    print(f"Markdown documentation saved to: {md_path}")

if __name__ == "__main__":
    main()
