# VueScan: Professional Scanning Software

## Overview
VueScan is a powerful scanning application that works with most high-quality flatbed and film scanners to produce scans with excellent color fidelity and color balance. It's widely used by photographers, archivists, and professionals who need reliable scanning capabilities.

## Key Features

### 1. Scanner Support
- **Wide Compatibility**: 6,000+ scannersupported
- **Legacy Hardware**: Works with discontinued scanners
- **RAW Scanning**: Save in RAW DNG format
- **Batch Scanning**: Process multiple items automatically

### 2. Image Quality
- **Color Management**: ICC profiles and color spaces
- **Dust & Scratch Removal**: Infrared cleaning
- **Multi-Exposure**: HDR for transparent materials
- **Grain Reduction**: For film scanning

### 3. File Formats
- **Input**: TIFF, JPEG, PDF, RAW
- **Output**: TIFF, JPEG, PDF, Searchable PDF, OCR text, RAW
- **Color Depth**: Up to 64-bit color
- **DPI Range**: 1-9600 dpi

## Installation

### Windows
```powershell
# Using Chocolatey (unofficial)
choco install vuescan

# Silent Install
VueScanSetup.exe /S
```

### macOS
```bash
# Using Homebrew install --cask vuescan

# Or downloadMG
hdiutil attach VueScan.dmg
sudo cp -R "/Volumes/VueScan/VueScan.app" /Applications
hdiutil detach /Volumes/VueScan
```

### Linux
```bash
# Debian/Ubuntu
wget https://www.hamrick.com/files/vuex6497.deb
sudo dpkg -i vuex6497.deb

# Red Hat/CentOS
wget https://www.hamrick.com/files/vuex6497.rpm
sudo rpm -i vuex6497.rpm
```

## Usage Guide

### Basic Scanning
1. Launch VueScan
2. Select your scanner
3. Choose document/film type
4. Adjust settings as needed
5. Click "Scan"

### Command Line Interface

#### Windows CMD
```batch
# Basic scan to file
"C:\Program Files\VueScan\vuescan.exe" /dpi 300 /flatbed /color 2 /output "C:\Scans\output.tif"

# Batch scan with auto-naming
"C:\Program Files\VueScan\vuescan.exe" /dpi 600 /flatbed /color 1 /output "C:\Scans\scan_@.tif" /count 5
```

#### macOS/Linux
```bash
# Basic scan
/usr/local/bin/vuescan -o "$HOME/Scans/scan.tif" --dpi 300 --mode Color

# Batch scan with auto-increment
for in {1..5}; do
    /usr/local/bin/vuescan -o "$HOME/Scans/scan_$i.tif" --dpi 600 --mode Color
    echo "Press Enter to scanext document..."
    read
    
    # Eject document feeder
    osascript -e 'tell application "VueScan" to activate'
    osascript -e 'tell application "System Events" to keystroke "e" using {commandown}'
done
```

#### Advanced Options
```batch
# Film scanning with infrared cleaning
vuescan.exe /source "Film" /film_type "Color negative" /infrared 3 /dpi 2400 /output "scan.tiff"

# Document scanning with OCR
vuescan.exe /source "Document" /ocr /ocr_language "English" /output "document.pdf"

# Multi-page PDF
vuescan.exe /source "ADF Duplex" /output "document.pdf" /count 10 /batch
```

## Advanced Features

### 1. Batch Scanning

#### PowerShell Script
```powershell
# Scan multiple film strips
$scanner = "Canon 9000F"
$outputDir = "C:\Scans\Film"
$filmType = "Color negative"
$dpi = 2400

# Create output directory if it doesn't exist
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# Scan 6 frames
1..6 | ForEach-Object {
    $outputFile = Join-Path $outputDir "film_frame_$_.tiff"
    Write-Host "Scanning frame $_ to $outputFile"
    
    & "C:\Program Files\VueScan\vuescan.exe" /dpi $dpi /source "Film" /film_type "$filmType" /infrared 3 "$outputFile"
    
    # Wait for user to advance film
    if ($_ -lt 6) {
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}
```

### 2. Configuration Management

#### Windows Registry
```batch
# Export VueScan settings
reg export "HKEY_CURRENT_USER\Software\Hamrick\VueScan" vuescan_settings.reg

# Import settings
reg import vuescan_settings.reg
```

## Troubleshooting

### Common Issues

#### 1. Scanner Not Detected
- Check USB connection
- Installatest drivers
- Try different USB port
- Restart VueScan

#### 2. Poor Scan Quality
- Clean scanner glass
- Update VueScan to latest version
- Adjust exposure and color settings
- Use higher DPI for film

#### 3. Performance Issues
- Close other applications
- Increase memory allocation
- Disable preview
- Use smaller scan area

## Alternatives

### 1. SilverFast
- Professional scanning software
- Better color management
- Higher price point

### 2. Epson Scan
- Free with Epson scanners
- Good for basic scanning
- Limited features

### 3. NAPS2
- Open source
- Good for document scanning
- Limited film support

## Tips & Best Practices

### 1. Film Scanning
- Use proper film holders
- Clean film before scanning
- Use infrared cleaning for color negatives
- Save in RAW format for post-processing

### 2. Document Archiving
- Use 300 DPI for text
- Enable OCR for searchable PDFs
- Use consistent naming
- Include metadata

### 3. Photo Restoration
- Scan at highest optical resolution
- Save in TIFFormat
- Use multi-exposure for faded photos
- Keep original scans beforediting

## License
VueScan is commercial software with a free trial. Various licensing options are available for home and professional use.

## Support
- [Official Website](https://www.hamrick.com/)
- [Documentation](https://www.hamrick.com/vuescandoc.html)
- [Forums](https://www.hamrick.com/vuescandoc/forum/)
- [Contact Support](https://www.hamrick.com/support.html)
