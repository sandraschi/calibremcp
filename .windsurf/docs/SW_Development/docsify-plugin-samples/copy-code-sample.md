# Copy Code Plugin - Complete Guide

## Introduction

The Copy Code plugin adds a handy copy button to all code blocks in your documentation, making it easy for users to copy code snippets with a single click.

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

```javascript
// This code block will have a copy button
function hello() {
  console.log('Hello, world!');
}
```

## Configuration Options

### Global Configuration

```javascript
window.$docsify = {
  copyCode: {
    // Button text (supports HTML)
    buttonText: 'Copy',
    
    // Text shown after copying (supports HTML)
    successText: 'Copied!',
    
    // How long to show the success text (ms)
    successTextTimeout: 2000,
    
    // Show the copy button the left side
    align: 'right', // 'left' or 'right'
    
    // Custom styling
    style: {
      background: '#f5f5f5',
      color: '#666',
      'border-radius': '4px',
      'font-size': '12px',
      'padding': '2px 8px',
      'position': 'absolute',
      'right': '4px',
      'top': '4px',
      'cursor': 'pointer',
      'border': '1px solid #ddd',
      'opacity': '0.8',
      'z-index': '1'
    },
    
    // Custom class for the buttonClass: 'copy-code-button',
    
    // Custom class for the success text
    successClass: 'copy-code-success',
    
    // Show line numbershowLineNumbers: true,
    
    // Only show copy button when hovering over the code block
    showOnHover: false,
    
    // Customize the copy function
    copy: function(text) {
      // This function is called when the copy button is clicked
      // You can modify the text before it's copied
      return text;
    }
  }
};
```

### Per-Code Block Configuration

You can configure individual code blocks using HTML comments:

````markdown
```javascript
// This code block has custom copy settings
// @copy-code:button-text="Copy Me"
// @copy-code:success-text="Done!"
// @copy-code:align="left"
function custom() {
  console.log('Custom settings for this block');
}
```
````

```javascript
// This code block has custom copy settings
// @copy-code:button-text="Copy Me"
// @copy-code:success-text="Done!"
// @copy-code:align="left"
function custom() {
  console.log('Custom settings for this block');
}
```

## Styling

### Custom CSS

You can style the copy button using CSS:

```css
/* Custom copy button style */
.copy-code-button {
  background: #4CAF50 !important;
  color: white !important;
  border: none !important;
  border-radius: 4px !important;
  padding: 4px 12px !important;
  font-size: 12px !important;
  cursor: pointer !important;
  transition: all 0.3s ease !important;
}

.copy-code-button:hover {
  background: #45a049 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.copy-code-success {
  background: #4CAF50 !important;
  color: white !important;
}

/* Hide copy button for specificode blocks */
.no-copy-button .copy-code-button {
  display: none;
}
```

### Disable Copy for Specific Blocks

To disable the copy button for a specificode block, add a `no-copy` class:

````markdown
```javascript no-copy
// This code block won't have a copy button
functionoCopy() {
  console.log('No copy button here');
}
```
````

```javascript no-copy
// This code block won't have a copy button
functionoCopy() {
  console.log('No copy button here');
}
```

## Advanced Usage

### Custom Button Content

You can use HTML in the button text:

```javascript
window.$docsify = {
  copyCode: {
    buttonText: '<i class="fa-copy"></i>',
    successText: '<i class="fa-check"></i>'
  }
};
```

### Event Listeners

You can listen for copy events:

```javascript
document.addEventListener('copy-code:after', function(e) {
  console.log('Code copied:', {
    text: e.detail.text,
    codeEl: e.detail.codeEl,
    buttonEl: e.detail.buttonEl
  });
});
```

### Availablevents

- `copy-code:before`: Fires before copying
- `copy-code:after`: Fires after copying
- `copy-code:success`: Fires when copy isuccessful
- `copy-code:error`: Fires if there's an error

## Best Practices

1. **Be Consistent**
   - Use the same styling for all copy buttons
   - Keep the button position consistent (left oright)

2. **Clear Feedback**
   - Provide clear visual feedback when code is copied
   - Use a success message that's visible but not distracting

3. **Accessibility**
   - Ensure sufficient color contrast
   - Add appropriate ARIA labels
   - Make sure the button is keyboard-navigable

## Troubleshooting

- **Copy buttonot appearing?**
  - Make sure the plugin is properly loaded
  - Check for JavaScript errors in the console
  - Verifyour CSS isn't hiding the button

- **Copy not working?**
  - Check if the browser supports the Clipboard API
  - Make sure there are no JavaScript errors
  - Try the custom copy function for advanced scenarios

---

For more information, visithe [docsify-copy-code GitHub repository](https://github.com/jperasmus/docsify-copy-code).
