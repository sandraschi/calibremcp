# Sidebar Collapse Plugin - Complete Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
  - [CDN](#cdn)
  - [npm](#npm)
- [Basic Usage](#basic-usage)
  - [Minimal Setup](#minimal-setup)
  - [Basiconfiguration](#basic-configuration)
- [Advanced Configuration](#advanced-configuration)
  - [Custom Icons](#custom-icons)
  - [Persistence Options](#persistence-options)
  - [Custom Selectors](#custom-selectors)
  - [Animation Settings](#animation-settings)
  - [Event Hooks](#event-hooks)
- [Theming and Styling](#theming-and-styling)
  - [Custom CSS Variables](#custom-css-variables)
  - [Dark Theme Support](#dark-theme-support)
  - [Custom Animations](#custom-animations)
- [Accessibility](#accessibility)
  - [Keyboard Navigation](#keyboard-navigation)
  - [Screen Reader Support](#screen-reader-support)
  - [Focus Management](#focus-management)
- [Performance Considerations](#performance-considerations)
- [Troubleshooting](#troubleshooting)
- [Browser Support](#browser-support)
- [Migrating from Other Versions](#migrating-from-other-versions)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Sidebar Collapse plugin enhances your Docsify documentation by adding collapsible sections to the sidebar. It automatically adds toggle buttons nexto folders and supports persistent state across page loads, making it easier to navigate large documentation sites.

### Key Features

- Automaticollapsible sections for nested navigation
- Persistent state using localStorage
- Customizable icons and animations
- Keyboard navigation support
- Mobile-responsive design
- Dark theme support
- Event hooks for customization

## Installation

### CDN

Add the following scripto your `index.html` file, after the main Docsify script:

```html
<!-- Sidebar Collapse Plugin -->
<script src="https://cdn.jsdelivr.net/npm/docsify-sidebar-collapse/dist/docsify-sidebar-collapse.min.js"></script>
```

### npm

If you're using a build system:

```bash
npm install docsify-sidebar-collapse --save
```

Then include it in your project:

```javascript
import 'docsify-sidebar-collapse';
```

## Basic Usage

### Minimal Setup

Enable the plugin with default settings:

```javascript
window.$docsify = {
  loadSidebar: true,  // Required for sidebar
  subMaxLevel: 3,     // Maximum header level to include
  plugins: [
    // Other plugins...
    window.DocsifySidebarCollapse.init()
  ]
};
```

### Basiconfiguration

Customize the plugin behavior:

```javascript
window.$docsify = {
  loadSidebar: true,
  subMaxLevel: 3,
  plugins: [
    window.DocsifySidebarCollapse.init({
      // Collapse all sections by default
      collapseAll: false,
      
      // Show the first active section
      openFirstActive: true,
      
      // Auto-save the state
      persistState: true,
      
      // Custom storage key for persistence
      storageKey: 'docsify-sidebar-collapse-state',
      
      // Custom selectors: {
        // The main sidebar container
        sidebar: '.sidebar',
        
        // List items that contain submenus
        items: '.sidebar-nav > ul > li',
        
        // Links thatrigger the toggles: '.sidebar-nav > ul > li > a',
        
        // Submenu containersubmenus: '.sidebar-nav > ul > li > ul',
        
        // Active link
        activeLink: '.sidebar-nav a.active',
        
        // Icons: {
          // Open state
          open: '<svg>...</svg>',
          
          // Closed state
          closed: '<svg>...</svg>',
          
          // Loading state
          loading: '<span>Loading...</span>'
        }
      },
      
      // Animation settings
      animation: {
        // Enable/disable animations
        enabled: true,
        
        // Animation duration in milliseconds
        duration: 300,
        
        // Animation easing function
        easing: 'ease-in-out'
      },
      
      // Callbacks: {
        // Called when a section is opened
        onOpen: function(element) {
          console.log('Section opened:', element);
        },
        
        // Called when a section is closed
        onClose: function(element) {
          console.log('Section closed:', element);
        },
        
        // Called when the state isaved
        onSave: function(state) {
          console.log('State saved:', state);
        },
        
        // Called when the state is loaded
        onLoad: function(state) {
          console.log('State loaded:', state);
          return state; // Return modified state if needed
        }
      }
    })
  ]
};
```

## Advanced Configuration

### Custom Icons

You can replace the default icons with your own SVG or HTML:

```javascript
window.$docsify = {
  plugins: [
    window.DocsifySidebarCollapse.init({
      selectors: {
        icons: {
          // Custom SVG icon for open state
          open: `
            <svg width="12" height="12" viewBox="0 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19l-7-7-7"/>
            </svg>
          `,
          
          // Custom SVG icon for closed state
          closed: `
            <svg width="12" height="12" viewBox="0 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 5l7-7"/>
            </svg>
          `
        }
      }
    })
  ]
};
```

### Persistence Options

Customize how the sidebar state is persisted:

```javascript
window.$docsify = {
  plugins: [
    window.DocsifySidebarCollapse.init({
      // UsessionStorage instead of localStorage: window.sessionStorage,
      
      // Custom storage key
      storageKey: 'my-custom-storage-key',
      
      // Disable persistence
      persistState: false,
      
      // Custom serialization
      serialize: function(state) {
        return JSON.stringify(state);
      },
      
      // Custom deserialization
      deserialize: function(data) {
        try {
          return JSON.parse(data);
        } catch (e) {
          return {};
        }
      }
    })
  ]
};
```

### Custom Selectors

If your HTML structure is different, you can customize the selectors:

```javascript
window.$docsify = {
  plugins: [
    window.DocsifySidebarCollapse.init({
      selectors: {
        // The main sidebar container
        sidebar: '.my-sidebar',
        
        // List items that contain submenus
        items: '.my-sidebar-nav > .menu-item',
        
        // Links thatrigger the toggles: '.my-sidebar-nav > .menu-item > .menu-link',
        
        // Submenu containersubmenus: '.my-sidebar-nav > .menu-item > .submenu',
        
        // Active link
        activeLink: '.my-sidebar-nav .active',
        
        // Icons container (appended toggles)
        iconContainer: '.menu-icon',
        
        // Class added to items with submenus
        hasSubmenuClass: 'has-children',
        
        // Class added topen items
        openClass: 'is-open',
        
        // Class added to active items
        activeClass: 'is-active',
        
        // Class added to the sidebar when initializedClass: 'is-initialized'
      }
    })
  ]
};
```

## Theming and Styling

### Custom CSS Variables

Customize the appearance using CSS variables:

```css
:root {
  /* Colors */
  --sidebar-toggle-color: #666;
  --sidebar-toggle-hover-color: #000;
  --sidebar-toggle-active-color: #42b983;
  --sidebar-toggle-bg: transparent;
  --sidebar-toggle-hover-bg: rgba(0, 0, 0, 0.05);
  --sidebar-toggle-active-bg: rgba(66, 185, 131, 0.1);
  
  /* Sizes */
  --sidebar-toggle-size: 24px;
  --sidebar-toggle-icon-size: 12px;
  
  /* Transitions */
  --sidebar-toggle-transition: all 0.2s ease;
}

/* Dark theme */
[data-theme="dark"] {
  --sidebar-toggle-color: #8b949e;
  --sidebar-toggle-hover-color: #c9d1d9;
  --sidebar-toggle-active-color: #58a6ff;
  --sidebar-toggle-bg: transparent;
  --sidebar-toggle-hover-bg: rgba(240, 246, 252, 0.1);
  --sidebar-toggle-active-bg: rgba(88, 166, 255, 0.1);
}
```

### Custom Animations

Add custom animations for the sidebar transitions:

```css
/* Slide animation */
.sidebar-nav ul {
  overflow: hidden;
  transition: height 0.3s ease-in-out;
}

/* Fade animation */
.sidebar-nav li > ul {
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.sidebar-nav li.is-open > ul {
  opacity: 1;
  transform: translateY(0);
}

/* Rotate icon */
.sidebar-toggle-icon {
  transition: transform 0.3s ease;
}

.sidebar-nav li.is-open > a > .sidebar-toggle-icon {
  transform: rotate(90deg);
}
```

## Accessibility

### Keyboard Navigation

The plugin supports keyboard navigation out of the box:

- `Tab` - Navigate between interactivelements
- `Enter` or `Space` - Toggle the current section
- `Arrow Right` - Open the current section
- `Arrow Left` - Close the current section
- `Arrow Down` - Move to the next item
- `Arrow Up` - Move to the previous item
- `Home` - Move to the first item
- `End` - Move to the last item

### Screen Reader Support

Add ARIAttributes for better screen reader support:

```javascript
window.$docsify = {
  plugins: [
    window.DocsifySidebarCollapse.init({
      selectors: {
        // Add ARIAttributes: {
          button: {
            'aria-expanded': 'false',
            'aria-controls': 'submenu-${index}'
          },
          submenu: {
            'id': 'submenu-${index}',
            'aria-hidden': 'true'
          }
        }
      }
    })
  ]
};
```

## Performance Considerations

1. **Large Sidebars**
   - For very large sidebars, consider virtual scrolling
   - Load sections dynamically as needed
   - Use `subMaxLevel` to limithe depth of the navigation

2. **Animations**
   - Use `will-change` for better performance
   - Prefer `transform` and `opacity` for animations
   - Disable animations on low-poweredevices

3. **Persistence**
   - Limithe amount of data stored in localStorage
   - Use `sessionStorage` for temporary state
   - Implement a cleanup mechanism for oldata

## Troubleshooting

### Common Issues

1. **Sections not collapsing**
   - Verify the plugin script is loaded after Docsify
   - Check the browser console for errors
   - Ensure the selectors match your HTML structure

2. **State not persisting**
   - Check if localStorage is available
   - Verify the storage key is not being overwritten
   - Check for conflicts with other scripts

3. **Styling issues**
   - Check for CSSpecificity conflicts
   - Verify custom styles are loaded after the plugin styles
   - Use the browser's dev tools to inspecthelements

### Debugging

Enable debug mode for more detailed logs:

```javascript
window.$docsify = {
  plugins: [
    window.DocsifySidebarCollapse.init({
      debug: true
    })
  ]
};
```

## Browser Supporthe plugin works in all modern browsers:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Opera (latest)

## Migrating from Other Versions

### From v1 to v2

1. Update the plugin scripto the latest version
2. Check for breaking changes in the configuration options
3. Update any custom styles to match the new class names
4. Testhe sidebar on all pages

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT
