# CalibreMCP 📚

**FastMCP 2.11.3 server for comprehensive Calibre e-book library management + Academic Research through Claude Desktop**

[![FastMCP](https://img.shields.io/badge/FastMCP-2.11.3-blue)](https://github.com/jlowin/fastmcp)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Calibre](https://img.shields.io/badge/Calibre-6.0+-orange)](https://calibre-ebook.com)
[![ArXiv](https://img.shields.io/badge/ArXiv-API-red)](https://arxiv.org)

Austrian efficiency for Sandra's 1000+ book digital library + academic research platform. Built with realistic AI-assisted development timelines (days, not weeks).

## 🆕 **MAJOR ENHANCEMENT PLANNED - 2025-08-28**

**CalibreMCP is being transformed from library browser to complete e-reader + academic research platform:**

### **🔥 New Capabilities Coming**
- **📖 Full File Reading**: EPUB, PDF (sophisticated), CBZ/CBR comic readers
- **📊 Stateful Features**: Reading progress, recommendations, reading lists (FastMCP 2.11.3)
- **📚 Library Management**: Book upload, bulk import, format conversion
- **🌐 External Integration**: Anna's Archive search + download
- **🎓 Academic Research**: ArXiv integration, citation management, academic PDF reader
- **🧠 AI Features**: Personalized recommendations, research trend analysis

**Development Timeline**: 18-24 hours (3-4 focused days)
**Status**: Comprehensive plan complete, ready for implementation

---

## 📖 About Calibre Software

**Calibre** is the world's most popular open-source e-book library management software, created by Kovid Goyal. It's a complete e-book solution that handles:

### Core Calibre Features

- **Library Management**: Organize thousands of books with metadata, covers, and custom tags
- **Format Conversion**: Convert between 50+ e-book formats (EPUB, MOBI, PDF, AZW, etc.)
- **E-book Editing**: Built-in editor for EPUB files with syntax highlighting
- **News/Magazine Sync**: Download news from 300+ sources and convert to e-books
- **Device Sync**: Transfer books to e-readers, tablets, and smartphones
- **Server Mode**: Web-based library access and streaming to any device
- **Metadata Management**: Automatic metadata retrieval from multiple sources
- **Custom Columns**: Extensible metadata system for specialized cataloging

### Calibre Server REST API

- **Web Interface**: Full library access through browser at `http://localhost:8080`
- **OPDS Support**: Standard e-book catalog protocol for reader apps
- **Authentication**: Optional user management and access control
- **Search API**: Powerful query syntax with field-specific searches
- **Streaming**: Direct e-book streaming without downloads
- **Cover Generation**: Automatic cover art creation and management

Calibre excels at managing large personal libraries (1000+ books) with sophisticated search, organizational, and conversion capabilities.

---

## 🚀 CalibreMCP Features

### **Current Phase 1 Tools (Production Ready)** ✅

1. **`list_books(query?, limit=50, sort="title")`**
   - Browse/search library with flexible filtering
   - Natural language queries, sorting, result limits
   - Returns structured `LibrarySearchResponse` with metadata

2. **`get_book_details(book_id)`**
   - Complete metadata and file information
   - All formats, cover URLs, download links, series info
   - Full book object with computed fields

3. **`search_books(text, fields?, operator?)`**
   - Advanced search with field targeting
   - Boolean AND/OR operations, field-specific queries
   - Filtered results with relevance scoring

4. **`test_calibre_connection()`**
   - Connection testing and diagnostics
   - Server info, library stats, auth verification
   - Performance metrics and capability detection

### **🔥 MAJOR ENHANCEMENTS PLANNED**

### **Phase 1 Enhanced: File Reading Tools (4 tools)** 🚧
- **`read_epub(book_id, chapter?, bookmark_id?)`** - Extract EPUB text with navigation
- **`read_pdf(book_id, page?, section?, use_toc=True)`** - Sophisticated PDF reader with TOC
- **`read_comic(book_id, page_range?)`** - CBZ/CBR comic reader with image extraction  
- **`get_book_content_info(book_id)`** - Content structure analysis (chapters, pages, TOC)

### **Phase 2: Stateful Features (FastMCP 2.11.3) (6 tools)** 🚧
- **`save_reading_progress(book_id, position, notes?)`** - Track reading across sessions
- **`get_reading_progress(book_id)`** - Retrieve saved reading position
- **`create_reading_list(name, book_ids[], tags[])`** - Organize reading collections
- **`manage_reading_lists(action, list_id, book_ids?)`** - Reading list management
- **`rate_book(book_id, rating, review?)`** - Book rating and review system
- **`get_reading_recommendations(count=10, genre?)`** - AI-powered suggestions

### **Phase 3: Library Management (4 tools)** 🚧  
- **`upload_book(file_path, metadata?, auto_detect=True)`** - Add new books to library
- **`bulk_import_books(directory_path, recursive=True)`** - Mass book import
- **`convert_book_format(book_id, target_format, quality)`** - Format conversion
- **`manage_duplicates(action, auto_merge?)`** - Duplicate detection and handling

### **Phase 4: External Integration (3 tools)** 🚧
- **`search_annas_archive(query, format_filter?, limit=20)`** - Anna's Archive search
- **`download_from_annas_archive(result_id, target_dir)`** - Automated download
- **`get_annas_archive_info(url)`** - Metadata extraction

### **Phase 5: Academic Research - ArXiv Integration (7 tools)** 🚧
- **`search_arxiv(query, subject_class?, max_results=20)`** - Academic paper search
- **`get_arxiv_paper_info(arxiv_id)`** - Paper metadata extraction
- **`download_arxiv_paper(arxiv_id, target_dir?)`** - Academic paper download  
- **`get_arxiv_categories()`** - Available research categories
- **`read_academic_pdf(paper_id, section?)`** - Academic-optimized PDF reader
- **`extract_paper_citations(paper_id)`** - Citation extraction and management
- **`create_research_notes(paper_id, notes, tags[])`** - Research note organization

### **Phase 6: Advanced Features (5 tools)** 🚧
- **`get_pdf_toc(book_id)`** - Extract PDF table of contents
- **`navigate_pdf_section(book_id, toc_id)`** - Section-based PDF navigation
- **`search_book_content(book_id, query, context_lines=2)`** - Full-text search within books
- **`extract_book_images(book_id)`** - Image extraction from any format
- **`create_book_summary(book_id)`** - AI-powered content summaries

**Total New Tools**: ~30 additional functions transforming CalibreMCP into complete e-reader + research platform

---

## 🎓 Academic Research Features

### **ArXiv Integration**
- **Official API**: Respectful integration with ArXiv.org academic repository
- **Search Capabilities**: Title, author, abstract, subject classification
- **Format Support**: PDF download with academic metadata
- **Citation Management**: BibTeX export, reference tracking
- **Research Workflow**: Seamless integration with general library

### **Academic PDF Reader** 
- **Structure Detection**: Automatic identification of Abstract, Introduction, Methods, Results, Discussion
- **Section Navigation**: Jump directly to paper sections
- **Figure Extraction**: Browse academic figures and tables with captions  
- **Citation Linking**: Click references to jump to bibliography
- **Research Notes**: Section-specific note-taking and highlighting

### **Academic Workflow**
1. **Literature Search** → ArXiv + Anna's Archive for academic books
2. **Paper Collection** → Auto-import with rich academic metadata
3. **Structured Reading** → Section-based navigation with progress tracking
4. **Note Management** → Research notes linked to specific content
5. **Citation Building** → Automated bibliography generation
6. **Knowledge Discovery** → Related paper recommendations based on reading history

---

## 📦 Installation & Setup

### **Prerequisites**

- **Python 3.11+** with pip
- **Calibre 6.0+** installed and running
- **Calibre Content Server** enabled (see configuration below)
- **FastMCP 2.11.3+** for stateful features

### **Step 1: Install CalibreMCP**

```powershell
cd d:\dev\repos\calibremcp
pip install -e .

# Install enhanced dependencies (when implemented)
pip install ebooklib PyMuPDF rarfile pytesseract arxiv
```

### **Step 2: Configure Calibre Content Server**

Enable Calibre's built-in web server for API access:

#### Option A: GUI Configuration

1. Open Calibre → Preferences → Sharing over the net
2. Enable "Start Content Server automatically"
3. Set port to 8080 (default)
4. Configure authentication if needed
5. Apply and restart Calibre

#### Option B: Command Line Server

```powershell
# Start Calibre content server
calibre-server --port=8080 --enable-auth --manage-users

# Or without authentication
calibre-server --port=8080
```

### **Step 3: Environment Configuration**

Create `.env` file in the project root:

```env
# Calibre server connection
CALIBRE_SERVER_URL=http://localhost:8080
CALIBRE_USERNAME=your_username
CALIBRE_PASSWORD=your_password

# Performance settings
CALIBRE_TIMEOUT=30
CALIBRE_MAX_RETRIES=3
CALIBRE_DEFAULT_LIMIT=50

# Academic features
ARXIV_MAX_RESULTS=20
ARXIV_DEFAULT_CATEGORIES=cs.AI,cs.CL,cs.LG
ENABLE_ACADEMIC_FEATURES=true

# External integrations  
ANNAS_ARCHIVE_ENABLED=true
ENABLE_OCR=false  # Set true if tesseract installed
```

---

## 🔧 Claude Desktop Integration

Add CalibreMCP to your Claude Desktop configuration:

### **claude_desktop_config.json**

```json
{
  "mcpServers": {
    "calibre-mcp": {
      "command": "python",
      "args": ["-m", "calibre_mcp.server"],
      "env": {
        "CALIBRE_SERVER_URL": "http://localhost:8080",
        "CALIBRE_USERNAME": "your_username",
        "CALIBRE_PASSWORD": "your_password",
        "ENABLE_ACADEMIC_FEATURES": "true",
        "ARXIV_MAX_RESULTS": "20"
      }
    }
  }
}
```

---

## 💡 Enhanced Usage Examples

### **Current Library Management**

```python
# "Show me the last 20 books I added to my library, sorted by date"
list_books(limit=20, sort="date")

# "Find all my programming books"  
list_books("programming", limit=50, sort="rating")

# "Tell me everything about book ID 12345"
get_book_details(12345)
```

### **Enhanced Reading (Planned)**

```python
# "Read chapter 3 of book 12345"
read_epub(12345, chapter=3)

# "Show me the table of contents for this PDF"
get_pdf_toc(67890)

# "Continue reading from where I left off"
progress = get_reading_progress(12345)
read_epub(12345, bookmark_id=progress.bookmark_id)
```

### **Academic Research (Planned)**

```python
# "Search ArXiv for papers about transformer architectures"
search_arxiv("transformer architecture", subject_class="cs.CL", max_results=10)

# "Download and add this ArXiv paper to my library"
download_arxiv_paper("2017.01234", target_dir="academic_papers")

# "Read the methodology section of this paper"
read_academic_pdf("arxiv_2017_01234", section="methodology")
```

### **Stateful Features (Planned)**

```python
# "Save my reading progress and add a note"
save_reading_progress(12345, {"chapter": 5, "page": 120}, notes="Interesting discussion on AI ethics")

# "Create a reading list for machine learning books"
create_reading_list("ML Reading", book_ids=[12345, 67890], tags=["technical", "priority"])

# "Give me book recommendations based on my reading history"
get_reading_recommendations(count=5, genre="science_fiction")
```

---

## 🎯 Austrian Efficiency Features

### **Real Use Cases Prioritized**

- **Fast browsing** - 50 books max by default (no analysis paralysis)
- **Smart search** - Natural language queries with relevance
- **Series management** - Automatic series detection and sorting
- **Format awareness** - Know which books have EPUB, PDF, MOBI
- **Performance first** - Sub-second responses for 1000+ book libraries
- **Academic integration** - Seamless research paper + book management
- **Reading continuity** - Stateful progress tracking across sessions

### **Practical, Not Perfect**

- **No stubs** - All implemented tools are 100% functional
- **Error resilience** - Graceful handling of server issues
- **Diagnostic tools** - Built-in connection testing and troubleshooting
- **Realistic timelines** - Days not weeks for major enhancements
- **Educational focus** - Academic features for learning and research

### **Sandra's Enhanced Workflow**

- **Weeb-friendly** - Handles Japanese characters and metadata
- **Academic quality** - Research paper integration with personal library
- **Budget conscious** - Efficient API calls, minimal server load
- **Direct communication** - Clear error messages, no AI platitudes
- **Stateful continuity** - Resume reading sessions, track progress
- **Research integration** - ArXiv papers alongside general books

---

## 🛣️ Development Roadmap

### **Enhanced Phases (Planned Implementation)**

**Phase 1: Enhanced Core Reading (4-5 hours)**
- Sophisticated PDF reader with TOC navigation
- Enhanced EPUB reader with chapter navigation  
- Comic reader for CBZ/CBR files
- Content structure analysis

**Phase 2: Stateful Features (3-4 hours)**
- FastMCP 2.11.3 stateful integration
- Reading progress tracking
- Reading list management
- Rating and recommendation system

**Phase 3: Library Management (2-3 hours)**
- Book upload and import system
- Format conversion tools
- Duplicate detection and management

**Phase 4: External Integration (3-4 hours)**
- Anna's Archive search and download
- Metadata matching and import
- Progress tracking for downloads

**Phase 5: Academic Integration (3-4 hours)**
- ArXiv API integration
- Academic PDF reader enhancements
- Citation management tools
- Research note organization

**Phase 6: Advanced Features (2-3 hours)**
- AI-powered recommendations
- Full-text search across library
- Reading analytics and statistics
- Performance optimization

**Total Development Time**: 18-24 hours (3-4 focused days)

---

## 🧪 Testing & Development

### **Enhanced MCP Inspector Testing**

```powershell
# Start development server with inspector
python -m calibre_mcp.server

# Navigate to: http://127.0.0.1:6274
# Test all phases systematically:
# - Phase 1: File reading tools (EPUB, PDF, Comics)
# - Phase 2: Stateful features (progress, lists, recommendations)  
# - Phase 3: Library management (upload, convert, organize)
# - Phase 4: External integration (Anna's Archive)
# - Phase 5: Academic features (ArXiv, citations, research)
```

### **Academic Feature Testing (When Implemented)**

```powershell
# Test ArXiv integration
python -c "
import arxiv
search = arxiv.Search(query='transformer', max_results=5)
for result in search.results():
    print(f'{result.title} - {result.entry_id}')
"

# Test PDF academic structure detection
python -c "
import fitz
doc = fitz.open('academic_paper.pdf')
toc = doc.get_toc()
print(f'TOC entries: {len(toc)}')
"
```

---

## 🚨 Troubleshooting

### **Current Issues**

#### **Connection Failed**
```
Error: Connection failed: [Errno 10061] No connection could be made
```

**Solution**:
1. Verify Calibre Content Server is running
2. Check server URL and port (default: 8080)
3. Test with: `http://localhost:8080` in browser

#### **Authentication Failed**
```
Error: Authentication failed - check username/password
```

**Solution**:
1. Verify credentials in `.env` file
2. Test login via web interface
3. Check if authentication is actually enabled

### **Future Enhancement Troubleshooting**

#### **Academic Features (When Implemented)**
- ArXiv API connectivity issues
- PDF structure detection failures
- Citation extraction problems
- Research note synchronization

#### **Stateful Features (When Implemented)**
- State persistence failures
- Reading progress corruption
- Recommendation algorithm issues
- Session management problems

---

## 📈 Performance & Scaling

### **Current Performance**
- **Small library (< 100 books)**: < 100ms response times
- **Medium library (100-1000 books)**: < 500ms response times  
- **Large library (1000+ books)**: < 2s response times

### **Enhanced Performance Targets**
- **File reading**: < 5s for EPUB/PDF text extraction
- **Academic search**: < 3s for ArXiv API queries
- **Stateful operations**: < 1s for progress saves/loads
- **Recommendation generation**: < 10s for AI-powered suggestions

---

## 🎉 Success Metrics

### **Current Phase 1 Achievement (✅ Complete)**
- ✅ 4/4 core tools implemented and tested
- ✅ FastMCP 2.0 compliance with proper structure
- ✅ Comprehensive error handling and diagnostics  
- ✅ Austrian efficiency: 45-minute implementation
- ✅ Real working code - no stubs or placeholders
- ✅ Production-ready for immediate Claude Desktop use

### **Enhanced Target Achievements**
- 🎯 Transform into complete e-reader platform
- 🎯 Academic research integration
- 🎯 Stateful user experience with FastMCP 2.11.3
- 🎯 External content integration (Anna's Archive)
- 🎯 AI-powered personalized recommendations
- 🎯 Maintain Austrian efficiency principles

**Timeline Commitment**: Complete enhancement in realistic AI-assisted timeline (3-4 focused days vs. weeks/months of traditional development)

---

*Built with Austrian efficiency for Sandra's comprehensive e-book + academic research workflow. Enhanced with stateful features, external integrations, and AI-powered recommendations. "Sin temor y sin esperanza" - practical without hype or doom.*