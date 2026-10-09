# Per-repo fleet start config for calibre-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'calibre-mcp'
    BackendPort  = 10720
    FrontendPort = 10721
    HealthPath   = '/health'
    WebRoot      = 'webapp\frontend'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'app.main:app'
        WorkDir       = 'webapp\backend'
        PythonPath    = 'webapp\backend;src'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10720' }
        # Bind address for uvicorn. Default loopback (local-only).
        # Set $env:CALIBRE_BIND='0.0.0.0' (or webapp\start-lan.ps1) for LAN /
        # Tailscale access from other devices (phone, tablet, second PC).
        Host          = if ($env:CALIBRE_BIND) { $env:CALIBRE_BIND } else { '127.0.0.1' }
    }
    Frontend = @{
        Kind           = 'next'
        PackageManager = 'npm'
        PortEnvVar     = 'PORT'
        ApiTargetEnv   = 'API_URL'
    }
}
