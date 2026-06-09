# Register Calibre MCP (stdio) in Cursor and/or Claude Desktop.
param(
    [string]$InstallDir,
    [switch]$Cursor,
    [switch]$Claude,
    [switch]$Interactive
)

$ErrorActionPreference = "Stop"

$ServerKey = "calibre-mcp"

function Get-BackendExePath {
    param([string]$Root)
    $candidates = @(
        (Join-Path $Root "resources\calibre-mcp-backend.exe"),
        (Join-Path $Root "calibre-mcp-backend.exe")
    )
    foreach ($path in $candidates) {
        if (Test-Path -LiteralPath $path) {
            return (Resolve-Path -LiteralPath $path).Path
        }
    }
    throw "Bundled backend not found under $Root"
}

function Get-CursorConfigPath {
    Join-Path $env:USERPROFILE ".cursor\mcp.json"
}

function Get-ClaudeConfigPath {
    Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
}

function Backup-ConfigFile {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    $dir = Split-Path -Parent $Path
    $file = Split-Path -Leaf $Path
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    if ($file -match '^(.+)\.json$') {
        $backupName = "$($Matches[1])_$stamp.json.bak"
    } else {
        $backupName = "${file}_$stamp.bak"
    }
    $backup = Join-Path $dir $backupName
    Copy-Item -LiteralPath $Path -Destination $backup -Force
    Write-Host "Backup: $backup"
    return $backup
}

function ConvertTo-HashtableRecursive {
    param($InputObject)
    if ($null -eq $InputObject) { return $null }
    if ($InputObject -is [System.Collections.IDictionary]) {
        $out = [ordered]@{}
        foreach ($key in $InputObject.Keys) {
            $out[$key] = ConvertTo-HashtableRecursive $InputObject[$key]
        }
        return $out
    }
    if ($InputObject -is [System.Array]) {
        return @($InputObject | ForEach-Object { ConvertTo-HashtableRecursive $_ })
    }
    if ($InputObject -is [pscustomobject]) {
        $out = [ordered]@{}
        foreach ($prop in $InputObject.PSObject.Properties) {
            $out[$prop.Name] = ConvertTo-HashtableRecursive $prop.Value
        }
        return $out
    }
    return $InputObject
}

function Read-ConfigDocument {
    param([string]$Path)
    $doc = [ordered]@{}
    if (Test-Path -LiteralPath $Path) {
        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        if (-not [string]::IsNullOrWhiteSpace($raw)) {
            $parsed = $raw | ConvertFrom-Json
            $doc = ConvertTo-HashtableRecursive $parsed
        }
    }
    return $doc
}

function Register-McpClient {
    param(
        [string]$Path,
        [string]$BackendExe
    )

    $beforeCount = 0
    if (Test-Path -LiteralPath $Path) {
        $existing = Read-ConfigDocument -Path $Path
        if ($existing.mcpServers) {
            $beforeCount = @($existing.mcpServers.Keys).Count
        }
    }

    $null = Backup-ConfigFile -Path $Path

    $doc = Read-ConfigDocument -Path $Path
    if (-not $doc.mcpServers) {
        $doc.mcpServers = [ordered]@{}
    } elseif ($doc.mcpServers -isnot [System.Collections.IDictionary]) {
        $doc.mcpServers = ConvertTo-HashtableRecursive $doc.mcpServers
    }

    $doc.mcpServers[$ServerKey] = [ordered]@{
        command = $BackendExe
        args    = @("--stdio")
    }

    $afterCount = @($doc.mcpServers.Keys).Count
    if ($beforeCount -gt 0 -and $afterCount -lt $beforeCount) {
        throw "Refusing to write $Path: would drop MCP servers ($beforeCount -> $afterCount)."
    }

    $parent = Split-Path -Parent $Path
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $json = ($doc | ConvertTo-Json -Depth 32)
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

function Show-InstallDialog {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $form = New-Object System.Windows.Forms.Form
    $form.Text = "Calibre MCP - AI client setup"
    $form.Width = 500
    $form.Height = 300
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false

    $label = New-Object System.Windows.Forms.Label
    $label.Text = "Register Calibre MCP for stdio (JSON-RPC). Cursor / Claude spawn the bundled server - no separate Python install.`n`nThe desktop app can still run for the web UI (HTTP backend on port 10720)."
    $label.AutoSize = $false
    $label.Width = 460
    $label.Height = 80
    $label.Location = New-Object System.Drawing.Point(15, 15)
    $form.Controls.Add($label)

    $cursorBox = New-Object System.Windows.Forms.CheckBox
    $cursorBox.Text = "Cursor (%USERPROFILE%\.cursor\mcp.json)"
    $cursorBox.Checked = $true
    $cursorBox.Location = New-Object System.Drawing.Point(20, 105)
    $form.Controls.Add($cursorBox)

    $claudeBox = New-Object System.Windows.Forms.CheckBox
    $claudeBox.Text = "Claude Desktop (claude_desktop_config.json)"
    $claudeBox.Checked = $false
    $claudeBox.Location = New-Object System.Drawing.Point(20, 135)
    $form.Controls.Add($claudeBox)

    $ok = New-Object System.Windows.Forms.Button
    $ok.Text = "Register"
    $ok.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $ok.Location = New-Object System.Drawing.Point(290, 200)
    $form.Controls.Add($ok)

    $skip = New-Object System.Windows.Forms.Button
    $skip.Text = "Skip"
    $skip.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $skip.Location = New-Object System.Drawing.Point(380, 200)
    $form.Controls.Add($skip)

    $form.AcceptButton = $ok
    $form.CancelButton = $skip
    $result = $form.ShowDialog()

    return [pscustomobject]@{
        Proceed = ($result -eq [System.Windows.Forms.DialogResult]::OK)
        Cursor  = $cursorBox.Checked
        Claude  = $claudeBox.Checked
    }
}

if ([string]::IsNullOrWhiteSpace($InstallDir)) {
    $InstallDir = Split-Path -Parent $PSScriptRoot
    if ($InstallDir -match "resources$") {
        $InstallDir = Split-Path -Parent $InstallDir
    }
}

$backendExe = Get-BackendExePath -Root $InstallDir

if ($Interactive -and -not $Cursor -and -not $Claude) {
    $choice = Show-InstallDialog
    if (-not $choice.Proceed) {
        Write-Host "Skipped MCP client registration."
        exit 0
    }
    if ($choice.Cursor) { $Cursor = $true }
    if ($choice.Claude) { $Claude = $true }
}

if (-not $Cursor -and -not $Claude) {
    Write-Host "Nothing to register. Pass -Cursor, -Claude, or -Interactive."
    exit 0
}

$updated = @()
if ($Cursor) {
    $path = Get-CursorConfigPath
    Register-McpClient -Path $path -BackendExe $backendExe
    $updated += "Cursor ($path)"
}
if ($Claude) {
    $path = Get-ClaudeConfigPath
    Register-McpClient -Path $path -BackendExe $backendExe
    $updated += "Claude Desktop ($path)"
}

Write-Host "Registered $ServerKey (stdio) -> $backendExe --stdio"
foreach ($item in $updated) {
    Write-Host "  - $item"
}
