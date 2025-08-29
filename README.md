# CalibreMCP 📚

**FastMCP 2.0 server for comprehensive Calibre e-book library management through Claude Desktop**

[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-blue)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Austrian Efficiency](https://img.shields.io/badge/Austrian-Efficiency-red)](https://en.wikipedia.org/wiki/Austrian_school)

*Austrian efficiency for Sandra's 1000+ book digital library. Built with realistic AI-assisted development timelines (days, not weeks).*

## 🚀 Quick Start

### **Prerequisites**

- **Python 3.11+** with pip
- **Calibre 6.0+** installed and running
- **Calibre Content Server** enabled on port 8080

### **Installation**

```bash
cd d:\dev\repos\calibremcp
pip install -e .
```

### **Start Calibre Server**

```bash
# Option 1: Through Calibre GUI
# Calibre → Connect/share → Start Content Server

# Option 2: Command line
calibre-server --port=8080
```

### **Test Connection**

```bash
python -c "
from calibre_mcp.calibre_api import quick_library_test
import asyncio
print('✅ Working' if asyncio.run(quick_library_test()) else '❌ Failed')
"
```

### **Claude Desktop Integration**

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "calibre-mcp": {
      "command": "python",
      "args": ["-m", "calibre_mcp.server"],
      "env": {
        "CALIBRE_SERVER_URL": "http://localhost:8080"
      }
    }
  }
}
```

## Features

### Core Features
- **Full Library Access** - Search, browse, and manage your entire Calibre collection
- **Smart Metadata** - Automatic metadata enhancement and validation
- **Format Conversion** - On-the-fly conversion between formats
- **Reading Progress** - Track reading progress across devices
- **Tag Management** - Smart tagging and categorization
- **Library Statistics** - Detailed insights into your collection

### AI-Powered Tools
- **Book Recommendations** - Get personalized book suggestions based on content similarity
- **Content Analysis** - Extract entities, themes, and sentiment from book content
- **Reading Insights** - Analyze your reading habits and preferences
- **Metadata Enhancement** - AI-assisted metadata correction and enrichment

### Advanced Series Management
- **Series Analysis** - Identify and fix issues in book series
- **Metadata Validation** - Ensure consistency across your library
- **Series Merging** - Combine duplicate or related series
- **Automatic Organization** - Keep your series properly ordered and managed

## Usage Examples

### AI-Powered Recommendations
```python
# Get book recommendations based on a book
recommendations = await get_book_recommendations(book_id="123")

# Get personalized recommendations based on preferences
preferences = {
    "favorite_authors": ["Brandon Sanderson", "N.K. Jemisin"],
    "favorite_genres": ["Fantasy", "Science Fiction"]
}
personalized_recs = await get_book_recommendations(user_preferences=preferences)
```

### Content Analysis
```python
# Analyze book content
analysis = await analyze_book_content(
    book_content="...",
    options={
        "extract_entities": True,
        "analyze_sentiment": True,
        "identify_themes": True
    }
)
```

### Series Management
```python
# Analyze series in your library
analysis = await analyze_series(
    library_path="/path/to/calibre/library",
    update_metadata=True
)

# Fix common series metadata issues
fix_results = await fix_series_metadata(
    library_path="/path/to/calibre/library",
    dry_run=False
)

# Merge two series
merge_results = await merge_series(
    library_path="/path/to/calibre/library",
    source_series="The Kingkiller Chronicle",
    target_series="Kingkiller Chronicle",
    dry_run=True
)
```

## Documentation

Full documentation available at [docs/](docs/).

## Testing

```bash
# Unit tests
python -m pytest tests/test_api.py -v

# Integration tests  
python -m pytest tests/integration_tests.py -v

# MCP Inspector
python -m calibre_mcp.server
# Opens: http://127.0.0.1:6274
```

## 🔧 Configuration

### **Environment Variables**

```env
CALIBRE_SERVER_URL=http://localhost:8080
CALIBRE_USERNAME=your_username      # If auth enabled
CALIBRE_PASSWORD=your_password      # If auth enabled
CALIBRE_TIMEOUT=30
CALIBRE_DEFAULT_LIMIT=50
```

### **With Authentication**

```bash
# Enable Calibre authentication
calibre-server --port=8080 --enable-auth --manage-users

# Add user and set environment
export CALIBRE_USERNAME="sandra"
export CALIBRE_PASSWORD="your_password"
```

## 🚨 Troubleshooting

### **Connection Failed**

```bash
# Check if Calibre server is running
netstat -an | findstr 8080  # Windows
curl http://localhost:8080  # Test in browser
```

### **No Books Found**

```bash
# Verify library has books
calibredb list --limit=5

# Check library path
calibre-debug --get-library
```

### **Authentication Issues**

```bash
# Test credentials
curl -u username:password http://localhost:8080/ajax/interface-data/init
```

See **[Troubleshooting Guide](docs/Troubleshooting.md)** for comprehensive solutions.

## 🏗 Architecture

```
calibremcp/
├── src/calibre_mcp/
│   ├── server.py           # 4 FastMCP tools
│   ├── calibre_api.py      # HTTP API client
│   └── config.py           # Configuration management
├── config/
│   ├── settings.yaml       # Server configuration
│   └── calibre_config.yaml # Calibre-specific settings
├── tests/
│   ├── test_api.py         # Unit tests
│   └── integration_tests.py # Integration tests
└── docs/                   # Complete documentation
```

## 💯 Success Metrics

### **Phase 1 Complete** ✅

- ✅ 4/4 core MCP tools implemented and tested
- ✅ FastMCP 2.0 compliance with proper structure  
- ✅ Comprehensive error handling and diagnostics
- ✅ Austrian efficiency: 45-minute realistic timeline
- ✅ Production-ready for immediate Claude Desktop use

## 📄 License

MIT License - Austrian efficiency in e-book management.

---

**Built with Austrian efficiency for Sandra's comprehensive e-book workflow.**

*"Sin temor y sin esperanza" - practical without hype or doom.*
