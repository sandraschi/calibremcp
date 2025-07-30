# Code Samples

This page demonstratesyntax highlighting for various programming languages.

## Python

```python
defibonacci(n):
    """Generate the Fibonacci sequence up to n terms."""
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

# Example usage
print(fibonacci(10))
```

## JavaScript

```javascript
// Async/Await example
async function fetchData(url) {
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
}

// Usage
fetchData('https://api.example.com/data')
  .then(data => console.log('Data:', data));
```

## HTML

```html
<!DOCTYPE html>
<htmlang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }
    </style>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This a sample HTML page.</p>
</body>
</html>
```

## CSS

```css
/* Responsive grid layout */
.container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    padding: 20px;
}

.card {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 20px;
    transition: transform 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .card {
        background: #2d2d2d;
        color: #f0f0f0;
    }
}
```

## SQL

```sql
-- Create a table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_atIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULTRUE
);

-- Insert sample data
INSERT INTO users (username, email) 
VALUES ('johndoe', 'john@example.com');

-- Query with JOIN
SELECT u.username, p.title, p.content
FROM users u
JOIN posts p ON u.id = p.user_id
WHERE u.is_active = TRUE
ORDER BY p.created_at DESC
LIMIT 10;
```

## PowerShell

```powershell
# Function to get file sizes in a directory
function Get-DirectorySize {
    param (
        [string]$Path = '.',
        [string]$Filter = '*.*'
    )
    
    Get-ChildItem -Path $Path -Filter $Filter -Recurse -File | 
    Measure-Object -Property Length -Sum | 
    Select-Object @{
        Name = 'Path'; 
        Expression = { (Resolve-Path $Path).Path }
    }, 
    @{
        Name = 'FileCount'; 
        Expression = { $_.Count }
    }, 
    @{
        Name = 'SizeMB'; 
        Expression = { [math]::Round(($_.Sum / 1MB), 2) }
    }
}

# Usaget-DirectorySize -Path 'C:\Temp' -Filter '*.log'
```

## Bash/Shell

```bash
#!/bin/bash

# Check if a filexists and is readable
check_file() {
    if [ ! -e "$1" ]; then
        echo "Error: File $1 does not exist"
        return 1
    fif [ ! -r "$1" ]; then
        echo "Error: Cannot read $1 (permission denied)"
        return 1
    fi
    return 0
}

# Process log files
process_logs() {
    localog_dir="/var/log"
    local output_file="log_summary_$(date +%Y%m%d).txt"
    
    # Find all .log files modified in the last 7 days
    find "$log_dir" -name "*.log" -mtime -7 -type f | while read -r file; do
        if check_file "$file"; then
            echo "=== $file ===" >> "$output_file"
            grep -i "error\|warning" "$file" | head -n 10 >> "$output_file"
            echo -e "\n" >> "$output_file"
        fi
    done
}

# Main execution
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

process_logs
```

## JSON

```json
{
  "name": "Sample API Response",
  "version": "1.0.0",
  "status": "success",
  "data": {
    "user": {
      "id": 12345,
      "username": "johndoe",
      "email": "john@example.com",
      "preferences": {
        "theme": "dark",
        "notifications": true,
        "language": "en-US"
      }
    },
    "roles": ["user", "editor"],
    "last_login": "2025-06-28T15:30:00Z"
  },
  "pagination": {
    "total": 1,
    "page": 1,
    "per_page": 10
  }
}
```

## YAML

```yaml
# Sample configuration file
application:
  name: My Awesome App
  version: 1.0.0
  environment: production
  debug: false
  port: 3000

database:
  host: localhost
  port: 5432
  name: myapp_production
  user: admin

server:
  host: 0.0.0.0
  cors:
    allowed_origins:
      - https://example.com
      - https://api.example.com
  rate_limit:
    enabled: true
    max_requests: 100
    window: 60s

# Feature flags
features:
  dark_mode: true
  notifications: true
  analytics: false

# Logging configuration
logging:
  level: info
  file: /var/log/myapp.log
  max_size: 10MB
  max_files: 5
  format: json
```

## Markdown Tips

To create code blocks with syntax highlighting, use triple backticks followed by the language identifier:

````markdown
```python
def hello():
    print("Hello, World!")
```
````

## Supported Languages

Docsify uses Prism.js for syntax highlighting, which supports many languages including:

- HTML, CSS, JavaScript
- Python, Ruby, PHP
- Java, C, C++, C#, Go
- SQL, GraphQL
- JSON, YAML, XML
- Bash, PowerShell
- Markdown, Git
- And many more...
