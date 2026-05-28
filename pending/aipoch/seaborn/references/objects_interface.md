# Seaborn Objects Interface

The `seaborn.objects` interface provides a modern, declarative API for building visualizations through composition. This guide covers the complete objects interface introduced in seaborn version 0.12+.

## Core Concepts

The objects interface separates **what you want to show** (data and mappings) from **how to show it** (marks, stats, and moves). The steps for building a plot are:

1. Create a `Plot` object containing data and aesthetic mappings
2. Add layers via `.add()`, combining marks and statistical transformations
3. Customize using methods like `.scale()`, `.label()`, `.limit()`, `.theme()`, etc.
4. Render using `.show()` or `.save()`

## Basic Usage

```python
from seaborn import objects as so
import pandas as pd

# Create a plot with data and mappings
p = so.Plot(data=df, x='x_var', y='y_var')

# Add a mark (visual representation)
p = p.add(so.Dot())

# Show (will display automatically in Jupyter)
p.show()
```

## Plot Class

The `Plot` class is the foundation of the objects interface.

### Initialization

```python
so.Plot(data=None, x=None, y=None, color=None, alpha=None,
        fill=None, fillalpha=None, fillcolor=None, marker=None,
        pointsize=None, stroke=None, text=None, **variables)
```

**Parameters:**
- `data` - DataFrame or dictionary of data vectors
- `x, y` - Positional variables
- `color` - Color encoding variable
- `alpha` - Opacity variable
- `marker` - Marker shape variable
- `pointsize` - Point size variable
- `stroke` - Line width variable
- `text` - Text label variable
- `**variables` - Other mappings using property names

**Examples:**
```python
# Basic mapping
so.Plot(df, x='total_bill', y='tip')

# Multiple mappings
so.Plot(df, x='total_bill', y='tip', color='day', pointsize='size')

# All variables in Plot
p = so.Plot(df, x='x', y='y', color='cat')
p.add(so.Dot())  # Uses all mappings

# Variables defined in add()
p = so.Plot(df, x='x', y='y')
p.add(so.Dot(), color='cat')  # Only this layer uses color mapping
```

### Methods

#### add()

Adds a layer to the plot containing a mark and optional statistical transformations/moves.

```python
Plot.add(mark, *transforms, orient=None, legend=True, data=None,
         **variables)
```

**Parameters:**
- `mark` - Mark object defining the visual representation
- `*transforms` - Stat and/or Move objects for data transformation
- `orient` - Orientation, one of "x", "y", or "v"/"h"
- `legend` - Whether to include in the legend (True/False)
- `data` - Override data for this layer
- `**variables` - Override or add variable mappings

**Examples:**
```python
# Simple mark
p.add(so.Dot())

# Mark with statistical transformation
p.add(so.Line(), so.PolyFit(order=2))

# Mark with multiple transformations
p.add(so.Bar(), so.Agg(), so.Dodge())

# Layer-specific mapping
p.add(so.Dot(), color='category')
p.add(so.Line(), so.Agg(), color='category')

# Layer-specific data
p.add(so.Dot())
p.add(so.Line(), data=summary_df)
```

#### facet()

Create subplots based on categorical variables.

```python
Plot.facet(col=None, row=None, order=None, wrap=None)
```

**Parameters:**
- `col` - Variable for column faceting
- `row` - Variable for row faceting
- `order` - Dictionary containing facet order (keys are variable names)
- `wrap` - Wrap after this many columns

**Examples:**
```python
p.facet(col='time', row='sex')
p.facet(col='category', wrap=3)
p.facet(col='day', order={'day': ['Thur', 'Fri', 'Sat', 'Sun']})
```

#### pair()

Create pairwise subplots for multiple variables.

```python
Plot.pair(x=None, y=None, wrap=None, cross=True)
```

**Parameters:**
- `x` - Variables for x-axis pairing
- `y` - Variables for y-axis pairing (if None, uses x)
- `wrap` - Wrap after this many columns
- `cross` - Whether to include all x/y combinations (vs. only diagonal)

