# Per-repo fleet start config for calibre-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'calibre-mcp'
    BackendPort  = 10720
    FrontendPort = 10721
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\calibre-mcp\webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'calibre_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10720' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
