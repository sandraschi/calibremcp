# CalibreMCP Troubleshooting Guide

**Comprehensive troubleshooting for common issues and Austrian efficiency problem-solving**

---

## 🚨 Quick Diagnosis

### **Is CalibreMCP Working?**

Run this 30-second diagnostic:

```bash
# 1. Test MCP server startup
python -m calibre_mcp.server &
# Should show: "🚀 Starting CalibreMCP - FastMCP 2.0 Server"

# 2. Test Calibre connection
python -c "
from calibre_mcp.calibre_api import quick_library_test
import asyncio
result = asyncio.run(quick_library_test())
print('✅ Working' if result else '❌ Failed')
"

# 3. Test configuration
python -c "
from calibre_mcp.config import CalibreConfig
config = CalibreConfig.load_config()
print(f'Server: {config.server_url}')
print(f'Auth: {config.has_auth}')
"
```

**Expected Output:**

- Server starts without errors
- Connection test returns `✅ Working`
- Configuration shows correct server URL

---

## 🔧 Connection Issues

### **Problem: "Connection failed: [Errno 10061] No connection could be made"**

**Diagnosis:**
Calibre Content Server is not running or not accessible.

**Solutions:**

#### **Step 1: Check if Calibre Server is Running**

```bash
# Windows
netstat -an | findstr 8080

# Linux/macOS  
netstat -an | grep 8080
lsof -i :8080
```

If no output, Calibre server is not running.

#### **Step 2: Start Calibre Content Server**

**Option A: Through Calibre GUI**

1. Open Calibre application
2. Click "Connect/share" → "Start Content Server"
3. Verify port is set to 8080
4. Click "Start server"

**Option B: Command Line**

```bash
# Basic server
calibre-server --port=8080

# With authentication
calibre-server --port=8080 --enable-auth --manage-users

# Custom library path
calibre-server --port=8080 --library-path="C:\Users\Sandra\Calibre Library"
```

#### **Step 3: Test Connection**

```bash
# Test with browser
# Navigate to: http://localhost:8080

# Test with curl
curl http://localhost:8080/ajax/interface-data/init
```

#### **Step 4: Check Firewall**

```bash
# Windows: Allow port 8080 through Windows Defender
# Add inbound rule for port 8080

# Linux: Check iptables
sudo iptables -L | grep 8080

# Add rule if needed
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### **Problem: "Calibre server not found - check server URL"**

**Diagnosis:**
Incorrect server URL or port number.

**Solutions:**

#### **Check Configuration**

```python
from calibre_mcp.config import CalibreConfig
config = CalibreConfig.load_config()
print(f"Configured URL: {config.server_url}")
```

#### **Common URL Issues**

- **Wrong port**: `http://localhost:8080` not `http://localhost:80`
- **Missing protocol**: `http://localhost:8080` not `localhost:8080`  
- **HTTPS vs HTTP**: Check if server uses SSL
- **IP vs hostname**: Try `127.0.0.1:8080` instead of `localhost:8080`

#### **Test Different URLs**

```bash
# Try variations
curl http://localhost:8080/ajax/interface-data/init
curl http://127.0.0.1:8080/ajax/interface-data/init
curl http://[your-ip]:8080/ajax/interface-data/init
```

#### **Check Calibre Server Settings**

```bash
# Get Calibre server info
calibre-server --help

# Check current server status
calibre-server --list-libraries
```

---

## 🔐 Authentication Issues

### **Problem: "Authentication failed - check username/password"**

**Diagnosis:**
Incorrect credentials or authentication not properly configured.

**Solutions:**

#### **Step 1: Verify Credentials**

```bash
# Test authentication with curl
curl -u username:password http://localhost:8080/ajax/interface-data/init

# Example
curl -u sandra:mypassword http://localhost:8080/ajax/interface-data/init
```

#### **Step 2: Check Environment Variables**

```bash
# Windows
echo %CALIBRE_USERNAME%
echo %CALIBRE_PASSWORD%

# Linux/macOS
echo $CALIBRE_USERNAME
echo $CALIBRE_PASSWORD
```

#### **Step 3: Reset Calibre User**

```bash
# Manage Calibre users
calibre-server --manage-users

# Commands in user management:
# add username password
# remove username
# list
# change-password username
```

#### **Step 4: Test Without Authentication**

```bash
# Temporarily disable auth to test connection
calibre-server --port=8080
# (Remove --enable-auth flag)

# Test CalibreMCP without credentials
export CALIBRE_USERNAME=""
export CALIBRE_PASSWORD=""
python -c "from calibre_mcp.calibre_api import quick_library_test; import asyncio; print(asyncio.run(quick_library_test()))"
```

### **Problem: Authentication works in browser but fails in CalibreMCP**

**Diagnosis:**
Special characters in password or encoding issues.

**Solutions:**

#### **Check Password Characters**

```bash
# Avoid special characters that need URL encoding
# Problematic: @, #, %, &, +, =, ?, /
# Safe: letters, numbers, -, _, .
```

#### **URL Encode Password**

```python
import urllib.parse
password = "my@password#123"
encoded = urllib.parse.quote(password)
print(f"Encoded password: {encoded}")
```

