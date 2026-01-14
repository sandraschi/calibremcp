# Webapp Setup Guide

Quick setup instructions for the Calibre webapp.

## Prerequisites

- Python 3.11+
- Node.js 18+
- CalibreMCP server installed and working

## Backend Setup

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

## Next Steps

1. **Test Backend**: Visit http://localhost:13000/docs to see API documentation
2. **Test Frontend**: Visit http://localhost:3000 to see the webapp
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
