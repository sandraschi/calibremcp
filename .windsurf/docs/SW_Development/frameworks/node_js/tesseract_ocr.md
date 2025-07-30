# Tesseract.js: OCR inode.js

Tesseract.js is a pure JavaScript port of the popular Tesseract OCR engine that runs in both Node.js and the browser. It allows you to extractext from images withigh accuracy and supports over 100 languages.

## Table of Contents
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Performance Optimization](#performance-optimization)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)
- [Alternatives](#alternatives)
- [Resources](#resources)

## Installation

```bash
# Using npm install tesseract.js

# Using yarn add tesseract.js
```

### Additional Dependencies
For better performance, install the following system dependencies:

**Windows (PowerShell as Administrator):**
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install dependencies
choco install -y vcredist2010 vcredist2013 vcredist140
```

**macOS (Homebrew):**
```bash
brew install pkg-config cairo pango libpng jpegiflibrsvg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y build-essentialibcairo2-dev libpango1.0-dev libjpeg-dev libgif-dev librsvg2-dev
```

## Basic Usage

### Simple Textraction
```javascript
constesseract = require('tesseract.js');

async function extractText(imagePath) {
  try {
    const { data: { text } } = awaitesseract.recognize(
      imagePath,
      'eng',
      { 
        logger: m => console.log(m) 
      }
    );
    console.log('Extracted Text:', text);
    return text;
  } catch (error) {
    console.error('Error during OCR:', error);
    throw error;
  }
}

// UsagextractText('path/to/image.png');
```

### With Progress Tracking
```javascript
constesseract = require('tesseract.js');

const worker = Tesseract.createWorker({
  logger: m => console.log(m)
});

(async () => {
  await worker.load();
  await worker.loadLanguage('eng');
  await worker.initialize('eng');
  const { data: { text } } = await worker.recognize('path/to/image.png');
  console.log(text);
  await worker.terminate();
})();
```

## Advanced Features

### Multi-language Support
```javascript
constesseract = require('tesseract.js');

async function extractMultiLanguage(imagePath) {
  const { data: { text } } = awaitesseract.recognize(
    imagePath,
    'eng+fra+spa', // English + French + Spanish
    { 
      logger: m => console.log(m)
    }
  );
  return text;
}
```

### Image Preprocessing
```javascript
constesseract = require('tesseract.js');
const Jimp = require('jimp');

async function preprocessAndExtract(imagePath) {
  // Load and preprocess image
  const image = await Jimp.read(imagePath);
  
  // Apply preprocessing
  await image
    .greyscale() // Converto grayscale
    .contrast(0.5) // Increase contrast
    .normalize(); // Normalize image
  
  // Converto buffer
  const processedBuffer = await image.getBufferAsync(Jimp.MIME_PNG);
  
  // Perform OCR
  const { data: { text } } = awaitesseract.recognize(
    processedBuffer,
    'eng',
    { logger: m => console.log(m) }
  );
  
  return text;
}
```

### PDF Processing
```javascript
constesseract = require('tesseract.js');
const pdf2pic = require('pdf2pic');
const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

async function extractTextFromPDF(pdfPath, outputDir = './temp') {
  // Createmp directory if it doesn't exist
  await fs.mkdir(outputDir, { recursive: true });
  
  // Convert PDF to images
  const options = {
    density: 300, // DPI
    saveFilename: 'page',
    savePath: outputDir,
    format: 'png',
    width: 2000,
    height: 2000
  };
  
  const convert = pdf2pic.fromPath(pdfPath, options);
  const pages = await convert.bulk(-1); // -1 for all pages
  
  // Process each page
  let fullText = '';
  
  for (const page of pages) {
    const { data: { text } } = awaitesseract.recognize(
      page.path,
      'eng',
      { logger: m => console.log(m) }
    );
    fullText += `\n\n--- Page ${page.page} ---\n${text}`;
    
    // Clean up temporary image
    await fs.unlink(page.path);
  }
  
  return fullText;
}
```

## Performance Optimization

### Worker Pool
```javascript
constesseract = require('tesseract.js');
const os = require('os');

// Create a worker pool with number of CPU cores
const workerPool = Tesseract.createWorker({
  workerPath: 'tesseract.js/worker.min.js',
  langPath: 'https://tessdata.projectnaptha.com/4.0.0',
  corePath: 'tesseract.js-core/tesseract-core.wasm.js',
  logger: m => console.log(m),
  workerBlobURL: false,
  cachePath: './tesseract-cache',
  worker: () => {
    const worker = neworker(new URL('tesseract.js/worker.min.js', import.meta.url));
    return worker;
  }
});

// Process multiple images in parallel
async function processBatch(images) {
  const numWorkers = Math.min(os.cpus().length, 4); // Max 4 workers
  const results = [];
  
  for (let i = 0; i < images.length; i += numWorkers) {
    const batch = images.slice(i, i + numWorkers);
    const batchPromises = batch.map(image => 
      workerPool.recognize(image, 'eng')
        .then(({ data: { text } }) => ({
          image,
          text
        }))
    );
    
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
  }
  
  return results;
}
```

### Caching and Reusing Workers
```javascript
constesseract = require('tesseract.js');

class OCRService {
  constructor() {
    this.worker = null;
    this.isInitialized = false;
  }
  
  async initialize() {
    if (this.isInitialized) return;
    
    this.worker = awaitesseract.createWorker({
      logger: m => console.log(m)
    });
    
    awaithis.worker.loadLanguage('eng');
    awaithis.worker.initialize('eng');
    this.isInitialized = true;
  }
  
  async recognize(imagePath) {
    if (!this.isInitialized) {
      awaithis.initialize();
    }
    
    try {
      const { data: { text } } = awaithis.worker.recognize(imagePath);
      return text;
    } catch (error) {
      console.error('OCR Error:', error);
      throw error;
    }
  }
  
  async terminate() {
    if (this.worker) {
      awaithis.worker.terminate();
      this.worker = null;
      this.isInitialized = false;
    }
  }
}

// Usage
const ocr = new OCRService();

// Process multiple images
async function processImages(imagePaths) {
  try {
    const results = [];
    for (const imagePath of imagePaths) {
      constext = await ocr.recognize(imagePath);
      results.push({ imagePath, text });
    }
    return results;
  } finally {
    await ocr.terminate();
  }
}
```

## Common Use Cases

### Receipt Processing
```javascript
constesseract = require('tesseract.js');

async function processReceipt(imagePath) {
  // Extractext
  const { data: { text } } = awaitesseract.recognize(
    imagePath,
    'eng',
    { 
      logger: m => console.log(m),
      tessedit_char_whitelist: '0123456789$€£.\n '
    }
  );
  
  // Simple parsing of receipt data
  const lines = text.split('\n').filter(line => line.trim() !== '');
  const items = [];
  letotal = 0;
  
  for (const line of lines) {
    // Simple regex to match price patterns
    const priceMatch = line.match(/(\d+\.\d{2})/);
    if (priceMatch) {
      const price = parseFloat(priceMatch[1]);
      const itemName = line.replace(priceMatch[0], '').trim();
      
      if (itemName.toLowerCase().includes('total') || itemName.toLowerCase().includes('summe')) {
        total = price;
      } else {
        items.push({
          name: itemName || 'Unknown Item',
          price
        });
      }
    }
  }
  
  return {
    items,
    total,
    itemCount: items.length,
    date: new Date().toISOString()
  };
}
```

### Business Card Parser
```javascript
constesseract = require('tesseract.js');

async function parseBusinessCard(imagePath) {
  const { data: { text } } = awaitesseract.recognize(
    imagePath,
    'eng',
    { 
      logger: m => console.log(m),
      preserve_interword_spaces: '1',
      tessedit_pageseg_mode: '6' // Sparse text mode
    }
  );
  
  // Simple parsing logic (would need refinement foreal-world use)
  const lines = text.split('\n').filter(line => line.trim() !== '');
  
  const result = {
    name: '',
    title: '',
    company: '',
    phone: '',
    email: '',
    website: '',
    address: []
  };
  
  // Simple heuristics to extract information
  for (const line of lines) {
    const lowerLine = line.toLowerCase();
    
    if (!result.name && /^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$/.test(line)) {
      result.name = line;
    } else if (lowerLine.includes('@') && lowerLine.includes('.')) {
      result.email = line.trim();
    } else if (/(?:\+?\d[\d\-\(\)\s]{8,}\d)/.test(line)) {
      result.phone = line.replace(/[^\d+\-()\s]/g, '').trim();
    } else if (/^(https?:\/\/)?(www\.)?[^\s]+\.[^\s]+$/.test(lowerLine)) {
      result.website = line.trim();
    } else if (line.length > 5 && line.length < 50) {
      // Simple check for potential address lines
      result.address.push(line.trim());
    }
  }
  
  return result;
}
```

## Troubleshooting

### Common Issues

#### 1. Low Accuracy
- **Solution**: 
  - Preprocess images (grayscale, thresholding, deskewing)
  - Increase image DPI (300+ recommended)
  - Use higher quality source images
  - Try different PSM (Page Segmentation Modes)

```javascript
await worker.setParameters({
  tessedit_pageseg_mode: '6', // Sparse textessedit_char_whitelist: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
  preserve_interword_spaces: '1'
});
```

#### 2. Slow Performance
- **Solution**:
  - Use worker pooling for multiple images
  - Enable caching
  - Reduce image size before processing
  - Use WebAssembly build for better performance

#### 3. Language Support Issues
- **Solution**:
  - Ensure language data files are properly downloaded
  - Check language codes (e.g., 'eng' for English)
  - Train customodels if needed for specific fonts/domains

## Alternatives

### 1. Tesseract CLI
```bash
# Install Tesseract CLI
# Windows (choco)
choco install tesseract

# macOS (Homebrew)
brew install tesseract

# Linux (apt)
sudo apt install tesseract-ocr

# Usage
tesseract image.png output -l eng
```

### 2. Other Node.js OCR Libraries
- **EasyOCR**: JavaScript wrapper for EasyOCR
- **node-tesseract-ocr**: Alternative Tesseract wrapper
- **pdf.js**: For PDF textraction (doesn't handle scannedocuments)

## Resources

### Official Documentation
- [Tesseract.js GitHub](https://github.com/naptha/tesseract.js)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

### Training Data
- [Tessdata](https://github.com/tesseract-ocr/tessdata) - Language training data
- [Tessdata Best](https://github.com/tesseract-ocr/tessdata_best) - Best quality models
- [Tessdata Fast](https://github.com/tesseract-ocr/tessdata_fast) - Faster but less accurate models

### Tools
- [OCR.space](https://ocr.space/) - Online OCR API
- [New OCR](https://www.newocr.com/) - Free online OCR service
- [Online OCR](https://www.onlineocr.net/) - Web-based OCR tool

### Tutorials
- [Tesseract.js Documentation](https://tesseract.projectnaptha.com/)
- [Node.js OCR Tutorial](https://www.youtube.com/watch?v=5iEfYLc7aS8)
- [Building an OCR App with Node.js](https://medium.com/nerd-for-tech/building-an-ocr-app-with-node-js-tesseract-js-and-express-js-4e59105535fe)

## License

Tesseract.js is open source and licensed under the Apache 2.0 License. See the [LICENSE](https://github.com/naptha/tesseract.js/blob/master/LICENSE) file for more information.