#### **Test with Simple Password**

```bash
# Create test user with simple password
calibre-server --manage-users
# add testuser simplepass123

# Test with simple credentials
export CALIBRE_USERNAME="testuser"
export CALIBRE_PASSWORD="simplepass123"
```

---

## ⚡ Performance Issues

### **Problem: "Request timeout after 30s"**

**Diagnosis:**
Calibre server is slow or overloaded.

**Solutions:**

#### **Step 1: Increase Timeout**

```env
# .env file
CALIBRE_TIMEOUT=60
CALIBRE_MAX_RETRIES=5
```

#### **Step 2: Check Server Load**

```bash
# Check Calibre server CPU/memory usage
# Windows
tasklist | findstr calibre

# Linux/macOS
ps aux | grep calibre
top -p $(pgrep calibre)
```

#### **Step 3: Optimize Library**

```bash
# Check library size
calibre-debug --paths
# Look for library path and check folder size

# Optimize Calibre database
calibre-debug --run-plugin="Optimize Database"
```

#### **Step 4: Reduce Query Complexity**

```python
# Use smaller limits
await list_books(limit=25)  # instead of 100+

# Use specific searches  
await search_books("python", ["title"])  # instead of all fields
```

### **Problem: "Slow search responses (>5 seconds)"**

**Solutions:**

#### **Optimize Search Settings**

```yaml
# config/settings.yaml
calibre:
  default_limit: 25
  search_timeout: 15

performance:
  max_concurrent_requests: 3
  enable_search_indexing: true
```

#### **Use Field-Specific Searches**

```python
# Faster: search specific fields
await search_books("programming", ["tags"])

# Slower: search all fields
await search_books("programming")  # searches title, authors, tags, comments
```

#### **Check Library Size Impact**

```bash
# Count books in library
calibre-debug --command "list" | wc -l

# For libraries with 1000+ books:
# - Use more specific queries
# - Reduce default limits
# - Enable search indexing
```

---

## 📚 Library Issues

### **Problem: "No books found" but library has books**

**Diagnosis:**
Library path issues or permissions problems.

**Solutions:**

#### **Step 1: Verify Library Path**

```bash
# Check current library
calibre-debug --get-library

# List libraries
calibre-server --list-libraries

# Set specific library
calibre-server --library-path="C:\Users\Sandra\Calibre Library"
```

#### **Step 2: Check Library Permissions**

```bash
# Windows: Check folder permissions
icacls "C:\Users\Sandra\Calibre Library"

# Linux/macOS: Check permissions
ls -la "/Users/sandra/Calibre Library"
```

#### **Step 3: Test Library Directly**

```bash
# List books via command line
calibredb list --library-path="C:\Users\Sandra\Calibre Library"

# Get library info
calibredb library_info --library-path="C:\Users\Sandra\Calibre Library"
```

#### **Step 4: Create Test Library**

```bash
# Create new test library
calibredb create_library test_library

# Add test book
calibredb add book.epub --library-path=test_library

# Test CalibreMCP with test library
calibre-server --library-path=test_library --port=8080
```

### **Problem: "Books have missing metadata"**

**Solutions:**

#### **Check Book Import Status**

```bash
# Re-scan library for metadata
calibredb list --for-machine | head -5  # Check first 5 books

# Look for missing fields:
# - title: "Unknown"
# - authors: []
# - formats: {}
```

#### **Fix Missing Metadata**

```bash
# Add metadata to specific book
calibredb set_metadata 123 --title="Correct Title" --authors="Author Name"

# Auto-detect metadata
calibredb ebooks_meta book.epub  # Check file metadata
```

---

## 🔍 Search Issues

### **Problem: "Search returns no results for known books"**

**Diagnosis:**
Search syntax issues or index problems.

**Solutions:**

#### **Step 1: Test Basic Search**

```python
# Test with exact title
await list_books("exact book title")

# Test with single word
await list_books("python")

# Test without query (browse all)
await list_books()
```

#### **Step 2: Check Search Syntax**

```python
# Correct syntax
await search_books("programming", ["title", "tags"], "OR")

# Common mistakes:
# - Wrong field names: "author" vs "authors"
# - Invalid operators: "or" vs "OR"
# - Empty field list: []
```

#### **Step 3: Debug Search Query**

```python
# Enable debug logging
import logging
logging.getLogger("calibre_mcp").setLevel(logging.DEBUG)

# Check what query is sent to Calibre
await search_books("test query")
# Look for log: "Calibre search query: ..."
```

#### **Step 4: Test Direct Calibre Search**

```bash
# Test search via calibredb
calibredb search "python" --library-path="your-library-path"

# Test search in Calibre GUI
# Open Calibre → Search box → Enter query
```

### **Problem: "Search returns wrong results"**

**Solutions:**

#### **Understanding Calibre Search Logic**

```python
# OR search: title:python OR tags:python
await search_books("python", ["title", "tags"], "OR")

# AND search: title:python AND tags:python  
await search_books("python", ["title", "tags"], "AND")

# Single field: only in title
await search_books("python", ["title"])
```

#### **Use Exact Matching**

