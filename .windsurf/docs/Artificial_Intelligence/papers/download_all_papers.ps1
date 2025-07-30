# Script to download all seminal AI papers

# Base paths
$basePath = "D:\Dev\repos\mywienerlinien\.windsurf\docs\3_ai\papers"

# List of papers to download
$papers = @(
    @{
        title = "Attention Is All You Need"
        authors = "Vaswani et al."
        year = 2017
        category = "transformers"
        arxivId = "1706.03762"
    },
    @{
        title = "Deep Learning"
        authors = "LeCun, Bengio, Hinton"
        year = 2015
        category = "foundational"
        arxivId = "1012.5582"
    },
    @{
        title = "ImageNet Classification with Deep Convolutional Neural Networks"
        authors = "Krizhevsky, Sutskever, Hinton"
        year = 2012
        category = "computer_vision"
        arxivId = "1102.0183"
    },
    @{
        title = "Playing Atari with Deep Reinforcement Learning"
        authors = "Mnih et al."
        year = 2013
        category = "reinforcement_learning"
        arxivId = "1312.5602"
    },
    @{
        title = "Generative Adversarial Networks"
        authors = "Goodfellow et al."
        year = 2014
        category = "generative_models"
        arxivId = "1406.2661"
    },
    @{
        title = "Concrete Problems in AI Safety"
        authors = "Amodei et al."
        year = 2016
        category = "ai_safety"
        arxivId = "1606.06565"
    }
)

# Create output directories
$categories = $papers | ForEach-Object { $_.category } | Select-Object -Unique
foreach ($cat in $categories) {
    $dir = Join-Path $basePath $cat
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# Download each paper
foreach ($paper in $papers) {
    $category = $paper.category
    $outputDir = Join-Path $basePath $category
    $fileName = $paper.title -replace '[^\w]', '_' + ".pdf"
    $outputPath = Join-Path $outputDir $fileName
    $pdfUrl = "https://arxiv.org/pdf/$($paper.arxivId).pdf"
    
    # Skip if file already exists
    if (Test-Path $outputPath) {
        Write-Host "Already exists: $($paper.title)" -ForegroundColor DarkGray
        continue
    }
    
    # Download the paper
    Write-Host "Downloading $($paper.title)..." -ForegroundColor Cyan
    
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($pdfUrl, $outputPath)
        
        # Create metadata
        $metadata = @{
            title = $paper.title
            authors = $paper.authors
            year = $paper.year
            category = $paper.category
            pdfUrl = $pdfUrl
            arxivId = $paper.arxivId
            downloaded = (Get-Date -Format "yyyy-MM-dd")
        } | ConvertTo-Json
        
        $metadataPath = $outputPath -replace '\.pdf$', '.json'
        $metadata | Out-File -FilePath $metadataPath -Encoding utf8
        
        Write-Host "✓ Downloaded: $($paper.title)" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error downloading $($paper.title): $_" -ForegroundColor Red
    }
    
    # Be nice to arXiv servers
    Start-Sleep -Seconds 2
}

Write-Host "`nPaper download process completed!" -ForegroundColor Green
