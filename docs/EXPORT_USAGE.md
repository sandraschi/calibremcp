# Book Export Usage Guide

This guide explains how to use the Calibre MCP export tools to export books in various formats.

## Available Export Tools

### 1. `export_books_csv` - CSV Export
Export book metadata to CSV format (Excel/Google Sheets compatible).

### 2. `export_books_json` - JSON Export
Export book metadata to JSON format (for data exchange/backup).

### 3. `export_books_pandoc` - Pandoc Export
Export books using Pandoc to various formats (DOCX, HTML, PDF, EPUB, etc.).

---

## Quick Start Examples

### CSV Export

```python
# Export all books to CSV (saves to Desktop automatically)
export_books_csv()

# Export books by specific author
export_books_csv(author="Conan Doyle", output_path="conan_doyle_books.csv")

# Export specific books with custom fields
export_books_csv(
    book_ids=[1, 2, 3],
    include_fields=["title", "authors", "rating", "tags"]
)

# Export mystery books with no limit
export_books_csv(tag="mystery", limit=-1)
```

### JSON Export

```python
# Export all books to JSON (pretty formatted)
export_books_json()

# Export with compact format
export_books_json(pretty=False)

# Export specific books
export_books_json(book_ids=[1, 2, 3])
```

### Pandoc Export (Advanced Memory MCP Pattern)

```python
# Export to DOCX (like Advanced Memory MCP uses)
export_books_pandoc(format_type="docx")

# Export to HTML
export_books_pandoc(format_type="html", author="Conan Doyle")

# Export to PDF (requires LaTeX)
export_books_pandoc(format_type="pdf", limit=50)

# Export to EPUB
export_books_pandoc(format_type="epub", tag="mystery", limit=50)
```

---

## How Pandoc Export Works

Similar to Advanced Memory MCP, our Pandoc export works in three steps:

1. **Fetch book metadata** from the Calibre library
2. **Convert to Markdown** format (structured with headers, fields, etc.)
3. **Use Pandoc** to convert Markdown to the target format (DOCX, HTML, PDF, etc.)

### Process Flow

```
Books Database → Markdown → Pandoc → Target Format (DOCX/HTML/PDF/etc.)
```

### Example Markdown Structure

The tool generates Markdown like this:

```markdown
# Calibre Library Export

Exported on: 2025-01-21 14:30:00
Total books: 5

---

## The Adventures of Sherlock Holmes

**ID:** 123
**Authors:** Arthur Conan Doyle
**Series:** Sherlock Holmes
**Rating:** ★★★★
**Tags:** mystery, detective, classic
**Publisher:** Penguin Books
**Publication Date:** 1892-01-01
**ISBN:** 9780140439074

**Comments:**
A collection of twelve detective stories...

---

## A Study in Scarlet

**ID:** 124
...
```

---

## Installation Requirements

### For CSV/JSON Export
- **No additional dependencies** - uses Python standard library

