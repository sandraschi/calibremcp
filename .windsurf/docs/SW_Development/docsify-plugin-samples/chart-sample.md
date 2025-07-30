# Docsify Chart Plugin - Complete Guide

## Introduction

The docsify-chart plugin allows you to create beautiful, interactive charts in your documentation using Chart.js.

## Basic Usage

### Line Chart

```markdown
<!-- chart line
    title "Monthly Users"
    x-axis Jan, Feb, Mar, Apr, May, Jun
    y-axis "Number of Users" 0 -->
100, 200, 300, 400, 500, 600
<!-- chart-end -->
```

<!-- chart line
    title "Monthly Users"
    x-axis Jan, Feb, Mar, Apr, May, Jun
    y-axis "Number of Users" 0 -->
100, 200, 300, 400, 500, 600
<!-- chart-end -->

### Bar Chart

```markdown
<!-- chart bar
    title "Quarterly Revenue"
    x-axis Q1, Q2, Q3, Q4
    y-axis "Revenue ($)" 0
    labels 2022,2023 -->
12000, 19000, 3000, 5000
25000, 10000, 2000, 8000
<!-- chart-end -->
```

<!-- chart bar
    title "Quarterly Revenue"
    x-axis Q1, Q2, Q3, Q4
    y-axis "Revenue ($)" 0
    labels 2022,2023 -->
12000, 19000, 3000, 5000
25000, 10000, 2000, 8000
<!-- chart-end -->

## Chartypes

### Pie Chart

```markdown
<!-- chart pie
    title "Market Share"
    labelsearch,Direct,Email,Social,Referral -->
300, 500, 100, 40, 120
<!-- chart-end -->
```

<!-- chart pie
    title "Market Share"
    labelsearch,Direct,Email,Social,Referral -->
300, 500, 100, 40, 120
<!-- chart-end -->

### Doughnut Chart

```markdown
<!-- chart doughnutitle "Traffic Sources"
    labels Mobile,Tablet,Desktop -->
300, 150, 600
<!-- chart-end -->
```

<!-- chart doughnutitle "Traffic Sources"
    labels Mobile,Tablet,Desktop -->
300, 150, 600
<!-- chart-end -->

## Advanced Features

### Multiple Datasets

```markdown
<!-- chart line
    title "Website Performance"
    x-axis Jan, Feb, Mar, Apr, May, Jun
    y-axis "Response Time (ms)" 0
    labels Desktop,Mobile
    colors #4285F4,#EA4335
    fill false,false -->
50, 60, 55, 45, 50, 48
70, 75, 72, 68, 65, 63
<!-- chart-end -->
```

<!-- chart line
    title "Website Performance"
    x-axis Jan, Feb, Mar, Apr, May, Jun
    y-axis "Response Time (ms)" 0
    labels Desktop,Mobile
    colors #4285F4,#EA4335
    fill false,false -->
50, 60, 55, 45, 50, 48
70, 75, 72, 68, 65, 63
<!-- chart-end -->

### Custom Styling

```markdown
<!-- chart bar
    title "Custom Styled Chart"
    x-axis A, B, C, D
    y-axis "Values" 0
    background-colors rgba(75, 192, 192, 0.2)
    border-colors rgba(75, 192, 192, 1)
    border-width 2
    border-radius 5
    border-skipped false
    bar-percentage 0.6
    category-percentage 0.8 -->
10, 20, 30, 40
<!-- chart-end -->
```

<!-- chart bar
    title "Custom Styled Chart"
    x-axis A, B, C, D
    y-axis "Values" 0
    background-colors rgba(75, 192, 192, 0.2)
    border-colors rgba(75, 192, 192, 1)
    border-width 2
    border-radius 5
    border-skipped false
    bar-percentage 0.6
    category-percentage 0.8 -->
10, 20, 30, 40
<!-- chart-end -->

## Configuration Options

### Global Configuration

```javascript
window.$docsify = {
  chart: {
    // Default chart options
    default: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
        },
        title: {
          display: true,
          padding: { top: 10, bottom: 30 }
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  }
};
```

### Per-Chart Options

```markdown
<!-- chart line
    title "Custom Options"
    x-axis Jan, Feb, Mar
    y-axis "Values" 0
    options {"plugins": {"legend": {"position": "top"}},"elements": {"line": {"tension": 0.5}}} -->
10, 20, 30
20, 30, 10
<!-- chart-end -->
```

<!-- chart line
    title "Custom Options"
    x-axis Jan, Feb, Mar
    y-axis "Values" 0
    options {"plugins": {"legend": {"position": "top"}},"elements": {"line": {"tension": 0.5}}} -->
10, 20, 30
20, 30, 10
<!-- chart-end -->

## Interactive Features

### Click Events

```javascript
document.addEventListener('chartjs:init', function(e) {
  const chart = e.detail.chart;
  chart.canvas.onclick = function(evt) {
    const points = chart.getElementsAtEventForMode(
      evt, 'nearest', { intersect: true }, true
    );
    
    if (points.length) {
      const firstPoint = points[0];
      const label = chart.data.labels[firstPoint.index];
      const value = chart.data.datasets[firstPoint.datasetIndex].data[firstPoint.index];
      
      console.log('Clicked:', { label, value });
    }
  };
});
```

## Best Practices

1. **Responsive Design**
   - Set `maintainAspectRatio: false` andefine a fixed height container
   ```html
   <div style="height: 300px;">
     <!-- chart will go here -->
   </div>
   ```

2. **Performance**
   - Limithe number of data points for better performance
   - Use simpler chartypes (e.g., line/bar) for large datasets

3. **Accessibility**
   - Provide meaningful titles and labels
   - Ensure sufficient color contrast
   - Consider adding a datable alternative

## Troubleshooting

- **Charts not rendering?**
  - Check browser console for errors
  - Ensure Chart.js is loaded before the plugin
  - Verify the chart syntax is correct

- **Styling issues?**
  - Check for CSS conflicts
  - Ensure proper container dimensions
  - Verify color formats (hex, rgb, rgba)

---

For more information, visithe [Chart.js documentation](https://www.chartjs.org/docs/latest/).
