# Seaborn Function Reference Manual

This document provides a comprehensive reference for all major seaborn functions, organized by category.

## Relational Plots

### scatterplot()

**Purpose:** Create a scatter plot with points representing individual observations.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary of arrays
- `x, y` - Variables for the x and y axes
- `hue` - Grouping variable that will produce elements with different colors
- `size` - Grouping variable that will produce elements with different sizes
- `style` - Grouping variable that will produce elements with different styles
- `palette` - Palette name, list, or dict
- `hue_order` - Specified order for the appearance of the hue levels
- `hue_norm` - Normalization for numeric color encoding (tuple or Normalize object)
- `sizes` - Range of sizes for size encoding (tuple or dict)
- `size_order` - Specified order for the appearance of the size levels
- `size_norm` - Normalization for numeric size encoding
- `markers` - Marker styles (string, list, or dict)
- `style_order` - Specified order for the appearance of the style levels
- `legend` - How to draw the legend: "auto", "brief", "full", or False
- `ax` - Matplotlib Axes object to plot on

**Example:**
```python
sns.scatterplot(data=df, x='height', y='weight',
                hue='gender', size='age', style='smoker',
                palette='Set2', sizes=(20, 200))
```

### lineplot()

**Purpose:** Draw a line plot with automatic aggregation of repeated measurements and confidence intervals.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary of arrays
- `x, y` - Variables for the x and y axes
- `hue` - Grouping variable that will produce elements with different colors
- `size` - Grouping variable that will produce elements with different line widths
- `style` - Grouping variable that will produce elements with different line styles (dashes)
- `units` - Grouping variable identifying sampling units (no aggregation within units)
- `estimator` - Method for aggregating across multiple observations (default: mean)
- `errorbar` - Error bar method: "sd", "se", "pi", ("ci", level), ("pi", level), or None
- `n_boot` - Number of bootstrap iterations for computing confidence intervals
- `seed` - Random seed for reproducible bootstrapping
- `sort` - Whether to sort the data before plotting
- `err_style` - Error display style: "band" (shaded band) or "bars" (error bars)
- `err_kws` - Additional parameters for error display
- `markers` - Marker styles for emphasizing data points
- `dashes` - Dash styles for the lines
- `legend` - How to draw the legend
- `ax` - Matplotlib Axes object to plot on

**Example:**
```python
sns.lineplot(data=timeseries, x='time', y='signal',
             hue='condition', style='subject',
             errorbar=('ci', 95), markers=True)
```

### relplot()

**Purpose:** Figure-level interface for drawing relational plots (scatter or line) onto a FacetGrid.

**Key Parameters:**
Includes all parameters from `scatterplot()` and `lineplot()`, plus:
- `kind` - "scatter" or "line"
- `col` - Categorical variable for column faceting
- `row` - Categorical variable for row faceting
- `col_wrap` - Wrap the column variable at this width
- `col_order` - Order of column facets
- `row_order` - Order of row facets
- `height` - Height (in inches) of each facet
- `aspect` - Aspect ratio (width = height * aspect)
- `facet_kws` - Additional parameters passed to FacetGrid

**Example:**
```python
sns.relplot(data=df, x='time', y='measurement',
            hue='treatment', style='batch',
            col='cell_line', row='timepoint',
            kind='line', height=3, aspect=1.5)
```

## Distribution Plots

### histplot()

