# PowerShell script to run Python analysis and capture output
$pythonPath = "C:\Users\sandr\AppData\Local\Programs\Python\Python313\python.exe"
$scriptPath = Join-Path $PSScriptRoot "analyze_db_direct.py"
$outputFile = Join-Path $PSScriptRoot "..\samples\db_analysis.json"

# Run Python script and capture output
$output = & $pythonPath $scriptPath 2>&1

# Display output
$output

# Check if output file was created
if (Test-Path $outputFile) {
    Write-Host "Analysis complete. Results saved to: $outputFile"
} else {
    Write-Host "Analysis may have failed. Output file not found: $outputFile"
}
