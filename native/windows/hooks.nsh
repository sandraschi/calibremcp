; Fleet Tauri: kill UI + backend before install/uninstall.
!macro KillFleetSidecars
  DetailPrint "Stopping fleet processes..."
  ExecWait 'taskkill /F /IM calibre-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM calibre-mcp-native.exe /T' $0
  !if "${INSTALLMODE}" == "currentUser"
    nsis_tauri_utils::KillProcessCurrentUser "calibre-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcessCurrentUser "calibre-mcp-native.exe"
    Pop $0
  !else
    nsis_tauri_utils::KillProcess "calibre-mcp-backend.exe"
    Pop $0
    nsis_tauri_utils::KillProcess "calibre-mcp-native.exe"
    Pop $0
  !endif
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetSidecars
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetSidecars
!macroend
!macro NSIS_HOOK_POSTINSTALL
  IfFileExists "$INSTDIR\resources\install-mcp-clients.ps1" 0 mcp_hook_done
    DetailPrint "Optional: register Calibre MCP (stdio) in Cursor / Claude Desktop"
    ExecShell "" "powershell.exe" '-NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Normal -File "$INSTDIR\resources\install-mcp-clients.ps1" -InstallDir "$INSTDIR" -Interactive' SW_SHOW
  mcp_hook_done:
!macroend

