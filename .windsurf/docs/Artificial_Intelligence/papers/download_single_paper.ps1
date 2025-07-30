# Script to download a single paper

# Parameters
$paperTitle = "Attention Is All You Need"
$authors = "Vaswani et al."
$year = 2017
$category = "transformers"
$arxivId = "1706.03762"

# Setup paths
$basePath = "D:\Dev\repos\mywienerlinien\.windsurf\docs\3_ai\papers"
$outputDir = Join-Path $basePath $category
$fileName = $paperTitle -replace '[^\w]', '_'
$fileName = $fileName + ".pdf"
$outputPath = Join-Path $outputDir $fileName

# Create directory if it doesn't exist
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Download the paper
Write-Host "Downloading $paperTitle..." -ForegroundColor Cyan
$pdfUrl = "https://arxiv.org/pdf/$arxivId.pdf"

try {
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($pdfUrl, $outputPath)
    
    # Create metadata
    $metadata = @{
        title = $paperTitle
        authors = $authors
        year = $year
        category = $category
        pdfUrl = $pdfUrl
        arxivId = $arxivId
        downloaded = (Get-Date -Format "yyyy-MM-dd")
    } | ConvertTo-Json
    
    $metadataPath = $outputPath -replace '\.pdf$', '.json'
    $metadata | Out-File -FilePath $metadataPath -Encoding utf8
    
    Write-Host "Successfully downloaded: $paperTitle" -ForegroundColor Green
    Write-Host "Saved to: $outputPath" -ForegroundColor Green
} catch {
    Write-Host "Error downloading $paperTitle" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
}