**Purpose:** Plot univariate or bivariate histograms with flexible binning.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary
- `x, y` - Variables (y is optional for bivariate plots)
- `hue` - Grouping variable
- `weights` - Variable for weighting observations
- `stat` - Aggregate statistic: "count", "frequency", "probability", "percent", "density"
- `bins` - Number of bins, bin edges, or method ("auto", "fd", "doane", "scott", "stone", "rice", "sturges", "sqrt")
- `binwidth` - Width of each bin (overrides bins)
- `binrange` - Range of bins (tuple)
- `discrete` - Treat x as a discrete variable (bars centered on values)
- `cumulative` - Compute a cumulative distribution
- `common_bins` - Use the same bins for all hue levels
- `common_norm` - Jointly normalize across hue levels
- `multiple` - Method for drawing multiple elements: "layer", "dodge", "stack", "fill"
- `element` - Visual element: "bars", "step", "poly"
- `fill` - Whether to fill the bars/elements
- `shrink` - Scale the width of bars (used for multiple="dodge")
- `kde` - Overlay a Kernel Density Estimate (KDE) curve
- `kde_kws` - Parameters for the KDE
- `line_kws` - Parameters for step/poly elements
- `thresh` - Minimum count threshold for bins
- `pthresh` - Minimum probability threshold
- `pmax` - Maximum probability for color scaling
- `log_scale` - Logarithmic scaling for axes (bool or base)
- `legend` - Whether to show the legend
- `ax` - Matplotlib Axes object

**Example:**
```python
sns.histplot(data=df, x='measurement', hue='condition',
             stat='density', bins=30, kde=True,
             multiple='layer', alpha=0.5)
```

### kdeplot()

**Purpose:** Plot univariate or bivariate kernel density estimates.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary
- `x, y` - Variables (y is optional for bivariate plots)
- `hue` - Grouping variable
- `weights` - Variable for weighting observations
- `palette` - Palette name or list
- `hue_order` - Order of hue levels
- `hue_norm` - Normalization for numeric color encoding
- `multiple` - Method for handling multiple elements: "layer", "stack", "fill"
- `common_norm` - Jointly normalize across hue levels
- `common_grid` - Use the same grid for all hue levels
- `cumulative` - Compute a cumulative distribution
- `bw_method` - Bandwidth method: "scott", "silverman", or a scalar
- `bw_adjust` - Bandwidth adjustment factor (higher values are smoother)
- `log_scale` - Logarithmic scaling for axes
- `levels` - Number or values of contour levels (bivariate)
- `thresh` - Minimum density threshold for contours
- `gridsize` - Grid resolution
- `cut` - Extension beyond data extremes (in bandwidth units)
- `clip` - Data range for the curve (tuple)
- `fill` - Whether to fill the area under the curve/contours
- `legend` - Whether to show the legend
- `ax` - Matplotlib Axes object

**Example:**
```python
# Univariate
sns.kdeplot(data=df, x='measurement', hue='condition',
            fill=True, common_norm=False, bw_adjust=1.5)

# Bivariate
sns.kdeplot(data=df, x='var1', y='var2',
            fill=True, levels=10, thresh=0.05)
```

### ecdfplot()

**Purpose:** Plot empirical cumulative distribution functions.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary
- `x, y` - Variables (specify one)
- `hue` - Grouping variable
- `weights` - Variable for weighting observations
- `stat` - "proportion" or "count"
- `complementary` - Plot the complementary CDF (1 - ECDF)
- `palette` - Palette name or list
- `hue_order` - Order of hue levels
- `hue_norm` - Normalization for numeric color encoding
- `log_scale` - Logarithmic scaling for axes
- `legend` - Whether to show the legend
- `ax` - Matplotlib Axes object

**Example:**
```python
sns.ecdfplot(data=df, x='response_time', hue='treatment',
             stat='proportion', complementary=False)
```

### rugplot()

**Purpose:** Plot marginal distributions by drawing ticks along the axes to show individual observations.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary
- `x, y` - Variables (specify one or both)
- `hue` - Grouping variable
- `height` - Height of the ticks (proportion of the axis)
- `expand_margins` - Add margin space for the rug plot
- `palette` - Palette name or list
- `hue_order` - Order of hue levels
- `hue_norm` - Normalization for numeric color encoding
- `legend` - Whether to show the legend
- `ax` - Matplotlib Axes object

**Example:**
```python
sns.rugplot(data=df, x='value', hue='category', height=0.05)
```

### displot()

