# Calibre Library Structure Documentation

## Overview

This document describes the structure and organization of Calibre libraries used by CalibreMCP. Understanding this structure is essential for effective library management and tool development.

**NEW**: CalibreMCP now automatically discovers Calibre libraries by reading Calibre's configuration files and scanning common locations, making it universally useful across different systems and setups.

## Library Discovery

### Automatic Discovery

CalibreMCP automatically discovers Calibre libraries using multiple methods:

1. **Calibre Configuration Files**: Reads from Calibre's global configuration
   - Windows: `%APPDATA%\calibre\global.py`
   - macOS: `~/Library/Preferences/calibre/global.py`
   - Linux: `~/.config/calibre/global.py`

2. **Library Database**: Parses `library_infos.json` and `library_infos.pickle`

3. **Common Locations**: Scans standard Calibre library locations

4. **Environment Variables**: Supports `CALIBRE_LIBRARY_PATH` and `CALIBRE_LIBRARIES`

5. **Parent Directory Scanning**: Discovers libraries in parent directories

### Configuration

```python
from calibre_mcp.config import CalibreConfig

# Auto-discovery enabled by default
config = CalibreConfig.load_config()

# List all discovered libraries
libraries = config.list_libraries()
for lib in libraries:
    print(f"{lib['name']}: {lib['path']}")

# Switch active library
config.set_active_library("IT Library")
```

## Library Organization

### Base Directory Structure

```
L:\Multimedia Files\Written Word\
├── Calibre-Bibliothek (Main Library - 4,982 books)
├── Calibre-Bibliothek Bullshit
├── Calibre-Bibliothek Comics  
├── Calibre-Bibliothek Deutsch
├── Calibre-Bibliothek IT
├── Calibre-Bibliothek Japanisch
├── Calibre-Bibliothek Magazines
├── Calibre-Bibliothek Manga
├── Calibre-Bibliothek Private
├── Calibre-Bibliothek Test
├── Calibre-Bibliothek-Private-2
├── Digitale Bibliothek
├── Light Novels
├── Manuals
└── metadata.db (35MB database)
```

### Specialized Libraries

| Library Name | Purpose | Content Type |
|--------------|---------|--------------|
| **Calibre-Bibliothek** | Main collection | General books, literature, non-fiction |
| **Calibre-Bibliothek IT** | Technology books | Programming, software, technical manuals |
| **Calibre-Bibliothek Japanisch** | Japanese content | Japanese literature, language learning |
| **Calibre-Bibliothek Manga** | Manga collection | Japanese comics and graphic novels |
| **Calibre-Bibliothek Comics** | Western comics | Graphic novels, comic books |
| **Calibre-Bibliothek Deutsch** | German content | German literature and books |
| **Calibre-Bibliothek Magazines** | Periodicals | Magazines, journals, periodicals |
| **Light Novels** | Light novel collection | Japanese light novels |
| **Manuals** | Technical documentation | User manuals, technical guides |

## Individual Book Structure

### Standard Calibre Pattern

Each book follows the standard Calibre organization pattern:

```
Author Name/
└── Book Title (ID)/
    ├── cover.jpg          # Book cover image
    ├── metadata.opf       # Metadata in OPF format
    └── Book Title - Author.format  # Book file (EPUB, PDF, etc.)
```

### Example Structure

```
18 Afghan Women/
└── My Pen Is the Wing of a Bird_ New (10942)/
    ├── cover.jpg (2MB)
    ├── metadata.opf (2.3KB)
    └── My Pen Is the Wing of a Bird_ N - 18 Afghan Women.epub (2.4MB)
```

## Database Structure

### Metadata Database

Each Calibre library contains a `metadata.db` SQLite database that stores:

- **Books**: Title, authors, series, publication info
- **Authors**: Author names and metadata
- **Series**: Series information and book ordering
- **Tags**: Categorization and tagging system
- **Formats**: Available file formats for each book
- **Identifiers**: ISBN, DOI, and other identifiers
- **Custom Fields**: User-defined metadata fields

