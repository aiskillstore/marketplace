# Graph Objects - Low-level API

The `plotly.graph_objects` module provides fine-grained control over figure construction through Python classes that represent Plotly components.

## Core Classes

- **`go.Figure`** - The main figure container
- **`go.FigureWidget`** - Jupyter-compatible interactive widget
- **Trace types** - 40+ chart types (Scatter, Bar, Heatmap, etc.)
- **Layout components** - Axes, Annotations, Shapes, etc.

## Main Advantages

1. **Data validation** - Provides useful error messages for invalid attributes
2. **Built-in documentation** - Accessible via docstrings
3. **Flexible syntax** - Supports dictionary or attribute access
4. **Convenience methods** - `.add_trace()`, `.update_layout()`, etc.
5. **Magic underscore notation** - A compact way to access nested attributes
6. **Integrated I/O** - `.show()`, `.write_html()`, `.write_image()`

## Basic Figure Construction

### Creating an Empty Figure

```python
import plotly.graph_objects as go

fig = go.Figure()
```

### Adding Traces

```python
# Method 1: Adding traces one at a time
fig = go.Figure()
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name='Line 1'))
fig.add_trace(go.Scatter(x=[1, 2, 3], y=[2, 3, 4], name='Line 2'))

# Method 2: Passing data to the constructor
fig = go.Figure(data=[
    go.Scatter(x=[1, 2, 3], y=[4, 5, 6], name='Line 1'),
    go.Scatter(x=[1, 2, 3], y=[2, 3, 4], name='Line 2')
])
```

## Common Trace Types

### Scatter (Lines and Markers)

```python
fig.add_trace(go.Scatter(
    x=[1, 2, 3, 4],
    y=[10, 11, 12, 13],
    mode='lines+markers',  # 'lines', 'markers', 'lines+markers', 'text'
    name='Trace 1',
    line=dict(color='red', width=2, dash='dash'),
    marker=dict(size=10, color='blue', symbol='circle')
))
```

### Bar (Bar Charts)

```python
fig.add_trace(go.Bar(
    x=['A', 'B', 'C'],
    y=[1, 3, 2],
    name='Bar Chart',
    marker=dict(color='lightblue'),
    text=[1, 3, 2],
    textposition='auto'
))
```

### Heatmap

```python
fig.add_trace(go.Heatmap(
    z=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    x=['A', 'B', 'C'],
    y=['X', 'Y', 'Z'],
    colorscale='Viridis'
))
```

### 3D Scatter (3D Scatter Plots)

```python
fig.add_trace(go.Scatter3d(
    x=[1, 2, 3],
    y=[4, 5, 6],
    z=[7, 8, 9],
    mode='markers',
    marker=dict(size=5, color='red')
))
```

## Layout Configuration

### Updating the Layout

```python
fig.update_layout(
    title='Figure Title',
    title_font_size=20,
    xaxis_title='X Axis',
    yaxis_title='Y Axis',
    width=800,
    height=600,
    template='plotly_white',
    showlegend=True,
    hovermode='closest'  # 'x', 'y', 'closest', 'x unified', False
)
```

### Magic Underscore Notation

A compact way to set nested attributes:

```python
# Instead of this:
fig.update_layout(title=dict(text='Title', font=dict(size=20)))

# Use underscores:
fig.update_layout(
    title_text='Title',
    title_font_size=20
)
```

### Axis Configuration

```python
fig.update_xaxes(
    title='X Axis',
    range=[0, 10],
    showgrid=True,
    gridwidth=1,
    gridcolor='lightgray',
    type='log',  # 'linear', 'log', 'date', 'category'
    tickformat='.2f',
    dtick=1  # Tick spacing
)

fig.update_yaxes(
    title='Y Axis',
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor='black'
)
```

## Updating Traces

```python
# Update all traces
fig.update_traces(
    marker=dict(size=10, opacity=0.7)
)

# Update specific traces
fig.update_traces(
    marker=dict(color='red'),
    selector=dict(name='Line 1')
)

# Update by position
fig.data[0].marker.size = 15
```

## Adding Annotations

```python
fig.add_annotation(
    x=2, y=5,
    text='Important Point',
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor='red',
    ax=40,  # Arrow x offset
    ay=-40  # Arrow y offset
)
```

## Adding Shapes

```python
# Rectangle
fig.add_shape(
    type='rect',
    x0=1, y0=2, x1=3, y1=4,
    line=dict(color='red', width=2),
    fillcolor='lightblue',
    opacity=0.3
)

# Line
fig.add_shape(
    type='line',
    x0=0, y0=0, x1=5, y1=5,
    line=dict(color='green', width=2, dash='dash')
)

# Convenience methods for horizontal/vertical lines
fig.add_hline(y=5, line_dash='dash', line_color='red')
fig.add_vline(x=3, line_dash='dot', line_color='blue')
```

## Figure Structure

Figures follow a tree-like hierarchical structure:

```python
fig = go.Figure(data=[trace1, trace2], layout=go.Layout(...))

# Access via dictionary syntax
fig['layout']['title'] = 'New Title'
fig['data'][0]['marker']['color'] = 'red'

# Or access via attribute syntax
fig.layout.title = 'New Title'
fig.data[0].marker.color = 'red'
```

## Complex Chart Types

### Candlestick

```python
fig.add_trace(go.Candlestick(
    x=df['date'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name='Stock Price'
))
```

### Sankey Diagram

```python
fig = go.Figure(data=[go.Sankey(
    node=dict(
        label=['A', 'B', 'C', 'D'],
        color='blue'
    ),
    link=dict(
        source=[0, 1, 0, 2],
        target=[2, 3, 3, 3],
        value=[8, 4, 2, 8]
    )
)])
```

### 3D Surface

```python
fig = go.Figure(data=[go.Surface(
    z=z_data,  # 2D array
    x=x_data,
    y=y_data,
    colorscale='Viridis'
)])
```

## Using DataFrames

Building traces from pandas DataFrames:

```python
import pandas as pd

df = pd.DataFrame({
    'x': [1, 2, 3, 4],
    'y': [10, 11, 12, 13]
})

fig = go.Figure()
for group_name, group_df in df.groupby('category'):
    fig.add_trace(go.Scatter(
        x=group_df['x'],
        y=group_df['y'],
        name=group_name,
        mode='lines+markers'
    ))
```

## When to use Graph Objects

Use `graph_objects` when:
- Creating chart types not available in Plotly Express
- Building complex multi-trace charts from scratch
- Precise control over individual components is needed
- Creating specialized visualizations (3D meshes, isosurfaces, custom shapes)
- Building subplots with mixed chart types

Use Plotly Express when:
- Quickly creating standard charts
- Working with tidy DataFrame data
- Automatic generation of styling and legends is required