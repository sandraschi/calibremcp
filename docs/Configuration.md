# CalibreMCP Configuration Guide

**Complete guide to configuring CalibreMCP for optimal performance**

---

## 🎯 Configuration Overview

CalibreMCP uses a hierarchical configuration system with three priority levels:

1. **Environment Variables** (highest priority)
2. **YAML Configuration Files** (medium priority)  
3. **Default Values** (lowest priority)

This allows flexible deployment while maintaining sane defaults.

---

## 📁 Configuration Files

### **`config/settings.yaml`**
Main server configuration with performance tuning and feature flags.

```yaml
server:
  name: "CalibreMCP 📚"
  version: "1.0.0"
  description: "FastMCP 2.0 server for Calibre e-book management"

calibre:
  server_url: "http://localhost:8080"
  timeout: 30
  max_retries: 3
  default_limit: 50
  max_limit: 200

features:
  enable_search: true
  enable_metadata_retrieval: true
  enable_cover_images: true
  enable_downloads: true

performance:
  search_timeout: 15
  max_concurrent_requests: 5
  enable_search_indexing: false

logging:
  level: "INFO"
  log_file: "calibremcp.log"
  console_output: true

austrian_efficiency:
  prefer_speed: true
  weeb_friendly: true
  academic_quality: true
  budget_conscious: true
```

### **`config/calibre_config.yaml`**  
Calibre-specific settings with presets and library management.

```yaml
presets:
  local_development:
    server_url: "http://localhost:8080"
    timeout: 30
    
  remote_server:
    server_url: "http://192.168.1.100:8080"
    timeout: 45

libraries:
  personal:
    name: "Personal Library"
    default_tags: ["personal", "to-read"]
    
  academic:
    name: "Academic Library"
    default_tags: ["academic", "research"]

formats:
  preferred_reading: ["EPUB", "PDF", "MOBI"]
  download_priority:
    1: "EPUB"
    2: "PDF"
    3: "MOBI"
```

---

## 🌍 Environment Variables

### **Core Connection Settings**

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CALIBRE_SERVER_URL` | Calibre server URL | `http://localhost:8080` | `https://calibre.example.com` |
| `CALIBRE_USERNAME` | Username for authentication | None | `sandra` |
| `CALIBRE_PASSWORD` | Password for authentication | None | `secure_password_123` |
| `CALIBRE_TIMEOUT` | Request timeout (seconds) | `30` | `60` |
| `CALIBRE_MAX_RETRIES` | Maximum request retries | `3` | `5` |

### **Performance Settings**

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CALIBRE_DEFAULT_LIMIT` | Default search results | `50` | `25` |
| `CALIBRE_MAX_LIMIT` | Maximum search results | `200` | `100` |
| `CALIBRE_LIBRARY_NAME` | Primary library name | `Default Library` | `Sandra's Library` |

