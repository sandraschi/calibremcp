# PowerShell script to analyze SQLite database schema
$dbPath = "D:\Dev\repos\calibremcp\samples\metadata.db"
$outputFile = "D:\Dev\repos\calibremcp\samples\database_schema.txt"

# Check if SQLite is available
if (-not (Get-Command sqlite3 -ErrorAction SilentlyContinue)) {
    Write-Host "SQLite command line tool not found. Please install it or add it to your PATH."
    exit 1
}

# Get list of tables
$tables = & sqlite3 $dbPath ".tables"

# Initialize output
$output = @("# Database Schema Analysis")
$output += "Generated: $(Get-Date)"
$output += "Database: $dbPath"
$output += ""

# Process each table
foreach ($table in $tables -split '\s+') {
    if ([string]::IsNullOrWhiteSpace($table)) { continue }
    
    $output += "## Table: $table"
    $output += ""
    
    # Get table schema
    $schema = & sqlite3 $dbPath ".schema $table"
    $output += "```sql"
    $output += $schema
    $output += "```"
    $output += ""
    
    # Get row count
    $count = & sqlite3 $dbPath "SELECT COUNT(*) FROM $table"
    $output += "**Row Count:** $count"
    $output += ""
    
    # Get column info
    $columns = & sqlite3 -header -csv $dbPath "PRAGMA table_info($table)" | ConvertFrom-Csv
    $output += "### Columns"
    $output += "| Name | Type | Not Null | Default | PK |"
    $output += "|------|------|----------|---------|----|"
    foreach ($col in $columns) {
        $output += ("| {0} | {1} | {2} | {3} | {4} |" -f 
            $col.name, 
            $col.type, 
            $col.notnull, 
            $col.dflt_value, 
            $col.pk)
    }
    $output += ""
    
    # Get foreign keys
    $fks = & sqlite3 -header -csv $dbPath "PRAGMA foreign_key_list($table)" | ConvertFrom-Csv -ErrorAction SilentlyContinue
    if ($fks) {
        $output += "### Foreign Keys"
        $output += "| From | To Table | To Column | On Update | On Delete |"
        $output += "|------|----------|-----------|-----------|-----------|"
        foreach ($fk in $fks) {
            $output += ("| {0} | {1} | {2} | {3} | {4} |" -f 
                $fk.from, 
                $fk.table, 
                $fk.to, 
                $fk.on_update, 
                $key.on_delete)
        }
        $output += ""
    }
    
    # Get sample data (first 2 rows)
    $sample = & sqlite3 -header -csv $dbPath "SELECT * FROM $table LIMIT 2" | ConvertFrom-Csv -ErrorAction SilentlyContinue
    if ($sample) {
        $output += "### Sample Data"
        $output += "```json"
        $output += ($sample | ConvertTo-Json -Depth 3)
        $output += "```"
        $output += ""
    }
    
    $output += "---"
    $output += ""
}

# Save to file
$output | Out-File -FilePath $outputFile -Encoding utf8
Write-Host "Database schema analysis saved to: $outputFile"
