# Financial Report with Formulas Example

This example demonstrates creating a complete income statement with proper formatting, formulas, and financial calculations.

## Complete Implementation

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, numbers
from openpyxl.utils import get_column_letter

def create_financial_report():
    wb = Workbook()
    ws = wb.active
    ws.title = "Income Statement"

    # Title
    ws.merge_cells('A1:D1')
    ws['A1'] = "COMPANY NAME - Income Statement"
    ws['A1'].font = Font(size=14, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')

    # Period headers
    ws['A2'] = "Account"
    ws['B2'] = "Q1"
    ws['C2'] = "Q2"
    ws['D2'] = "Total"

    # Format headers
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    for cell in ws[2]:
        cell.font = header_font
        cell.fill = header_fill

    # Revenue section
    ws['A3'] = "Revenue"
    ws['A3'].font = Font(bold=True)

    revenue_items = [
        ["Product Sales", 50000, 55000],
        ["Service Revenue", 30000, 35000],
        ["Other Income", 5000, 7000]
    ]

    row = 4
    for item in revenue_items:
        ws[f'A{row}'] = item[0]
        ws[f'B{row}'] = item[1]
        ws[f'C{row}'] = item[2]
        ws[f'D{row}'] = f"=SUM(B{row}:C{row})"
        row += 1

    # Total Revenue
    ws[f'A{row}'] = "Total Revenue"
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'B{row}'] = f"=SUM(B4:B{row-1})"
    ws[f'C{row}'] = f"=SUM(C4:C{row-1})"
    ws[f'D{row}'] = f"=SUM(D4:D{row-1})"
    total_revenue_row = row
    row += 1

    # Expenses section
    ws[f'A{row}'] = "Expenses"
    ws[f'A{row}'].font = Font(bold=True)
    row += 1

    expense_items = [
        ["Salaries", 25000, 26000],
        ["Rent", 8000, 8000],
        ["Marketing", 5000, 7000],
        ["Utilities", 2000, 2200],
        ["Supplies", 3000, 3500]
    ]

    expense_start = row
    for item in expense_items:
        ws[f'A{row}'] = item[0]
        ws[f'B{row}'] = item[1]
        ws[f'C{row}'] = item[2]
        ws[f'D{row}'] = f"=SUM(B{row}:C{row})"
        row += 1

    # Total Expenses
    ws[f'A{row}'] = "Total Expenses"
    ws[f'A{row}'].font = Font(bold=True)
    ws[f'B{row}'] = f"=SUM(B{expense_start}:B{row-1})"
    ws[f'C{row}'] = f"=SUM(C{expense_start}:C{row-1})"
    ws[f'D{row}'] = f"=SUM(D{expense_start}:D{row-1})"
    total_expense_row = row
    row += 1

    # Net Income
    row += 1
    ws[f'A{row}'] = "Net Income"
    ws[f'A{row}'].font = Font(size=12, bold=True)
    ws[f'B{row}'] = f"=B{total_revenue_row}-B{total_expense_row}"
    ws[f'C{row}'] = f"=C{total_revenue_row}-C{total_expense_row}"
    ws[f'D{row}'] = f"=D{total_revenue_row}-D{total_expense_row}"

    # Format Net Income row
    net_income_fill = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")
    for col in ['A', 'B', 'C', 'D']:
        ws[f'{col}{row}'].fill = net_income_fill
        ws[f'{col}{row}'].font = Font(bold=True)

    # Apply currency format to all numeric cells
    for row_cells in ws[f'B3:D{row}']:
        for cell in row_cells:
            if cell.value and cell.value != "Account":
                cell.number_format = numbers.FORMAT_CURRENCY_USD_SIMPLE

    # Add borders
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for row in ws[f'A2:D{row}']:
        for cell in row:
            cell.border = thin_border

    # Adjust column widths
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15

    wb.save('financial_report.xlsx')
    print("Financial report created successfully!")

# Execute
create_financial_report()
```

## Key Features Demonstrated

1. **Merged Cells**: Title spanning multiple columns
2. **Section Headers**: Bold formatting for category headers
3. **Dynamic Formulas**: SUM formulas that adapt to row positions
4. **Currency Formatting**: Professional financial number display
5. **Conditional Styling**: Highlighted net income row
6. **Borders**: Professional table appearance
7. **Column Sizing**: Proper width for readability

## Usage Notes

Modify this template for different financial reports:
- Change revenue/expense categories
- Add more periods (Q3, Q4, Annual)
- Include additional calculated metrics (margins, ratios)
- Add charts for visualization