### For Pandoc Export
1. **Install Pandoc:**
   - **Windows:** Download from [pandoc.org/installing](https://pandoc.org/installing.html)
   - **macOS:** `brew install pandoc`
   - **Linux:** `sudo apt-get install pandoc` (Debian/Ubuntu)

2. **Verify Installation:**
   ```bash
   pandoc --version
   ```

3. **For PDF Export (Optional):**
   - **Windows:** Install MiKTeX
   - **macOS/Linux:** Install TeX Live
   - Note: PDF export is slower and requires LaTeX

---

## Output Locations

### Default Behavior
- If `output_path` is not specified, files are saved to **Desktop**
- Filenames are auto-generated with timestamp:
  - CSV: `calibre_books_export_20250121_143000.csv`
  - JSON: `calibre_books_export_20250121_143000.json`
  - Pandoc: `calibre_books_export_20250121_143000.{format}`

### Custom Paths
You can specify any path:
```python
export_books_csv(output_path="C:/Exports/my_books.csv")
export_books_pandoc(format_type="docx", output_path="D:/Documents/books.docx")
```

---

## Filtering Options

All export tools support the same filtering:

### By Author
```python
export_books_csv(author="Conan Doyle")
export_books_pandoc(format_type="html", author="Mick Herron")
```

### By Tag
```python
export_books_csv(tag="mystery")
export_books_json(tag="science fiction")
```

### By Book IDs
```python
export_books_csv(book_ids=[1, 2, 3, 5, 8])
export_books_pandoc(format_type="docx", book_ids=[10, 20, 30])
```

### Combined Filters
```python
export_books_csv(author="Conan Doyle", tag="detective")
```

---

## Response Format

All export tools return a consistent response:

```json
{
  "success": true,
  "file_path": "C:/Users/Name/Desktop/calibre_books_export_20250121_143000.csv",
  "books_exported": 42,
  "export_date": "2025-01-21T14:30:00",
  "format": "csv"  // or "json", "docx", etc.
}
```

If Pandoc is not available:
```json
{
  "success": false,
  "error": "Pandoc is not installed or not in PATH...",
  "pandoc_available": false,
  "file_path": null,
  "books_exported": 0
}
```

---

## Advanced Usage

### Custom CSV Fields

```python
export_books_csv(
    include_fields=["title", "authors", "rating", "tags", "isbn"]
)
```

Available fields: `id`, `title`, `authors`, `tags`, `series`, `rating`, `pubdate`, `publisher`, `isbn`, `comments`, `formats`, `has_cover`, `timestamp`

### Large Exports

```python
# Export all books (no limit)
export_books_csv(limit=-1)

# Export with pagination
export_books_csv(limit=1000)  # First 1000
# Then use offset or filter for next batch
```

### Format-Specific Options

**PDF Export:**
```python
export_books_pandoc(format_type="pdf", limit=50)  # PDF is slower, use smaller limits
```

**HTML Export:**
```python
export_books_pandoc(format_type="html")  # Fast, works well for large exports
```

---

## Comparison with Advanced Memory MCP

| Feature | Advanced Memory MCP | Calibre MCP |
|---------|---------------------|-------------|
| Pandoc Integration | ✅ Yes (`adn_export`) | ✅ Yes (`export_books_pandoc`) |
| CSV Export | ❌ No | ✅ Yes (`export_books_csv`) |
| JSON Export | ✅ Yes | ✅ Yes (`export_books_json`) |
| Markdown → Pandoc | ✅ Yes | ✅ Yes |
| Format Support | Many formats | docx, html, pdf, epub, latex, odt, rtf, txt |
| Auto-detection | ✅ Desktop path | ✅ Desktop path |
| Filtering | ✅ Yes | ✅ Yes (author, tag, book_ids) |

---

## Troubleshooting

### Pandoc Not Found
```
Error: "Pandoc is not installed or not in PATH"
```
**Solution:** Install Pandoc and ensure it's in your system PATH.

### PDF Export Fails
```
Error: "Pandoc conversion failed: pdflatex not found"
```
**Solution:** Install LaTeX (MiKTeX on Windows, TeX Live on Linux/Mac).

### Large Export Timeout
```
Error: "Pandoc conversion timed out"
```
**Solution:** Use smaller `limit` parameter or export in batches.

### CSV Encoding Issues
The CSV export uses `utf-8-sig` encoding which is compatible with Excel.
If you still have issues, try opening the file with UTF-8 encoding in your spreadsheet application.

---

## Best Practices

1. **Use CSV for spreadsheet analysis** (Excel, Google Sheets)
2. **Use JSON for data exchange/backup** (API integration, backup)
3. **Use Pandoc DOCX for reports** (sharing, printing, documentation)
4. **Use Pandoc HTML for web viewing** (fast, works everywhere)
5. **Use Pandoc PDF for final documents** (but it's slower, use smaller limits)

For regular exports, CSV is recommended. For formatted documents, use Pandoc with DOCX or HTML.