### **Debug Settings**

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CALIBRE_DEBUG` | Enable debug logging | `0` | `1` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |

---

## 🔧 Setup Scenarios

### **Scenario 1: Local Development**

**Calibre Setup:**
```bash
# Start Calibre Content Server
calibre-server --port=8080 --enable-local-write
```

**Environment Configuration:**
```env
# .env file
CALIBRE_SERVER_URL=http://localhost:8080
CALIBRE_TIMEOUT=30
CALIBRE_DEFAULT_LIMIT=25
CALIBRE_DEBUG=1
```

**Testing:**
```bash
# Test connection
python -c "
from calibre_mcp.calibre_api import quick_library_test
import asyncio
print(asyncio.run(quick_library_test('http://localhost:8080')))
"
```

### **Scenario 2: Local Production**

**Calibre Setup:**
```bash
# Start with authentication
calibre-server --port=8080 --enable-auth --manage-users
# Create user: sandra / password
```

**Environment Configuration:**
```env
CALIBRE_SERVER_URL=http://localhost:8080
CALIBRE_USERNAME=sandra
CALIBRE_PASSWORD=your_secure_password
CALIBRE_TIMEOUT=60
CALIBRE_MAX_RETRIES=5
CALIBRE_DEFAULT_LIMIT=50
```

**Claude Desktop Integration:**
```json
{
  "mcpServers": {
    "calibre-mcp": {
      "command": "python",
      "args": ["-m", "calibre_mcp.server"],
      "env": {
        "CALIBRE_SERVER_URL": "http://localhost:8080",
        "CALIBRE_USERNAME": "sandra",
        "CALIBRE_PASSWORD": "your_secure_password"
      }
    }
  }
}
```

### **Scenario 3: Remote Server**

**Calibre Setup:**
```bash
# On remote server (192.168.1.100)
calibre-server --port=8080 --listen-on=0.0.0.0 --enable-auth
```

**Environment Configuration:**
```env
CALIBRE_SERVER_URL=http://192.168.1.100:8080
CALIBRE_USERNAME=sandra
CALIBRE_PASSWORD=your_secure_password
CALIBRE_TIMEOUT=45
CALIBRE_MAX_RETRIES=3
```

**Network Testing:**
```bash
# Test network connectivity
curl http://192.168.1.100:8080/ajax/interface-data/init
```

### **Scenario 4: Cloud/HTTPS Server**

**Calibre Setup:**
```bash
# Behind reverse proxy with SSL
# nginx/apache handles HTTPS termination
calibre-server --port=8080 --enable-auth
```

**Environment Configuration:**
```env
CALIBRE_SERVER_URL=https://calibre.yourdomain.com
CALIBRE_USERNAME=sandra
CALIBRE_PASSWORD=your_secure_password
CALIBRE_TIMEOUT=60
CALIBRE_MAX_RETRIES=5
```

---

## ⚙️ Advanced Configuration

### **Custom Configuration File**

Create a custom config file and load it:

```python
# custom_config.json
{
  "server_url": "http://localhost:8080",
  "username": "sandra",
  "timeout": 45,
  "default_limit": 25,
  "library_name": "Custom Library"
}
```

```python
# Load custom configuration
from calibre_mcp.config import CalibreConfig

config = CalibreConfig.load_config("custom_config.json")
```

### **Performance Tuning**

#### **For Large Libraries (1000+ books)**
```yaml
# config/settings.yaml
performance:
  search_timeout: 30
  max_concurrent_requests: 3
  enable_search_indexing: true
  
calibre:
  default_limit: 25  # Smaller results for faster response
  max_limit: 100
  timeout: 60
```

#### **For Fast Networks**
```yaml
performance:
  search_timeout: 10
  max_concurrent_requests: 10
  
calibre:
  timeout: 15
  max_retries: 2
```

#### **For Slow Networks**
```yaml
performance:
  search_timeout: 60
  max_concurrent_requests: 2
  
calibre:
  timeout: 120
  max_retries: 5
```

### **Memory Optimization**

```yaml
performance:
  max_cache_size_mb: 25  # Reduce for low-memory systems
  cleanup_interval_minutes: 15
  
calibre:
  default_limit: 20  # Smaller result sets
```

---

## 🛡️ Security Configuration

### **Authentication Setup**

#### **Enable Calibre Authentication**
```bash
# Interactive user management
calibre-server --manage-users

# Add user: sandra
# Set password: secure_password_123
# Set permissions: read/write
```

#### **Environment Variables (Recommended)**
```env
# Store credentials securely
CALIBRE_USERNAME=sandra
CALIBRE_PASSWORD=secure_password_123
```

#### **Config File (Less Secure)**
```yaml
# config/calibre_config.yaml
auth:
  username: "sandra"
  # password: leave empty, use environment variable
