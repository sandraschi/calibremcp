!macro NSIS_HOOK_POSTINSTALL
  IfFileExists "$INSTDIR\resources\install-mcp-clients.ps1" 0 mcp_hook_done
    DetailPrint "Optional: register Calibre MCP (stdio) in Cursor / Claude Desktop"
    ExecShell "" "powershell.exe" '-NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Normal -File "$INSTDIR\resources\install-mcp-clients.ps1" -InstallDir "$INSTDIR" -Interactive' SW_SHOW
  mcp_hook_done:
!macroend