**Examples:**
```python
# Pairwise combinations of all variables
p = so.Plot(df).pair(x=['a', 'b', 'c'])
p.add(so.Dot())

# Rectangular grid
p = so.Plot(df).pair(x=['a', 'b'], y=['c', 'd'])
p.add(so.Dot(), alpha=0.5)
```

#### scale()

Customize how data is mapped to visual properties.

```python
Plot.scale(**scales)
```

**Parameters:** Arguments with property names as keys and Scale objects as values

**Examples:**
```python
p.scale(
    x=so.Continuous().tick(every=5),
    y=so.Continuous().label(like='{x:.1f}'),
    color=so.Nominal(['#1f77b4', '#ff7f0e', '#2ca02c']),
    pointsize=(5, 10)  # Shorthand for range
)
```

#### limit()

Set axis limits.

```python
Plot.limit(x=None, y=None)
```

**Parameters:**
- `x` - (min, max) tuple for x-axis
- `y` - (min, max) tuple for y-axis

**Examples:**
```python
p.limit(x=(0, 100), y=(0, 50))
```

#### label()

Set axis labels and titles.

```python
Plot.label(x=None, y=None, color=None, title=None, **labels)
```

**Parameters:** Arguments with property names as keys and label strings as values

**Examples:**
```python
p.label(
    x='Total Bill ($)',
    y='Tip Amount ($)',
    color='Day of Week',
    title='Restaurant Tips Analysis'
)
```

#### theme()

Apply matplotlib style settings.

```python
Plot.theme(config, **kwargs)
```

**Parameters:**
- `config` - rcParams dictionary or seaborn theme dictionary
- `**kwargs` - Individual rcParams parameters

**Examples:**
```python
# Seaborn theme
p.theme({**sns.axes_style('whitegrid'), **sns.plotting_context('talk')})

# Custom rcParams
p.theme({'axes.facecolor': 'white', 'axes.grid': True})

# Single parameter
p.theme(axes_facecolor='white', font_scale=1.2)
```

#### layout()

Configure subplot layout.

```python
Plot.layout(size=None, extent=None, engine=None)
```

**Parameters:**
- `size` - (width, height) in inches
- `extent` - (left, bottom, right, top) extent of subplots
- `engine` - "tight", "constrained", or None

**Examples:**
```python
p.layout(size=(10, 6), engine='constrained')
```

#### share()

Control axis sharing across facets.

```python
Plot.share(x=None, y=None)
```

**Parameters:**
- `x` - Share x-axis: True, False, or "col"/"row"
- `y` - Share y-axis: True, False, or "col"/"row"

**Examples:**
```python
p.share(x=True, y=False)  # All plots share x, y is independent
p.share(x='col')  # Share x only within columns
```

#### on()

Draw on an existing matplotlib figure or axes.

```python
Plot.on(target)
```

**Parameters:**
- `target` - matplotlib Figure or Axes object

**Examples:**
```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(10, 10))
so.Plot(df, x='x', y='y').add(so.Dot()).on(axes[0, 0])
so.Plot(df, x='x', y='z').add(so.Line()).on(axes[0, 1])
```

#### show()

Render and display the plot.

```python
Plot.show(**kwargs)
```

**Parameters:** Passed to `matplotlib.pyplot.show()`

#### save()

Save the plot to a file.

```python
Plot.save(filename, **kwargs)
```

**Parameters:**
- `filename` - Output filename
- `**kwargs` - Passed to `matplotlib.figure.Figure.savefig()`

**Examples:**
```python
p.save('plot.png', dpi=300, bbox_inches='tight')
p.save('plot.pdf')
```

## Mark Objects

Marks define the visual representation of data.

### Dot

Point/marker for individual observations.

```python
so.Dot(artist_kws=None, **kwargs)
```

**Properties:**
- `color` - Fill color
- `alpha` - Opacity
- `fillcolor` - Alternate color property
- `fillalpha` - Alternate opacity property
- `edgecolor` - Edge color
- `edgealpha` - Edge opacity
- `edgewidth` - Edge line width
- `marker` - Marker style
- `pointsize` - Marker size
- `stroke` - Edge width

