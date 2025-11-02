# FastMCP 2.13.0 "Cache Me If You Can" - Persistence Research

**Release Date**: October 25, 2025  
**Latest Version**: 2.13.0.2 (October 28, 2025)  
**Research Date**: 2025-01-XX

## Summary

FastMCP 2.13.0 introduces **pluggable storage backends** for persistent state management, built on `py-key-value-aio`. This enables:
- Persistent state across server restarts
- Encrypted disk storage by default
- OAuth token persistence
- Application state storage
- Long-running sessions

## Key Features

### 1. Storage Backends (`py-key-value-aio`)

**Library**: `py-key-value-aio` (by @strawgate, FastMCP maintainer)

**Features**:
- Simple key-value interface
- Built-in encryption for disk storage
- Platform-aware token management
- Support for multiple backends:
  - **Filesystem** (encrypted disk storage by default)
  - **Redis**
  - **DynamoDB**
  - **Elasticsearch**
  - **In-memory**
  - And more!

**Capabilities**:
- TTL (Time-To-Live) support
- Caching layers
- Encryption wrappers
- Async/await support

### 2. OAuth Token Persistence

- OAuth tokens automatically persist across server restarts
- Platform-aware storage (uses system keychain where appropriate)
- No need for external databases for token management

### 3. Application State Storage

- Store arbitrary state without external databases
- Enable stateful MCP applications
- Long-running sessions with cached credentials

### 4. Response Caching Middleware

- Cache tool and resource responses
- Configurable TTLs
- Reduces redundant API calls
- Speeds up repeated queries

### 5. Server Lifespans

- Proper initialization and cleanup hooks
- Run once per server instance (not per client session)
- Better resource management for:
  - Database connections
  - Background tasks
  - Server-level state

**⚠️ Breaking Change**: If using the `lifespan` parameter, behavior changed from per-session to per-server-instance.

## Integration Plan for CalibreMCP

### Current State
- Uses custom `StorageBackend` abstraction
- Local storage via SQLite (`metadata.db`)
- Remote storage via Calibre Content Server API
- No persistent state across restarts

### Migration Path

1. **Update FastMCP dependency**
   ```toml
   dependencies = [
       "fastmcp>=2.13.0",
       # ... other deps
   ]
   ```

2. **Add storage backend**
   - Use FastMCP's built-in storage
   - Can layer on top of existing SQLite database
   - Use for:
     - OAuth tokens (if we add OAuth)
     - Session state
     - Cache metadata
     - User preferences

3. **Response Caching**
   - Add caching middleware for expensive operations:
     - Book search queries
     - Metadata enrichment
     - Library statistics
     - Tag analysis

4. **Server Lifespans**
   - Move database connection initialization to lifespan
   - Proper cleanup on shutdown

## Resources

- **Release Notes**: https://github.com/jlowin/fastmcp/releases/tag/v2.13.0
- **PyPI**: https://pypi.org/project/fastmcp/ (2.13.0.2)
- **Documentation**: https://gofastmcp.com
- **Storage Library**: `py-key-value-aio` (by @strawgate)

## Next Steps

1. ✅ Research complete
2. ⏳ Update `pyproject.toml` to require FastMCP 2.13.0+
3. ⏳ Implement storage backend for CalibreMCP
4. ⏳ Add response caching middleware
5. ⏳ Migrate to server lifespans
6. ⏳ Test persistence across restarts
7. ⏳ Update documentation