**Purpose:** Figure-level interface for drawing distribution plots onto a FacetGrid.

**Key Parameters:**
Includes all parameters from `histplot()`, `kdeplot()`, and `ecdfplot()`, plus:
- `kind` - "hist", "kde", "ecdf"
- `rug` - Add a rug plot on the marginal axes
- `rug_kws` - Parameters for the rug plot
- `col` - Categorical variable for column faceting
- `row` - Categorical variable for row faceting
- `col_wrap` - Column wrap
- `col_order` - Order of column facets
- `row_order` - Order of row facets
- `height` - Height of each facet
- `aspect` - Aspect ratio
- `facet_kws` - Additional parameters passed to FacetGrid

**Example:**
```python
sns.displot(data=df, x='measurement', hue='treatment',
            col='timepoint', kind='kde', fill=True,
            height=3, aspect=1.5, rug=True)
```

### jointplot()

**Purpose:** Draw a plot of two variables with bivariate and univariate graphs.

**Key Parameters:**
- `data` - DataFrame
- `x, y` - Variables for the x and y axes
- `hue` - Grouping variable
- `kind` - "scatter", "kde", "hist", "hex", "reg", "resid"
- `height` - Figure size (square)
- `ratio` - Ratio of joint axes height to marginal axes height
- `space` - Space between the joint and marginal axes
- `dropna` - Drop missing values
- `xlim, ylim` - Axis limits (tuple)
- `marginal_ticks` - Show ticks on the marginal axes
- `joint_kws` - Parameters for the joint plot
- `marginal_kws` - Parameters for the marginal plots
- `hue_order` - Order of hue levels
- `palette` - Palette name or list

**Example:**
```python
sns.jointplot(data=df, x='var1', y='var2', hue='group',
              kind='scatter', height=6, ratio=4,
              joint_kws={'alpha': 0.5})
```

### pairplot()

**Purpose:** Plot pairwise relationships in a dataset.

**Key Parameters:**
- `data` - DataFrame
- `hue` - Grouping variable for color encoding
- `hue_order` - Order of hue levels
- `palette` - Palette name or list
- `vars` - Variables to plot (default: all numeric)
- `x_vars, y_vars` - Variables for x and y axes (for asymmetric grids)
- `kind` - "scatter", "kde", "hist", "reg"
- `diag_kind` - Type of plot for the diagonal: "auto", "hist", "kde", None
- `markers` - Marker styles
- `height` - Height of each facet
- `aspect` - Aspect ratio
- `corner` - Only plot the lower triangle
- `dropna` - Drop missing values
- `plot_kws` - Parameters for the off-diagonal plots
- `diag_kws` - Parameters for the diagonal plots
- `grid_kws` - Parameters for PairGrid

**Example:**
```python
sns.pairplot(data=df, hue='species', palette='Set2',
             vars=['sepal_length', 'sepal_width', 'petal_length'],
             corner=True, height=2.5)
```

## Categorical Plots

### stripplot()

**Purpose:** Draw a categorical scatterplot with jittered points.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary
- `x, y` - Variables (one categorical, one continuous)
- `hue` - Grouping variable
- `order` - Order of the categorical levels
- `hue_order` - Order of the hue levels
- `jitter` - Amount of jitter: True, float, or False
- `dodge` - Separate different hue levels along the categorical axis
- `orient` - "v" (vertical) or "h" (horizontal)
- `color` - Single color for all elements
- `palette` - Palette name or list
- `size` - Marker size
- `edgecolor` - Marker edge color
- `linewidth` - Marker edge width
- `native_scale` - Use numeric scale for the categorical axis
- `formatter` - Formatter for the categorical axis
- `legend` - Whether to show the legend
- `ax` - Matplotlib Axes object

**Example:**
```python
sns.stripplot(data=df, x='day', y='total_bill',
              hue='sex', dodge=True, jitter=0.2)
```

### swarmplot()

**Purpose:** Draw a categorical scatterplot with non-overlapping points.

