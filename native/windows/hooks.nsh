; -- native/windows/hooks.nsh --
; Kill UI + backend before install/uninstall (backend locks resources/*.exe).
; Multi-layer: Stop-Process (same-user) + taskkill (any user) + NSIS plugin.
; For SYSTEM/other-user zombie processes, the Rust free_port() function has a
; UAC elevation fallback that fires on the next app launch.
!macro KillFleetProcesses
  DetailPrint "Stopping Calibre MCP processes..."

  ; Stop-Process (same-user) + taskkill (any user)
  ExecWait 'powershell -NoProfile -Command "Stop-Process -Name calibre-mcp-backend -Force -ErrorAction SilentlyContinue; Stop-Process -Name calibre-mcp-native -Force -ErrorAction SilentlyContinue; taskkill /F /IM calibre-mcp-backend.exe /T 2>$null; taskkill /F /IM calibre-mcp-native.exe /T 2>$null"' $0

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
  Sleep 3000
!macroend

!macro UninstallPrevious
  DetailPrint "Checking for previous installation..."
  !if "${INSTALLMODE}" == "currentUser"
    ReadRegStr $R0 HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${IDENTIFIER}" "UninstallString"
  !else
    ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${IDENTIFIER}" "UninstallString"
  !endif
  ${If} $R0 != ""
    DetailPrint "Removing previous installation..."
    ExecWait '"$R0" /S' $0
    DetailPrint "Previous uninstall exit code: $0"
    Sleep 1500
  ${EndIf}
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetProcesses
  !insertmacro UninstallPrevious
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetProcesses
!macroend

!macro NSIS_HOOK_POSTINSTALL
  IfFileExists "$INSTDIR\resources\install-mcp-clients.ps1" 0 mcp_hook_done
    DetailPrint "Optional: register Calibre MCP in Cursor / Claude Desktop"
    ExecWait 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$INSTDIR\resources\install-mcp-clients.ps1" -Interactive'
  mcp_hook_done:
!macroend

