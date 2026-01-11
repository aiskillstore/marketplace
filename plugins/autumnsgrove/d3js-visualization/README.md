# D3.js Visualization Skill

A comprehensive D3.js visualization skill for creating professional, interactive data visualizations with support for custom charts, animations, and responsive design.

## Structure

```
d3js-visualization/
├── SKILL.md                      # Main skill documentation (33KB)
├── README.md                     # This file
├── scripts/
│   ├── chart-templates.js        # Reusable chart components (25KB)
│   └── data-helpers.js           # Data transformation utilities (18KB)
└── examples/
    ├── line-chart.html           # Interactive line chart example (14KB)
    ├── bar-chart.html            # Grouped/stacked bar chart (18KB)
    └── network-graph.html        # Force-directed network graph (15KB)
```

## What's Included

### SKILL.md
Comprehensive D3.js documentation covering:
- D3.js fundamentals (SVG, data binding, selections, scales, axes)
- Chart types and use cases (line, bar, scatter, pie, network graphs, etc.)
- Core D3 concepts (paths, shapes, layouts, force simulation)
- Detailed workflows (project setup, data loading, creating charts, adding interactivity)
- Best practices (chart selection, responsive design, performance, accessibility)
- Data transformation (aggregation, date/time handling, normalization)
- Advanced techniques (reusable charts, canvas rendering, WebGL)
- Common pitfalls and solutions
- Integration patterns (React, Vue, Angular, export functionality)

### scripts/chart-templates.js
Reusable chart functions following the reusable chart pattern:
- `lineChart()` - Customizable line chart with dots, animations, and callbacks
- `barChart()` - Bar chart with hover effects and transitions
- `scatterPlot()` - Scatter plot with size and color encoding
- `pieChart()` - Pie/donut chart with labels

Each chart template supports:
- Full customization via getter/setter methods
- Smooth animations and transitions
- Interactive callbacks (onHover, onClick)
- Responsive sizing

### scripts/data-helpers.js
Utility functions for data transformation:
- Data parsing and type conversion
- Statistical functions (mean, median, variance, etc.)
- Data aggregation and grouping
- Date/time utilities
- Data validation and cleaning
- Array manipulation helpers

### examples/line-chart.html
Complete interactive line chart example featuring:
- Time-series data visualization
- Zoom and pan functionality
- Interactive tooltips
- Hover line indicator
- Animated line drawing
- Responsive design
- Grid lines and styled axes

### examples/bar-chart.html
Comprehensive bar chart example with:
- Three visualization modes: grouped, stacked, normalized
- Interactive mode switching
- Animated transitions between modes
- Color-coded by region
- Legend with category labels
- Tooltips showing detailed data
- Responsive layout

### examples/network-graph.html
Force-directed network visualization featuring:
- Dynamic node layout with physics simulation
- Drag-and-drop node positioning
- Zoom and pan controls
- Interactive controls for simulation parameters
- Node highlighting on hover
- Connection visualization
- Group/community coloring
- Real-time statistics display
- Network regeneration

## Usage

### Using the Skill Documentation
Reference `SKILL.md` for comprehensive D3.js guidance, code examples, and best practices.

### Using Chart Templates
```html
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="scripts/chart-templates.js"></script>
<script>
  // Create and customize a line chart
  const chart = lineChart()
    .width(800)
    .height(400)
    .xValue(d => d.date)
    .yValue(d => d.value)
    .lineColor("steelblue")
    .showDots(true);

  // Render the chart
  d3.select("#chart")
    .datum(data)
    .call(chart);
</script>
```

### Using Data Helpers
```html
<script src="scripts/data-helpers.js"></script>
<script>
  // Parse CSV data
  const data = parseCSV(csvString, {
    date: d3.timeParse("%Y-%m-%d"),
    value: Number
  });

  // Calculate statistics
  const stats = calculateStats(data.map(d => d.value));
  console.log(stats); // { mean, median, min, max, ... }

  // Group data
  const grouped = groupBy(data, d => d.category);
</script>
```

### Viewing Examples
Open any HTML file in `examples/` directly in a web browser. No build step or server required - they use D3.js from CDN.

## Key Features

1. **Comprehensive Documentation**: 33KB of detailed D3.js guidance
2. **Production-Ready Templates**: Reusable chart components with full customization
3. **Working Examples**: Three complete, interactive visualizations
4. **Best Practices**: Performance optimization, accessibility, responsive design
5. **Modern D3.js**: Uses D3.js v7 patterns and conventions
6. **Zero Dependencies**: Examples work standalone with CDN
7. **Extensive Coverage**: Line charts, bar charts, scatter plots, pie charts, network graphs

## Chart Type Guide

**Line Charts** - Time series, trends, continuous data  
**Bar Charts** - Comparisons, distributions, categorical data  
**Scatter Plots** - Correlations, distributions, outliers  
**Pie/Donut Charts** - Part-to-whole relationships  
**Network Graphs** - Relationships, hierarchies, connections  

See SKILL.md for detailed guidance on when to use each chart type.

## Browser Support

All examples and templates work in modern browsers supporting:
- ES6+ JavaScript
- SVG
- D3.js v7

## Resources

- [D3.js Official Documentation](https://d3js.org/)
- [D3 Graph Gallery](https://d3-graph-gallery.com/)
- [Observable D3 Examples](https://observablehq.com/@d3)

## License

This skill is part of the ClaudeSkills collection. Use freely for learning and development.
