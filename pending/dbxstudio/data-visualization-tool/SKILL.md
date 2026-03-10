---
name: data-visualization-tool
description: Chart and visualization generation for DBX Studio. Use when a user wants to visualize data — bar charts, line graphs, pie charts, scatter plots, etc.
---

# Data Visualization — DBX Studio

## Chart Types Available

The `generate_chart` tool supports these types:

| Type | Best For |
|------|----------|
| `bar` | Comparisons between categories |
| `line` | Trends over time |
| `pie` | Part-to-whole relationships (< 7 slices) |
| `scatter` | Correlation between two numeric values |
| `area` | Cumulative trends over time |
| `histogram` | Distribution of a numeric column |

## Workflow

1. Understand what the user wants to visualize
2. Write the SQL query to get the data (`data_query`)
3. Call `generate_chart` with the config
4. Confirm chart title and axes are meaningful

## generate_chart Parameters

```json
{
  "chart_type": "bar",
  "title": "Monthly Revenue by Product Category",
  "x_axis": "category",
  "y_axis": "revenue",
  "data_query": "SELECT category, SUM(amount) AS revenue FROM orders GROUP BY 1 ORDER BY 2 DESC",
  "group_by": "category"
}
```

## Chart Selection Guide

**User says "trend" or "over time"** → `line` chart, x_axis = date column
**User says "compare" or "by category"** → `bar` chart
**User says "breakdown" or "share"** → `pie` chart (only if ≤ 7 categories)
**User says "distribution" or "spread"** → `histogram`
**User says "relationship" or "correlation"** → `scatter`

## Data Query Patterns

### Bar: Top N categories
```sql
SELECT category, COUNT(*) AS count
FROM orders
GROUP BY category
ORDER BY count DESC
LIMIT 10
```

### Line: Time series
```sql
SELECT DATE_TRUNC('day', created_at) AS date, SUM(amount) AS revenue
FROM orders
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1
```

### Pie: Proportion breakdown
```sql
SELECT status, COUNT(*) AS count
FROM orders
GROUP BY status
```

## Design Principles
- Always give the chart a descriptive title including the time period if relevant
- Keep x_axis and y_axis names human-readable (not raw column names)
- For large result sets, aggregate before charting (avoid raw row-level data)
- Pie charts: max 7 slices, group remainder as "Other"
