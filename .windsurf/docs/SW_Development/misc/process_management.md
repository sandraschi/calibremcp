# Process Management System

## Overview

The process management system provides a robust way to handle application lifecycle in Windows environments, focusing on graceful shutdowns, proper cleanup, and port conflict prevention. Thisystem is implemented in PowerShell for maximum compatibility and control.

## Core Principles

1. **Graceful Shutdown**
   - Applicationshould have a chance to clean up resources
   - Database connectionshould be properly closed
   - File handleshould be released
   - Temporary fileshould be removed

2. **Process Tracking**
   - Track process IDs (PIDs) of managed applications
   - Maintain processtate
   - Handle parent-child process relationships

3. **Port Management**
   - Detect port conflicts before starting
   - Gracefully handle port-in-use scenarios
   - Support for both TCP and UDProtocols

## Implementation Details

### 1. Process Lifecycle

```powershell
# Start a managed process
function Start-ManagedProcess {
    param(
        [string]$Command,
        [string]$Arguments,
        [string]$WorkingDirectory,
        [int]$Port
    )
    
    # Check for port conflicts
    if ($Port -and (Test-PortInUse -Port $Port)) {
        $existingProcess = Get-ProcessByPort -Port $Porthrow "Port $Port is in use by process $($existingProcess.Id) ($($existingProcess.ProcessName))"
    }
    
    # Starthe process
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $Command
    $processInfo.Arguments = $Arguments
    $processInfo.WorkingDirectory = $WorkingDirectory
    $processInfo.UseShellExecute = $false
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo
    $process.EnableRaisingEvents = $true
    
    # Set up event handlers
    $process.OutputDataReceived += { Write-Host $_.Data }
    $process.ErrorDataReceived += { Write-Error $_.Data }
    
    # Starthe process
    $process.Start() | Out-Null
    $process.BeginOutputReadLine()
    $process.BeginErrorReadLine()
    
    # Save process info
    $process | Add-Member -MemberType NoteProperty -Name 'StartTime' -Value (Get-Date)
    $process | Add-Member -MemberType NoteProperty -Name 'Port' -Value $Port
    
    return $process
}

# Stop a managed process
try {
    # Try graceful shutdown first
    if (-not $process.CloseMainWindow()) {
        # If no UI, try sending Ctrl+C
        $process.StandardInput.WriteLine([char]3)  # Ctrl+C
        
        # Wait for graceful exit
        if (-not $process.WaitForExit(5000)) {
            # Force stop if still running
            $process.Kill()
        }
    }
} catch {
    # Fallback to force stop
    $process.Kill()
}
```

### 2. Port Management

```powershell
function Test-PortInUse {
    param([int]$Port)
    
    try {
        # Method 1: Using .NET (fastest)
        $tcpListener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, $Port)
        try {
            $tcpListener.Start()
            $tcpListener.Stop()
            return $false
        } catch {
            return $true
        }
    } catch {
        # Method 2: Using netstat (fallback)
        $netstat = netstat -ano | findstr ":$Port"
        return [bool]$netstat
    }
}

function Get-ProcessByPort {
    param([int]$Port)
    
    try {
        # Method 1: Get-NetTCPConnection (Windows 8/2012+)
        if (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue) {
            $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
            if ($connection) {
                return Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            }
        }
        
        # Method 2: netstat fallback
        $netstatOutput = netstat -ano | findstr ":$Port.*LISTENING"
        if ($netstatOutput) {
            $parts = $netstatOutput -split '\s+'
            $processId = $parts[-1]
            return Get-Process -Id $processId -ErrorAction SilentlyContinue
        }
    } catch {
        Write-Warning "Error finding process on port $Port : $_"
    }
    
    return $null
}
```

## Usagexamples

### Starting a Managed Process

```powershell
# Start a Node.jserver
$nodeProcess = Start-ManagedProcess \
    -Command "node" \
    -Arguments "server.js --port 3000" \
    -WorkingDirectory "C:\myapp" \
    -Port 3000

# Register for process exit
Register-ObjectEvent -InputObject $nodeProcess -EventNamexited -Action {
    Write-Host "Node.js process exited with code: $($sender.ExitCode)"
}
```

### Graceful Shutdown Example

