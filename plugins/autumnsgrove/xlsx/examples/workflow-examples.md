# Essential Workflow Examples

This document contains the core workflow examples for common Excel operations.

## Workflow 1: Creating Charts

```python
from openpyxl import Workbook
from openpyxl.chart import LineChart, BarChart, PieChart, Reference

# Create workbook with sample data
wb = Workbook()
ws = wb.active
ws.title = "Sales Data"

# Add data
ws.append(["Month", "Product A", "Product B", "Product C"])
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
sales_a = [120, 135, 150, 140, 160, 175]
sales_b = [80, 90, 85, 95, 100, 110]
sales_c = [150, 145, 160, 155, 170, 180]

for i, month in enumerate(months):
    ws.append([month, sales_a[i], sales_b[i], sales_c[i]])

# Create Line Chart
line_chart = LineChart()
line_chart.title = "Monthly Sales Trend"
line_chart.style = 10
line_chart.y_axis.title = "Sales ($)"
line_chart.x_axis.title = "Month"

# Define data range
data = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=7)
categories = Reference(ws, min_col=1, min_row=2, max_row=7)

line_chart.add_data(data, titles_from_data=True)
line_chart.set_categories(categories)

# Add chart to worksheet
ws.add_chart(line_chart, "F2")

# Create Bar Chart on same sheet
bar_chart = BarChart()
bar_chart.type = "col"
bar_chart.title = "Sales Comparison"
bar_chart.y_axis.title = "Sales ($)"
bar_chart.x_axis.title = "Month"

bar_chart.add_data(data, titles_from_data=True)
bar_chart.set_categories(categories)

ws.add_chart(bar_chart, "F18")

# Create Pie Chart (last month data)
pie_chart = PieChart()
pie_chart.title = "June Sales Distribution"

# Use only June data (last row)
pie_data = Reference(ws, min_col=2, min_row=7, max_col=4, max_row=7)
pie_categories = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=1)

pie_chart.add_data(pie_data)
pie_chart.set_categories(pie_categories)

ws.add_chart(pie_chart, "N2")

wb.save("sales_charts.xlsx")
print("Charts created successfully!")
```

## Workflow 2: Applying Conditional Formatting

```python
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, IconSetRule

wb = Workbook()
ws = wb.active

# Add sample data
ws.append(["Product", "Sales", "Target", "Achievement %"])
products_data = [
    ["Product A", 1200, 1000, 120],
    ["Product B", 850, 1000, 85],
    ["Product C", 1500, 1200, 125],
    ["Product D", 950, 1000, 95],
    ["Product E", 800, 1000, 80],
]

for row in products_data:
    ws.append(row)

# Conditional Formatting 1: Color Scale (Sales column)
color_scale = ColorScaleRule(
    start_type='min',
    start_color='F8696B',  # Red for low values
    mid_type='percentile',
    mid_value=50,
    mid_color='FFEB84',    # Yellow for medium
    end_type='max',
    end_color='63BE7B'     # Green for high values
)
ws.conditional_formatting.add('B2:B6', color_scale)

# Conditional Formatting 2: Highlight cells above target (Achievement % > 100)
green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
above_target = CellIsRule(
    operator='greaterThan',
    formula=['100'],
    fill=green_fill
)
ws.conditional_formatting.add('D2:D6', above_target)

# Conditional Formatting 3: Highlight cells below 90% achievement
red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
below_target = CellIsRule(
    operator='lessThan',
    formula=['90'],
    fill=red_fill
)
ws.conditional_formatting.add('D2:D6', below_target)

# Conditional Formatting 4: Icon Sets
icon_set = IconSetRule('3Arrows', 'num', [0, 90, 100])
ws.conditional_formatting.add('D2:D6', icon_set)

wb.save('conditional_formatting.xlsx')
print("Conditional formatting applied!")
```

## Workflow 3: Data Validation

