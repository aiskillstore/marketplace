# Data Import and Transformation Example

This example demonstrates transforming CSV data into formatted Excel reports with charts.

## Complete Implementation

```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.chart import LineChart, Reference
from openpyxl.utils import get_column_letter
from datetime import datetime

def transform_csv_to_excel():
    # Read CSV file
    df = pd.read_csv('sales_raw.csv')

    # Data cleaning and transformation
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.strftime('%B %Y')
    df['Revenue'] = df['Quantity'] * df['Price']

    # Create pivot table
    pivot = df.pivot_table(
        values='Revenue',
        index='Product',
        columns='Month',
        aggfunc='sum',
        fill_value=0
    )

    # Create Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Summary"

    # Write pivot table to Excel
    ws.append(['Product'] + list(pivot.columns))

    for product, row_data in pivot.iterrows():
        ws.append([product] + list(row_data))

    # Format headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font

    # Add totals column
    col_letter = get_column_letter(ws.max_column + 1)
    ws.cell(row=1, column=ws.max_column + 1, value="Total")
    ws[f'{col_letter}1'].fill = header_fill
    ws[f'{col_letter}1'].font = header_font

    for row in range(2, ws.max_row + 1):
        formula = f"=SUM(B{row}:{get_column_letter(ws.max_column - 1)}{row})"
        ws[f'{col_letter}{row}'] = formula

    # Add chart
    chart = LineChart()
    chart.title = "Monthly Revenue Trend"
    chart.y_axis.title = "Revenue ($)"
    chart.x_axis.title = "Month"

    data = Reference(ws, min_col=2, min_row=1, max_col=ws.max_column - 1, max_row=ws.max_row)
    categories = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)

    ws.add_chart(chart, f"A{ws.max_row + 3}")

    wb.save('sales_transformed.xlsx')
    print("CSV transformed and saved to Excel!")

# Example usage
# transform_csv_to_excel()
```

## Input CSV Format

```csv
Date,Product,Quantity,Price
2024-01-15,Product A,10,50.00
2024-01-20,Product B,5,80.00
2024-02-10,Product A,12,50.00
2024-02-15,Product B,8,80.00
```

## Output Features

1. **Pivot Table**: Automatically aggregates data by product and month
2. **Formatted Headers**: Professional blue header row
3. **Total Column**: Sum formulas for each product
4. **Line Chart**: Visual representation of trends
5. **Clean Layout**: Auto-formatted for presentation

## Customization Options

Modify the transformation for different needs:

```python
# Different aggregation
pivot = df.pivot_table(
    values='Revenue',
    index='Product',
    columns='Month',
    aggfunc='mean',  # Change to 'mean', 'count', 'max', etc.
    fill_value=0
)

# Multiple aggregations
pivot = df.pivot_table(
    values='Revenue',
    index='Product',
    columns='Month',
    aggfunc=['sum', 'mean', 'count']
)

# Different grouping
pivot = df.pivot_table(
    values='Revenue',
    index=['Product', 'Category'],  # Multi-level index
    columns='Quarter',
    aggfunc='sum'
)
```

## Advanced: Pandas Integration with openpyxl

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.chart import BarChart, Reference

# Step 1: Read and analyze data with pandas
df = pd.read_excel('sales_data.xlsx')

# Perform analysis
summary = df.groupby('Product').agg({
    'Sales': ['sum', 'mean', 'count'],
    'Profit': 'sum'
}).round(2)

summary.columns = ['Total Sales', 'Avg Sales', 'Transactions', 'Total Profit']
summary['Profit Margin %'] = ((summary['Total Profit'] / summary['Total Sales']) * 100).round(2)

# Calculate top performers
top_products = summary.nlargest(5, 'Total Sales')

# Step 2: Write results to new Excel file
with pd.ExcelWriter('sales_analysis.xlsx', engine='openpyxl') as writer:
    # Write multiple sheets
    df.to_excel(writer, sheet_name='Raw Data', index=False)
    summary.to_excel(writer, sheet_name='Summary')
    top_products.to_excel(writer, sheet_name='Top 5 Products')

# Step 3: Enhance with openpyxl formatting
wb = load_workbook('sales_analysis.xlsx')

# Format Summary sheet
ws = wb['Summary']
header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
header_font = Font(color="FFFFFF", bold=True)

for cell in ws[1]:
    cell.fill = header_fill
    cell.font = header_font

# Add chart to Summary sheet
chart = BarChart()
chart.title = "Total Sales by Product"
chart.y_axis.title = "Sales ($)"

data = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
categories = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)

ws.add_chart(chart, "H2")

wb.save('sales_analysis.xlsx')
print("Analysis complete! Results saved to sales_analysis.xlsx")
```

## Usage Tips

1. **Data Validation**: Always check for missing values and data types before transformation
2. **Memory Efficiency**: For very large CSV files, use pandas chunking:
   ```python
   chunks = pd.read_csv('large_file.csv', chunksize=10000)
   for chunk in chunks:
       # Process each chunk
       pass
   ```
3. **Date Handling**: Ensure dates are parsed correctly with `pd.to_datetime()`
4. **Export Options**: Use `index=False` to avoid writing DataFrame index as a column