**Key Parameters:**
Same as `stripplot()`, except:
- No `jitter` parameter
- `size` - Marker size (crucial for avoiding overlap)
- `warn_thresh` - Threshold for warning when points are too many (default: 0.05)

**Note:** Computationally expensive for large datasets. `stripplot` is recommended for more than 1000 points.

**Example:**
```python
sns.swarmplot(data=df, x='day', y='total_bill',
              hue='time', dodge=True, size=5)
```

### boxplot()

**Purpose:** Draw a box plot to show quartiles and outliers.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary
- `x, y` - Variables (one categorical, one continuous)
- `hue` - Grouping variable
- `order` - Order of the categorical levels
- `hue_order` - Order of the hue levels
- `orient` - "v" or "h"
- `color` - Single color for the boxes
- `palette` - Palette name or list
- `saturation` - Color saturation
- `width` - Box width
- `dodge` - Separate different hue levels along the categorical axis
- `fliersize` - Size of the outlier markers
- `linewidth` - Width of the box lines
- `whis` - Proportion of the IQR past the quartiles to extend whiskers (default: 1.5)
- `notch` - Draw a notched box plot
- `showcaps` - Show the bars at the ends of the whiskers
- `showmeans` - Show the means
- `meanprops` - Properties of the mean markers
- `boxprops` - Properties of the box
- `whiskerprops` - Properties of the whiskers
- `capprops` - Properties of the caps
- `flierprops` - Properties of the fliers
- `medianprops` - Properties of the median lines
- `native_scale` - Use numeric scale
- `formatter` - Categorical axis formatter
- `legend` - Whether to show the legend
- `ax` - Matplotlib Axes object

**Example:**
```python
sns.boxplot(data=df, x='day', y='total_bill',
            hue='smoker', palette='Set3',
            showmeans=True, notch=True)
```

### violinplot()

**Purpose:** Draw a combination of boxplot and kernel density estimate.

**Key Parameters:**
Same as `boxplot()`, plus:
- `bw_method` - KDE bandwidth method
- `bw_adjust` - KDE bandwidth adjustment factor
- `cut` - Extension of KDE beyond data extremes
- `density_norm` - Method used to normalize density: "area", "count", "width"
- `inner` - Representation of data in the violin interior: "box", "quartile", "point", "stick", None
- `split` - Split the violins to compare hue levels
- `scale` - Scaling method: "area", "count", "width"
- `scale_hue` - Whether to scale across hue levels
- `gridsize` - KDE grid resolution

**Example:**
```python
sns.violinplot(data=df, x='day', y='total_bill',
               hue='sex', split=True, inner='quartile',
               palette='muted')
```

### boxenplot()

**Purpose:** Draw an enhanced box plot for larger datasets, showing more quantiles.

**Key Parameters:**
Same as `boxplot()`, plus:
- `k_depth` - Method for depth calculation: "tukey", "proportion", "trustworthy", "full", or integer
- `outlier_prop` - Proportion of data to be considered outliers
- `trust_alpha` - Alpha value for confidence depth
- `showfliers` - Whether to show outlier points

**Example:**
```python
sns.boxenplot(data=df, x='day', y='total_bill',
              hue='time', palette='Set2')
```

### barplot()

**Purpose:** Show point estimates and errors as rectangular bars.

**Key Parameters:**
- `data` - DataFrame, array, or dictionary
- `x, y` - Variables (one categorical, one continuous)
- `hue` - Grouping variable
- `order` - Order of the categorical levels
- `hue_order` - Order of the hue levels
- `estimator` - Aggregation function (default: mean)
- `errorbar` - Error display: "sd", "se", "pi", ("ci", level), ("pi", level), or None
- `n_boot` - Number of bootstrap iterations
- `seed` - Random seed
- `units` - Identifier of sampling units
- `weights` - Observation weights
- `orient` - "v" or "h"
- `color` - Single color for bars
- `palette` - Palette name or list
- `saturation` - Color saturation
- `width` - Bar width
- `dodge` - Separate different hue levels along the categorical axis
- `errcolor` - Color for the error bars
- `errwidth` - Thickness of error bar lines
- `capsize` - Width of the "caps" on error bars
- `native_scale` - Use numeric scale
- `formatter` - Categorical axis formatter
- `legend` - Whether to show the legend
- `ax` - Matplotlib Axes object