**Examples:**
```python
so.Plot(df, x='x', y='y').add(so.Dot(color='blue', pointsize=10))
so.Plot(df, x='x', y='y', color='cat').add(so.Dot(alpha=0.5))
```

### Line

Line connecting observations.

```python
so.Line(artist_kws=None, **kwargs)
```

**Properties:**
- `color` - Line color
- `alpha` - Opacity
- `linewidth` - Line width
- `linestyle` - Line style ("-", "--", "-.", ":")
- `marker` - Marker at data points
- `pointsize` - Marker size
- `edgecolor` - Marker edge color
- `edgewidth` - Marker edge width

**Examples:**
```python
so.Plot(df, x='x', y='y').add(so.Line())
so.Plot(df, x='x', y='y', color='cat').add(so.Line(linewidth=2))
```

### Path

Similar to Line, but connects points in data order (not sorted by x).

```python
so.Path(artist_kws=None, **kwargs)
```

Properties are the same as `Line`.

**Examples:**
```python
# Used for trajectories, loops, etc.
so.Plot(trajectory_df, x='x', y='y').add(so.Path())
```

### Bar

Rectangular bar plot.

```python
so.Bar(artist_kws=None, **kwargs)
```

**Properties:**
- `color` - Fill color
- `alpha` - Opacity
- `edgecolor` - Edge color
- `edgealpha` - Edge opacity
- `edgewidth` - Edge line width
- `width` - Bar width (data units)

**Examples:**
```python
so.Plot(df, x='category', y='value').add(so.Bar())
so.Plot(df, x='x', y='y').add(so.Bar(color='#1f77b4', width=0.5))
```

### Bars

Multiple bar plot (for aggregated data with error bars).

```python
so.Bars(artist_kws=None, **kwargs)
```

Properties are the same as `Bar`. Usually used with `Agg()` or `Est()` stats.

**Examples:**
```python
so.Plot(df, x='category', y='value').add(so.Bars(), so.Agg())
```

### Area

Filled area between a line and a baseline.

```python
so.Area(artist_kws=None, **kwargs)
```

**Properties:**
- `color` - Fill color
- `alpha` - Opacity
- `edgecolor` - Edge color
- `edgealpha` - Edge opacity
- `edgewidth` - Edge line width
- `baseline` - Baseline value (default: 0)

**Examples:**
```python
so.Plot(df, x='x', y='y').add(so.Area(alpha=0.3))
so.Plot(df, x='x', y='y', color='cat').add(so.Area())
```

### Band

Filled band between two lines (for ranges/intervals).

```python
so.Band(artist_kws=None, **kwargs)
```

Properties are the same as `Area`. Requires `ymin` and `ymax` mappings, or use with `Est()` stat.

**Examples:**
```python
so.Plot(df, x='x', ymin='lower', ymax='upper').add(so.Band())
so.Plot(df, x='x', y='y').add(so.Band(), so.Est())
```

### Range

Line with markers at both ends (for showing ranges).

```python
so.Range(artist_kws=None, **kwargs)
```

**Properties:**
- `color` - Line and marker color
- `alpha` - Opacity
- `linewidth` - Line width
- `marker` - Marker style at endpoints
- `pointsize` - Marker size
- `edgewidth` - Marker edge width

**Examples:**
```python
so.Plot(df, x='x', y='y').add(so.Range(), so.Est())
```

### Dash

Short horizontal or vertical lines (for distribution markers).

```python
so.Dash(artist_kws=None, **kwargs)
```

**Properties:**
- `color` - Line color
- `alpha` - Opacity
- `linewidth` - Line width
- `width` - Dash length (data units)

**Examples:**
```python
so.Plot(df, x='category', y='value').add(so.Dash())
```

### Text

Text labels at data points.

```python
so.Text(artist_kws=None, **kwargs)
```

