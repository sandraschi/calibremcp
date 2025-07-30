# Mermaid.js Integration - Complete Guide

## Introduction

Mermaid lets you create diagrams and visualizations using text and code. This guide shows how to use Mermaid with Docsify.

## Flowcharts

### Basic Flowchart

````markdown
```mermaid
flowchartD
    A[Start] --> B{Is it?}
    B -- Yes --> C[OK]
    C --> D[Rethink]
    D --> B -- No --> E[End]
```
````

```mermaid
flowchartD
    A[Start] --> B{Is it?}
    B -- Yes --> C[OK]
    C --> D[Rethink]
    D --> B -- No --> E[End]
```

### Flowchart with Subgraphs

````markdown
```mermaid
flowchartB
    subgraph One
    A[Process 1] --> B[Process 2]
    end
    
    subgraph Two
    C[Process 3] --> D[Process 4]
    end
    
    B --> C
```
````

```mermaid
flowchartB
    subgraph One
    A[Process 1] --> B[Process 2]
    end
    
    subgraph Two
    C[Process 3] --> D[Process 4]
    end
    
    B --> C
```

## Sequence Diagrams

### Basic Sequence

````markdown
```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail...
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
```
````

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail...
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
```

## Class Diagrams

### Basiclass Diagram

````markdown
```mermaid
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebranimal : +int age
    Animal : +Stringender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
    class Fish{
        -int sizeInFeet
        -canEat()
    }
    class Zebra{
        +bool is_wild
        +run()
    }
```
````

```mermaid
classDiagram
    Animal <|-- Duck
    Animal <|-- Fish
    Animal <|-- Zebranimal : +int age
    Animal : +Stringender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
    class Fish{
        -int sizeInFeet
        -canEat()
    }
    class Zebra{
        +bool is_wild
        +run()
    }
```

## Gantt Charts

### Projectimeline

````markdown
```mermaid
ganttitle Projectimeline
    dateFormat  YYYY-MM-DD
    section
    A task           :a1, 2023-01-01, 30d
    Another task     :after a1, 20d
    section Another
    Task in sec      :2023-01-12, 12d
    another task     : 24d
```
````

```mermaid
ganttitle Projectimeline
    dateFormat  YYYY-MM-DD
    section
    A task           :a1, 2023-01-01, 30d
    Another task     :after a1, 20d
    section Another
    Task in sec      :2023-01-12, 12d
    another task     : 24d
```

## Pie Charts

### Basic Pie Chart

````markdown
```mermaid
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```
````

```mermaid
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```

## Configuration

### Global Mermaid Configuration

```javascript
window.$docsify = {
  mermaid: {
    // Mermaid configuration options
    // See: https://mermaid-js.github.io/mermaid/#/Setup
    startOnLoad: true,
    theme: 'default',
    themeVariables: {
      primaryColor: '#f0f0f0',
      primaryTextColor: '#333',
      primaryBorderColor: '#7C0000',
      lineColor: '#F8B229',
      secondaryColor: '#006100',
      tertiaryColor: '#fff'
    },
    // Gantt configuration
    gantt: {
      titleTopMargin: 25,
      barHeight: 20,
      barGap: 4,
      topPadding: 50,
      leftPadding: 75,
      gridLineStartPadding: 35,
      fontSize: 11,
      fontFamily: '"Open-Sans", "sans-serif"',
      numberSectionStyles: 4,
      axisFormat: '%Y-%m-%d',
      // ...
    }
  }
};
```

## Advanced Features

### Using Themes

Mermaid supportseveral built-in themes:
- default
- forest
- dark
- neutral
- base

To set a theme:

```javascript
window.$docsify = {
  mermaid: {
    theme: 'dark'  // or 'default', 'forest', 'neutral', 'base'
  }
};
```

### Custom CSS

You can style Mermaidiagrams using CSS:

```css
/* Customize diagram colors */
.mermaid .label {
  color: #333;
}

/* Style flowchart nodes */
.mermaid .node rect,
.mermaid .node circle,
.mermaid .nodellipse,
.mermaid .node polygon {
  fill: #e0f7fa;
  stroke: #26c6da;
  stroke-width: 2px;
}

/* Style arrows */
.mermaid .arrowheadPath,
.mermaid .edgePath .path {
  stroke: #666;
  stroke-width: 1.5px;
}
```

## Best Practices

1. **Keep it Simple**
   - Break complex diagrams into smaller, focused ones
   - Use subgraphs torganize related elements

2. **Accessibility**
   - Addescriptive titles to all diagrams
   - Use sufficient color contrast
   - Consider adding alternative text descriptions

3. **Performance**
   - Avoid extremely large diagrams
   - Consider splitting very large sequence diagrams
   - Use the `data-config` attribute for complex configurations

## Troubleshooting

- **Diagrams not rendering?**
  - Check browser console for errors
  - Ensure Mermaid.js is properly loaded
  - Verifyour syntax is correct

- **Styling issues?**
  - Check for CSS conflicts
  - Verifyour theme settings
  - Ensure proper container sizing

---

For more information, visithe [Mermaid.js documentation](https://mermaid-js.github.io/mermaid/#/).
