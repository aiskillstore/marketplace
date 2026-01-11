# Dynamic Dashboard with Multiple Charts Example

This example demonstrates creating an executive dashboard with multiple chart types and summary statistics.

## Complete Implementation

```python
from openpyxl import Workbook
from openpyxl.chart import LineChart, BarChart, PieChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def create_dashboard():
    wb = Workbook()
    ws = wb.active
    ws.title = "Dashboard"

    # Title
    ws.merge_cells('A1:H1')
    ws['A1'] = "Sales Dashboard - 2024"
    ws['A1'].font = Font(size=18, bold=True, color="FFFFFF")
    ws['A1'].fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30

    # Data section
    ws['A3'] = "Month"
    ws['B3'] = "Sales"
    ws['C3'] = "Costs"
    ws['D3'] = "Profit"

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    sales = [45000, 52000, 48000, 61000, 58000, 65000]
    costs = [30000, 32000, 31000, 38000, 36000, 40000]

    for i, month in enumerate(months, start=4):
        ws[f'A{i}'] = month
        ws[f'B{i}'] = sales[i-4]
        ws[f'C{i}'] = costs[i-4]
        ws[f'D{i}'] = f"=B{i}-C{i}"

    # Summary statistics
    ws['F3'] = "Metric"
    ws['G3'] = "Value"

    metrics = [
        ["Total Sales", "=SUM(B4:B9)"],
        ["Total Costs", "=SUM(C4:C9)"],
        ["Total Profit", "=SUM(D4:D9)"],
        ["Avg Monthly Sales", "=AVERAGE(B4:B9)"],
        ["Profit Margin %", "=(G6/G4)*100"]
    ]

    for i, (metric, formula) in enumerate(metrics, start=4):
        ws[f'F{i}'] = metric
        ws[f'F{i}'].font = Font(bold=True)
        ws[f'G{i}'] = formula

    # Format header rows
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    for cell in ws[3]:
        if cell.value:
            cell.fill = header_fill
            cell.font = header_font

    # Chart 1: Line chart for Sales and Costs
    line_chart = LineChart()
    line_chart.title = "Sales vs Costs Trend"
    line_chart.y_axis.title = "Amount ($)"
    line_chart.x_axis.title = "Month"
    line_chart.height = 10
    line_chart.width = 20

    data = Reference(ws, min_col=2, min_row=3, max_col=3, max_row=9)
    categories = Reference(ws, min_col=1, min_row=4, max_row=9)

    line_chart.add_data(data, titles_from_data=True)
    line_chart.set_categories(categories)

    ws.add_chart(line_chart, "A11")

    # Chart 2: Bar chart for Profit
    bar_chart = BarChart()
    bar_chart.type = "col"
    bar_chart.title = "Monthly Profit"
    bar_chart.y_axis.title = "Profit ($)"
    bar_chart.x_axis.title = "Month"
    bar_chart.height = 10
    bar_chart.width = 20

    profit_data = Reference(ws, min_col=4, min_row=3, max_row=9)

    bar_chart.add_data(profit_data, titles_from_data=True)
    bar_chart.set_categories(categories)

    ws.add_chart(bar_chart, "K11")

    # Chart 3: Pie chart for Sales distribution
    pie_chart = PieChart()
    pie_chart.title = "Sales Distribution by Month"
    pie_chart.height = 10
    pie_chart.width = 12

    pie_data = Reference(ws, min_col=2, min_row=4, max_row=9)
    pie_categories = Reference(ws, min_col=1, min_row=4, max_row=9)

    pie_chart.add_data(pie_data)
    pie_chart.set_categories(pie_categories)

    ws.add_chart(pie_chart, "A27")

    # Adjust column widths
    for col in range(1, 8):
        ws.column_dimensions[get_column_letter(col)].width = 14

    wb.save('dashboard.xlsx')
    print("Dashboard created successfully!")

# Execute
create_dashboard()
```

## Key Features

1. **Professional Header**: Merged cell with branded styling
2. **Multiple Chart Types**: Line, bar, and pie charts
3. **Dynamic Metrics**: Formula-based KPI calculations
4. **Clean Layout**: Organized data and visualizations
5. **Auto-calculations**: Profit calculations using formulas

## Dashboard Components

### Data Section
- Monthly time series data
- Sales, costs, and calculated profit
- Clean table format with headers

### Summary Statistics
- Total sales, costs, and profit
- Average monthly performance
- Calculated profit margin percentage

### Visualizations
- **Line Chart**: Trend analysis for sales vs costs
- **Bar Chart**: Monthly profit comparison
- **Pie Chart**: Sales distribution across months

## Customization Options

### Adding More Metrics

```python
# Add more KPIs
additional_metrics = [
    ["Growth Rate %", "=((B9-B4)/B4)*100"],
    ["Cost Ratio %", "=(G5/G4)*100"],
    ["Best Month", "=INDEX(A4:A9,MATCH(MAX(D4:D9),D4:D9,0))"]
]

for i, (metric, formula) in enumerate(additional_metrics, start=len(metrics)+4):
    ws[f'F{i}'] = metric
    ws[f'F{i}'].font = Font(bold=True)
    ws[f'G{i}'] = formula
```

### Custom Chart Styling

```python
from openpyxl.chart.series import DataPoint

# Customize bar chart colors
bar_chart = BarChart()
# ... setup code ...

# Add custom colors
series = bar_chart.series[0]
series.graphicalProperties.solidFill = "4472C4"  # Blue bars
```

### Adding Sparklines

```python
# Add mini trend indicators
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties

# Create small inline charts for trends
mini_chart = LineChart()
mini_chart.height = 3
mini_chart.width = 5
mini_chart.legend = None

data = Reference(ws, min_col=2, min_row=4, max_row=9)
mini_chart.add_data(data)

ws.add_chart(mini_chart, "H4")
```

## Advanced Dashboard Features

### Conditional Formatting for KPIs

```python
from openpyxl.formatting.rule import CellIsRule

# Highlight positive profit in green
green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
positive_rule = CellIsRule(operator='greaterThan', formula=['0'], fill=green_fill)
ws.conditional_formatting.add('D4:D9', positive_rule)

# Highlight negative profit in red
red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
negative_rule = CellIsRule(operator='lessThan', formula=['0'], fill=red_fill)
ws.conditional_formatting.add('D4:D9', negative_rule)
```

### Data Refresh Instructions

```python
# Add refresh timestamp
from datetime import datetime

ws['I1'] = "Last Updated:"
ws['J1'] = datetime.now()
ws['J1'].number_format = 'yyyy-mm-dd hh:mm:ss'
```

## Best Practices for Dashboards

1. **Keep It Simple**: Focus on key metrics, avoid clutter
2. **Use Color Purposefully**: Consistent color scheme for brand alignment
3. **Logical Layout**: Group related information together
4. **Responsive Design**: Consider how dashboard looks at different zoom levels
5. **Clear Labels**: All charts and metrics should have descriptive titles
6. **Update Frequency**: Document when data should be refreshed

## Usage Tips

- Modify the data range to match your time period (weeks, quarters, years)
- Add more chart types (scatter, area, combo) as needed
- Include data validation for input cells
- Consider adding print area and page setup for reporting
- Use named ranges for easier formula management