**Properties:**
- `color` - Text color
- `alpha` - Opacity
- `fontsize` - Font size
- `halign` - Horizontal alignment: "left", "center", "right"
- `valign` - Vertical alignment: "bottom", "center", "top"
- `offset` - (x, y) offset from the point

Requires `text` mapping.

**Examples:**
```python
so.Plot(df, x='x', y='y', text='label').add(so.Text())
so.Plot(df, x='x', y='y', text='value').add(so.Text(fontsize=10, offset=(0, 5)))
```

## Stat Objects

Stat objects transform data before rendering. Used in combination with marks in the `.add()` method.

### Agg

Aggregate observations by group.

```python
so.Agg(func='mean')
```

**Parameters:**
- `func` - Aggregation function: "mean", "median", "sum", "min", "max", "count", or callable

**Examples:**
```python
so.Plot(df, x='category', y='value').add(so.Bar(), so.Agg('mean'))
so.Plot(df, x='x', y='y', color='group').add(so.Line(), so.Agg('median'))
```

### Est

Estimate central tendency and error intervals.

```python
so.Est(func='mean', errorbar=('ci', 95), n_boot=1000, seed=None)
```

**Parameters:**
- `func` - Estimator: "mean", "median", "sum", or callable
- `errorbar` - Error representation:
  - `("ci", level)` - Confidence interval via bootstrap
  - `("pi", level)` - Percentile interval
  - `("se", scale)` - Standard error scaled by factor
  - `"sd"` - Standard deviation
- `n_boot` - Number of bootstrap iterations
- `seed` - Random seed

**Examples:**
```python
so.Plot(df, x='category', y='value').add(so.Bar(), so.Est())
so.Plot(df, x='x', y='y').add(so.Line(), so.Est(errorbar='sd'))
so.Plot(df, x='x', y='y').add(so.Line(), so.Est(errorbar=('ci', 95)))
so.Plot(df, x='x', y='y').add(so.Band(), so.Est())
```

### Hist

Bin observations and count or aggregate.

```python
so.Hist(stat='count', bins='auto', binwidth=None, binrange=None,
        common_norm=True, common_bins=True, cumulative=False)
```

**Parameters:**
- `stat` - Type of statistic: "count", "density", "probability", "percent", "frequency"
- `bins` - Number of bins, binning method, or boundaries
- `binwidth` - Width of bins
- `binrange` - (min, max) range for binning
- `common_norm` - Normalize across groups jointly
- `common_bins` - Use same bins for all groups
- `cumulative` - Cumulative histogram

**Examples:**
```python
so.Plot(df, x='value').add(so.Bars(), so.Hist())
so.Plot(df, x='value').add(so.Bars(), so.Hist(bins=20, stat='density'))
so.Plot(df, x='value', color='group').add(so.Area(), so.Hist(cumulative=True))
```

### KDE

Kernel Density Estimation.

```python
so.KDE(bw_method='scott', bw_adjust=1, gridsize=200,
       cut=3, cumulative=False)
```

**Parameters:**
- `bw_method` - Bandwidth method: "scott", "silverman", or scalar
- `bw_adjust` - Bandwidth multiplier
- `gridsize` - Resolution of the density curve
- `cut` - How far to extend beyond data range (in bandwidth units)
- `cumulative` - Cumulative density

**Examples:**
```python
so.Plot(df, x='value').add(so.Line(), so.KDE())
so.Plot(df, x='value', color='group').add(so.Area(alpha=0.5), so.KDE())
so.Plot(df, x='x', y='y').add(so.Line(), so.KDE(bw_adjust=0.5))
```

### Count

Count the number of observations in each group.

```python
so.Count()
```

**Examples:**
```python
so.Plot(df, x='category').add(so.Bar(), so.Count())
```

### PolyFit

Polynomial regression fit.

```python
so.PolyFit(order=1)
```

**Parameters:**
- `order` - Order of the polynomial (1 = linear, 2 = quadratic, etc.)

**Examples:**
```python
so.Plot(df, x='x', y='y').add(so.Dot())
so.Plot(df, x='x', y='y').add(so.Line(), so.PolyFit(order=2))
```

