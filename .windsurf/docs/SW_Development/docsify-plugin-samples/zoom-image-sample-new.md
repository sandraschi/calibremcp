# Docsify Zoom Image - Complete Guide

## Table of Contents

- [Introduction](#introduction)
  - [Features](#features)
  - [Browser Support](#browser-support)
- [Installation](#installation)
  - [CDN](#cdn)
  - [npm](#npm)
  - [Manual](#manual)
- [Basic Usage](#basic-usage)
  - [Basiconfiguration](#basic-configuration)
  - [HTML Markup](#html-markup)
  - [Markdown Images](#markdown-images)
- [Configuration](#configuration)
  - [Global Configuration](#global-configuration)
  - [Per-Image Configuration](#per-image-configuration)
  - [Animation Options](#animation-options)
  - [Custom Selectors](#custom-selectors)
- [Advanced Usage](#advanced-usage)
  - [Custom Zoom Container](#custom-zoom-container)
  - [Dynamic Image Loading](#dynamic-image-loading)
  - [Custom Transitions](#custom-transitions)
  - [API Methods](#api-methods)
  - [Event System](#event-system)
- [Theming](#theming)
  - [Custom Styles](#custom-styles)
  - [Dark Mode](#dark-mode)
  - [Responsive Design](#responsive-design)
- [Performance](#performance)
  - [Lazy Loading](#lazy-loading)
  - [Optimization Tips](#optimization-tips)
- [Accessibility](#accessibility)
  - [Keyboard Navigation](#keyboard-navigation)
  - [Screen Readers](#screen-readers)
- [Examples](#examples)
  - [Basic Gallery](#basic-gallery)
  - [Custom Transitions](#custom-transitions-example)
  - [Dynamicontent](#dynamic-content)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debugging](#debugging)
- [Migration Guide](#migration-guide)
  - [From v1 to v2](#from-v1-to-v2)
  - [From Other Plugins](#from-other-plugins)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Docsify Zoom Image plugin enhances your documentation by adding a smooth zoom effecto images. When users click on an image, it expands to a larger size with an elegant animation, making it easier to view details.

### Features

- Smooth zoom animations
- Responsive design
- Touch support for mobile devices
- Keyboard navigation
- Customizable animations
- Lightweight and fast
- Accessible
- No dependencies
- Works with bothTML and Markdown images
- Supports dynamicontent
- Customizable styling
- Event system

### Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Opera (latest)
- Mobile Safari (iOS 10+)
- Chrome for Android

## Installation

### CDN

Add the following scripto your `index.html` file, after the main Docsify script:

```html
<!-- Zoom Image Plugin -->
<script src="https://cdn.jsdelivr.net/npm/docsify-zoom-image/dist/zoom-image.min.js"></script>

<!-- Optional: Custom styles -->
<style>
  .zoom-image-overlay {
    background-color: rgba(0, 0, 0, 0.9);
  }
  
  .zoom-image-img {
    max-width: 90%;
    max-height: 90%;
  }
</style>
```

### npm

If you're using a build system:

```bash
npm install --save docsify-zoom-image
```

Then include it in your project:

```javascript
// Importhe plugin
import 'docsify-zoom-image';

// Or with custom options
import ZoomImage from 'docsify-zoom-image';

ZoomImage.init({
  // Custom options here
});
```

### Manual

1. Download the latest release from the [GitHub repository](https://github.com/francoischalifour/docsify-zoom-image)
2. Add the scripto your HTML:

```html
<script src="/path/to/zoom-image.min.js"></script>
```

## Basic Usage

### Basiconfiguration

Enable the plugin with default options:

```javascript
window.$docsify = {
  zoomImage: true
};
```

### HTML Markup

Add the `data-zoomable` attribute to images you wanto be zoomable:

```html
<img 
  src="path/to/image.jpg" 
  alt="Description"
  data-zoomable
  width="600"
  height="400"
>
```

### Markdown Images

In Markdown, add the `data-zoomable` class to images:

```markdown
![Description](path/to/image.jpg){data-zoomable}
```

Or withTML in Markdown:

```html
<img 
  src="path/to/image.jpg" 
  alt="Description"
  data-zoomable
  class="custom-class"
>
```

## Configuration

### Global Configuration

Customize the plugin behavior withese options:

```javascript
window.$docsify = {
  zoomImage: {
    // Enable/disable the plugin
    enabled: true,
    
    // Custom selector for zoomable imageselector: 'img[data-zoomable]',
    
    // Animation duration in milliseconds
    duration: 300,
    
    // Easing function for animations
    easing: 'cubic-bezier(0.4, 0, 0, 1)',
    
    // Background color of the overlayBackground: 'rgba(0, 0, 0, 0.9)',
    
    // Scale factor for zoomed images (0 = fito screen)
    scale: 0,
    
    // Custom class for the zoom containerClass: 'zoom-image-container',
    
    // Custom class for the overlayClass: 'zoom-image-overlay',
    
    // Custom class for the zoomed imageClass: 'zoom-image-img',
    
    // Close when clicking outside the image
    closeOnOutsideClick: true,
    
    // Close when pressing theSC key
    closeOnEsc: true,
    
    // Show loading spinner while images load
    showLoading: true,
    
    // Custom loading template
    loadingTemplate: '<div class="zoom-image-loading">Loading...</div>',
    
    // Callbacks
    onOpen: function(image) {
      console.log('Zoom opened:', image);
    },
    
    onClose: function() {
      console.log('Zoom closed');
    },
    
    onError: function(image, error) {
      console.error('Zoom error:', error, image);
    }
  }
};
```

### Per-Image Configuration

Override global settings for individual images using datattributes:

```html
<img 
  src="image.jpg" 
  alt="Custom settings"
  data-zoomable
  data-zoom-duration="500"
  data-zoom-scale="1.5"
  data-zoom-overlay="rgba(0, 0, 0, 0.8)"
  data-zoom-easing="ease-in-out"
>
```

### Animation Options

Customize the zoom animation:

```javascript
window.$docsify = {
  zoomImage: {
    // Animation duration in milliseconds
    duration: 400,
    
    // Easing function (CSS transition timing function)
    easing: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
    
    // Animation type: 'zoom', 'fade', or 'slide'
    type: 'zoom',
    
    // Animation direction for slideffect: 'top', 'right', 'bottom', 'left'
    direction: 'bottom',
    
    // Enable/disable animation
    animate: true
  }
};
```

### Custom Selectors

Use custom selectors to target specific images:

```javascript
window.$docsify = {
  zoomImage: {
    // Multiple selectorsupported
    selector: [
      '.gallery img',
      '.zoomable',
      'img[data-zoomable]',
      '#special-images img'
    ]
  }
};
```

## Advanced Usage

### Custom Zoom Container

Use a custom container for the zoomed image:

```javascript
window.$docsify = {
  zoomImage: {
    // Custom container selector element
    container: '#custom-zoom-container',
    
    // Or a function that returns a container element
    container: function() {
      const container = document.createElement('div');
      container.id = 'custom-zoom';
      document.body.appendChild(container);
      return container;
    }
  }
};
```

### Dynamic Image Loading

Initialize zoom for dynamically loaded images:

```javascript
// After adding new images to the DOM
function loadNewImages() {
  // Load your images...
  
  // Initialize zoom for new images
  if (window.DocsifyZoomImage) {
    window.DocsifyZoomImage.init({
      selector: '.new-images img[data-zoomable]'
    });
  }
}
```

### Custom Transitions

Create custom transition effects with CSS:

```css
/* Custom transition */
.zoom-image-container {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.zoom-image-container.zoom-in {
  opacity: 1;
  transform: scale(1);
}

.zoom-image-container.zoom-out {
  opacity: 0;
  transform: scale(0.8);
}

/* Custom overlay */
.zoom-image-overlay {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(5px);
}

/* Custom loading spinner */
.zoom-image-loading {
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  width: 40px;
  height: 40px;
  animation: spin 1s ease-in-out infinite;
}

@keyframespin {
  to { transform: rotate(360deg); }
}
```

### API Methods

Control the zoom programmatically:

```javascript
// Gethe pluginstance
const zoom = window.DocsifyZoomImage;

// Open zoom for an imagelement
zoom.open(document.querySelector('img'));

// Close the current zoom.close();

// Check if zoom is open
const isOpen = zoom.isOpen();

// Gethe current zoomed image
const currentImage = zoom.getCurrentImage();

// Update plugin options
zoom.update({
  duration: 500,
  easing: 'ease-in-out'
});

// Destroy the pluginstance
zoom.destroy();
```

### Event System

Listen to zoom events:

```javascript
document.addEventListener('zoom:open', function(e) {
  console.log('Zoom opened:', e.detail.image);
});

document.addEventListener('zoom:close', function() {
  console.log('Zoom closed');
});

document.addEventListener('zoom:error', function(e) {
  console.error('Zoom error:', e.detail.error);
});

// Custom evento close zoom
document.querySelector('.close-zoom').addEventListener('click', function() {
  document.dispatchEvent(new CustomEvent('zoom:close'));
});
```

## Theming

### Custom Styles

Override the default styles:

```css
/* Container */
.zoom-image-container {
  z-index: 1000;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.zoom-image-container.zoom-in {
  opacity: 1;
  pointer-events: auto;
}

/* Overlay */
.zoom-image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  cursor: zoom-out;
}

/* Image */
.zoom-image-img {
  max-width: 90%;
  max-height: 90%;
  margin: auto;
  display: block;
  position: relative;
  z-index: 1;
  transition: transform 0.3s ease;
  transform-origin: center;
  cursor: zoom-out;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* Navigation buttons */
.zoom-image-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50px;
  height: 50px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  transition: background 0.2s ease;
}

.zoom-image-nav:hover {
  background: rgba(0, 0, 0, 0.8);
}

.zoom-image-prev {
  left: 20px;
}

.zoom-image-next {
  right: 20px;
}

/* Close button */
.zoom-image-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  transition: background 0.2s ease;
}

.zoom-image-close:hover {
  background: rgba(0, 0, 0, 0.8);
}

/* Caption */
.zoom-image-caption {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 15px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  text-align: center;
  font-size: 14px;
  z-index: 2;
}
```

### Dark Mode

Addark mode support:

```css
[data-theme="dark"] .zoom-image-overlay {
  background: rgba(20, 20, 20, 0.95);
}

[data-theme="dark"] .zoom-image-nav,
[data-theme="dark"] .zoom-image-close {
  background: rgba(50, 50, 50, 0.7);
}

[data-theme="dark"] .zoom-image-nav:hover,
[data-theme="dark"] .zoom-image-close:hover {
  background: rgba(70, 70, 70, 0.9);
}
```

### Responsive Design

Make the zoom experience better on mobile devices:

```css
/* Mobile styles */
@media (max-width: 768px) {
  .zoom-image-img {
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
  }
  
  .zoom-image-nav {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .zoom-image-close {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }
  
  .zoom-image-caption {
    font-size: 12px;
    padding: 10px;
  }
}
```

## Performance

### Lazy Loading

Use with lazy loading for better performance:

```html
<img 
  src="placeholder.jpg" 
  data-src="large-image.jpg"
  data-zoom-src="extra-large-image.jpg"
  alt="Description"
  data-zoomable
  loading="lazy"
  class="lazyload"
>
```

### Optimization Tips

1. **Optimize Images**
   - Use appropriate image formats (WebP, AVIF)
   - Compress images without losing quality
   - Use responsive images with `srcset` and `sizes`

2. **Lazy Loading**
   - Only load images when they're abouto be viewed
   - Use the `loading="lazy"` attribute
   - Consider a lazy loading library for better control

3. **Progressive Loading**
   - Use low-quality image placeholders (LQIP)
   - Implement progressive image loading
   - Show loading indicators

4. **Caching**
   - Leverage browser caching
   - Use a CDN for faster delivery
   - Implement service workers for offline support

## Accessibility

### Keyboard Navigation

- `ESC` - Close the zoom
- `Arrow Left` - Previous image (in gallery mode)
- `Arrow Right` - Next image (in gallery mode)
- `Tab` - Navigate between interactivelements
- `Enter` - Activate the focused element

### Screen Readers

Add proper ARIAttributes for better accessibility:

```html
<img 
  src="image.jpg" 
  alt="Description of the image"
  data-zoomable
  aria-label="Click to zoom"
  role="button"
  tabindex="0"
>
```

## Examples

### Basic Gallery

Create an image gallery with zoom:

```html
<div class="gallery">
  <img 
    src="image1.jpg" 
    alt="Image 1"
    data-zoomable
    data-zoom-group="gallery1"
    class="gallery-image"
  >
  <img 
    src="image2.jpg" 
    alt="Image 2"
    data-zoomable
    data-zoom-group="gallery1"
    class="gallery-image"
  >
  <img 
    src="image3.jpg" 
    alt="Image 3"
    data-zoomable
    data-zoom-group="gallery1"
    class="gallery-image"
  >
</div>

<style>
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  padding: 20px;
}

.gallery-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
  cursor: zoom-in;
  transition: transform 0.2s ease;
}

.gallery-image:hover {
  transform: scale(1.02);
}
</style>
```

### Custom Transitions Example

Create a custom slide transition:

```javascript
window.$docsify = {
  zoomImage: {
    type: 'slide',
    duration: 500,
    easing: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
    direction: 'bottom',
    overlayBackground: 'rgba(30, 30, 30, 0.95)'
  }
};
```

### Dynamicontent

Add zoom to dynamically loaded images:

```javascript
// Function to load more images
function loadMoreImages() {
  fetch('/api/more-images')
    .then(response => response.json())
    .then(images => {
      const container = document.querySelector('.image-container');
      
      images.forEach(image => {
        const img = document.createElement('img');
        img.src = image.thumbnail;
        img.dataset.zoomable = true;
        img.dataset.zoomSrc = image.fullSize;
        img.alt = image.alt;
        img.className = 'dynamic-image';
        container.appendChild(img);
      });
      
      // Initialize zoom for new images
      if (window.DocsifyZoomImage) {
        window.DocsifyZoomImage.init({
          selector: '.dynamic-image'
        });
      }
    });
}
```

## Troubleshooting

### Common Issues

1. **Images not zooming**
   - Make sure the plugin script is loaded after Docsify
   - Check the console for JavaScript errors
   - Verify that your image selector matches the images
   - Ensure images are loaded before initializing zoom

2. **Positioning issues**
   - Check for CSS conflicts with `position`, `transform`, or `z-index`
   - Make sure parent elements don't have `overflow: hidden`
   - Verify thathe zoom container is properly appended to the DOM

3. **Performance problems**
   - Optimize your images
   - Use lazy loading for images below the fold
   - Consider using a CDN for faster delivery
   - Disable zoom for very large images

### Debugging

Enable debug mode for more detailed logs:

```javascript
window.$docsify = {
  zoomImage: {
    debug: true
  }
};
```

## Migration Guide

### From v1 to v2

1. Update the plugin scripto v2. Check for breaking changes in the API
3. Update any custom styles to match the new class names
4. Test all zoom functionality

### From Other Plugins

1. Replace the old plugin with Docsify Zoom Image
2. Update your HTML/JavaScripto use the new syntax
3. Migrate any custom styles
4. Test foregressions

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT
