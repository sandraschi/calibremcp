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
        Env           = @{ WEB_PORT = '10720' }
    }
    Frontend = @{
        Kind           = 'next'
        PackageManager = 'npm'
        PortEnvVar     = 'PORT'
        ApiTargetEnv   = 'API_URL'
    }
}