### Perc

Compute percentiles.

```python
so.Perc(k=5, method='linear')
```

**Parameters:**
- `k` - Number of percentile intervals
- `method` - Interpolation method

**Examples:**
```python
so.Plot(df, x='x', y='y').add(so.Band(), so.Perc())
```

## Move Objects

Move objects adjust positions to resolve overlap or create specific layouts.

### Dodge

Shift positions side-by-side.

```python
so.Dodge(empty='keep', gap=0)
```

**Parameters:**
- `empty` - How to handle empty groups: "keep", "drop", "fill"
- `gap` - Gap between dodged elements (proportion)

**Examples:**
```python
so.Plot(df, x='category', y='value', color='group').add(so.Bar(), so.Dodge())
so.Plot(df, x='cat', y='val', color='hue').add(so.Dot(), so.Dodge(gap=0.1))
```

### Stack

Stack marks vertically.

```python
so.Stack()
```

**Examples:**
```python
so.Plot(df, x='x', y='y', color='category').add(so.Bar(), so.Stack())
so.Plot(df, x='x', y='y', color='group').add(so.Area(), so.Stack())
```

### Jitter

Add random noise to positions.

```python
so.Jitter(width=None, height=None, seed=None)
```

**Parameters:**
- `width` - Jitter in x direction (data units or proportion)
- `height` - Jitter in y direction
- `seed` - Random seed

**Examples:**
```python
so.Plot(df, x='category', y='value').add(so.Dot(), so.Jitter())
so.Plot(df, x='cat', y='val').add(so.Dot(), so.Jitter(width=0.2))
```

### Shift

Shift positions by a constant.

```python
so.Shift(x=0, y=0)
```

**Parameters:**
- `x` - Offset in x direction (data units)
- `y` - Offset in y direction

**Examples:**
```python
so.Plot(df, x='x', y='y').add(so.Dot(), so.Shift(x=1))
```

### Norm

Normalize values.

```python
so.Norm(func='max', where=None, by=None, percent=False)
```

**Parameters:**
- `func` - Normalization method: "max", "sum", "area", or callable
- `where` - Which axis to apply to: "x", "y", or None
- `by` - Grouping variables for independent normalization
- `percent` - Show as percentages

**Examples:**
```python
so.Plot(df, x='x', y='y', color='group').add(so.Area(), so.Norm())
```

## Scale Objects

Scales control how data values are mapped to visual properties.

### Continuous

For numeric data.

```python
so.Continuous(values=None, norm=None, trans=None)
```

**Methods:**
- `.tick(at=None, every=None, between=None, minor=None)` - Configure ticks
- `.label(like=None, base=None, unit=None)` - Format labels

**Parameters:**
- `values` - Explicit value range (min, max)
- `norm` - Normalization function
- `trans` - Transformation: "log", "sqrt", "symlog", "logit", "pow10", or callable

**Examples:**
```python
p.scale(
    x=so.Continuous().tick(every=10),
    y=so.Continuous(trans='log').tick(at=[1, 10, 100]),
    color=so.Continuous(values=(0, 1)),
    pointsize=(5, 20)  # Shorthand for Continuous range
)
```

### Nominal

For categorical data.

```python
so.Nominal(values=None, order=None)
```

**Parameters:**
- `values` - Explicit values (e.g., colors, markers)
- `order` - Category order

**Examples:**
```python
p.scale(
    color=so.Nominal(['#1f77b4', '#ff7f0e', '#2ca02c']),
    marker=so.Nominal(['o', 's', '^']),
    x=so.Nominal(order=['Low', 'Medium', 'High'])
)
```

### Temporal

For datetime data.

```python
so.Temporal(values=None, trans=None)
```

**Methods:**
- `.tick(every=None, between=None)` - Configure ticks
- `.label(concise=False)` - Format labels

**Examples:**
```python
p.scale(x=so.Temporal().tick(every=('month', 1)).label(concise=True))
```

## Complete Examples

### Layered plot with statistical transformations

