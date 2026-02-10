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

- Backend: http://localhost:13000
- Frontend: http://localhost:13001
- API docs: http://localhost:13000/docs

User data (comments, extended metadata) is persisted in a Docker volume.

## Local Run (No Docker)

If Docker cannot reach the registry, run the webapp locally:

**First-time setup** (run from Windows Explorer or native cmd - Cursor sandbox blocks pip/npm):
```batch
cd webapp
setup-local.bat
```

**Then start:**
```batch
start-local.bat
```

Requires: `.env` with `CALIBRE_LIBRARY_PATH` set.

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

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 13000
```

Backend will be available at: http://localhost:13000
API docs: http://localhost:13000/docs

## Frontend Setup

```powershell
cd webapp\frontend
npm install

# Copy environment file
Copy-Item .env.example .env.local

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:13001

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
  - **start.ps1**: Clears 10720 and 10721 (PowerShell `Get-NetTCPConnection` + `Stop-Process`), then starts backend and frontend in separate windows on those ports. Use for port-rule-compliant local run: `powershell -ExecutionPolicy Bypass -File webapp\start.ps1`.
  - **start-local.bat**: Clears 13000 and 13001 (netstat + taskkill), then starts backend 13000 and frontend 13001. Use for quick local dev without changing port.
  - **start-all.bat** (Docker): Runs `docker compose down` then `up -d`; does not clear host ports 10720/10722 if another process holds them (stop that process or use `docker compose down` and ensure no other container uses those ports).

## Next Steps

1. **Test Backend**: Visit http://localhost:13000/docs (or http://localhost:10720/docs if using start.ps1)
2. **Test Frontend**: Visit http://localhost:13001 or http://localhost:10721 (start.ps1)
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
- Verify backend is running on port 13000
- Check CORS settings in `backend/app/config.py`
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
