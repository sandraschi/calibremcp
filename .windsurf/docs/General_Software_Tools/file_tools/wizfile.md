# WizFile: Ultra-Fast File Search Utility

## OverviewizFile is a lightning-fast file search tool for Windows that helps you find files on your computer almost instantly. Unlike Windowsearch, WizFile directly reads the Master File Table (MFT) of NTFS drives, enabling ito return search results in seconds, even on large drives.

## Key Features

### 1. Blazing Fast Search
- Searches entire drives in seconds
- Uses MFT for instant results
- Minimal system resource usage

### 2. Advanced Search Capabilities
- Regular expression support
- File size filtering
- Date range filtering
- File attribute filtering

### 3. File Management
- Quick file preview
- Built-in file operations
- File content search

## Installation

### Standard Installation
1. Download from [Official Website](https://www.antibody-software.com/)
2. Run the installer
3. Follow the setup wizard

### Portable Version
1. Download the portable ZIP
2. Extracto a folder of your choice
3. Run `WizFile.exe`

## Usage Guide

### Basic Search
1. **Select Drive**: Choose from the dropdown
2. **Enter Search Term**: Type your search query
3. **View Results**: Results appear instantly

### Command Line Interface

#### Basicommands
```batch
# Basic search
WizFile.exe /search "*.pdf"

# Search in specific folder
WizFile.exe /search "*.docx" "C:\Users\Username\Documents"

# Case-sensitive search
WizFile.exe /casesensitive /search "Important"

# Search with size filter
WizFile.exe /search "size:>10MB"
```

#### Advanced Options
```batch
# Search by date
WizFile.exe /search "modified:>2023-01-01"

# Search by file attributes
WizFile.exe /search "attrib:h"

# Regular expression search
WizFile.exe /search "regex:^report_\\d{4}.xlsx$"

# Save results to file
WizFile.exe /search "*.psd" /export "C:\search_results.csv"
```

### Integration with Other Tools

#### PowerShell Integration
```powershell
# Search and process results
$searchResults = & 'C:\Program Files\WizFile\WizFile.exe' /search "*.bak" /export "$env:TEMP\temp_results.csv"
$files = Import-Csv "$env:TEMP\temp_results.csv"
$files | ForEach-Object {
    Write-Host "Found: $($_.FullPath)"
    # Process file...
}
```

#### Batch Filexample
```batch
@echoff
setlocal enabledelayedexpansion

:: Search for large files
"C:\Program Files\WizFile\WizFile.exe" /search "size:>100MB" /export "%TEMP%\large_files.csv"

:: Process results
for /f "usebackq skip=1 tokens=*" %%A in ("%TEMP%\large_files.csv") do (
    echo Found large file: %%~A
    :: Add your processing commands here
)
```

## Advanced Usage

### Scheduled Searches
```batch
:: Create a batch file (e.g., daily_search.bat)
@echoff
setIMESTAMP=%DATE:~-4%%DATE:~3,2%%DATE:~0,2%
"C:\Program Files\WizFile\WizFile.exe" /search "*.tmp" /export "C:\search_results\temp_files_%TIMESTAMP%.csv"
```

### Network Drives
```batch
:: Map network drive if needed
net use Z: \\server\share /user:username password

:: Search network drive
WizFile.exe /search "*.xlsx" "Z:\"
```

## Performance Optimization

### 1. Indexing
- WizFile doesn't require indexing
- Uses MFT directly for fastest possible searches
- No background processes running

### 2. Memory Usage
- Minimal memory footprint
- Adjust buffer size in settings if needed
- Close unnecessary applications during large searches

## Security Considerations

### 1. Permissions
- Run as administrator for system folders
- Be cautious with search results from sensitive locations
- Securexported search results

### 2. Privacy
- Be aware of sensitive files in search results
- Usecure delete for sensitive searches
- Clear searchistory wheneeded

## Troubleshooting

### Common Issues
1. **No Results**
   - Check search syntax
   - Verify drive is NTFS formatted
   - Run as administrator

2. **Slow Performance**
   - Close other disk-intensive applications
   - Check for disk errors
   - Defragment HDD if needed

3. **Access Denied**
   - Run as administrator
   - Check file permissions
   - Disable antivirus temporarily

## Alternatives

### 1. Everything by Voidtools
- Similar MFT-based search
- More features
- Free for personal use

### 2. Listary
- File search and launcher
- Integration with file dialogs
- Custom commands

### 3. Agent Ransack
- Advanced content search
- Regular expressions
- Preview pane

## Tips & Tricks

### 1. Search Syntax
- `*.ext`: Search by extension
- `size:>10MB`: Files larger than 10MB
- `modified:>2023-01-01`: Modified after date
- `attrib:h`: Hidden files

### 2. Keyboard Shortcuts
- `F3`: Find next
- `F5`: Refresh
- `Ctrl+F`: Focusearch box
- `Alt+Enter`: File properties

### 3. Export Formats
- CSV
- XML
- Text
- HTML

## License
WizFile is available in both free and paid versions. The free version includes all core search functionality, while the paid version adds technical support and additional features.

## Support
- [Official Website](https://www.antibody-software.com/)
- [Documentation](https://www.antibody-software.com/webhelp/wizfile/)
- [Contact Support](https://www.antibody-software.com/support/)