**Example:**
```python
sns.barplot(data=df, x='day', y='total_bill',
            hue='sex', estimator='median',
            errorbar=('ci', 95), capsize=0.1)
```

### countplot()

**Purpose:** Show the counts of observations in each categorical bin.

**Key Parameters:**
Same as `barplot()`, but:
- Specify only one of x or y (categorical variable)
- No estimator or errorbar parameters (shows counts only)
- `stat` - "count" or "percent"

**Example:**
```python
sns.countplot(data=df, x='day', hue='time',
              palette='pastel', dodge=True)
```

### pointplot()

**Purpose:** Show point estimates and confidence intervals using scatter plot glyphs connected by lines.

**Key Parameters:**
Same as `barplot()`, plus:
- `markers` - Marker styles
- `linestyles` - Line styles
- `scale` - Scaling factor for the markers
- `join` - Whether to join the points with a line
- `capsize` - Width of the "caps" on error bars

**Example:**
```python
sns.pointplot(data=df, x='time', y='total_bill',
              hue='sex', markers=['o', 's'],
              linestyles=['-', '--'], capsize=0.1)
```

### catplot()

**Purpose:** Figure-level interface for drawing categorical plots onto a FacetGrid.

**Key Parameters:**
Includes all parameters for categorical plots, plus:
- `kind` - "strip", "swarm", "box", "violin", "boxen", "bar", "point", "count"
- `col` - Categorical variable for column faceting
- `row` - Categorical variable for row faceting
- `col_wrap` - Column wrap
- `col_order` - Order of column facets
- `row_order` - Order of row facets
- `height` - Height of each facet
- `aspect` - Aspect ratio
- `sharex, sharey` - Share axes across facets
- `legend` - Whether to show the legend
- `legend_out` - Place the legend outside the figure
- `facet_kws` - Additional parameters passed to FacetGrid

**Example:**
```python
sns.catplot(data=df, x='day', y='total_bill',
            hue='smoker', col='time',
            kind='violin', split=True,
            height=4, aspect=0.8)
```

## Regression Plots

### regplot()

**Purpose:** Plot data and a linear regression model fit.

**Key Parameters:**
- `data` - DataFrame
- `x, y` - Variables or data vectors
- `x_estimator` - Estimator to apply to each bin of the x variable
- `x_bins` - Bin the x variable into discrete bins
- `x_ci` - Confidence interval for the binned estimates
- `scatter` - Whether to draw the scatter plot
- `fit_reg` - Whether to fit and draw a regression line
- `ci` - Confidence interval for the regression estimate (int or None)
- `n_boot` - Number of bootstrap iterations for computing confidence intervals
- `units` - Identifier of sampling units
- `seed` - Random seed
- `order` - Polynomial regression order
- `logistic` - Fit a logistic regression
- `lowess` - Fit a LOWESS smoother
- `robust` - Fit a robust regression
- `logx` - Log-transform the x variable
- `x_partial, y_partial` - Partial out these variables before plotting
- `truncate` - Whether to truncate the regression line at the data limits
- `dropna` - Drop missing values
- `x_jitter, y_jitter` - Add jitter to the data
- `label` - Legend label
- `color` - Color for all elements
- `marker` - Marker style
- `scatter_kws` - Keyword arguments for the scatter plot
- `line_kws` - Keyword arguments for the regression line
- `ax` - Matplotlib Axes object

**Example:**
```python
sns.regplot(data=df, x='total_bill', y='tip',
            order=2, robust=True, ci=95,
            scatter_kws={'alpha': 0.5})
```