```

### **Network Security**

#### **Local Network Only**
```bash
# Bind to specific interface
calibre-server --listen-on=192.168.1.100 --port=8080
```

#### **HTTPS with Reverse Proxy**
```nginx
# nginx configuration
server {
    listen 443 ssl;
    server_name calibre.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🚨 Troubleshooting Configuration

### **Connection Issues**

#### **"Connection refused"**
```bash
# Check if Calibre server is running
netstat -an | grep 8080
# or
lsof -i :8080

# Test with curl
curl http://localhost:8080/ajax/interface-data/init
```

**Solutions:**
1. Start Calibre Content Server
2. Check port number and URL
3. Verify firewall settings
4. Check if another application is using port 8080

#### **"Authentication failed"**
```bash
# Test authentication with curl
curl -u username:password http://localhost:8080/ajax/interface-data/init
```

**Solutions:**
1. Verify username/password in environment variables
2. Check if authentication is enabled in Calibre
3. Reset user password in Calibre
4. Ensure user has proper permissions

#### **"Request timeout"**
**Solutions:**
1. Increase `CALIBRE_TIMEOUT` value
2. Check network connectivity
3. Verify Calibre server isn't overloaded
4. Increase `max_retries` for unstable connections

### **Performance Issues**

#### **Slow search responses**
```yaml
# Optimize settings
calibre:
  default_limit: 25  # Reduce result count
  timeout: 60        # Increase timeout

performance:
  search_timeout: 30
  max_concurrent_requests: 3
```

#### **High memory usage**
```yaml
performance:
  max_cache_size_mb: 25
  cleanup_interval_minutes: 10

calibre:
  default_limit: 20
```

### **Configuration Validation**

#### **Test Configuration Loading**
```python
# Test config loading
from calibre_mcp.config import CalibreConfig

try:
    config = CalibreConfig.load_config()
    print(f"✅ Config loaded: {config.server_url}")
    print(f"✅ Auth configured: {config.has_auth}")
    print(f"✅ Timeout: {config.timeout}s")
except Exception as e:
    print(f"❌ Config error: {e}")
```

#### **Test API Connection**
```python
# Test API connectivity
from calibre_mcp.calibre_api import quick_library_test
import asyncio

result = asyncio.run(quick_library_test())
if result:
    print("✅ Calibre server accessible")
else:
    print("❌ Calibre server connection failed")
```

---

## 📊 Monitoring and Logging

### **Log Configuration**

```yaml
# config/settings.yaml
logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  log_file: "calibremcp.log"
  max_log_size_mb: 10
  backup_count: 3
  console_output: true
```

### **Log Analysis**

```bash
# Monitor logs in real-time
tail -f calibremcp.log

# Search for errors
grep ERROR calibremcp.log

# Search for performance issues
grep "timeout\|slow\|retry" calibremcp.log
```

### **Performance Metrics**

```python
# Enable performance logging
import logging
logging.getLogger("calibre_mcp").setLevel(logging.DEBUG)

# Metrics to monitor:
# - Search response times
# - Connection success rates
# - Cache hit rates
# - Error frequencies
```

---

## 🎛️ Configuration Best Practices

### **Austrian Efficiency Guidelines**

1. **Speed over perfection**: Use smaller result limits for faster responses
2. **Budget conscious**: Enable caching and optimize concurrent requests
3. **Practical configuration**: Use environment variables for sensitive data
4. **Clear error messages**: Enable debug logging during setup

### **Deployment Checklist**

- [ ] Calibre Content Server running and accessible
- [ ] Authentication configured (if needed)
- [ ] Environment variables set correctly
- [ ] Configuration files in place
- [ ] Network connectivity tested
- [ ] Firewall rules configured
- [ ] SSL/TLS configured (for production)
- [ ] Logging enabled and monitored
- [ ] Performance settings optimized for library size
- [ ] Backup configuration documented

### **Maintenance Schedule**

- **Daily**: Monitor logs for errors
- **Weekly**: Check performance metrics
- **Monthly**: Review and optimize configuration
- **Quarterly**: Update Calibre server and security settings

---

*Austrian efficiency in configuration: practical, secure, and performance-optimized.*
