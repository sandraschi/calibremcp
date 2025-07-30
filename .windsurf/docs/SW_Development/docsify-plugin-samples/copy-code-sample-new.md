# Copy Code Plugin - Complete Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Configuration](#configuration)
  - [Global Configuration](#global-configuration)
  - [Per-Code-Block Configuration](#per-code-block-configuration)
- [Customization](#customization)
  - [Styling](#styling)
  - [Localization](#localization)
  - [Button Position](#button-position)
- [Advanced Usage](#advanced-usage)
  - [Custom Button Text](#custom-button-text)
  - [Custom Button HTML](#custom-button-html)
  - [Custom Callbacks](#custom-callbacks)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Browser Support](#browser-support)
- [Migration Guide](#migration-guide)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Copy Code plugin adds a convenient copy button to all code blocks in your documentation, making it easy for users to copy code snippets with a single click. This plugin enhances the user experience by eliminating the need to manually select and copy code.

## Installation

1. Add the plugin scripto your `index.html` file, after the main Docsify script:

```html
<!-- Add this after the main docsify script -->
<script src="//cdn.jsdelivr.net/npm/docsify-copy-code"></script>
```

2. (Optional) Add the default styles:

```html
<link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify-copy-code/dist/copy-code.min.css" />
```

## Basic Usage

No configuration is needed for basic usage. The plugin automatically adds copy buttons to all code blocks.

### Example

````markdown
```javascript
// This code block will have a copy button
function hello() {
  console.log('Hello, world!');
}
```
````

## Configuration

### Global Configuration

Customize the plugin's behavior by adding a `copyCode` objecto your Docsify configuration:

```javascript
window.$docsify = {
  copyCode: {
    // Options
    buttonText: 'Copy to clipboard',
    errorText: 'Error',
    successText: 'Copied!',
    
    // Button appearance
    buttonClass: 'btn-copy',
    buttonStyle: 'background: #f5f5f5; border: 1px solid #ddd; border-radius: 3px;',
    
    // Position (top-right, bottom-right, top-left, bottom-left)
    position: 'top-right',
    
    // Show/hide line numbershowLineNumbers: true,
    
    // Callbacks
    onCopy: function(code) {
      // Called when code is copied
      console.log('Code copied:', code);
    },
    
    // Advanced options
    timeout: 2000, // Time to show success/error message (ms)
    autoUpdate: true, // Auto-update for dynamicontent
    
    // Custom selector for code blocks (default: 'pre[data-lang]')
    selector: 'pre[data-lang]',
    
    // Custom CSSelector for the button container
    buttonContainer: '.copy-code-button',
    
    // Custom CSS class for the buttonClass: 'copy-code-button',
    
    // Custom CSS class for the successtate
    successClass: 'copy-code-success',
    
    // Custom CSS class for therror staterrorClass: 'copy-code-error',
    
    // Whether to show the copy button mobile deviceshowOnMobile: true,
    
    // Whether to show the copy button desktop
    showOnDesktop: true
  }
};
```

### Per-Code-Block Configuration

You can customize individual code blocks using HTML comments:

````markdown
```javascript
// This code block has custom copy settings
// copy-code: {"buttonText": "Copy Me!", "position": "bottom-left"}
function customExample() {
  return "This a custom example";
}
```
````

## Customization

### Styling

You can customize the appearance of the copy button using CSS:

```css
/* Custom button style */
.btn-copy {
  background-color: #4CAF50 !important;
  color: white !important;
  border: none !important;
  border-radius: 4px !important;
  padding: 4px 8px !important;
  font-size: 12px !important;
  cursor: pointer !important;
  transition: background-color 0.3s !important;
}

.btn-copy:hover {
  background-color: #45a049 !important;
}

/* Successtate */
.copy-code-success {
  background-color: #4CAF50 !important;
}

/* Error state */
.copy-code-error {
  background-color: #f44336 !important;
}

/* Dark theme support */
[data-theme="dark"] .btn-copy {
  background-color: #2c3e50 !important;
  color: #ecf0f1 !important;
}

[data-theme="dark"] .btn-copy:hover {
  background-color: #34495e !important;
}
```

### Localization

Customize the button text and messages:

```javascript
window.$docsify = {
  copyCode: {
    buttonText: 'Copy',
    successText: 'Copied!',
    errorText: 'Error copying',
    // Or use a function for dynamic text
    buttonText: function(codeElement) {
      return 'Copy ' + (codeElement.getAttribute('data-lang') || 'code');
    }
  }
};
```

### Button Position

Choose from different button positions:

- `top-right` (default)
- `top-left`
- `bottom-right`
- `bottom-left`

```javascript
window.$docsify = {
  copyCode: {
    position: 'bottom-right'
  }
};
```

## Advanced Usage

### Custom Button Text

Use a function to generate dynamic button text:

```javascript
window.$docsify = {
  copyCode: {
    buttonText: function(codeElement) {
      const lang = codeElement.getAttribute('data-lang') || 'code';
      return `Copy ${lang}`;
    }
  }
};
```

### Custom Button HTML

Completely customize the button HTML:

```javascript
window.$docsify = {
  copyCode: {
    buttonHtml: `
      <button class="custom-copy-btn" aria-label="Copy code">
        <svg width="14" height="16" viewBox="0 14 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M2.40527 13.8533L1.14062 15.118V1.14062H13.0179V13.8533H2.40527ZM0.284505C0.127366 0.127366 0.284505 0H13.874C14.0312 0 14.1585 0.127366 14.1585 0.284505V16L10.346 12.1875H0.284505C0.127366 12.1875 0 12.0601 0 11.903V0.284505ZM4.25893.69308V5.26228H11.5893V3.69308H4.25893ZM4.25893 7.11551V8.68471H9.30692V7.11551H4.25893Z" fill="currentColor"/>
        </svg>
        <span class="copy-text">Copy</span>
      </button>
    `
  }
};
```

### Custom Callbacks

Add custom behavior when code is copied:

```javascript
window.$docsify = {
  copyCode: {
    onCopy: function(code, button, codeElement) {
      // Code that was copied
      console.log('Copied code:', code);
      
      // The copy button element
      console.log('Button:', button);
      
      // The code block element
      console.log('Codelement:', codeElement);
      
      // You can modify the button or codelement here
      button.classList.add('copied');
      
      // Return false to prevent default behavior
      // return false;
    }
  }
};
```

## Best Practices

1. **Accessibility**
   - Ensure the button has proper ARIAttributes
   - Provide clear visual feedback
   - Make sure the button is keyboard-navigable

2. **Performance**
   - Only enable the plugin on pages with code blocks
   - Use the `selector` option to limit which code blocks gethe button
   - Consider lazy-loading the plugin for better performance

3. **User Experience**
   - Provide clear feedback when code is copied
   - Consider showing a tooltip on hover
   - Make sure the button is visible but not obtrusive

4. **Mobile Considerations**
   - Ensure the button is largenough to tap on touch devices
   - Consider hiding the button very small screens if it affects usability
   - Test on various mobile devices

## Troubleshooting

### Common Issues

1. **Copy buttonot appearing**
   - Make sure the plugin script is loaded after Docsify
   - Check for JavaScript errors in the console
   - Verify that your code blocks match the selector (default: `pre[data-lang]`)

2. **Copy functionality not working**
   - Check if the Clipboard APIsupported in the browser
   - Make sure the page iserved over HTTPS (required for Clipboard API)
   - Test in a different browser

3. **Styling issues**
   - Check for CSS conflicts with your theme
   - Make sure your custom styles have higher specificity
   - Verify that your styles are being applied correctly

### Debugging

Enable debug mode for more detailed error messages:

```javascript
window.$docsify = {
  copyCode: {
    debug: true
  }
};
```

## Browser Supporthe plugin works in all modern browsers that supporthe Clipboard API:

- Chrome 66+
- Firefox 63+
- Edge 79+
- Safari 13.1+
- Opera 53+

For older browsers, the plugin will gracefully degrade and show an error message when the copy action is not supported.

## Migration Guide

### From v1 to v2

1. Update the plugin scripto the latest version
2. Check for breaking changes in the configuration options
3. Update any custom CSSelectors if needed
4. Testhe copy functionality in all target browsers

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT

---

For more information, visithe [docsify-copy-code GitHub repository](https://github.com/jperasmus/docsify-copy-code).
