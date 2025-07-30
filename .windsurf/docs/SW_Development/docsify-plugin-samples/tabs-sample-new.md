# Docsify Tabs - Complete Guide

## Table of Contents

- [Introduction](#introduction)
  - [Features](#features)
  - [Browser Support](#browser-support)
- [Installation](#installation)
  - [CDN](#cdn)
  - [npm](#npm)
  - [Manual](#manual)
- [Basic Usage](#basic-usage)
  - [Simple Tabs](#simple-tabs)
  - [Tab Groups](#tab-groups)
  - [Nested Tabs](#nested-tabs)
- [Advanced Usage](#advanced-usage)
  - [Dynamic Tabs](#dynamic-tabs)
  - [Tab Events](#tab-events)
  - [Tab Persistence](#tab-persistence)
  - [Tab Routing](#tab-routing)
- [Configuration](#configuration)
  - [Global Configuration](#global-configuration)
  - [Per-Instance Configuration](#per-instance-configuration)
- [Theming](#theming)
  - [Custom Styles](#custom-styles)
  - [Dark Mode](#dark-mode)
  - [Animations](#animations)
- [Accessibility](#accessibility)
  - [Keyboard Navigation](#keyboard-navigation)
  - [ARIAttributes](#aria-attributes)
  - [Screen Readers](#screen-readers)
- [API Reference](#api-reference)
  - [Methods](#methods)
  - [Events](#events)
  - [Configuration Options](#configuration-options)
- [Examples](#examples)
  - [Code Tabs](#code-tabs)
  - [Contentabs](#content-tabs)
  - [Custom Templates](#custom-templates)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Debugging](#debugging)
- [Performance](#performance)
  - [Optimization Tips](#optimization-tips)
  - [Lazy Loading](#lazy-loading)
- [Migration Guide](#migration-guide)
  - [From v1 to v2](#from-v1-to-v2)
  - [From Other Plugins](#from-other-plugins)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The Docsify Tabs plugin allows you torganize content into tabbed sections, making your documentation more organized and easier to navigate. It's fully responsive, accessible, and highly customizable.

### Features

- Simple markdown syntax
- Nested tabsupport
- Dynamic tab loading
- URL hash navigation
- Keyboard navigation
- Mobile-friendly
- Customizable themes
- Event system
- Tab persistence
- Lazy loading

### Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Opera (latest)

## Installation

### CDN

Add the following scripto your `index.html` file, after the main Docsify script:

```html
<!-- Tabs Plugin -->
<script src="https://cdn.jsdelivr.net/npm/docsify-tabs@1"></script>
```

### npm

If you're using a build system:

```bash
npm install --save docsify-tabs
```

Then include it in your project:

```javascript
import 'docsify-tabs';
```

### Manual

1. Download the latest release from the [GitHub repository](https://github.com/imyelo/docsify-tabs)
2. Add the scripto your HTML:

```html
<script src="/path/to/docsify-tabs.min.js"></script>
```

## Basic Usage

### Simple Tabs

Create a basic tab group:

````markdown
<!-- tabs:start -->

#### **Tab 1**
Content for tab 1

#### **Tab 2**
Content for tab 2

#### **Tab 3**
Content for tab 3

<!-- tabs:end -->
````

### Tab Groups

Create multiple tab groups on the same page:

````markdown
<!-- tabs:start group="Group 1" -->

#### **Firstab**
First group content

#### **Second Tab**
First group content

<!-- tabs:end -->

<!-- tabs:start group="Group 2" -->

#### **Alpha**
Second group content

#### **Beta**
Second group content

<!-- tabs:end -->
````

### Nested Tabs

Create tabs within tabs:

````markdown
<!-- tabs:start -->

#### **Outer 1**
Content for outer tab 1

#### **Outer 2**
<!-- tabs:start -->

##### **Inner 1**
Nested tab 1 content

##### **Inner 2**
Nested tab 2 content

<!-- tabs:end -->

<!-- tabs:end -->
````

## Advanced Usage

### Dynamic Tabs

Add tabs dynamically with JavaScript:

```javascript
// Add a new tab to an existingroup
function addTab(groupId, tabName, content) {
  const container = document.querySelector(`[data-tab-group="${groupId}"]`);
  if (!container) return;
  
  constabs = container.querySelector('.docsify-tabs');
  constabList = tabs.querySelector('.docsify-tabs__list');
  constabContent = tabs.querySelector('.docsify-tabs__content');
  
  // Create tabutton
  constabId = `tab-${Date.now()}`;
  constabButton = document.createElement('button');
  tabButton.className = 'docsify-tabs__tab';
  tabButton.textContent = tabName;
  tabButton.setAttribute('data-tab', tabId);
  tabButton.setAttribute('role', 'tab');
  tabButton.setAttribute('aria-selected', 'false');
  
  // Create tab panel
  constabPanel = document.createElement('div');
  tabPanel.className = 'docsify-tabs__panel';
  tabPanel.id = tabId;
  tabPanel.setAttribute('role', 'tabpanel');
  tabPanel.setAttribute('aria-labelledby', tabId);
  tabPanel.innerHTML = content;
  
  // Add to DOM
  tabList.appendChild(document.createElement('li')).appendChild(tabButton);
  tabContent.appendChild(tabPanel);
  
  // Initialize the new tab
  if (window.DocsifyTabs) {
    window.DocsifyTabs.initTab(tabs, tabButton, tabPanel);
  }
}
```

### Tab Events

Listen for tab changes:

```javascript
document.addEventListener('docsify-tabs:change', function(event) {
  console.log('Tab changed:', {
    tab: event.detail.tab,
    panel: event.detail.panel,
    group: event.detail.group
  });
});
```

### Tab Persistence

Remember the last active tab:

```javascript
window.$docsify = {
  tabs: {
    persist: true, // Enable persistence
    storage: 'local', // 'local' or 'session' storage
    maxAge: 86400000 // 24 hours in milliseconds
  }
};
```

### Tab Routing

Update URL hash when tabs change:

```javascript
window.$docsify = {
  tabs: {
    sync: true, // Sync with URL hash
    theme: 'material' // Optional theme
  }
};
```

## Configuration

### Global Configuration

```javascript
window.$docsify = {
  tabs: {
    // General
    persist: false,
    sync: false,
    theme: 'default',
    
    // Styling
    tabButtonClass: 'docsify-tabs__tab',
    tabPanelClass: 'docsify-tabs__panel',
    tabListClass: 'docsify-tabs__list',
    tabContainerClass: 'docsify-tabs',
    
    // Behavior
    lazyRender: false,
    dynamicHeight: true,
    animate: true,
    animationDuration: 300,
    
    // Callbacks
    onInit: function(tabs) {},
    onChange: function(tab, panel, group) {},
    
    // Templates: {
      tab: function(tab, index) {
        return `<button class="${this.tabButtonClass}" 
                       data-tab="${tab.id}" 
                       role="tab" 
                       aria-selected="${index === 0 ? 'true' : 'false'}">
          ${tab.title}
        </button>`;
      },
      panel: function(panel, index) {
        const isActive = index === 0 ? 'is-active' : '';
        return `<div class="${this.tabPanelClass} ${isActive}" 
                       id="${panel.id}" 
                       role="tabpanel" 
                       aria-labelledby="${panel.id}-tab"
                       ${index > 0 ? 'hidden' : ''}>
          ${panel.content}
        </div>`;
      }
    }
  }
};
```

### Per-Instance Configuration

Override global settings for specific tab groups:

````markdown
<!-- tabs:start group="custom" data-config='{"theme": "material", "persist": true}' -->

#### **Custom Tab**
Content with custom configuration

#### **Another Tab**
More content

<!-- tabs:end -->
````

## Theming

### Custom Styles

Override the default styles:

```css
/* Tab container */
.docsify-tabs {
  margin: 1.5rem 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Tab list */
.docsify-tabs__list {
  display: flex;
  margin: 0;
  padding: 0;
  list-style: none;
  background: #f8f9fa;
  border-bottom: 1px solid #eaecef;
}

/* Tabuttons */
.docsify-tabs__tab {
  padding: 0.75rem 1.25rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 0.9rem;
  font-weight: 500;
  color: #6a737d;
  cursor: pointer;
  transition: all 0.2s ease;
}

.docsify-tabs__tab:hover {
  color: #0366d6;
}

.docsify-tabs__tab[aria-selected="true"] {
  color: #0366d6;
  border-bottom-color: #0366d6;
}

/* Tab panels */
.docsify-tabs__panel {
  padding: 1.5rem;
  background: #fff;
}

/* Dark theme */
[data-theme="dark"] .docsify-tabs {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .docsify-tabs__list {
  background: #24292e;
  border-color: #444d56;
}

[data-theme="dark"] .docsify-tabs__tab {
  color: #8b949e;
}

[data-theme="dark"] .docsify-tabs__tab:hover,
[data-theme="dark"] .docsify-tabs__tab[aria-selected="true"] {
  color: #58a6ff;
  border-bottom-color: #58a6ff;
}

[data-theme="dark"] .docsify-tabs__panel {
  background: #0d1117;
  color: #c9d1d9;
}
```

### Dark Mode

The plugin automatically supports dark mode when using the `data-theme="dark"` attribute on the `html` or `body` element.

### Animations

Add custom animations for tab transitions:

```css
/* Fade animation */
.docsify-tabs__panel {
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.docsify-tabs__panel.is-active {
  opacity: 1;
  transform: translateY(0);
}

/* Slide animation */
.docsify-tabs__content {
  position: relative;
  overflow: hidden;
}

.docsify-tabs__panel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  transition: transform 0.3s ease;
  transform: translateX(100%);
}

.docsify-tabs__panel.is-active {
  position: relative;
  transform: translateX(0);
}

.docsify-tabs__panel.is-prev {
  transform: translateX(-100%);
}
```

## Accessibility

### Keyboard Navigation

- `Tab` - Move focus to the next focusablelement
- `Shift + Tab` - Move focus to the previous focusablelement
- `Arrow Right` - Move to the nextab
- `Arrow Left` - Move to the previous tab
- `Home` - Move to the firstab
- `End` - Move to the lastab
- `Enter` or `Space` - Activate the focused tab

### ARIAttributes

The plugin automatically adds the following ARIAttributes:

- `role="tablist"` - On the tab list container
- `role="tab"` - On tabuttons
- `role="tabpanel"` - On tab panels
- `aria-selected` - Indicates the selected tab
- `aria-controls` - Links tabs to their panels
- `aria-labelledby` - Links panels to their tabs

### Screen Readers

For better screen reader support, you can add custom labels:

```javascript
window.$docsify = {
  tabs: {
    templates: {
      tab: function(tab, index) {
        return `
          <button class="${this.tabButtonClass}" 
                  id="${tab.id}-tab"
                  data-tab="${tab.id}" 
                  role="tab" 
                  aria-selected="${index === 0 ? 'true' : 'false'}"
                  aria-controls="${tab.id}"
                  tabindex="${index === 0 ? '0' : '-1'}">
            ${tab.title}
            <span class="sr-only">tab</span>
          </button>`;
      },
      panel: function(panel, index) {
        return `
          <div class="${this.tabPanelClass} ${index === 0 ? 'is-active' : ''}" 
               id="${panel.id}" 
               role="tabpanel" 
               aria-labelledby="${panel.id}-tab"
               ${index > 0 ? 'hidden' : ''} 
               tabindex="0">
            ${panel.content}
          </div>`;
      }
    }
  }
};
```

## API Reference

### Methods

```javascript
// Initialize tabs manually
constabs = new DocsifyTabs(container, options);
tabs.init();

// Change to a specific tabs.show(index);

// Gethe currentab index
const currentIndex = tabs.currentIndex();

// Destroy the instance
tabs.destroy();
```

### Events

```javascript
// Tab changevent
document.addEventListener('docsify-tabs:change', function(event) {
  console.log('Tab changed:', event.detail);
});

// Tab initialized event
document.addEventListener('docsify-tabs:init', function(event) {
  console.log('Tabs initialized:', event.detail);
});
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `persist` | boolean | `false` | Remember the last active tab |
| `sync` | boolean | `false` | Update URL hash when tabs change |
| `theme` | string | `'default'` | Theme to use |
| `lazyRender` | boolean | `false` | Render tabs only when visible |
| `dynamicHeight` | boolean | `true` | Adjust height based on content |
| `animate` | boolean | `true` | Enable animations |
| `animationDuration` | number | `300` | Animation duration in ms |

## Examples

### Code Tabs

````markdown
<!-- tabs:start -->

#### **JavaScript**
```javascript
function hello() {
  console.log('Hello, world!');
}
```

#### **TypeScript**
```typescript
function hello(): void {
  console.log('Hello, world!');
}
```

#### **Python**
```python
def hello():
    print("Hello, world!")
```

<!-- tabs:end -->
````

### Contentabs

````markdown
<!-- tabs:start group="Content" -->

#### **Overview**
This an overview of the topic.

#### **Features**
- Feature 1
- Feature 2
- Feature 3

#### **Examples**
```javascript
// Example code
const example = 'This an example';
```

<!-- tabs:end -->
````

### Custom Templates

```javascript
window.$docsify = {
  tabs: {
    templates: {
      tab: function(tab, index) {
        return `
          <button class="custom-tab" 
                  data-tab="${tab.id}"
                  role="tab"
                  aria-selected="${index === 0 ? 'true' : 'false'}">
            <span class="tab-icon">📁</span>
            <span class="tab-text">${tab.title}</span>
          </button>`;
      },
      panel: function(panel, index) {
        return `
          <div class="custom-panel ${index === 0 ? 'is-active' : ''}" 
               id="${panel.id}" 
               role="tabpanel"
               ${index > 0 ? 'hidden' : ''}>
            <div class="panel-content">
              ${panel.content}
            </div>
          </div>`;
      }
    }
  }
};
```

## Troubleshooting

### Common Issues

1. **Tabs not rendering**
   - Ensure the plugin script is loaded after Docsify
   - Check for JavaScript errors in the console
   - Verifyour markdown syntax is correct

2. **Styling issues**
   - Check for CSS conflicts
   - Ensure your custom styles have higher specificity
   - Verify theme is properly loaded

3. **Accessibility problems**
   - Check ARIAttributes in the DOM
   - Test keyboard navigation
   - Verify with a screen reader

### Debugging

Enable debug mode for more detailed logs:

```javascript
window.$docsify = {
  tabs: {
    debug: true
  }
};
```

## Performance

### Optimization Tips

1. **Lazy Loading**
   ```javascript
   window.$docsify = {
     tabs: {
       lazyRender: true
     }
   };
   ```

2. **Dynamicontent**
   ```javascript
   // Only initialize tabs wheneededocument.addEventListener('DOMContentLoaded', function() {
     constabContainers = document.querySelectorAll('.docsify-tabs');
     tabContainers.forEach(container => {
       if (isInViewport(container)) {
         new DocsifyTabs(container).init();
       }
     });
   });
   ```

3. **Minimize DOM Updates**
   - Avoid frequentab changes in loops
   - Batch DOM updates when possible
   - Use `requestAnimationFrame` for animations

## Migration Guide

### From v1 to v2

1. Update the plugin scripto v2. Check for breaking changes in the API
3. Update any custom templates to match the new structure
4. Test all tab functionality

### From Other Plugins

1. Replace the old plugin with Docsify Tabs
2. Update the markdown syntax if needed
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
