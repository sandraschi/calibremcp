# Docsify Chart Plugin - Complete Guide

## Introduction

The `docsify-chart` plugin enables you to create beautiful, interactive charts in your documentation using Chart.js. This guide covers everything from basic setup to advanced customization.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
  - [Line Chart](#line-chart)
  - [Bar Chart](#bar-chart)
  - [Pie Chart](#pie-chart)
  - [Doughnut Chart](#doughnut-chart)
  - [Radar Chart](#radar-chart)
  - [Polarea Chart](#polar-area-chart)
- [Configuration](#configuration)
  - [Global Configuration](#global-configuration)
  - [Per-Chart Configuration](#per-chart-configuration)
- [Advanced Features](#advanced-features)
  - [Multiple Datasets](#multiple-datasets)
  - [Custom Colors](#custom-colors)
  - [Responsive Charts](#responsive-charts)
  - [Animation Options](#animation-options)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Browser Support](#browser-support)
- [Migration Guide](#migration-guide)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Add the plugin scripto your `index.html`:

```html
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<!-- docsify-chart plugin -->
<script src="//cdn.jsdelivr.net/npm/docsify-chart@1"></script>
```

2. Configure the plugin (optional):

```javascript
window.$docsify = {
  // Other docsify options...
  chart: {
    // Global chart configuration
    theme: 'default', // 'default' or 'dark'
    responsive: true,
    maintainAspectRatio: true,
    // Default chart options: {
      // Chart.js options
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      },
      // ... other Chart.js options
    }
  }
};
```

## Basic Usage

### Line Chart

```markdown
<!-- chart line
    title "Monthly Active Users"
    x-axis Jan, Feb, Mar, Apr, May, Jun
    y-axis "Number of Users" 0 -->
1200, 1900, 3000, 5000, 2000, 3000
<!-- chart-end -->
```

### Bar Chart

```markdown
<!-- chart bar
    title "Quarterly Sales"
    x-axis Q1, Q2, Q3, Q4
    y-axis "Revenue (in $1000)" 0 -->
[4000, 3000, 2000, 5000]
<!-- chart-end -->
```

### Pie Chart

```markdown
<!-- chart pie
    title "Market Share"
    labels Chrome, Firefox, Safari, Edge, Other
    colors #4285F4, #FF9500, #34A853, #EA4335, #9E9E9E -->
[65, 15, 10, 5, 5]
<!-- chart-end -->
```

### Doughnut Chart

```markdown
<!-- chart doughnutitle "Traffic Sources"
    labels Direct, Social, Referral, Email
    colors #4CAF50, #2196F3, #F44336, #FFC107 -->
[300, 500, 200, 100]
<!-- chart-end -->
```

### Radar Chart

```markdown
<!-- chart radar
    title "Skill Assessment"
    labels "HTML", "CSS", "JavaScript", "React", "Node.js"
    y-axis "Proficiency" 0 100 -->
[90, 85, 80, 75, 70]
<!-- chart-end -->
```

### Polarea Chart

```markdown
<!-- chart polarArea
    title "Project Progress"
    labels "Design", "Development", "Testing", "Documentation"
    colors "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0" -->
[30, 50, 15, 5]
<!-- chart-end -->
```

## Configuration

### Global Configuration

Configure default settings for all charts:

```javascript
window.$docsify = {
  chart: {
    theme: 'dark', // 'default' or 'dark'
    responsive: true,
    maintainAspectRatio: true,
    options: {
      // Chart.js options
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      },
      scales: {
        y: {
          beginAtZero: true
        }
      },
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          enabled: true,
          mode: 'index',
          intersect: false
        }
      }
    }
  }
};
```

### Per-Chart Configuration

Override global settings for specificharts:

```markdown
<!-- chart line
    title "Custom Configuration"
    x-axis Jan, Feb, Mar
    y-axis "Values" 0
    options.animation.duration 2000
    options.scales.y.ticks.stepSize 10
    options.plugins.legend.position "bottom" -->
[10, 20, 30]
<!-- chart-end -->
```

## Advanced Features

### Multiple Datasets

```markdown
<!-- chart line
    title "Yearly Comparison"
    x-axis Jan, Feb, Mar, Apr, May, Jun
    y-axis "Sales" 0
    datasets "2022"
    datasets "2023"
    colors #FF6384, #36A2EB -->
[65, 59, 80, 81, 56, 55]
[28, 48, 40, 19, 86, 27]
<!-- chart-end -->
```

### Custom Colors

```markdown
<!-- chart bar
    title "Custom Colors"
    x-axis A, B, C, D
    y-axis "Values" 0
    background-colors rgba(75, 192, 192, 0.6)
    border-colors rgba(75, 192, 192, 1)
    border-width 2 -->
[10, 20, 30, 40]
<!-- chart-end -->
```

### Responsive Charts

```markdown
<!-- chart line
    title "Responsive Chart"
    x-axis Jan, Feb, Mar, Apr
    y-axis "Values" 0
    responsive true
    maintain-aspect-ratio false
    width 100%
    height 300px -->
[12, 19, 3, 5]
<!-- chart-end -->
```

### Animation Options

```markdown
<!-- chart line
    title "Custom Animation"
    x-axis Jan, Feb, Mar
    y-axis "Values" 0
    options.animation.duration 2000
    options.animation.easing "easeInOutQuart"
    options.animation.delay 500 -->
[10, 20, 30]
<!-- chart-end -->
```

## Best Practices

1. **Data Formatting**
   - Keep datarrays consistent in length
   - Use appropriate data types (numbers for values)
   - Format large numbers for bettereadability

2. **Accessibility**
   - Provide meaningful titles and labels
   - Ensure sufficient color contrast
   - Consider adding a datable alternative

3. **Performance**
   - Limithe number of data points for better performance
   - Use appropriate chartypes for your data
   - Disable animations for large datasets

4. **Responsive Design**
   - Test charts on different screen sizes
   - Adjust aspect ratio as needed
   - Consider mobile users when designing interactions

## Troubleshooting

### Common Issues

1. **Charts not rendering**
   - Ensure Chart.js is loaded before the docsify-chart plugin
   - Check for JavaScript errors in the console
   - Verify the chart syntax is correct

2. **Missing data**
   - Check that datarrays match thexpected format
   - Ensure all required parameters are provided
   - Verify that data values are valid numbers

3. **Styling issues**
   - Check for CSS conflicts
   - Verify that color values are in the correct format
   - Ensure the chart container has proper dimensions

### Debugging

Enable debug mode for more detailed error messages:

```javascript
window.$docsify = {
  chart: {
    debug: true
  }
};
```

## Browser Supporthe plugin supports all modern browsers that support Chart.js:

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
4. Test all charts for compatibility

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

For more information, visithe [docsify-chart GitHub repository](https://github.com/andrewda/docsify-chart).