```powershell
function Stop-Application {
    param([System.Diagnostics.Process]$Process)
    
    Write-Host "Initiatingraceful shutdown..."
    
    # 1. Notify the application to shut down
    if ($Process.HasExited -eq $false) {
        # Try graceful shutdown first
        if ($Process.CloseMainWindow()) {
            Write-Host "Sent close window message"
            if ($Process.WaitForExit(5000)) {
                Write-Host "Process exited gracefully"
                return
            }
        }
        
        # 2. Try sending Ctrl+C if it's a console app
        try {
            $Process.StandardInput.WriteLine([char]3)  # Ctrl+C
            if ($Process.WaitForExit(3000)) {
                Write-Host "Process exited after Ctrl+C"
                return
            }
        } catch {
            # Ctrl+C not supported
        }
        
        # 3. Force stop as last resort
        Write-Host "Force stopping process..."
        $Process.Kill()
        $Process.WaitForExit(1000)
    }
    
    Write-Host "Shutdown complete"
}
```

## Best Practices

1. **Always Handle Cleanup**
   - Use `try/finally` blocks to ensuresources areleased
   - Implement proper signal handling in your applications
   - Clean up temporary files andatabase connections

2. **Log Everything**
   - Log processtart/stop events
   - Record exit codes and any errors
   - Include timestamps for debugging

3. **Handle Orphaned Processes**
   - Implement process tracking to detect and clean up orphans
   - Use process names and command-line arguments to identifyour processes

4. **Port Management**
   - Always check for port availability before starting
   - Implement retry logic with exponential backoff
   - Provide clear error messages when ports are in use

## Advanced Integration Examples

### 1. Windowservice with Auto-Restart

```powershell
# Install as a Windowservice with auto-restart
$serviceName = "MyAppService"
$scriptPath = "C:\\path\\to\\start.ps1"

# Create the service
New-Service \
    -Name $serviceName \
    -BinaryPathName "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" \
    -DisplayName "My Application Service" \
    -StartupType Automatic

# Configurecovery options
$action1 = New-ScheduledTaskAction -Execute "net.exe" -Argument "start $serviceName"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -DontStopOnIdleEnd
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask \
    -TaskName "${serviceName}_Recovery" \
    -Action $action1 \
    -Trigger $trigger \
    -Settings $settings \
    -Principal $principal \
    -Force | Out-Null
```

### 2. Docker Container Integration

```powershell
# Start a container withealth checks and auto-restart
$containerName = "myapp"
$port = 8080

# Pull the latest image
docker pull myapp:latest

# Stop and removexisting container
if (docker ps -a --filter "name=^${containerName}$" -q) {
    docker stop $containerName | Out-Null
    dockerm $containerName | Out-Null
}

# Start new container withealth check
dockerun -d \
    --name $containerName \
    -p "${port}:8080" \
    --restart unless-stopped \
    --health-cmd "curl -f http://localhost:8080/health || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    myapp:latest
```

### 3. CI/CD Pipeline (GitHub Actions)

```yaml
name: Deploy Application:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: windows-latesteps:
    - name: Checkout code
      uses: actions/checkout@v2
      
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Run tests
      run: npm test
      
    - name: Deploy to production
      run: |
        $ErrorActionPreference = 'Stop'
        .\deploy.ps1 -Environment Production
      env:
        DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        
    - name: Verify deployment
      run: |
        $status = Invoke-WebRequest -Uri "https://api.example.com/health" -UseBasicParsing | Select-Object -Expand StatusCode
        if ($status -ne 200) { exit 1 }
```

### 4. Scheduled Task with Error Handling

```powershell
# Create a scheduled task that runs daily with error handling
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"C:\scripts\daily-backup.ps1`" -ErrorAction Stop"
$trigger = New-ScheduledTaskTrigger -Daily -At "2am"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -DontStopOnIdleEnd -AllowStartIfOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register the task
Register-ScheduledTask \
    -TaskName "DailyBackup" \
    -Action $action \
    -Trigger $trigger \
    -Settings $settings \
    -Principal $principal \
    -Force | Out-Null

# Configure task to restart on failure
$task = Get-ScheduledTask -TaskName "DailyBackup"
$task.Settings.RestartCount = 3
$task.Settings.RestartInterval = "PT5M"
$task | Set-ScheduledTask
```

## Real-world Use Cases

### 1. Database Connection Pooling

```powershell
class DatabaseManager {
    [System.Data.SqlClient.SqlConnection[]]$Connections
    [int]$MaxConnections = 10
    
    DatabaseManager() {
        $this.Connections = New-Object System.Data.SqlClient.SqlConnection[] $this.MaxConnections
        $this.InitializePool()
    }
    
    [void] InitializePool() {
        for ($i = 0; $i -lt $this.MaxConnections; $i++) {
            $conn = New-Object System.Data.SqlClient.SqlConnection("Server=myServer;Database=myDB;Integrated Security=True")
            $this.Connections[$i] = $conn
        }
    }
    