### lmplot()

**Purpose:** Figure-level interface for drawing regression plots onto a FacetGrid.

**Key Parameters:**
Includes all parameters from `regplot()`, plus:
- `hue` - Grouping variable
- `col` - Column faceting
- `row` - Row faceting
- `palette` - Palette name or list
- `col_wrap` - Column wrap
- `height` - Height of each facet
- `aspect` - Aspect ratio
- `markers` - Marker styles
- `sharex, sharey` - Share axes
- `hue_order` - Order of hue levels
- `col_order` - Order of column facets
- `row_order` - Order of row facets
- `legend` - Whether to show the legend
- `legend_out` - Place the legend outside
- `facet_kws` - Parameters for FacetGrid

**Example:**
```python
sns.lmplot(data=df, x='total_bill', y='tip',
           hue='smoker', col='time', row='sex',
           height=3, aspect=1.2, ci=None)
```

### residplot()

**Purpose:** Plot the residuals of a linear regression.

**Key Parameters:**
Same as `regplot()`, but:
- Always plots residuals (y - predicted) vs x
- Adds a horizontal line at y=0
- `lowess` - Fit a LOWESS smoother to the residuals

**Example:**
```python
sns.residplot(data=df, x='x', y='y', lowess=True,
              scatter_kws={'alpha': 0.5})
```

## Matrix Plots

### heatmap()

**Purpose:** Plot rectangular data as a color-encoded matrix.

**Key Parameters:**
- `data` - 2D array-like data
- `vmin, vmax` - Values to anchor the colormap
- `cmap` - Colormap name or object
- `center` - Value at which to center the colormap
- `robust` - Use robust quantiles to set the colormap range
- `annot` - Annotate cells: True, False, or array
- `fmt` - String formatting code for annotations (e.g., ".2f")
- `annot_kws` - Keyword arguments for annotations
- `linewidths` - Width of the lines that will divide each cell
- `linecolor` - Color of the lines that will divide each cell
- `cbar` - Whether to draw a colorbar
- `cbar_kws` - Keyword arguments for the colorbar
- `cbar_ax` - Axes in which to draw the colorbar
- `square` - Force the Axes aspect to be "equal" so each cell is square
- `xticklabels, yticklabels` - Tick labels (True, False, int, or list)
- `mask` - Boolean array to mask cells
- `ax` - Matplotlib Axes object

**Example:**
```python
# Correlation matrix
corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
            cmap='coolwarm', center=0, square=True,
            linewidths=1, cbar_kws={'shrink': 0.8})
```

### clustermap()

**Purpose:** Plot a matrix dataset as a hierarchically-clustered heatmap.

**Key Parameters:**
Includes all parameters from `heatmap()`, plus:
- `pivot_kws` - Keyword arguments for pivoting (if needed)
- `method` - Linkage method: "single", "complete", "average", "weighted", "centroid", "median", "ward"
- `metric` - Distance metric for clustering
- `standard_scale` - Standardize data: 0 (rows), 1 (cols), or None
- `z_score` - Z-score normalization: 0 (rows), 1 (cols), or None
- `row_cluster, col_cluster` - Whether to cluster rows/columns
- `row_linkage, col_linkage` - Precomputed linkage matrices
- `row_colors, col_colors` - Additional color annotations
- `dendrogram_ratio` - Proportion of the figure size to devote to the dendrogram
- `colors_ratio` - Proportion of the figure size to devote to the color annotations
- `cbar_pos` - Position of the colorbar (tuple: x, y, width, height)
- `tree_kws` - Keyword arguments for the dendrogram
- `figsize` - Figure size

**Example:**
```python
sns.clustermap(data, method='average', metric='euclidean',
               z_score=0, cmap='viridis',
               row_colors=row_colors, col_colors=col_colors,
               figsize=(12, 12), dendrogram_ratio=0.1)
```

## Multi-Plot Grids

