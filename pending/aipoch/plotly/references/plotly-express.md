# Plotly Express - High-Level API

Plotly Express (px) is a high-level interface for creating data visualizations, designed to achieve plotting with minimal code (usually 1-5 lines).

## Installation

```bash
uv pip install plotly
```

## Key Advantages

- Concise syntax for common chart types
- Automatic color encoding and legend generation
- Seamless collaboration with pandas DataFrames
- Smart default settings for layout and styling
- Returns `graph_objects.Figure` objects for easy further customization

## Basic Usage Pattern

```python
import plotly.express as px
import pandas as pd

# Most functions follow this pattern
fig = px.chart_type(
    data_frame=df,
    x="column_x",
    y="column_y",
    color="category_column",  # Automatic coloring by category
    size="size_column",        # Map size by numerical value
    title="Chart Title"
)
fig.show()
```

## 40+ Chart Types

### Basic Charts
- `px.scatter()` - Scatter plots with optional trendlines
- `px.line()` - Line charts for time series
- `px.bar()` - Bar charts (vertical/horizontal)
- `px.area()` - Area charts
- `px.pie()` - Pie charts

### Statistical Charts
- `px.histogram()` - Histograms with automatic binning
- `px.box()` - Box plots for showing distributions
- `px.violin()` - Violin plots
- `px.strip()` - Strip plots
- `px.ecdf()` - Empirical Cumulative Distribution Function plots

### Maps
- `px.scatter_geo()` - Geographic scatter plots
- `px.choropleth()` - Choropleth maps
- `px.scatter_mapbox()` - Mapbox scatter plots
- `px.density_mapbox()` - Density heatmaps on maps

### Specialized Charts
- `px.sunburst()` - Hierarchical sunburst charts
- `px.treemap()` - Treemap visualizations
- `px.funnel()` - Funnel charts
- `px.parallel_coordinates()` - Parallel coordinates plots
- `px.scatter_matrix()` - Scatter plot matrix (SPLOM)
- `px.density_heatmap()` - 2D density heatmaps
- `px.density_contour()` - Density contour plots

### 3D Charts
- `px.scatter_3d()` - 3D scatter plots
- `px.line_3d()` - 3D line charts

## Common Parameters

All Plotly Express functions support these styling parameters:

```python
fig = px.scatter(
    df, x="x", y="y",
    # Dimensions
    width=800,
    height=600,

    # Labels
    title="Figure Title",
    labels={"x": "X Axis", "y": "Y Axis"},

    # Colors
    color="category",
    color_discrete_map={"A": "red", "B": "blue"},
    color_continuous_scale="Viridis",

    # Sorting
    category_orders={"category": ["A", "B", "C"]},

    # Themes
    template="plotly_dark"  # Or "simple_white", "seaborn", "ggplot2"
)
```

## Data Formats

Plotly Express supports:
- **Long-form data** (tidy data): Each row represents an observation
- **Wide-form data**: Multiple columns as separate traces

```python
# Long-form (Recommended)
df_long = pd.DataFrame({
    'fruit': ['apple', 'orange', 'apple', 'orange'],
    'contestant': ['A', 'A', 'B', 'B'],
    'count': [1, 3, 2, 4]
})
fig = px.bar(df_long, x='fruit', y='count', color='contestant')

# Wide-form
df_wide = pd.DataFrame({
    'fruit': ['apple', 'orange'],
    'A': [1, 3],
    'B': [2, 4]
})
fig = px.bar(df_wide, x='fruit', y=['A', 'B'])
```

## Trendlines

Add statistical trendlines to scatter plots:

```python
fig = px.scatter(
    df, x="x", y="y",
    trendline="ols",  # "ols", "lowess", "rolling", "ewm", "expanding"
    trendline_options=dict(log_x=True)  # Other options
)
```

## Faceting (Subplots)

Automatically create faceted plots:

```python
fig = px.scatter(
    df, x="x", y="y",
    facet_row="category_1",    # Separate by row
    facet_col="category_2",    # Separate by column
    facet_col_wrap=3           # Column wrap limit
)
```

## Animations

Create animated visualizations:

```python
fig = px.scatter(
    df, x="gdp", y="life_exp",
    animation_frame="year",     # Create animation frames based on this column
    animation_group="country",  # Group animation elements
    size="population",
    color="continent",
    hover_name="country"
)
```

## Hover Data

Customize hover tooltip information:

```python
fig = px.scatter(
    df, x="x", y="y",
    hover_data={
        "extra_col": True,      # Add column
        "x": ":.2f",            # Format existing data
        "hidden_col": False     # Hide column
    },
    hover_name="name_column"    # Bold title in hover box
)
```

## Further Customization

Plotly Express returns a `graph_objects.Figure` object, which can be deeply customized:

```python
fig = px.scatter(df, x="x", y="y")

# Use graph_objects methods
fig.update_layout(
    title="Custom Title",
    xaxis_title="X Axis",
    font=dict(size=14)
)

fig.update_traces(
    marker=dict(size=10, opacity=0.7)
)

fig.add_hline(y=0, line_dash="dash")
```

## When to use Plotly Express

Use Plotly Express when:
- Quickly creating standard chart types
- Working with pandas DataFrames
- Needing automatic color/size encoding
- Wanting reasonable default effects with minimal code

Use graph_objects when:
- Building custom chart types not included in px
- Needing fine-grained control over every element
- Creating complex figures with multiple traces
- Building specialized visualization components