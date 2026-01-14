# Calibre Webapp Backend

FastAPI HTTP wrapper for CalibreMCP server.

## Setup

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Install calibre_mcp in editable mode so backend can import it
pip install -e ../../
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 13000
```

## Startup Behavior

On startup, the backend automatically:

1. **Discovers Calibre libraries** - Scans for available Calibre libraries
2. **Caches libraries list** - Stores libraries in memory for fast dropdown population via `/api/libraries/list`
3. **Initializes database** - Switches to the current library (or first available) to initialize the Calibre database
4. **Ready for operations** - Database is initialized and ready for searches and book reading

The libraries cache is automatically updated when libraries are switched via `/api/libraries/switch`.

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:13000/docs
- ReDoc: http://localhost:13000/redoc

## Key Endpoints

### Fast Libraries List (for dropdowns)
- `GET /api/libraries/list` - Returns cached libraries list (fast, populated at startup)

### Full Library Operations
- `GET /api/libraries` - List all libraries (calls MCP tool, may be slower)
- `GET /api/libraries/stats` - Get library statistics
- `POST /api/libraries/switch` - Switch active library

## Environment Variables

Create a `.env` file:

```env
CORS_ORIGINS=http://localhost:13001
```

## Architecture

- **Dual Interface**: FastMCP HTTP endpoints mounted at `/mcp` (stdio for MCP clients, HTTP for webapp)
- **Direct Import Fallback**: If FastMCP HTTP mount fails, falls back to direct Python imports
- **Libraries Cache**: In-memory cache for fast library dropdown population
- **Startup Initialization**: Automatically discovers and loads libraries on server start