    [System.Data.SqlClient.SqlConnection] GetConnection() {
        foreach ($conn in $this.Connections) {
            if ($conn.State -eq [System.Data.ConnectionState]::Closed) {
                $conn.Open()
                return $conn
            }
        }
        throw "No available connections in the pool"
    }
    
    [void] CloseAll() {
        foreach ($conn in $this.Connections) {
            if ($conn -and $conn.State -ne [System.Data.ConnectionState]::Closed) {
                $conn.Close()
                $conn.Dispose()
            }
        }
    }
}

# Usage
$dbManager = [DatabaseManager]::new()
try {
    $conn = $dbManager.GetConnection()
    # Use connection
} finally {
    if ($conn) { $conn.Close() }
}

# On application exit
Register-ObjectEvent -InputObject $global:MyApp -EventName OnExit -Action {
    $dbManager.CloseAll()
}
```

### 2. File Lock Management

```powershell
class FileLockManager {
    [System.Collections.Generic.Dictionary[string, System.IO.FileStream]]$FileLocks
    
    FileLockManager() {
        $this.FileLocks = [System.Collections.Generic.Dictionary[string, System.IO.FileStream]]::new()
    }
    
    [System.IO.FileStream] AcquireLock([string]$filePath) {
        if ($this.FileLocks.ContainsKey($filePath)) {
            throw "File is already locked: $filePath"
        }
        
        try {
            $stream = [System.IO.File]::Open(
                $filePath,
                [System.IO.FileMode]::OpenOrCreate,
                [System.IO.FileAccess]::ReadWrite,
                [System.IO.FileShare]::None
            )
            $this.FileLocks[$filePath] = $stream
            return $stream
        } catch {
            throw "Failed to acquire lock on $filePath : $_"
        }
    }
    
    [void] ReleaseLock([string]$filePath) {
        if ($this.FileLocks.TryGetValue($filePath, [ref]$stream)) {
            $stream.Close()
            $stream.Dispose()
            $this.FileLocks.Remove($filePath)
        }
    }
    