```python
(
    so.Plot(df, x='total_bill', y='tip', color='time')
    .add(so.Dot(), alpha=0.5)
    .add(so.Line(), so.PolyFit(order=2))
    .scale(color=so.Nominal(['#1f77b4', '#ff7f0e']))
    .label(x='Total Bill ($)', y='Tip ($)', title='Tips Analysis')
    .theme({**sns.axes_style('whitegrid')})
)
```

### Faceted distribution plot

```python
(
    so.Plot(df, x='measurement', color='treatment')
    .facet(col='timepoint', wrap=3)
    .add(so.Area(alpha=0.5), so.KDE())
    .add(so.Dot(), so.Jitter(width=0.1), y=0)
    .scale(x=so.Continuous().tick(every=5))
    .label(x='Measurement (units)', title='Treatment Effects Over Time')
    .share(x=True, y=False)
)
```

### Grouped bar plot

```python
(
    so.Plot(df, x='category', y='value', color='group')
    .add(so.Bar(), so.Agg('mean'), so.Dodge())
    .add(so.Range(), so.Est(errorbar='se'), so.Dodge())
    .scale(color=so.Nominal(order=['A', 'B', 'C']))
    .label(y='Mean Value', title='Comparison by Category and Group')
)
```

### Complex multi-layer plot

```python
(
    so.Plot(df, x='date', y='value')
    .add(so.Dot(color='gray', pointsize=3), alpha=0.3)
    .add(so.Line(color='blue', linewidth=2), so.Agg('mean'))
    .add(so.Band(color='blue', alpha=0.2), so.Est(errorbar=('ci', 95)))
    .facet(col='sensor', row='location')
    .scale(
        x=so.Temporal().label(concise=True),
        y=so.Continuous().tick(every=10)
    )
    .label(
        x='Date',
        y='Measurement',
        title='Sensor Measurements by Location'
    )
    .layout(size=(12, 8), engine='constrained')
)
```

## Migration from Functional Interface

### Scatter Plot

**Functional Interface:**
```python
sns.scatterplot(data=df, x='x', y='y', hue='category', size='value')
```

**Objects Interface:**
```python
so.Plot(df, x='x', y='y', color='category', pointsize='value').add(so.Dot())
```

### Line Plot with Confidence Interval

**Functional Interface:**
```python
sns.lineplot(data=df, x='time', y='measurement', hue='group', errorbar='ci')
```

**Objects Interface:**
```python
(
    so.Plot(df, x='time', y='measurement', color='group')
    .add(so.Line(), so.Est())
)
```

### Histogram

**Functional Interface:**
```python
sns.histplot(data=df, x='value', hue='category', stat='density', kde=True)
```

**Objects Interface:**
```python
(
    so.Plot(df, x='value', color='category')
    .add(so.Bars(), so.Hist(stat='density'))
    .add(so.Line(), so.KDE())
)
```

### Bar Plot with Error Bars

**Functional Interface:**
```python
sns.barplot(data=df, x='category', y='value', hue='group', errorbar='ci')
```

**Objects Interface:**
```python
(
    so.Plot(df, x='category', y='value', color='group')
    .add(so.Bar(), so.Agg(), so.Dodge())
    .add(so.Range(), so.Est(), so.Dodge())
)
```

## Tips and Best Practices

1. **Method chaining**: Each method returns a new Plot object, supporting fluent chaining.
2. **Layer composition**: Stack different marks by combining multiple `.add()` calls.
3. **Transformation order**: In `.add(mark, stat, move)`, the stat is applied first, then the move.
4. **Variable precedence**: Layer-specific mappings override Plot-level mappings.
5. **Scale shortcuts**: For simple ranges, use a tuple like `color=(min, max)` without a full Scale object.
6. **Jupyter rendering**: Plot objects render automatically when returned as a cell result; otherwise use `.show()`.
7. **Saving**: Use `.save()` instead of `plt.savefig()` for proper handling.
8. **Accessing Matplotlib**: Use `.on(ax)` to integrate into existing matplotlib figures.