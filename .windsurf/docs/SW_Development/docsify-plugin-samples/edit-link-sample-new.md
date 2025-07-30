# Edit Link Plugin - Complete Guide

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Basiconfiguration](#basic-configuration)
  - [GitHub Repository](#github-repository)
  - [GitLab Repository](#gitlab-repository)
  - [Bitbucket Repository](#bitbucket-repository)
  - [Custom Repository](#custom-repository)
- [Advanced Configuration](#advanced-configuration)
  - [Customizing the Link](#customizing-the-link)
  - [Customizing the Position](#customizing-the-position)
  - [Conditional Display](#conditional-display)
  - [Custom Link Generator](#custom-link-generator)
- [Styling](#styling)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Browser Support](#browser-support)
- [Migration Guide](#migration-guide)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Thedit Link plugin adds an "Edithis page" link to your documentation, allowing users to quickly edithe current page'source file on GitHub, GitLab, Bitbucket, or other supported platforms. This particularly useful for open-source projects where you wanto encourage community contributions.

## Installation

1. Add the plugin scripto your `index.html` file, after the main Docsify script:

```html
<!-- Add this after the main docsify script -->
<script src="//cdn.jsdelivr.net/npm/docsify-edit-link"></script>
```

2. Configure the plugin your Docsify configuration:

```javascript
window.$docsify = {
  // Basiconfiguration (GitHub example)
  repo: 'username/repository',
  
  // OR use full URL
  // repo: 'https://github.com/username/repository',
  
  // Plugin configuration
  editLink: {
    // Options go here
  }
};
```

## Basiconfiguration

### GitHub Repository

```javascript
window.$docsify = {
  // Required: GitHub repository
  repo: 'username/repository',
  
  // Optional: Customize the link text
  editLinkText: 'Edithis page',
  
  // Optional: Customize the link title (tooltip)
  editLinkTitle: 'Edithis page on GitHub',
  
  // Optional: Customize the link target
  editLinkTarget: '_blank',
  
  // Optional: Show edit link only for specific paths
  editLinkShow: function(currentPath) {
    return !currentPath.includes('private/');
  }
};
```

### GitLab Repository

```javascript
window.$docsify = {
  // Required: GitLab repository URL
  repo: 'https://gitlab.com/username/repository',
  
  // Required: Specify the type of repository
  editLink: {
    type: 'gitlab'
  },
  
  // Optional: Customize the link text
  editLinkText: 'Edithis page on GitLab'
};
```

### Bitbucket Repository

```javascript
window.$docsify = {
  // Required: Bitbucket repository URL
  repo: 'https://bitbucket.org/username/repository',
  
  // Required: Specify the type of repository
  editLink: {
    type: 'bitbucket'
  },
  
  // Optional: Customize the link text
  editLinkText: 'Edithis page on Bitbucket'
};
```

### Custom Repository

```javascript
window.$docsify = {
  // Required: Custom repository URL
  repo: 'https://custom-git-host.com/username/repository',
  
  // Required: Custom link templateditLink: {
    type: 'custom',
    template: 'https://custom-git-host.com/username/repository/edit/branch/path/{file}',
    
    // Optional: Custom text for the link
    text: 'Edithis page',
    
    // Optional: Custom title for the link (tooltip)
    title: 'Edithis page on ourepository',
    
    // Optional: Custom CSS class for the link
    class: 'custom-edit-link',
    
    // Optional: Custom position ('top' or 'bottom')
    position: 'bottom',
    
    // Optional: Custom icon (HTML or Unicode)
    icon: '✏️',
    
    // Optional: Customize which fileshow thedit link
    show: function(currentPath) {
      // Return true to show the link, false to hide it
      return !currentPath.includes('private/');
    }
  }
};
```

## Advanced Configuration

### Customizing the Link

```javascript
window.$docsify = {
  repo: 'username/repository',
  
  editLink: {
    // Custom text for the link
    text: 'Help improve this page',
    
    // Custom title (tooltip)
    title: 'Edithis page on GitHub',
    
    // Custom CSS class: 'edit-button',
    
    // Custom icon (HTML or Unicode)
    icon: '✎',
    
    // Custom position ('top' or 'bottom')
    position: 'bottom',
    
    // Custom target attribute
    target: '_blank',
    
    // Custom rel attribute
    rel: 'noopener noreferrer',
    
    // Custom attributes (object)
    attributes: {
      'data-tracking': 'edit-link',
      'aria-label': 'Edithis page on GitHub'
    }
  }
};
```

### Customizing the Position

```javascript
window.$docsify = {
  repo: 'username/repository',
  
  editLink: {
    // Position can be 'top' or 'bottom' (default: 'bottom')
    position: 'top',
    
    // Or use a custom function to position the link
    position: function(content, currentPath) {
      // Return a DOM element where the link should be inserted
      // For example, insert after the first h1
      const h1 = content.querySelector('h1');
      return h1 ? h1.nextElementSibling : null;
    }
  }
};
```

### Conditional Display

```javascript
window.$docsify = {
  repo: 'username/repository',
  
  editLink: {
    // Show edit link only for specific pathshow: function(currentPath) {
      // Don't show for private files
      if (currentPath.includes('private/')) {
        return false;
      }
      
      // Only show for markdown files
      if (!currentPath.endsWith('.md')) {
        return false;
      }
      
      // Show for all other cases
      return true;
    }
  }
};
```

### Custom Link Generator

```javascript
window.$docsify = {
  repo: 'username/repository',
  
  editLink: {
    // Custom function to generate thedit link: function(repo, currentPath) {
      // repo: The repository URL
      // currentPath: The current file path (e.g., 'guide/configuration.md')
      
      // Example: Custom branch
      const branch = 'main';
      
      // Example: Custom file path transformation
      let filePath = currentPath;
      if (currentPath.startsWith('docs/')) {
        filePath = currentPath.replace('docs/', '');
      }
      
      // Return the full URL
      return `${repo}/edit/${branch}/${filePath}`;
    }
  }
};
```

## Styling

Customize the appearance of thedit link with CSS:

```css
/* Basic styling */
.docsify-edit-link {
  display: inline-block;
  font-size: 14px;
  color: #2196f3;
  text-decoration: none;
  margin: 0 20px 0;
  padding: 5px 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.docsify-edit-link:hover {
  background-color: #f5f5f5;
  text-decoration: none;
  color: #1976d2;
  border-color: #bdbdbd;
}

/* Icon styling */
.docsify-edit-link .icon {
  margin-right: 5px;
  font-size: 0.9em;
}

/* Position athe top of the content */
.docsify-edit-link--top {
  margin-bottom: 20px;
}

/* Position athe bottom of the content */
.docsify-edit-link--bottom {
  margin-top: 20px;
}

/* Dark theme support */
[data-theme="dark"] .docsify-edit-link {
  color: #64b5f6;
  border-color: #424242;
}

[data-theme="dark"] .docsify-edit-link:hover {
  background-color: #2d2d2d;
  color: #90caf9;
  border-color: #616161;
}
```

## Best Practices

1. **Repository Structure**
   - Keep your documentation in a dedicatedirectory (e.g., `docs/`)
   - Use consistent file naming conventions
   - Organize files in a logical folder structure

2. **Branch Management**
   - Consider using a dedicated branch for documentation (e.g., `gh-pages`)
   - Use pull requests for documentation changes
   - Protect your main branch

3. **Accessibility**
   - Ensure the link has proper ARIAttributes
   - Provide clear andescriptive link text
   - Maintain sufficient color contrast

4. **Performance**
   - Only load the plugin wheneeded
   - Minimize custom JavaScript
   - Usefficient selectors for custom positioning

5. **Security**
   - Be cautious with user-generated content
   - Validate all inputs in custom link generators
   - Use `rel="noopener noreferrer"` for externalinks

## Troubleshooting

### Common Issues

1. **Edit link not appearing**
   - Verify the repository URL is correct
   - Check for JavaScript errors in the console
   - Ensure the current pagexists in the repository

2. **Incorrect edit URL**
   - Verify the branch name in the URL
   - Check the file path transformation logic
   - Ensure the repository type is correctly specified

3. **Styling issues**
   - Check for CSS conflicts with your theme
   - Verify custom styles are being applied
   - Test in multiple browsers

### Debugging

Enable debug mode for more detailed error messages:

```javascript
window.$docsify = {
  repo: 'username/repository',
  
  editLink: {
    debug: true
  }
};
```

## Browser Supporthe plugin works in all modern browsers, including:

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
4. Testhedit link functionality

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

For more information, visithe [docsify-edit-link GitHub repository](https://github.com/njleonzhang/docsify-edit-link).