    [void] ReleaseAllLocks() {
        foreach ($kvp in $this.FileLocks.GetEnumerator()) {
            try {
                $kvp.Value.Close()
                $kvp.Value.Dispose()
            } catch {
                Write-Warning "Erroreleasing lock on $($kvp.Key): $_"
            }
        }
        $this.FileLocks.Clear()
    }
}
```

## Troubleshootinguide

### Common Issues and Solutions

#### 1. Port Conflicts

**Symptoms**:
- "Address already in use" errors
- Application fails to start

**Diagnosis**:
```powershell
# Find process using a specific port
function Find-ProcessUsingPort {
    param([int]$Port)
    
    Write-Host "Checking for processes using port $Port..."
    
    # Method 1: Get-NetTCPConnection (Windows 8/2012+)
    if (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue) {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connection) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                return $process
            }
        }
    }
    
    # Method 2: netstat fallback
    $netstatOutput = netstat -ano | findstr ":$Port.*LISTENING"
    if ($netstatOutput) {
        $parts = $netstatOutput -split '\s+'
        $processId = $parts[-1]
        return Get-Process -Id $processId -ErrorAction SilentlyContinue
    }
    
    return $null
}
```

**Solutions**:
- Use a different port
- Terminate the conflicting process
- Implement port reuse with `SO_REUSEADDR`
- Wait and retry with exponential backoff

#### 2. Process Won'terminate

**Symptoms**:
- Process remains in Task Manager after shutdown
- Application hangs during exit

**Diagnosis**:
```powershell
# Get process tree
function Get-ProcessTree {
    param([int]$ProcessId)
    
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $process) { return }
    
    $tree = @()
    $queue = [System.Collections.Queue]::new()
    $queue.Enqueue($process)
    
    while ($queue.Count -gt 0) {
        $current = $queue.Dequeue()
        $tree += $current
        
        # Get child processes
        Get-CimInstance -ClassName Win32_Process | Where-Object { 
            $_.ParentProcessId -eq $current.Id 
        } | ForEach-Object {
            $childProcess = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue
            if ($childProcess) {
                $queue.Enqueue($childProcess)
            }
        }
    }
    
    return $tree
}
```

**Solutions**:
- Ensure all threads are marked as background threads
- Implement proper signal handling (SIGINT, SIGTERM)
- Use `Process.Kill()` as last resort
- Check for open file handles or network connections

#### 3. Permission Issues

**Symptoms**:
- "Access denied" errors
- Process fails to start

**Diagnosis**:
```powershell
# Check effective permissions
function Test-ProcessPermission {
    param([string]$Path, [Security.Principal.WindowsIdentity]$Identity = [Security.Principal.WindowsIdentity]::GetCurrent())
    
    $rules = (Get-Acl -Path $Path).Access
    $access = $false
    
    foreach ($rule in $rules) {
        if ($rule.IdentityReference -eq $Identity.Name -or 
            $rule.IdentityReference -eq $Identity.Groups) {
            if ($rule.FileSystemRights -band [System.Security.AccessControl.FileSystemRights]::FullControl) {
                return $true
            }
        }
    }
    
    return $false
}
```

**Solutions**:
- Run as administrator if required
- Adjust folder permissions
- Check User Account Control (UAC) settings
- Verify service account permissions

#### 4. Resource Leaks

**Symptoms**:
- Memory usage grows over time
- Too many open file handles
- Application becomes unresponsive

**Diagnosis**:
```powershell
# Monitoresource usage
function Get-ProcessResources {
    param([int]$ProcessId)
    
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $process) { return }
    
    $handleCount = $process.HandleCount
    $threadCount = $process.Threads.Count
    $memoryMB = [math]::Round($process.WorkingSet64 / 1MB, 2)
    
    [PSCustomObject]@{
        ProcessId = $process.Id
        ProcessName = $process.ProcessName
        Handles = $handleCounthreads = $threadCount
        MemoryMB = $memoryMB
        CPU = $process.TotalProcessorTime
        StartTime = $process.StartTime
    }
}
```

**Solutions**:
- Implement `IDisposable` pattern
- Use `using` statements
- Monitor and limit resource usage
- Implement circuit breakers

## Performance Considerations

1. **Processtartup**
   - Minimize startup time
   - Use warm-up routines
   - Consider pre-starting services

2. **Memory Management**
   - Monitor memory usage
   - Implement cleanup routines
   - Use object pooling where appropriate

3. **Network Efficiency**
   - Reuse connections
   - Implementimeouts and retries
   - Use connection pooling

## Security Best Practices

1. **Principle of Least Privilege**
   - Run with minimal required permissions
   - Uservice accounts
   - Implement proper access controls

2. **Secure Communication**
   - Use TLS/SSL
   - Validate certificates
   - Implement secure credential storage

3. **Audit and Logging**
   - Log security events
   - Monitor for suspicious activity
   - Implement proper log rotation

## Monitoring and Maintenance

### Performance Counters

```powershell
# Create performance counters
functionew-PerformanceCounter {
    param(
        [string]$CategoryName,
        [string]$CounterName,
        [string]$HelpText
    )
    
    if (-not [System.Diagnostics.PerformanceCounterCategory]::Exists($CategoryName)) {
        $counterData = New-Object System.Diagnostics.CounterCreationDataCollection
        
        $counter = New-Object System.Diagnostics.CounterCreationData
        $counter.CounterName = $CounterName
        $counter.CounterHelp = $HelpText
        $counter.CounterType = [System.Diagnostics.PerformanceCounterType]::NumberOfItems32
        
        $counterData.Add($counter) | Out-Null
        
        [System.Diagnostics.PerformanceCounterCategory]::Create(
            $CategoryName,
            "Performance counters for $CategoryName",
            [System.Diagnostics.PerformanceCounterCategoryType]::SingleInstance,
            $counterData
        ) | Out-Null
    }
}

# Example usage
New-PerformanceCounter \
    -CategoryName "MyApplication" \
    -CounterName "RequestsProcessed" \
    -HelpText "Total number of requests processed"
```

### Event Log Integration

```powershell
# Write to Windows Event Log
function Write-EventLogEntry {
    param(
        [string]$Source,
        [string]$Message,
        [System.Diagnostics.EventLogEntryType]$EntryType = 'Information',
        [int]$EventId = 1000
    )
    
    if (-not [System.Diagnostics.EventLog]::SourceExists($Source)) {
        [System.Diagnostics.EventLog]::CreateEventSource($Source, 'Application')
    }
    
    [System.Diagnostics.EventLog]::WriteEntry($Source, $Message, $EntryType, $EventId)
}

# Example usage
try {
    # Application code here
    Write-EventLogEntry -Source 'MyApplication' -Message 'Application started successfully'
} catch {
    Write-EventLogEntry -Source 'MyApplication' -Message "Error: $_" -EntryTyperror -EventId 5000
    throw
}
```

## See Also

- [Windows Process Management](https://docs.microsoft.com/en-us/windows/win32/procthread/processes-and-threads)
- [PowerShell Process Cmdlets](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/?view=powershell-7.2#process)
- [Graceful Shutdown Patterns](https://docs.microsoft.com/en-us/dotnet/standard/parallel-programming/graceful-shutdown)
- [Windowservice Recovery Options](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn486827(v=ws.11))
