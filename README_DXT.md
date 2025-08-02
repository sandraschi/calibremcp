# Calibre MCP DXT Package

This document provides instructions for building, installing, and using the Calibre MCP DXT package, which enables automation of Calibre ebook management through the MCP protocol.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- Calibre (with command-line tools) installed on your system
- Windows, macOS, or Linux (Windows recommended for best compatibility)

## Building the DXT Package

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/sandraschi/calibremcp.git
   cd calibremcp
   ```

2. **Build the DXT package** using the provided build script:
   ```powershell
   # Windows (PowerShell)
   .\build_dxt.ps1
   
   # Linux/macOS
   # chmod +x build_dxt.ps1
   # pwsh -File build_dxt.ps1
   ```

   This will:
   - Create a virtual environment
   - Install all dependencies
   - Run tests (can be skipped with `-NoTests`)
   - Generate the DXT package in the `dist` directory

3. **Verify the DXT package** was created:
   ```
   dist/calibre-mcp-{version}.dxt
   ```

## Installing the DXT Package

1. **Copy the DXT file** to your Claude Desktop packages directory:
   - Windows: `%APPDATA%\Claude\packages\`
   - macOS: `~/Library/Application Support/Claude/packages/`
   - Linux: `~/.config/claude/packages/`

2. **Restart Claude Desktop** to load the new package

3. **Verify installation** by checking the Claude Desktop logs or using the MCP client to list available services

## Configuring Calibre MCP

Before using the MCP service, you may need to configure it to work with your Calibre installation:

1. Copy `.env.example` to `.env` and update the settings:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your preferred text editor and update the following settings:
   ```ini
   # Path to the Calibre library
   CALIBRE_LIBRARY_PATH="C:/Users/YourUsername/Calibre Library"
   
   # Calibre-Web configuration (optional)
   CALIBRE_WEB_URL="http://localhost:8083"
   CALIBRE_WEB_USERNAME="admin"
   CALIBRE_WEB_PASSWORD="your_password"
   
   # Default output format for conversions
   DEFAULT_OUTPUT_FORMAT="epub"
   
   # Maximum concurrent conversions
   MAX_CONCURRENT_CONVERSIONS=2
   
   # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   LOG_LEVEL="INFO"
   
   # Automatically update metadata from online sources
   AUTO_UPDATE_METADATA=true
   
   # Default language for metadata and conversions
   DEFAULT_LANGUAGE="en"
   
   # Thumbnail settings
   THUMBNAIL_WIDTH=300
   
   # Enable OPDS feed generation
   ENABLE_OPDS=true
   ```

3. Start the MCP server through Claude Desktop or manually:
   ```bash
   python -m calibremcp.server
   ```

## Using the Calibre MCP Service

Once installed, you can interact with the Calibre MCP service using the Claude Desktop MCP client or any HTTP client.

### Example: Adding a Book

```python
import requests

# Add a book to the Calibre library
response = requests.post(
    "http://localhost:8080/books",
    json={
        "file_path": "/path/to/book.epub",
        "title": "Sample Book",
        "authors": ["John Doe"],
        "tags": ["fiction", "sample"],
        "series": "Sample Series",
        "series_index": 1,
        "options": {
            "add_automatically": True,
            "save_cover": True,
            "overwrite_duplicates": False
        }
    }
)
print("Add book result:", response.json())
```

### Example: Converting a Book

```python
# Convert a book to a different format
response = requests.post(
    "http://localhost:8080/books/1/convert",
    json={
        "output_format": "mobi",
        "output_path": "/path/to/output/",
        "options": {
            "keep_original": True,
            "output_profile": "kindle"
        }
    }
)
print("Conversion result:", response.json())
```

### Example: Searching for Books

```python
# Search for books in the library
response = requests.get(
    "http://localhost:8080/books",
    params={
        "query": "science fiction",
        "sort_by": "title",
        "sort_order": "asc",
        "limit": 10,
        "offset": 0
    }
)
print("Search results:", response.json())
```

## Available Prompts

The following prompts are available for natural language interaction:

- **Add Book**: "Add the book at {file_path} to my Calibre library with title {title}, author {author}, and series {series} with options {options}."
- **Convert Book**: "Convert the book with ID {book_id} to {output_format} format and save to {output_path} with options {options}."
- **Search Books**: "Find books matching {query} in my Calibre library with filters {filters} and sort by {sort_field} in {sort_order} order."
- **Update Metadata**: "Update metadata for book with ID {book_id} from {source} with options {options}."
- **Export Library**: "Export {selection} books to {output_dir} in {format} format with options {options}."
- **Create Catalog**: "Create a {format} catalog of my Calibre library with fields {fields} and save to {output_file} with options {options}."
- **Manage Devices**: "{action} my {device_name} by {method} with options {options}."
- **Edit Metadata**: "Update the {field} to {value} for book with ID {book_id} with options {options}."
- **Bulk Operations**: "{action} all books matching {query} with options {options}."
- **Manage Series**: "{action} the series {series_name} with options {options}."

## Troubleshooting

### Common Issues

1. **Calibre Not Found**:
   - Ensure Calibre is installed and the `calibredb` command is in your system PATH
   - On Windows, the default installation path is `C:\Program Files\Calibre2`
   - On macOS, install via Homebrew: `brew install --cask calibre`
   - On Linux, install via your package manager: `sudo apt install calibre`

2. **Permission Issues**:
   - Make sure the user running the MCP service has read/write permissions to the Calibre library
   - On Linux/macOS, you may need to run the service with `sudo`

3. **Conversion Failures**:
   - Check that the required conversion tools are installed with Calibre
   - Verify there's enough disk space for the output files
   - Check the logs for specific error messages

### Viewing Logs

Logs can be found in the standard Claude Desktop log location:
- Windows: `%APPDATA%\Claude\logs\`
- macOS: `~/Library/Logs/Claude/`
- Linux: `~/.local/share/claude/logs/`

## Development

### Testing Changes

1. Make your changes to the code
2. Run tests:
   ```bash
   pytest -v
   ```
3. Rebuild the DXT package
4. Copy to Claude Desktop packages directory and restart

### Directory Structure

```
calibremcp/
├── config/                    # Configuration files
│   └── default.toml          # Default configuration
├── src/
│   └── calibremcp/           # Main package
│       ├── __init__.py       # Package initialization
│       ├── server.py         # Main server implementation
│       ├── calibre.py        # Calibre library interface
│       ├── models.py         # Data models
│       └── utils.py          # Utility functions
├── tests/                    # Test files
├── dxt_build.py              # DXT package builder
├── build_dxt.ps1             # Build script (PowerShell)
├── dxt_manifest.json         # DXT package manifest
└── pyproject.toml            # Project configuration
```

## License

MIT License - See [LICENSE](LICENSE) for details.
