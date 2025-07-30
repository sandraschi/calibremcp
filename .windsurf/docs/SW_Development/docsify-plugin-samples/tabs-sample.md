# Docsify Tabs - Complete Guide

## Introduction

The Tabs plugin allows you torganize content into tabbed sections, making your documentation more organized and easier to navigate. This guide covers everything from basic usage to advanced customization.

## Basic Usage

### Installation

```html
<!-- Add this to your index.html -->
<script src="//cdn.jsdelivr.net/npm/docsify-tabs@1"></script>
```

### Basic Tabs

```markdown
<!-- tabs:start -->

#### **English**
Hello! Thisome content in English.

#### **French**
Bonjour! Voici du contenu en français.

#### **Spanish**
¡Hola! Estes un contenido en español.

<!-- tabs:end -->
```

<!-- tabs:start -->

#### **English**
Hello! Thisome content in English.

#### **French**
Bonjour! Voici du contenu en français.

#### **Spanish**
¡Hola! Estes un contenido en español.

<!-- tabs:end -->

## Tab Groups

Create multiple independentab groups on the same page:

```markdown
<!-- tabs:start group="languages" -->
#### **JavaScript**
```javascript
console.log('Hello from JavaScript!');
```
#### **Python**
```python
print("Hello from Python!")
```
<!-- tabs:end -->

<!-- tabs:start group="frameworks" -->
#### **React**
```jsx
function App() {
  return <h1>Hello React!</h1>;
}
```
#### **Vue**
```vue
<template>
  <h1>Hello Vue!</h1>
</template>
```
<!-- tabs:end -->
```

<!-- tabs:start group="languages" -->
#### **JavaScript**
```javascript
console.log('Hello from JavaScript!');
```
#### **Python**
```python
print("Hello from Python!")
```
<!-- tabs:end -->

<!-- tabs:start group="frameworks" -->
#### **React**
```jsx
function App() {
  return <h1>Hello React!</h1>;
}
```
#### **Vue**
```vue
<template>
  <h1>Hello Vue!</h1>
</template>
```
<!-- tabs:end -->

## Nested Tabs can be nested within other tabs:

```markdown
<!-- tabs:start -->

#### **Frontend**
Frontend content here.

<!-- tabs:start -->
#### **React**
React content
#### **Vue**
Vue content
#### **Angular**
Angular content
<!-- tabs:end -->

#### **Backend**
Backend content here.

<!-- tabs:start -->
#### **Node.js**
Node.js content
#### **Django**
Django content
#### **Flask**
Flask content
<!-- tabs:end -->

<!-- tabs:end -->
```

<!-- tabs:start -->

#### **Frontend**
Frontend content here.

<!-- tabs:start -->
#### **React**
React content
#### **Vue**
Vue content
#### **Angular**
Angular content
<!-- tabs:end -->

#### **Backend**
Backend content here.

<!-- tabs:start -->
#### **Node.js**
Node.js content
#### **Django**
Django content
#### **Flask**
Flask content
<!-- tabs:end -->

<!-- tabs:end -->

## Tab Attributes

Customize tabs with attributes:

```markdown
<!-- tabs:start -->

#### **Defaultab**
This tab will be active by default.

#### **Inactive Tab** {data-tab-active="false"}
This tab won't be active initially.

#### **Custom Name** {data-name="Custom Tab Name"}
This tab has a custom name.

#### **With Icon** {data-name=":rocket: Launch"}
This tab has an emojicon.

<!-- tabs:end -->
```

<!-- tabs:start -->

#### **Defaultab**
This tab will be active by default.

#### **Inactive Tab** {data-tab-active="false"}
This tab won't be active initially.

#### **Custom Name** {data-name="Custom Tab Name"}
This tab has a custom name.

#### **With Icon** {data-name=":rocket: Launch"}
This tab has an emojicon.

<!-- tabs:end -->

## Styling Tabs

Customize the appearance with CSS:

```css
:root {
  --docsifytabs-tab-highlight-color: #42b983;
  --docsifytabs-tab-background: #f8f8f8;
  --docsifytabs-tab-background-active: #fff;
  --docsifytabs-border-color: #e0e0e0;
  --docsifytabs-border-px: 2px;
  --docsifytabs-border-radius-px: 8px;
  --docsifytabs-margin: 1.5em 0;
}
```

## JavaScript API

Listen for tab changevents:

```javascript
document.addEventListener('docsify-tabs:change', function(e) {
  console.log('Tab changed to:', e.detail.tab);
  console.log('Tab group:', e.detail.group);
  console.log('Previous tab:', e.detail.previousTab);
});
```

## Advanced Usage

### Programmaticontrol

```javascript
// Switch to a specific tab (zero-based index)
document.dispatchEvent(new CustomEvent('docsify-tabs:switch', {
  detail: {
    index: 1, // Tab index to switch to
    group: 'languages' // Optional tab group name
  }
}));
```

### Custom Templates

```javascript
window.$docsify = {
  tabs: {
    template: function(tabs) {
      return [
        '<div class="custom-tabs">',
        '  <div class="custom-tabs-nav">',
        '    <div class="custom-tabs-nav-item" v-for="(tab, index) in tabs" :class="{ active: tab.active }" @click="select(index)">',
        '      {{ tab.title }}',
        '    </div>',
        '  </div>',
        '  <div class="custom-tabs-content">',
        '    <div class="custom-tabs-pane" v-for="(tab, index) in tabs" v-show="tab.active">',
        '      <div-html="tab.content"></div>',
        '    </div>',
        '  </div>',
        '</div>'
      ].join('\n');
    }
  }
};
```

## Best Practices

1. **Keep it simple**: Don't nestoo many levels deep
2. **Be consistent**: Use similar styling across all tabs
3. **Mobile-friendly**: Test on different screen sizes
4. **Performance**: Avoid heavy content in tabs that aren't immediately visible
5. **Accessibility**: Ensure proper contrast and keyboard navigation

## Troubleshooting

- **Tabs not rendering?** Make sure you've included the plugin script
- **Content not showing?** Check for JavaScript errors in the console
- **Styling issues?** Check for CSS conflicts with your theme

---