```python
# Exact phrase search
await search_books('"Python Programming"', ["title"])

# Partial word search
await search_books("prog", ["title"])  # matches "Programming"
```

---

## 🖥️ Claude Desktop Integration Issues

### **Problem: "CalibreMCP tools not appearing in Claude Desktop"**

**Solutions:**

#### **Step 1: Check MCP Configuration**

```json
// claude_desktop_config.json
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

#### **Step 2: Verify File Paths**

```bash
# Check if module is importable
python -c "import calibre_mcp.server; print('✅ Module found')"

# Check if server script exists
python -m calibre_mcp.server
# Should start without errors
```

#### **Step 3: Test MCP Inspector**

```bash
# Start MCP Inspector
python -m calibre_mcp.server
# Navigate to: http://127.0.0.1:6274
# Should show 4 tools: list_books, get_book_details, search_books, test_calibre_connection
```

#### **Step 4: Check Claude Desktop Logs**

```bash
# Windows: Check Event Viewer or Claude logs
# macOS: Check Console.app for Claude messages
# Look for: MCP server startup errors, tool registration failures
```

### **Problem: "Tools appear but return errors in Claude Desktop"**

**Solutions:**

#### **Check Environment Variables in Claude Desktop**

```json
// Ensure env vars are passed to Claude Desktop
{
  "mcpServers": {
    "calibre-mcp": {
      "command": "python",
      "args": ["-m", "calibre_mcp.server"],
      "env": {
        "CALIBRE_SERVER_URL": "http://localhost:8080",
        "CALIBRE_USERNAME": "sandra",
        "CALIBRE_PASSWORD": "your_password",
        "CALIBRE_TIMEOUT": "60"
      }
    }
  }
}
```

#### **Test Tools Individually**

```python
# Test each tool manually
from calibre_mcp.server import list_books, get_book_details, search_books, test_calibre_connection
import asyncio

async def test_tools():
    # Test connection first
    conn = await test_calibre_connection()
    print(f"Connection: {conn.connected}")
    
    if conn.connected:
        # Test each tool
        books = await list_books(limit=5)
        print(f"Books found: {len(books.results)}")
        
        if books.results:
            details = await get_book_details(books.results[0].book_id)
            print(f"Book details: {details.title}")

asyncio.run(test_tools())
```

---

## 🐛 Advanced Debugging

### **Enable Debug Logging**

```env
# .env file
CALIBRE_DEBUG=1
LOG_LEVEL=DEBUG
```

```python
# In code
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("calibre_mcp")
logger.setLevel(logging.DEBUG)
```

### **Network Debugging**

```bash
# Monitor network traffic
# Windows: Use Wireshark or Fiddler
# Linux: Use tcpdump
sudo tcpdump -i any port 8080

# Monitor HTTP requests
curl -v http://localhost:8080/ajax/interface-data/init
```

### **Database Debugging**

```bash
# Check Calibre database directly
sqlite3 "Calibre Library/metadata.db"
.tables
.schema books
SELECT title, author_sort FROM books LIMIT 5;
.quit
```

### **Performance Profiling**

```python
import time
import asyncio
from calibre_mcp.server import list_books

async def profile_search():
    start = time.time()
    result = await list_books("programming", limit=50)
    end = time.time()
    
    print(f"Search took: {(end-start)*1000:.0f}ms")
    print(f"Results: {len(result.results)}")
    print(f"Server reported: {result.search_time_ms}ms")

asyncio.run(profile_search())
```

---

## 📋 Diagnostic Checklist

When reporting issues, include this diagnostic information:

### **System Information**

- [ ] Operating System (Windows 10/11, macOS, Linux)
- [ ] Python version (`python --version`)
- [ ] Calibre version (`calibre --version`)
- [ ] CalibreMCP version

### **Configuration**

- [ ] Server URL and port
- [ ] Authentication enabled (yes/no)
- [ ] Library path and size (number of books)
- [ ] Environment variables used

### **Error Details**

- [ ] Exact error message
- [ ] When error occurs (startup, search, specific tool)
- [ ] Debug logs (with `CALIBRE_DEBUG=1`)
- [ ] Network connectivity test results

### **Reproduction Steps**

- [ ] Minimal steps to reproduce the issue
- [ ] Expected behavior vs actual behavior
- [ ] Workarounds attempted

---

## 🆘 Getting Help

### **Self-Service Debugging**

1. Run the Quick Diagnosis (top of this guide)
2. Check relevant sections above
3. Enable debug logging
4. Test with minimal configuration

### **Austrian Efficiency Problem-Solving**

- **Speed over perfection**: Start with simple tests
- **Direct communication**: Provide exact error messages  
- **Practical solutions**: Test one change at a time
- **Budget conscious**: Use built-in diagnostic tools

### **Common Solutions Summary**

- **Connection issues**: Check if Calibre server is running
- **Authentication issues**: Verify username/password
- **Performance issues**: Increase timeouts, reduce limits
- **Search issues**: Test with basic queries first
- **Claude Desktop issues**: Check MCP configuration

---

*Austrian efficiency in troubleshooting: systematic, practical, and results-focused.*
