# Calibre Webapp

Modern web application frontend for CalibreMCP server.

## Architecture

- **Backend**: FastAPI HTTP wrapper around MCP server
- **Frontend**: Next.js 15 with React Server Components
- **Dual Interface**: FastMCP HTTP endpoints for webapp, stdio for MCP clients

## Features

- **Automatic Library Discovery**: Backend automatically discovers and loads Calibre libraries on startup
- **Fast Libraries List**: Cached endpoint `/api/libraries/list` for instant dropdown population
- **Full MCP Client**: Complete implementation of all 17 MCP tools as REST endpoints
- **Database Initialization**: Automatic database initialization on startup for immediate searches

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Install calibre_mcp in editable mode
pip install -e ../../

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 13000
```

Backend runs on http://localhost:13000

**On startup**, the backend will:
1. Discover available Calibre libraries
2. Cache libraries list for fast dropdown access
3. Initialize database with current/first library
4. Be ready for searches and book operations

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:13001

## Documentation

- [Backend README](backend/README.md) - Backend setup and API details
- [API Endpoints](backend/ENDPOINTS.md) - Complete API reference
- [Setup Guide](SETUP.md) - Detailed setup instructions
