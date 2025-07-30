# Download Seminal AI Papers Script
# This script downloads key AI papers from arXiv and other sources

# Create a function to download files with error handling
function Download-Paper {
    param (
        [string]$url,
        [string]$outputPath,
        [string]$paperName
    )
    
    Write-Host "Downloading $paperName..." -ForegroundColor Cyan
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($url, $outputPath)
        if (Test-Path $outputPath) {
            Write-Host "✓ Successfully downloaded $paperName" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Failed to download $paperName" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Error downloading $paperName : $_" -ForegroundColor Red
        return $false
    }
}

# Create a function to create paper metadata
function New-PaperMetadata {
    param (
        [string]$title,
        [string]$authors,
        [string]$year,
        [string]$category,
        [string]$pdfUrl,
        [string]$arxivId
    )
    
    $metadata = @{
        title = $title
        authors = $authors
        year = $year
        category = $category
        pdfUrl = $pdfUrl
        arxivId = $arxivId
        downloaded = (Get-Date -Format "yyyy-MM-dd")
    }
    
    return $metadata | ConvertTo-Json
}

# Main script execution
$basePath = "D:\\Dev\\repos\\mywienerlinien\\.windsurf\\docs\\3_ai\\papers"
$papers = @(
    # Foundational Papers
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

# Create output directories if they don't exist
$categories = $papers | ForEach-Object { $_.category } | Select-Object -Unique
foreach ($cat in $categories) {
    $dir = Join-Path $basePath $cat
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Download each paper
foreach ($paper in $papers) {
    $category = $paper.category
    $arxivId = $paper.arxivId
    $pdfUrl = "https://arxiv.org/pdf/$arxivId.pdf"
    $fileName = "$($paper.title -replace '[^\w]', '_').pdf"
    $outputDir = Join-Path $basePath $category
    $outputPath = Join-Path $outputDir $fileName
    
    # Create directory if it doesn't exist
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    # Download the paper if it doesn't exist
    if (-not (Test-Path $outputPath)) {
        $success = Download-Paper -url $pdfUrl -outputPath $outputPath -paperName $paper.title
        
        # Create metadata file if download was successful
        if ($success) {
            $metadata = New-PaperMetadata @paper -pdfUrl $pdfUrl
            $metadataPath = $outputPath -replace '\.pdf$', '.json'
            $metadata | Out-File -FilePath $metadataPath -Encoding utf8
        }
    } else {
        Write-Host " Already exists: $($paper.title)" -ForegroundColor DarkGray
    }
}

Write-Host "`nPaper download process completed!" -ForegroundColor Green
