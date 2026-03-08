# Webapp Setup Guide

Quick setup instructions for the Calibre webapp.

## Docker (Recommended)

```powershell
cd webapp

# Set your Calibre library path
$env:CALIBRE_LIBRARY_PATH = "L:/path/to/your/calibre/library"

# Or create .env from example
Copy-Item .env.docker.example .env
# Edit .env and set CALIBRE_LIBRARY_PATH

docker compose up -d
```

- Backend: http://localhost:10720
- Frontend: http://localhost:10722
- API docs: http://localhost:10720/docs

User data (comments, extended metadata) is persisted in a Docker volume.

## Local Run (No Docker)

If Docker cannot reach the registry, run the webapp locally:

**First-time setup** (run from Windows Explorer or native cmd - Cursor sandbox blocks pip/npm):
```batch
cd webapp
setup-local.bat
```

**Then start:**
```powershell
.\start.ps1
```
Or `.\start.bat` from webapp. Requires: `.env` with `CALIBRE_LIBRARY_PATH` set.

## Manual Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- CalibreMCP server installed and working

### Backend Setup

```powershell
cd webapp\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Copy environment file
Copy-Item .env.example .env

# Run the server (or use start.ps1 to start both backend and frontend)
uvicorn app.main:app --reload --host 0.0.0.0 --port 10720
```

Backend will be available at: http://localhost:10720
API docs: http://localhost:10720/docs

## Frontend Setup

```powershell
cd webapp\frontend
npm install

# Copy environment file
Copy-Item .env.example .env.local

# Run development server (or use start.ps1 from webapp for both)
npm run dev
```

Frontend will be available at: http://localhost:10721 (when using start.ps1) or Next default port.

## Project Structure

```
webapp/
├── backend/          # FastAPI HTTP wrapper
│   ├── app/
│   │   ├── main.py   # FastAPI application
│   │   ├── api/      # API endpoints
│   │   ├── mcp/      # MCP client wrapper
│   │   └── utils/   # Utilities
│   └── requirements.txt
│
└── frontend/         # Next.js 15 frontend
    ├── app/          # Next.js App Router pages
    ├── components/   # React components
    ├── lib/          # API client & utilities
    └── package.json
```

## Port rules and startup (mcp-central-docs)

- **Reservoir ports** (10700-10800): calibre-mcp uses **10720** (backend) and **10721** (frontend) for local runs that follow the ecosystem port rules.
- **Docker**: Compose maps host **10720** -> backend 13000, **10722** -> frontend 13001 (registry: 10720 = calibre-mcp Webapp).
- **Zombie kill**: Start scripts MUST clear the port before binding.
  - **start.ps1**: Clears 10720 and 10721, then starts backend and frontend in separate windows. Use: `powershell -ExecutionPolicy Bypass -File webapp\start.ps1` or `webapp\start.bat`.
- **start-all.bat** / **docker-up.ps1** (Docker): Runs `docker compose down` then `up -d`. Host ports: backend 10720, frontend 10722.

## Next Steps

1. **Test Backend**: Visit http://localhost:10720/docs
2. **Test Frontend**: Visit http://localhost:10721 (local) or http://localhost:10722 (Docker)
3. **Implement Features**: Follow the implementation guide in `docs/WEBAPP_IMPLEMENTATION_GUIDE.md`

## Troubleshooting

### Backend won't start
- Ensure CalibreMCP is installed: `pip install -e ..`
- Check Python version: `python --version` (should be 3.11+)
- Verify dependencies: `pip list | Select-String fastapi`

### Frontend won't start
- Check Node version: `node --version` (should be 18+)
- Clear cache: `Remove-Item -Recurse -Force node_modules, .next`
- Reinstall: `npm install`

### API calls fail
- Verify backend is running (port 10720 for local, or Docker 10720)
- Check CORS settings in `backend/app/config.py`
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