### FacetGrid

**Purpose:** Multi-plot grid for plotting conditional relationships.

**Initialization:**
```python
g = sns.FacetGrid(data, row=None, col=None, hue=None,
                  col_wrap=None, sharex=True, sharey=True,
                  height=3, aspect=1, palette=None,
                  row_order=None, col_order=None, hue_order=None,
                  hue_kws=None, dropna=False, legend_out=True,
                  despine=True, margin_titles=False,
                  xlim=None, ylim=None, subplot_kws=None,
                  gridspec_kws=None)
```

**Methods:**
- `map(func, *args, **kwargs)` - Apply a plotting function to each facet
- `map_dataframe(func, *args, **kwargs)` - Apply a plotting function to the full DataFrame
- `set_axis_labels(x_var, y_var)` - Set axis labels
- `set_titles(template, **kwargs)` - Set titles for the subplots
- `set(kwargs)` - Set attributes on all axes
- `add_legend(legend_data, title, label_order, **kwargs)` - Add a legend
- `savefig(*args, **kwargs)` - Save the figure

**Example:**
```python
g = sns.FacetGrid(df, col='time', row='sex', hue='smoker',
                  height=3, aspect=1.5, margin_titles=True)
g.map(sns.scatterplot, 'total_bill', 'tip', alpha=0.7)
g.add_legend()
g.set_axis_labels('Total Bill ($)', 'Tip ($)')
g.set_titles('{col_name} | {row_name}')
```

### PairGrid

**Purpose:** Subplot grid for plotting pairwise relationships in a dataset.

**Initialization:**
```python
g = sns.PairGrid(data, hue=None, vars=None,
                 x_vars=None, y_vars=None,
                 hue_order=None, palette=None,
                 hue_kws=None, corner=False,
                 diag_sharey=True, height=2.5,
                 aspect=1, layout_pad=0.5,
                 despine=True, dropna=False)
```

**Methods:**
- `map(func, **kwargs)` - Apply a function to all subplots
- `map_diag(func, **kwargs)` - Apply a function to the diagonal
- `map_offdiag(func, **kwargs)` - Apply a function to the off-diagonal
- `map_upper(func, **kwargs)` - Apply a function to the upper triangle
- `map_lower(func, **kwargs)` - Apply a function to the lower triangle
- `add_legend(legend_data, **kwargs)` - Add a legend
- `savefig(*args, **kwargs)` - Save the figure

**Example:**
```python
g = sns.PairGrid(df, hue='species', vars=['a', 'b', 'c', 'd'],
                 corner=True, height=2.5)
g.map_upper(sns.scatterplot, alpha=0.5)
g.map_lower(sns.kdeplot)
g.map_diag(sns.histplot, kde=True)
g.add_legend()
```

### JointGrid

**Purpose:** Grid for drawing a bivariate plot with marginal univariate plots.

**Initialization:**
```python
g = sns.JointGrid(data=None, x=None, y=None, hue=None,
                  height=6, ratio=5, space=0.2,
                  dropna=False, xlim=None, ylim=None,
                  marginal_ticks=False, hue_order=None,
                  palette=None)
```

**Methods:**
- `plot(joint_func, marginal_func, **kwargs)` - Draw the joint and marginal plots together
- `plot_joint(func, **kwargs)` - Draw the joint distribution (center plot)
- `plot_marginals(func, **kwargs)` - Draw the marginal distributions
- `refline(x, y, **kwargs)` - Add reference lines
- `set_axis_labels(xlabel, ylabel, **kwargs)` - Set axis labels
- `savefig(*args, **kwargs)` - Save the figure

**Example:**
```python
g = sns.JointGrid(data=df, x='x', y='y', hue='group',
                  height=6, ratio=5, space=0.2)
g.plot_joint(sns.scatterplot, alpha=0.5)
g.plot_marginals(sns.histplot, kde=True)
g.set_axis_labels('Variable X', 'Variable Y')
```