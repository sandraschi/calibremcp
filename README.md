# CalibreMCP 

[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![Web Interface](https://img.shields.io/badge/Web--Interface-Professional-purple)]()
[![FastMCP](https://img.shields.io/badge/FastMCP-3.2+-blue)](https://github.com/jlowin/fastmcp)
[![Calibre](https://img.shields.io/badge/Calibre-6.0+-orange)](https://calibre-ebook.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.5.0-blue)](pyproject.toml)
[![Status](https://img.shields.io/badge/Status-Active-success)](README.md)
[![Portmanteau Tools](https://img.shields.io/badge/Tools-22-orange)](docs/development/README.md)
[![Docstring Compliance](https://img.shields.io/badge/Docstrings-100%25-brightgreen)](docs/TOOL_DOCSTRING_STANDARD.md)
[![Austrian Efficiency](https://img.shields.io/badge/Austrian-Efficiency-red)](https://en.wikipedia.org/wiki/Austrian_school)

**FastMCP 3.2+ server for Calibre e-book library management with sampling, agentic workflows, skills, prompts, universal connect pattern, and LanceDB metadata RAG**

**Features:**
- **FastMCP 3.2** - Universal connect pattern, sampling, agentic tool chaining, optional SearchTools/CodeMode transforms
- **Concurrency Safety** - Thread-safe database operations with row-level locking for multi-client access
- **Universal Connect** - Support for simultaneous stdio + HTTP access from multiple clients
- **Metadata RAG (LanceDB)** - Semantic search over title, authors, tags, comments via `calibre_metadata_index_build` and `calibre_metadata_search` (`lancedb_metadata/`); see `docs/AGENTIC_AND_RAG.md`
- **Calibre FTS + phrase locations** - `search_fulltext(resolve_locations=True)`: PDF page / EPUB spine / Calibre `ebook-viewer --open-at search:` hints (`utils/fts_location_resolver.py`)
- **Full-book RAG** - FTS-driven chunk index (`rag_index_build` / `rag_retrieve`), portmanteau `calibre_rag`, DeepIngestor; consolidation design in `docs/FULL_TEXT_RAG_DESIGN.md`
- **Skills & Prompts** - Registered prompts and skill workflows (reading recommendations, library health, semantic search, agentic guide); bundled **`skill://calibre-expert/SKILL.md`**
- **Docs** - **[Full index](docs/DOCUMENTATION_INDEX.md)**  [MCP prompt catalog](docs/PROMPTS.md)  [Cookbook](docs/COOKBOOK.md) (recipes; pairs with [SEARCH_QUERY_EXAMPLES.md](docs/SEARCH_QUERY_EXAMPLES.md))  [MCP output schemas & skills (UTF-8)](docs/mcp-technical/MCP_OUTPUT_SCHEMAS_AND_SKILLS.md)  [MCP Apps / Prefab (optional rich cards)](docs/mcp-technical/MCP_APPS_PREFAB.md)
- **MCP Apps (Prefab)**  Optional **`show_book_prefab_card`**, **`show_libraries_prefab_card`** (Our Calibre): install with **`uv sync --extra apps`**; rich cards in capable clients; **`CALIBRE_PREFAB_APPS=0`** to disable. Fleet guide: [mcp-apps-prefab-ui.md](https://github.com/sandraschi/mcp-central-docs/blob/master/fastmcp/mcp-apps-prefab-ui.md)
- **Neural Media RAG & DeepIngestor** - Full-text LanceDB retrieval via `calibre_rag` and `rag_retrieve` when index is built
- **Webapp** - Full browser UI: sidebar nav, books/authors/series/tags, **Semantic Search (RAG)**, **Skills**, **Agentic** pages, AI chat (Ollama/LM Studio), **Stabilized Smart Import Hub** (arXiv, Gutenberg, Anna's Archive with lander detection)
- **Calibre Plugin** - Edit extended metadata (translator, first_published, user comments) in Calibre GUI; VL from query
- **Portmanteau Tools** - 21 consolidated portmanteau tools + RAG helpers (e.g. **`calibre_metadata_export_json`**); see FastMCP registration
- **Windows Compatibility** -  Fixed Unicode encoding issues, starts reliably on Windows
- **Standardized Documentation** - 100% compliance with docstring standards
- **Default Library Auto-Loading** - No manual library setup needed
- **Natural Language Search** - Intelligent parsing via FastMCP 3.1 sampling and agentic workflows (SEP-1577)
- **Auto-Open Books** -  Unique search results automatically launch in system viewer
- **Title-Specific Search** -  Fast, exact title matching with `title` parameter
- **Comprehensive Search** - All verbs (search, list, find, query, get) work seamlessly
- **Verb Mapping** - Claude automatically maps user queries to correct operations
- **Comment Management** - Dedicated CRUD operations for book comments
- **Random Book Opening** - Open random books by author/tag/series with `manage_viewer(operation="open_random")`
- **Metadata Display** - Show comprehensive book metadata with formatted HTML popup via `manage_metadata(operation="show")`

*Austrian efficiency for Sandra's 1000+ book digital library. Built with realistic AI-assisted development timelines (days, not weeks).*

##  Quick Start

### **Prerequisites**

- **Calibre 6.0+** installed and running
- **Calibre Content Server** enabled on port 8080 (optional, for remote access)
- **Node.js** (for MCPB package installation)
- **Python 3.11+** (for development/standard install)

### **Understanding Calibre Library Access Methods**

CalibreMCP supports multiple ways to access your Calibre library, each with different use cases:

#### **1. Direct Database Access (Local Libraries)**  **Supported - Primary Method**

**What it is:** Direct read/write access to Calibre's SQLite database (`metadata.db`)

**How it works:**
- CalibreMCP directly opens and queries the SQLite database file
- No Calibre application or server needs to be running
- Fast, efficient, and supports all operations

**When to use:**
-  **Default method** - Works automatically when you provide a library path
-  Local libraries on the same machine
-   performance for read operations
-  Full read/write access to metadata

**Configuration:**
- Set `calibre_library_path` to your Calibre library directory
- No additional setup required

**Example:**
```json
{
  "mcpServers": {
    "calibre-mcp": {
      "env": {
        "CALIBRE_LIBRARY_PATH": "L:/Multimedia Files/Written Word/Calibre-Bibliothek"
      }
    }
  }
}
```

#### **2. Calibre Content Server API**  **Supported - Remote Access**

**What it is:** HTTP API provided by Calibre's Content Server (`calibre-server`)

**How it works:**
- Uses Calibre's built-in Content Server (not the web interface)
- Communicates via HTTP/REST API
- Requires Calibre Content Server to be running

**When to use:**
-  Remote libraries (different machine/network)
-  When you want to access library over network
-  When Calibre GUI is running on another machine

**Configuration:**
- Start Calibre Content Server: `calibre-server --port=8080`
- Set `CALIBRE_SERVER_URL` environment variable
- **Authentication:** Optional for read-only access, **required for write/edit operations**

** Important Authentication Note:**
- **Read operations** (search, list, get details) work **without authentication**
- **Write/Edit operations** (update metadata, add books, delete) **require authentication**
- If you need to modify your library remotely, you must enable authentication

**Remote Access Setup:**

For accessing Calibre Content Server on a remote machine, you have two options:

**Option A: Port Forwarding (SSH/Network)**
```bash
# On the machine running Calibre Content Server
calibre-server --port=8080

# On your local machine, set up SSH port forwarding
ssh -L 8080:localhost:8080 user@remote-machine

# Then use localhost in your config
# CALIBRE_SERVER_URL: "http://localhost:8080"
```

**Option B: Tailscale (Recommended for Secure Remote Access)**
```bash
# On the machine running Calibre Content Server
calibre-server --port=8080 --listen-on=0.0.0.0

# On Tailscale network, use the Tailscale IP
# CALIBRE_SERVER_URL: "http://100.x.x.x:8080" (your Tailscale IP)
```

** Security Note:** When exposing Calibre Content Server over a network:
- **Read-only access** works without authentication (for browsing/searching)
- **Write/edit operations require authentication** - enable auth if you need to modify the library
- Use Tailscale or VPN for secure access (recommended)
- Avoid exposing directly to the internet without proper security

**Example Configuration:**
```json
{
  "mcpServers": {
    "calibre-mcp": {
      "env": {
        "CALIBRE_SERVER_URL": "http://localhost:8080",
        "CALIBRE_USERNAME": "optional_username",
        "CALIBRE_PASSWORD": "optional_password"
      }
    }
  }
}
```

**Start Calibre Content Server:**
```bash
# Option 1: Through Calibre GUI
# Calibre  Connect/share  Start Content Server

# Option 2: Command line (local only)
calibre-server --port=8080

# Option 3: Command line (network accessible - use with Tailscale/VPN)
calibre-server --port=8080 --listen-on=0.0.0.0

# With authentication (required for write/edit operations, optional for read-only)
calibre-server --port=8080 --listen-on=0.0.0.0 --enable-auth --manage-users
```

#### **3. Calibre Web Server**  **Not Supported**

**What it is:** Calibre's web-based user interface (different from Content Server)

**Status:** CalibreMCP does **not** support the Calibre Web Server interface. We use the Content Server API instead.

**Why not supported:**
- Web Server is designed for human interaction, not API access
- Content Server provides a proper REST API for programmatic access
- Direct database access is more efficient for local libraries

#### **4. Calibre CLI Tools**  **Available but Not Used by CalibreMCP**

**What it is:** Calibre provides command-line tools for library management

**Available CLI Tools:**
- `calibredb` - Database management (add, remove, export books, manage metadata)
- `ebook-convert` - Format conversion
- `ebook-meta` - Metadata reading/writing
- `calibre-server` - Content Server (used by CalibreMCP)

**Status:** CalibreMCP does **not** use these CLI tools. We use:
- Direct SQLite access for local libraries (faster, more reliable)
- Content Server API for remote libraries (proper API, not CLI)

**Why not used:**
- Direct database access is faster than CLI tools
- CLI tools require subprocess execution (slower, error-prone)
- API access is more reliable and provides better error handling

**Note:** You can still use Calibre CLI tools independently if needed:
```bash
# List books
calibredb list

# Convert format
ebook-convert book.epub book.pdf

# Get metadata
ebook-meta book.epub
```

#### **5. Calibre Plugin (Optional)** - GUI Integration

A Calibre plugin provides GUI integration for extended metadata and webapp features.

**Features:**
- Edit first_published, translator, user comments (Ctrl+Shift+M)
- Create virtual libraries from search queries (requires webapp backend)
- Syncs with `calibre_mcp_data.db` - no MCP process needed for metadata

**Install:** `calibre-customize -b calibre_plugin` or `calibre-customize -a calibre_mcp_integration.zip`

See [docs/integrations/CALIBRE_PLUGIN_DESIGN.md](docs/integrations/CALIBRE_PLUGIN_DESIGN.md).

#### **6. Webapp (Optional)** - Browser Interface

A Next.js webapp provides a full browser UI for the Calibre library.

**Features:**
- Retractable sidebar: Overview, Libraries, Books, Search, Authors, Series, Tags, Publishers, Import, Export, Chat, Logs, Settings, Help
- AI Chat (Ollama, LM Studio, OpenAI-compatible) with personality presets and Settings
- Book modal with full metadata (rating, publisher, series, identifiers, comments/description), Read button, author Wikipedia links
- Logs page: Log file viewer with tail, filter, level filter, live tail (polling with backoff), plus System status view
- Import (add by path), Export (CSV/JSON)

**Start:** Use `webapp\start.ps1` for reservoir ports (10720 backend, 10721 frontend) with kill-port zombie clear. Or legacy: `cd webapp/backend; uvicorn app.main:app --port 13000` and `cd webapp/frontend; npm run dev`  
See [webapp/README.md](webapp/README.md), [webapp/SETUP.md](webapp/SETUP.md) (port rules, zombie kill).

#### **7. Logging**

- **Stdio mode** (`python -m calibre_mcp`): Writes to `logs/calibremcp.log` with rotation (10MB, 5 backups)
- **Webapp backend**: Writes to `logs/webapp.log` with rotation
- Log files are tail-able via the webapp Logs page

---

### **Start Calibre Content Server** (if using remote access)

```bash
# Option 1: Through Calibre GUI
# Calibre  Connect/share  Start Content Server

# Option 2: Command line
calibre-server --port=8080

# With authentication
calibre-server --port=8080 --enable-auth --manage-users
```

---

##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx calibre-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "calibre-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/calibre-mcp", "run", "calibre-mcp"]
  }
}
```
### **1. PyPI Package Install (Recommended)** 

**Simple pip installation - no repository cloning required!**

```bash
# Install from PyPI
pip install calibre-mcp

# Configure Claude Desktop
{
  "mcpServers": {
    "calibre-mcp": {
      "command": "python",
      "args": ["-m", "calibre_mcp.server"],
      "env": {
        "CALIBRE_LIBRARY_PATH": "C:/path/to/your/calibre/library"
      }
    }
  }
}
```

**Advantages:**
-  **Universal compatibility** - Works with any MCP client
-  **Simple installation** - Just one pip command
-  **Always up-to-date** - Install latest version directly
-  **No repository cloning** - Clean, minimal setup
-  **Easy updates** - `pip install --upgrade calibre-mcp`

---

### **2. MCPB Package** 

**One-click installation via MCPB package - no Python setup required!**

> ** Important:** MCPB packages **only work with Claude Desktop**. They do not work with other MCP clients. The installation method is drag-and-drop only - there is no command-line installation option.

#### **What is MCPB?**

MCPB (Model Context Protocol Bundle) is a packaging format for MCP servers that bundles **self-contained source** (and assets) into a single `.mcpb` file for **Claude Desktop** drag-and-drop install. Fleet layout and rules: **[MCP Central Docs  MCPB_PACKAGING_STANDARDS.md](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/MCPB_PACKAGING_STANDARDS.md)** and **[PACKAGING_STANDARDS.md 5](https://github.com/sandraschi/mcp-central-docs/blob/master/standards/PACKAGING_STANDARDS.md#5-python-mcp-repo-uv-justfile-llmstxt-glama-mcpb-pack)** (no `pyproject.toml` / lockfiles inside the bundle; install Python deps via **`uv sync`** or PyPI from a clone).

CalibreMCPs pack root is **`mcpb/`** (`manifest.json`, `assets/`, synced `src/calibre_mcp/`). See **`mcpb/README.md`**. Build: **`just mcpb-pack`** or **`.\scripts\build-mcpb-package.ps1 -NoSign`**  **`dist\calibre-mcp.mcpb`**.

#### **Install MCPB CLI (for building packages)**

The MCPB CLI is only needed if you want to **build** packages from source. End users don't need it.

```bash
npm install -g @anthropic-ai/mcpb
mcpb --version
```

#### **Get the CalibreMCP Package**

**Option A: Download Pre-built Package**
- Download the latest `calibre-mcp.mcpb` from [Releases](../../releases)

**Option B: Build from Source** (requires cloning repo)
```bash
# Install MCPB CLI
npm install -g @anthropic-ai/mcpb

# Clone repository
git clone https://github.com/sandra/calibre-mcp.git
cd calibre-mcp

# Build the package
.\scripts\build-mcpb-package.ps1

# Package will be created at: dist\calibre-mcp.mcpb
```

#### **Install in Claude Desktop** (Drag-and-Drop Only)

** Important:** MCPB packages **must be installed via drag-and-drop** in Claude Desktop. There is no command-line installation method.

1. **Open Claude Desktop Settings:**
   - Click the ** Settings** icon in Claude Desktop
   - Navigate to the **MCP Servers** or **Extensions** section

2. **Drag and Drop the Package:**
   - Locate the `calibre-mcp.mcpb` file on your computer
   - **Drag the file** into the Claude Desktop settings page
   - Drop it in the designated area (usually shows "Drop MCPB package here" or similar)

3. **Wait for Installation:**
   - Claude Desktop will automatically:
     - Extract the package
     - Install dependencies
     - Register the server
   - You'll see a success message when complete

4. **Configure:**
   - After installation, Claude Desktop will prompt you to configure:
     - **Calibre Library Path** (required) - Path to your Calibre library directory
     - **Calibre Server URL** (optional) - URL if using Calibre Content Server
     - **Timeout** (optional) - Operation timeout in seconds

5. **Verify Installation:**
   - The server should appear in your MCP servers list
   - You should see "20 tools, 20 prompts" in the Claude Desktop interface
   - Test by asking Claude to list your libraries or books

** Benefits:**
- No Python environment setup required
- Automatic dependency management
- One-click (drag-and-drop) installation
- Works across all platforms (Windows, macOS, Linux)
- All dependencies bundled in the package

** Limitations:**
- **Only works with Claude Desktop** (not other MCP clients)
- **Must use drag-and-drop** (no CLI installation)
- Requires Claude Desktop to be running during installation

---

### **3. Standard MCP Configuration** (Manual Setup)

**For Claude Desktop and other MCP clients**, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "calibre-mcp": {
      "command": "python",
      "args": ["src/calibre_mcp/server.py"],
      "cwd": "/path/to/calibre-mcp",
      "env": {
        "PYTHONPATH": "src",
        "CALIBRE_SERVER_URL": "http://localhost:8080",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**For other MCP clients**, configure according to your client's MCP server setup requirements.

** Benefits:**
- No repository cloning required
- Simple pip install
- Automatic dependency management
- Works with any MCP client

---

### **3. Python Development Install** (Legacy/Development)

** Note: This method requires cloning the repository and setting up a Python environment.**

##  Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

###  Quick Start
Run immediately via `uvx`:
```bash
uvx calibre-mcp
```

###  Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "calibre-mcp": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/calibre-mcp", "run", "calibre-mcp"]
  }
}
```
#### **Test Connection**

```bash
python -c "
from calibre_mcp.calibre_api import quick_library_test
import asyncio
print(' Working' if asyncio.run(quick_library_test()) else ' Failed')
"
```

#### **Verify Server Will Load in Claude** 

Before committing or restarting Claude, verify the server will load:

```bash
# Quick check (fast, recommended)
python scripts/quick_check.py

# Comprehensive check (includes linting)
python scripts/pre_commit_check.py

# Check recent logs for errors
python scripts/check_logs.py --errors-only
```

**Standardized Workflow (After "add tool to do x"):**

1. **Add tool** following all standards
2. **Run ruff iteratively** until zero errors:
   - `uv run ruff check .`  Fix errors  Run again  Repeat until clean
   - `uv run ruff format .` (format after linting passes)
3. **Run pytest**: `uv run python -m pytest -v`
4. **Run restart script**: `.\scripts\restart_claude_and_check_mcp.ps1`

**Quick Check (Claude Already Running):**
```powershell
.\scripts\restart_claude_and_check_mcp.ps1 -NoRestart
```

**Full Restart & Check:**
```powershell
.\scripts\restart_claude_and_check_mcp.ps1
```

**Note:** 
- **SOTA Script** - Generic MCP server debugging script (copied from central docs repo)
- Uses `taskkill` to stop Claude (no UAC needed)
- Auto-detects server name, log file location, Claude path
- Checks only the **LAST** startup attempt (ignores older failures)
- See [MCP Development Workflow](docs/MCP_DEVELOPMENT_WORKFLOW.md) for complete process

## Features

### Core Features
- **Advanced Search** - Powerful filtering and search capabilities:
  - Text search across titles, authors, series, tags, and comments
  - Filter by publication date and date added
  - File size and format filtering
  - Empty/non-empty comments
  - Star ratings (exact, minimum, or unrated)
  - Publisher filtering (single or multiple)
- **Full Library Access** - Browse and manage your entire Calibre collection
- **Smart Metadata** - Automatic metadata enhancement and validation
- **Format Conversion** - On-the-fly conversion between formats
- **Reading Progress** - Track reading progress across devices
- **Tag Management** - Smart tagging and categorization
- **Library Statistics** - Detailed insights into your collection
- **Advanced OCR Processing** - Multiple OCR backends with different capabilities:
  - **GOT-OCR2.0 Integration**:  open-source OCR with formatted text preservation
  - **ABBYY FineReader CLI**: Traditional commercial OCR with multi-language support
  - **OCR Modes**: Plain text, formatted text, fine-grained region OCR, HTML rendering
  - **Auto Provider Selection**: Automatically chooses  available OCR backend

### AI-Powered Tools
- **Local LLM Auto-Discovery** - Automatically detects and connects to running Ollama/LM Studio instances (no config needed)
- **Book Recommendations** - Get personalized book suggestions based on content similarity
- **Content Analysis** - Extract entities, themes, and sentiment from book content
- **Reading Insights** - Analyze your reading habits and preferences
- **Metadata Enhancement** - AI-assisted metadata correction and enrichment

### Advanced Series Management
- **Series Analysis** - Identify and fix issues in book series
- **Metadata Validation** - Ensure consistency across your library
- **Series Merging** - Combine duplicate or related series
- **Automatic Organization** - Keep your series properly ordered and managed

##  AI Hardware Requirements

While basic operations run on any hardware, AI-powered features (Ollama integration, local embeddings) have specific requirements:

- **Minimal (No AI)**: Any CPU, 4GB RAM. Works for search, metadata, and webapp browsing.
- **Recommended (Local LLM 8B)**: NVIDIA RTX 3060 (12GB VRAM) or Mac M1/M2/M3 (16GB+). Capable of chat and basic analysis.
- **High Performance (Local LLM 70B)**: NVIDIA RTX 3090/4090 (24GB VRAM) or Mac Studio. Required for deep content analysis and complex reasoning.

> [!IMPORTANT]
> **Local LLM Usage**: AI features are **OPTIONAL**. You can run CalibreMCP without any GPU. If enabling local AI (Ollama), ensure your hardware meets the model's requirements. CPU inference is available but significantly slower.

##  Natural Language Search & Auto-Open

CalibreMCP supports **conversational book access** with intelligent parsing and automatic viewer launching.

### **Natural Language Search**

The MCP client LLM automatically parses natural language queries into structured searches:

**User Input  MCP Tool Call:**
- "search books by harari"  `query_books(operation="search", author="harari")`
- "books about china"  `query_books(operation="search", tag="china")`
- "books from last year"  `query_books(operation="search", added_after="2024-01-01")`
- "find sapiens"  `query_books(operation="search", title="sapiens")`

**FastMCP 2.14.4 Sampling (SEP-1577):**
For ambiguous queries, the server uses `ctx.sample()` with tools to orchestrate agentic workflows. Supports dialogic returns (execution_time_ms, recommendations) for SOTA MCP compliance.

### **Auto-Open Books**

When searches return exactly 1 result, books automatically launch in your system's default viewer:

```python
# Auto-open enabled
result = query_books(operation="search", title="homo deus", auto_open=True)

# Returns:
{
  "total": 1,
  "auto_opened": true,
  "opened_book": {
    "title": "Homo Deus: A Brief History of Tomorrow",
    "format": "EPUB"
  }
}
```

**Supported Formats:** EPUB, PDF, MOBI, AZW3, CBZ, CBR, TXT, HTML, RTF

### **Book Access Commands**

**Natural Phrasings:**
- "I want to read 'Homo Deus'"  Search & auto-open
- "Show me 'The Burning Court'"  Search & auto-open
- "Open 'Sapiens' for reading"  Search & auto-open

**All map to:** Title search with auto-open enabled

## Usage Examples

### Natural Language & Auto-Open Examples

**Conversational Book Access:** The MCP client parses natural language and auto-opens books:

```python
# User says: "I want to read 'Homo Deus'"  Auto-search and open
results = await query_books(
    operation="search",
    title="homo deus",
    auto_open=True,           # Auto-launch viewer if unique result
    auto_open_format="EPUB"   # Preferred format
)
# Result: Book opens in system viewer, returns metadata

# User says: "books about china"  Tag search
results = await query_books(
    operation="search",
    tag="china"
)

# User says: "find sapiens"  Title search with sampling
results = await query_books(
    operation="search",
    title="sapiens"  # Fast title-only search (bypasses FTS)
)
```

### Search Examples

**Using Portmanteau Tools:** All user queries (search, list, find, query, get) map to `query_books`:

```python
# User says: "list books by conan doyle"  query_books with operation="search"
results = await query_books(
    operation="search",
    author="Conan Doyle",
    format_table=True
)

# Search by title, author, or series
results = await query_books(
    operation="search",
    text="python programming"
)

# Filter by date ranges
from datetime import datetime, timedelta
last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
today = datetime.now().strftime("%Y-%m-%d")
results = await query_books(
    operation="search",
    pubdate_start="2020-01-01",
    added_after=last_month,
    added_before=today
)

# Filter by file size and format
results = await query_books(
    operation="search",
    min_size=1048576,    # 1MB
    max_size=10485760,   # 10MB
    formats=["EPUB", "PDF"]
)

# Find books with empty comments or no publisher
results = await query_books(
    operation="search",
    has_empty_comments=True,
    has_publisher=False
)

# Find highly rated books
results = await query_books(operation="search", min_rating=4)

# Find unrated books
results = await query_books(operation="search", unrated=True)

# Find books by publisher
results = await query_books(operation="search", publisher="O'Reilly Media")

# Combined search with multiple filters
results = await query_books(
    operation="search",
    text="machine learning",
    min_rating=4,
    pubdate_start="2020-01-01",
    formats=["EPUB"],
    limit=20,
    offset=0
)

# List all books (simple operation, no filters)
results = await query_books(operation="list", limit=50)
```

### OCR Processing Examples

```python
# Auto-select  OCR provider (GOT-OCR2.0 preferred, FineReader fallback)
result = await process_ocr(source="/path/to/scanned_book.pdf")

# Use GOT-OCR2.0 for formatted text preservation
result = await process_ocr(
    source="/path/to/book_page.png",
    provider="got-ocr",
    ocr_mode="format",
    render_html=True
)

# Traditional FineReader OCR for searchable PDFs
result = await process_ocr(
    source="/path/to/scanned_document.pdf",
    provider="finereader",
    language="english",
    output_format="pdf"
)

# Fine-grained OCR on specific region
result = await process_ocr(
    source="/path/to/document.png",
    provider="got-ocr",
    ocr_mode="fine-grained",
    region=[100, 200, 400, 500]  # [x1, y1, x2, y2]
)
```

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

##  Configuration

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

##  Troubleshooting

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

##  Architecture

```
calibremcp/
 src/calibre_mcp/
    server.py           # 4 FastMCP tools
    calibre_api.py      # HTTP API client
    config.py           # Configuration management
 config/
    settings.yaml       # Server configuration
    calibre_config.yaml # Calibre-specific settings
 tests/
    test_api.py         # Unit tests
    integration_tests.py # Integration tests
 docs/                   # Complete documentation
```

##  Success Metrics

### **Phase 1 Complete** 

-  4/4 core MCP tools implemented and tested
-  FastMCP 2.0 compliance with proper structure  
-  Comprehensive error handling and diagnostics
-  Austrian efficiency: 45-minute realistic timeline
-  Production-ready for immediate use with Claude Desktop and other MCP clients

##  License

MIT License - Austrian efficiency in e-book management.

---

**Built with Austrian efficiency for Sandra's comprehensive e-book workflow.**

*"Sin temor y sin esperanza" - practical without hype or doom.*
