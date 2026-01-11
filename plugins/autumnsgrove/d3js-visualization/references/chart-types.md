# Chart Types and Use Cases

## Line Charts

**Use for:** Time series, trends, continuous data

### Best Practices
- Use for showing change over time
- Good for 1-5 lines; more becomes cluttered
- Always include axis labels and legend
- Consider using area charts for cumulative data

### When to Avoid
- Discrete categories (use bar chart)
- Comparing many series (use small multiples)
- Part-to-whole relationships (use pie/treemap)

## Bar Charts

**Use for:** Comparisons, distributions, categorical data

### Variants
- **Vertical bars:** Standard comparisons
- **Horizontal bars:** Long category names, rankings
- **Grouped bars:** Comparing subcategories
- **Stacked bars:** Part-to-whole with categories
- **Normalized stacked:** Percentage composition

### Best Practices
- Always start axis at zero (or use break indicator)
- Sort bars logically (by value, alphabetically, or custom)
- Use consistent color scheme
- Limit to 10-15 categories

## Scatter Plots

**Use for:** Correlations, distributions, outliers, clustering

### Best Practices
- Use when showing relationship between two variables
- Color by third dimension or category
- Size by magnitude (bubble chart)
- Add trend line if correlation exists
- Use transparency for overlapping points

### Enhancements
- Add brush for selection
- Link to detail view
- Annotate outliers
- Include confidence intervals

## Pie/Donut Charts

**Use for:** Part-to-whole relationships (with caution)

### Best Practices
- Limit to 5-7 slices maximum
- Sort slices by size
- Start largest slice at 12 o'clock
- Use donut for displaying total in center
- Consider bar chart as alternative

### When to Avoid
- Comparing similar values (human eye poor at angle comparison)
- More than 7 categories
- Showing change over time

## Network Graphs

**Use for:** Relationships, hierarchies, connections

### Layouts
- **Force-directed:** General networks
- **Tree:** Hierarchical data
- **Sankey:** Flow and magnitude
- **Chord:** Relationships between entities

### Best Practices
- Limit nodes for readability (cluster if needed)
- Use color for node types
- Size nodes by importance/degree
- Weight edges by connection strength
- Add interactivity (hover, drag, click)

## Chart Selection Decision Tree

### Showing Change Over Time?
- Continuous data → Line chart
- Discrete periods → Bar chart
- Multiple metrics → Small multiples or area chart

### Comparing Categories?
- Few categories (<10) → Bar chart
- Many categories → Dot plot or horizontal bar
- Multiple groups → Grouped or small multiples
- Part-to-whole → Stacked bar or treemap

### Showing Relationships?
- Two variables → Scatter plot
- Three variables → Bubble chart (color/size)
- Network data → Force-directed graph
- Hierarchical → Tree diagram

### Showing Distribution?
- Single variable → Histogram
- Multiple groups → Box plot or violin plot
- Two variables → Heatmap or 2D histogram