```python
from openpyxl import Workbook
from openpyxl.data_validation import DataValidation

wb = Workbook()
ws = wb.active

# Setup headers
ws.append(["Employee", "Department", "Status", "Rating", "Start Date"])

# Data Validation 1: Dropdown list for Department
dept_validation = DataValidation(
    type="list",
    formula1='"Sales,Marketing,Engineering,HR,Finance"',
    allow_blank=False
)
dept_validation.error = 'Please select a department from the list'
dept_validation.errorTitle = 'Invalid Department'
dept_validation.prompt = 'Select a department'
dept_validation.promptTitle = 'Department Selection'

ws.add_data_validation(dept_validation)
dept_validation.add('B2:B100')  # Apply to column B

# Data Validation 2: Dropdown list for Status
status_validation = DataValidation(
    type="list",
    formula1='"Active,On Leave,Terminated"',
    allow_blank=False
)
status_validation.error = 'Please select a valid status'
status_validation.errorTitle = 'Invalid Status'

ws.add_data_validation(status_validation)
status_validation.add('C2:C100')

# Data Validation 3: Numeric range for Rating (1-5)
rating_validation = DataValidation(
    type="whole",
    operator="between",
    formula1=1,
    formula2=5,
    allow_blank=True
)
rating_validation.error = 'Rating must be between 1 and 5'
rating_validation.errorTitle = 'Invalid Rating'
rating_validation.prompt = 'Enter a rating from 1 to 5'
rating_validation.promptTitle = 'Rating'

ws.add_data_validation(rating_validation)
rating_validation.add('D2:D100')

# Data Validation 4: Date validation (past dates only)
date_validation = DataValidation(
    type="date",
    operator="lessThanOrEqual",
    formula1="TODAY()",
    allow_blank=False
)
date_validation.error = 'Start date cannot be in the future'
date_validation.errorTitle = 'Invalid Date'

ws.add_data_validation(date_validation)
date_validation.add('E2:E100')

# Add sample data
ws.append(["John Doe", "Sales", "Active", 4, "2023-01-15"])
ws.append(["Jane Smith", "Engineering", "Active", 5, "2022-06-01"])

wb.save('data_validation.xlsx')
print("Data validation rules applied!")
```

## Workflow 4: Working with Multiple Worksheets

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

wb = Workbook()

# Remove default sheet
default_sheet = wb.active
wb.remove(default_sheet)

# Create multiple sheets
sheet_names = ["Q1 Sales", "Q2 Sales", "Q3 Sales", "Q4 Sales", "Annual Summary"]
for name in sheet_names:
    wb.create_sheet(title=name)

# Add data to each quarterly sheet
quarters = ["Q1 Sales", "Q2 Sales", "Q3 Sales", "Q4 Sales"]
quarter_data = [
    [15000, 12000, 18000],  # Q1
    [16000, 13000, 19000],  # Q2
    [15500, 12500, 18500],  # Q3
    [17000, 14000, 20000],  # Q4
]

for i, quarter in enumerate(quarters):
    ws = wb[quarter]

    # Headers
    ws.append(["Product", "Sales"])
    ws['A1'].font = Font(bold=True)
    ws['B1'].font = Font(bold=True)

    # Data
    products = ["Product A", "Product B", "Product C"]
    for j, product in enumerate(products):
        ws.append([product, quarter_data[i][j]])

# Create summary sheet with cross-sheet formulas
summary = wb["Annual Summary"]
summary.append(["Product", "Q1", "Q2", "Q3", "Q4", "Annual Total"])

# Format header
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(color="FFFFFF", bold=True)
for cell in summary[1]:
    cell.fill = header_fill
    cell.font = header_font

products = ["Product A", "Product B", "Product C"]
for i, product in enumerate(products, start=2):
    summary[f'A{i}'] = product

    # Cross-sheet formulas
    summary[f'B{i}'] = f"='Q1 Sales'!B{i}"
    summary[f'C{i}'] = f"='Q2 Sales'!B{i}"
    summary[f'D{i}'] = f"='Q3 Sales'!B{i}"
    summary[f'E{i}'] = f"='Q4 Sales'!B{i}"
    summary[f'F{i}'] = f"=SUM(B{i}:E{i})"

# Add grand total row
summary['A5'] = "Grand Total"
summary['A5'].font = Font(bold=True)
for col in ['B', 'C', 'D', 'E', 'F']:
    summary[f'{col}5'] = f"=SUM({col}2:{col}4)"
    summary[f'{col}5'].font = Font(bold=True)

# Adjust column widths
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for col in range(1, ws.max_column + 1):
        ws.column_dimensions[get_column_letter(col)].width = 15

wb.save('multi_sheet_workbook.xlsx')
print("Multi-sheet workbook created!")
```

## Key Takeaways

1. **Charts**: Use Reference objects to define data ranges and categories
2. **Conditional Formatting**: Apply rules for visual data analysis
3. **Data Validation**: Ensure data quality with dropdowns and constraints
4. **Multiple Sheets**: Use cross-sheet formulas for summary reports

For more detailed examples, see the other example files in this directory.