### Database Size

- **Main Library**: 35MB metadata database
- **Total Books**: 4,982 books in main library
- **Average per book**: ~7KB metadata per book

## File Formats

### Supported Formats

CalibreMCP supports the following book formats:

| Format | Extension | Description |
|--------|-----------|-------------|
| **EPUB** | `.epub` | Standard e-book format |
| **PDF** | `.pdf` | Portable Document Format |
| **MOBI** | `.mobi` | Amazon Kindle format |
| **AZW3** | `.azw3` | Amazon Kindle format v3 |
| **FB2** | `.fb2` | FictionBook format |
| **TXT** | `.txt` | Plain text format |
| **RTF** | `.rtf` | Rich Text Format |
| **HTML** | `.html` | HyperText Markup Language |

### Cover Images

- **Format**: JPEG
- **Naming**: `cover.jpg`
- **Size**: Typically 1-5MB
- **Resolution**: Various (usually 600x800 or higher)

## Library Management Features

### Multi-Library Support

CalibreMCP provides tools for:

- **Library Discovery**: Automatic detection of all Calibre libraries
- **Library Switching**: Change active library context
- **Cross-Library Search**: Search across multiple libraries simultaneously
- **Library Statistics**: Analytics for each library

### Austrian Efficiency Organization

The library structure supports Sandra's efficiency principles:

- **Clear Separation**: Different content types in separate libraries
- **Specialized Collections**: IT, Japanese, Manga, Comics in dedicated libraries
- **Easy Navigation**: Logical folder structure for quick access
- **Metadata Consistency**: Standardized metadata across all libraries

## Integration with CalibreMCP Tools

### Core Operations

- **`list_books`**: Browse books with filtering and sorting
- **`get_book_details`**: Retrieve complete book metadata
- **`search_books`**: Full-text search across libraries
- **`test_calibre_connection`**: Verify library accessibility

### Library Management

- **`list_libraries`**: Discover all available libraries
- **`switch_library`**: Change active library context
- **`get_library_stats`**: Get comprehensive library analytics
- **`cross_library_search`**: Search across multiple libraries

### Specialized Features

- **`japanese_book_organizer`**: Organize Japanese content libraries
- **`it_book_curator`**: Manage IT and programming book collections
- **`reading_recommendations`**: AI-powered reading suggestions

## Best Practices

### Library Organization

1. **Use Descriptive Names**: Clear library names indicating content type
2. **Consistent Structure**: Maintain standard Calibre folder structure
3. **Regular Maintenance**: Keep metadata updated and organized
4. **Backup Strategy**: Regular backups of metadata databases

### Performance Considerations

1. **Database Size**: Large libraries may have slower query performance
2. **File Access**: Network drives may impact file access speed
3. **Concurrent Access**: Multiple tools accessing same library simultaneously
4. **Memory Usage**: Large metadata databases require adequate RAM

## Troubleshooting

### Common Issues

1. **Library Not Found**: Check library path configuration
2. **Permission Errors**: Ensure read/write access to library directories
3. **Database Corruption**: Use Calibre's built-in repair tools
4. **Missing Files**: Verify book files exist in expected locations

### Diagnostic Tools

- **`test_calibre_connection`**: Verify library accessibility
- **`analyze_library_health`**: Check for missing files and metadata issues
- **`find_duplicate_books`**: Identify potential duplicate entries

## Future Enhancements

### Planned Features

1. **Library Synchronization**: Sync changes between libraries
2. **Advanced Analytics**: Deeper insights into reading patterns
3. **Automated Organization**: AI-powered library organization
4. **Cloud Integration**: Support for cloud-based libraries

### Integration Opportunities

1. **Calibre Content Server**: Direct integration with Calibre's web interface
2. **Mobile Apps**: Mobile library management capabilities
3. **Reading Apps**: Integration with e-reader applications
4. **Social Features**: Sharing and recommendation systems

---

*This documentation is maintained as part of the CalibreMCP project and follows the Austrian efficiency principles for clear, comprehensive, and actionable information.*