For more information, visithe [official docsify-tabs documentation](https://jhildenbiddle.github.io/docsify-tabs/).


{{ ... }}
Listen for tab changevents:

```javascript
document.addEventListener('docsify-tabs:change', function(e) {
  console.log('Tab changed to:', e.detail.tab);
  console.log('## Getting Started

### Basic Tabs

```markdown
<!-- tabs:start -->

#### **English**
Hello! Thisome content in English.

#### **French**
Bonjour! Voici du contenu en français.

#### **Spanish**
¡Hola! Estes un contenido en español.

<!-- tabs:end -->
```

### Nested Tabs

```markdown
<!-- tabs:start -->

#### **Tab 1**
Content for Tab 1.

#### **Tab 2**
Content for Tab 2 with nested tabs:

<!-- tabs:start -->

##### **Nested Tab A**
Nested content A.

##### **Nested Tab**
Nested content B.

<!-- tabs:end -->

#### **Tab 3**
Content for Tab 3.

<!-- tabs:end -->
```

## Complete Configuration Reference

### Global Configuration

```javascript
window.$docsify = {
  tabs: {
    // Basic Settings
    defaultTab: 0,           // Defaultab to display (0-based index or 'first'/'last')
    maxTabs: 5,              // Maximum number of tabs to display
    loadAllTabs: false,      // Load all tab content at once
    sync: true,              // Sync tabs withe same name across the page
    persist: false,          // Persisthe active tab across page loads
    
    // Styling
    theme: 'default',        // 'default' or 'material'
    tabHeadings: 'all',      // 'all' or 'active'
    
    // Animation: 200,          // Animation duration in milliseconds
    
    // Custom Classes
    tabContainerClass: 'docsify-tabs',
    tabNavigationClass: 'docsify-tabs__nav',
    tabItemClass: 'docsify-tabs__tab',
    tabActiveClass: 'docsify-tabs__tab--active',
    tabContentClass: 'docsify-tabs__content',
    
    // Callbacks
    onTabShow: function(tab) {
      // Called when a tab ishown
      console.log('Tab shown:', tab);
    },
    
    onTabHide: function(tab) {
      // Called when a tab is hidden
      console.log('Tab hidden:', tab);
    },
    
    // Advancedynamic: false,          // Enable dynamic tab loading
    updateHash: true,        // Update URL hash when switching tabs
    useStorage: true,        // Use localStorage to persistab state
    storageKey: 'docsify-tabs' // Key to use for localStorage
  }
};
```

### Per-Instance Configuration

```markdown
<!-- tabs:start { "maxTabs": 3, "theme": "material", "persist": true } -->

#### **Tab 1**
Content for Tab 1.

#### **Tab 2**
Content for Tab 2.

#### **Tab 3**
Content for Tab 3.

#### **Tab 4**
This tab won't be shown because maxTabs iseto 3.

<!-- tabs:end -->
```

## Advanced Usage

### Lazy Loading Content

Load content only when a tab is activated:

```markdown
<!-- tabs:start -->

#### **Tab 1**
This content loads immediately.

#### **Tab 2**
<!-- tabs:lazy -->
This content loads only when Tab 2 is activated.

#### **Tab 3**
<!-- tabs:lazy -->
This content loads only when Tab 3 is activated.

<!-- tabs:end -->
```

### Dynamic Tabs with JavaScript

```javascript
// Example: Add a new tab programmatically
function addTab(containerId, tabName, content) {
  const container = document.querySelector(`#${containerId} .docsify-tabs`);
  if (!container) return;
  
  // Create new tab
  constab = document.createElement('button');
  tab.className = 'docsify-tabs__tab';
  tab.textContent = tabName;
  
  // Create new content
  const contentDiv = document.createElement('div');
  contentDiv.className = 'docsify-tabs__content';
  contentDiv.innerHTML = content;
  
  // Add to container.querySelector('.docsify-tabs__nav').appendChild(tab);
  container.querySelector('.docsify-tabs__content').appendChild(contentDiv);
  
  // Reinitialize tabs
  if (window.DocsifyTabs) {
    window.DocsifyTabs.init(container);
  }
}
```

## Complete Stylinguide

### Defaultheme

```css
/* Tab Container */
.docsify-tabs {
  margin: 1.5em 0;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  overflow: hidden;
}

/* Tab Navigation */
.docsify-tabs__nav {
  display: flex;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;
  list-style: none;
  background: #f6f8fa;
  border-bottom: 1px solid #e1e4e8;
}

/* Tab Items */
.docsify-tabs__tab {
  padding: 0.5em 1em;
  margin: 0;
  border: none;
  border-right: 1px solid #e1e4e8;
  background: none;
  font: inherit;
  font-size: 0.9em;
  color: #24292e;
  cursor: pointer;
  transition: all 0.2s ease;
}

.docsify-tabs__tab:last-child {
  border-right: none;
}

.docsify-tabs__tab:hover {
  background: #eaecef;
}

.docsify-tabs__tab--active {
  background: white;
  color: #0366d6;
  font-weight: 600;
  border-bottom: 2px solid #0366d6;
  margin-bottom: -1px;
}

/* Tab Content */
.docsify-tabs__content {
  padding: 1.5em;
  background: white;
}

/* Nested Tabs */
.docsify-tabs .docsify-tabs {
  margin: 0;
  border: none;
  border-radius: 0;
}

.docsify-tabs .docsify-tabs__nav {
  background: #f0f2f5;
  border-bottom: 1px solid #d9dde2;
}

.docsify-tabs .docsify-tabs__tab {
  font-size: 0.85em;
  padding: 0.4em 0.8em;
  border-right: 1px solid #d9dde2;
}

/* Dark Theme */
[data-theme="dark"] .docsify-tabs {
  border-color: #444c56;
}

[data-theme="dark"] .docsify-tabs__nav {
  background: #2d333b;
  border-color: #444c56;
}

[data-theme="dark"] .docsify-tabs__tab {
  color: #adbac7;
  border-color: #444c56;
}

[data-theme="dark"] .docsify-tabs__tab:hover {
  background: #373e47;
}

[data-theme="dark"] .docsify-tabs__tab--active {
  background: #1e2228;
  color: #539bf5;
  border-color: #539bf5;
}

[data-theme="dark"] .docsify-tabs__content {
  background: #22272e;
  color: #adbac7;
}

/* Material Theme */
.docsify-tabs--material .docsify-tabs__nav {
  background: #f5f5f5;
  border-bottom: none;
  box-shadow: 0 2px rgba(0, 0, 0, 0.1);
}

.docsify-tabs--material .docsify-tabs__tab {
  position: relative;
  padding: 0 16px;
  height: 48px;
  line-height: 48px;
  text-transform: uppercase;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
  color: rgba(0, 0, 0, 0.6);
  border: none;
  transition: all 0.2s ease;
}

.docsify-tabs--material .docsify-tabs__tab--active {
  color: #1976d2;
  background: transparent;
  border-bottom: 2px solid #1976d2;
  margin-bottom: 0;
}

.docsify-tabs--material .docsify-tabs__tab:focus {
  outline: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .docsify-tabs__nav {
    flex-direction: column;
  }
  
  .docsify-tabs__tab {
    width: 100%;
    text-align: left;
    border-right: none;
    border-bottom: 1px solid #e1e4e8;
  }
  
  .docsify-tabs__tab--active {
    border-bottom: 2px solid #0366d6;
  }
}
```

## Performance Optimization

1. **Use Lazy Loading**
   - Only load content wheneeded with `<!-- tabs:lazy -->`
   - Especially useful for content with images or complex components

2. **Limitab Count**
   - Keep the number of tabs reasonable (3-5 recommended)
   - Use `maxTabs` to limithe number of visible tabs

3. **Optimize Content**
   - Minimize complex layouts inside tabs
   - Defer non-critical JavaScript and CSS
   - Use responsive images

4. **Usefficient Selectors**
   - Avoid complex CSSelectors for tab styles
   - Use class-based styling when possible

## Accessibility Features

### Keyboard Navigation
- `Tab`: Move focus to the next focusablelement
- `Shift + Tab`: Move focus to the previous focusablelement
- `Left/Right Arrow`: Navigate between tabs
- `Home`: Move to the firstab
- `End`: Move to the lastab
- `Enter/Space`: Activate the focused tab

### ARIAttributes
The plugin automatically adds the following ARIAttributes:
- `role="tablist"` on the tab list
- `role="tab"` on each tab
- `role="tabpanel"` on each content panel
- `aria-selected` to indicate the selected tab
- `aria-controls` to associate tabs witheir panels
- `aria-labelledby` to associate panels witheir tabs

### Screen Reader Support
- Tabs are announced as a tab list
- The selected state is announced when changing tabs
- The tab panel content is automatically focused when selected

## Browser Compatibility

The plugin is tested and works in:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- IE 11 (with polyfills)

## Migration Guide

### From v1 to v2
1. Update the plugin scripto the latest version
2. Check for breaking changes in the configuration options
3. Update any custom CSSelectors if needed
4. Test all tab functionality, especially keyboard navigation

## Troubleshooting

### Common Issues

#### Tabs Not Rendering
1. Verify the plugin script is included after Docsify
2. Check for JavaScript errors in the console
3. Ensure the HTML structure is correct

#### Content Not Showing
1. Check for syntax errors in your Markdown
2. Make sure all tabs are properly closed
3. Verify there are no JavaScript errors

#### Styling Issues
1. Check for CSS conflicts with your theme
2. Ensure your custom styles have sufficient specificity
3. Test in multiple browsers

### Debugging

Enable debug mode to get more detailed logs:

```javascript
window.$docsify = {
  debug: true,
  tabs: {
    debug: true
  }
};
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Report bugs and request features
2. Submit pull requests
3. Improve documentation
4. Test in different browsers

## License

MIT

---

For more information, visithe [docsify-tabs GitHub repository](https://github.com/jhildenbiddle/docsify-tabs).
