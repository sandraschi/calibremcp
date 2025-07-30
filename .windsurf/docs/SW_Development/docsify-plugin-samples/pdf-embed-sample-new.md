# PDF Embed Plugin - Complete Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)
- [Theming and Styling](#theming-and-styling)
- [Troubleshooting](#troubleshooting)
- [Browser Support](#browser-support)

## Introduction

The PDF Embed plugin allows you to embed PDFiles directly in your documentation using the PDF.js library. It provides a cleand interactive way to display PDF content with features like zoom, search, and print.

## Installation

### CDN Method

Add these scripts to your `index.html`:

```html
<!-- PDF.js library -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.min.js"></script>
<script>window.pdfjsLib = pdfjsLib;</script>

<!-- PDF Embed Plugin -->
<script src="//cdn.jsdelivr.net/npm/docsify-pdf-embed@latest/dist/pdf-embed.min.js"></script>

<!-- Optional: WebAssembly for better performance -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js"></script>
```

### npmethod

```bash
npm install pdfjs-dist docsify-pdf-embed --save
```

## Basic Usage

### Simplembed

```markdown
[PDF Document](/path/to/document.pdf)
```

### With Custom Size

```markdown
[PDF Document](/path/to/document.pdf ':include width=100% height=600px')
```

### With Title

```markdown
[My Document](/path/to/document.pdf ':include :title=My PDF Document')
```

## Configuration

### Global Configuration

```javascript
window.$docsify = {
  pdfEmbed: {
    // Enable/disable the plugin
    enabled: true,
    
    // PDF.js worker path (relative or absolute)
    workerSrc: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js',
    
    // Default scale: 1.5,
    
    // Show download button
    showDownloadButton: true,
    
    // Show print button
    showPrintButton: true,
    
    // Show fullscreen button
    showFullscreenButton: true,
    
    // Enable text selection
    enableTextSelection: true,
    
    // Enable hand tool (pan/scroll)
    enableHandTool: true,
    
    // Enable search
    enableSearch: true,
    
    // Enable presentation modenablePresentationMode: false,
    
    // Custom CSS className: 'pdf-embed',
    
    // Custom button text
    buttons: {
      download: 'Download',
      print: 'Print',
      fullscreen: 'Fullscreen',
      zoomIn: 'Zoom In',
      zoomOut: 'Zoom Out',
      handTool: 'Hand Tool',
      search: 'Search',
      presentation: 'Presentation Mode'
    },
    
    // Custom styles: {
      container: 'border: 1px solid #eaecef; border-radius: 4px;',
      toolbar: 'background: #f6f8fa; padding: 8px;',
      button: 'background: none; border: none; cursor: pointer;',
      page: 'margin: 10px auto; box-shadow: 0 10px rgba(0,0,0,0.1);'
    },
    
    // Callbacks
    onLoad: function(pdf) {
      console.log('PDF loaded', pdf);
    },
    
    onError: function(error) {
      console.error('PDF error', error);
    },
    
    onPageChange: function(pageNumber) {
      console.log('Page changed to', pageNumber);
    }
  }
};
```

## Advanced Usage

### Lazy Loading

```markdown
[PDF Document](/path/to/large.pdf ':include :lazy')
```

### Start at Specific Page

```markdown
[PDF Document](/path/to/document.pdf ':include :page=3')
```

### Custom Controls

```javascript
window.$docsify = {
  pdfEmbed: {
    // Disable default controlshowDownloadButton: false,
    showPrintButton: false,
    showFullscreenButton: false,
    
    // Add custom controls
    onLoad: function(pdf) {
      const container = document.querySelector('.pdf-embed-container');
      const customControls = document.createElement('div');
      customControls.innerHTML = `
        <button class="custom-prev">Previous</button>
        <span class="page-info">Page 1 of ${pdf.numPages}</span>
        <button class="custom-next">Next</button>
      `;
      container.prepend(customControls);
      
      // Add event listeners
      customControls.querySelector('.custom-prev').addEventListener('click', () => {
        // Previous page logic
      });
      
      customControls.querySelector('.custom-next').addEventListener('click', () => {
        // Next page logic
      });
    }
  }
};
```

## Theming and Styling

### Custom CSS

```css
/* Container */
.pdf-embed {
  margin: 20px 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Toolbar */
.pdf-embed-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-bottom: 1px solid #eaecef;
}

/* Buttons */
.pdf-embed-button {
  background: #fff;
  border: 1px solid #d1d5da;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.pdf-embed-button:hover {
  background: #f3f4f6;
}

/* Page */
.pdf-embed-page {
  margin: 0 auto;
  box-shadow: 0 1px rgba(0,0,0,0.05);
}

/* Dark theme */
[data-theme="dark"] .pdf-embed-toolbar {
  background: #24292e;
  border-color: #444d56;
}

[data-theme="dark"] .pdf-embed-button {
  background: #2d333b;
  border-color: #444c56;
  color: #adbac7;
}

[data-theme="dark"] .pdf-embed-button:hover {
  background: #373e47;
}
```

## Troubleshooting

### Common Issues

1. **PDF not loading**
   - Check the browser console for errors
   - Verify the PDF path is correct
   - Ensure CORS is properly configured if loading from a different domain

2. **Missing worker file**
   - Make sure the PDF.js worker file is correctly specified
   - Use the same version for both PDF.js and its worker

3. **Performance issues**
   - Use WebAssembly for better performance
   - Consider lazy loading for large PDFs
   - Reduce the initial scale for fasterendering

## Browser Supporthe plugin works in all modern browsers that supporthe required JavaScript features:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Opera (latest)

For older browsers, you may need to include polyfills for:
- Promise
- fetch
- Object.assign
- Array.from
