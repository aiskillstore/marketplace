# Chart Examples

Complete examples for all chart types supported by python-pptx.

## Bar Chart (Column Clustered)

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Inches

# Prepare slide
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only
title = slide.shapes.title
title.text = "Quarterly Revenue Comparison"

# Define chart data
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('2024', (8.2, 9.1, 8.8, 10.5))
chart_data.add_series('2025', (9.5, 10.8, 11.2, 13.1))

# Add chart
x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart

# Format chart
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.include_in_layout = False

# Format value axis
value_axis = chart.value_axis
value_axis.has_major_gridlines = True
value_axis.maximum_scale = 15.0

# Format plot area
plot = chart.plots[0]
plot.has_data_labels = True
```

## Line Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Inches

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Website Traffic Trends"

chart_data = CategoryChartData()
chart_data.categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
chart_data.add_series('Website Traffic', (25000, 28000, 31000, 29000, 33000, 36000))
chart_data.add_series('Conversions', (1250, 1400, 1550, 1450, 1650, 1800))

x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.LINE, x, y, cx, cy, chart_data
).chart

chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.RIGHT

# Add markers to line
plot = chart.plots[0]
for series in plot.series:
    series.marker.style = 'circle'
    series.marker.size = 7
```

## Pie Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Inches

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Market Share by Region"

chart_data = CategoryChartData()
chart_data.categories = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
chart_data.add_series('Market Share', (38, 28, 25, 9))

x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.PIE, x, y, cx, cy, chart_data
).chart

chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.RIGHT
chart.plots[0].has_data_labels = True

# Format data labels
data_labels = chart.plots[0].data_labels
data_labels.show_percentage = True
data_labels.show_category_name = True
```

## Stacked Bar Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Product Sales Breakdown"

chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Product A', (12, 15, 14, 18))
chart_data.add_series('Product B', (8, 10, 11, 13))
chart_data.add_series('Product C', (5, 7, 6, 9))

x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_STACKED, x, y, cx, cy, chart_data
).chart

chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
```

## Area Chart

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Cumulative Growth"

chart_data = CategoryChartData()
chart_data.categories = ['2020', '2021', '2022', '2023', '2024', '2025']
chart_data.add_series('Revenue', (100, 125, 155, 190, 235, 290))

x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.AREA, x, y, cx, cy, chart_data
).chart

chart.has_legend = True
```

## Chart with Custom Colors

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
from pptx.dml.color import RGBColor

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Sales by Product Category"

chart_data = CategoryChartData()
chart_data.categories = ['Electronics', 'Clothing', 'Home', 'Sports']
chart_data.add_series('Sales', (45, 32, 28, 15))

x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart

# Apply custom colors to series
plot = chart.plots[0]
series = plot.series[0]

# Define custom colors for each category
colors = [
    RGBColor(0, 112, 192),   # Blue
    RGBColor(237, 125, 49),  # Orange
    RGBColor(165, 165, 165), # Gray
    RGBColor(255, 192, 0)    # Yellow
]

for idx, point in enumerate(series.points):
    fill = point.format.fill
    fill.solid()
    fill.fore_color.rgb = colors[idx]
```

## Multi-Series Line Chart with Formatting

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Performance Metrics"

chart_data = CategoryChartData()
chart_data.categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
chart_data.add_series('Revenue', (100, 110, 105, 120, 130, 145))
chart_data.add_series('Profit', (20, 25, 22, 28, 32, 38))
chart_data.add_series('Costs', (80, 85, 83, 92, 98, 107))

x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.LINE_MARKERS, x, y, cx, cy, chart_data
).chart

# Format chart
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.font.size = Pt(11)

# Format axes
value_axis = chart.value_axis
value_axis.has_major_gridlines = True
value_axis.major_gridlines.format.line.color.rgb = RGBColor(217, 217, 217)

category_axis = chart.category_axis
category_axis.tick_labels.font.size = Pt(10)
```

## Chart from pandas DataFrame

```python
import pandas as pd
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

# Load data
df = pd.read_csv('sales_data.csv')

slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Sales Data Analysis"

# Convert DataFrame to chart data
chart_data = CategoryChartData()
chart_data.categories = df['Month'].tolist()
chart_data.add_series('Sales', df['Amount'].tolist())

x, y, cx, cy = Inches(1), Inches(2), Inches(8), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart

chart.has_legend = False
chart.plots[0].has_data_labels = True
```
