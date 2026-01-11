# Excel Automation Best Practices

## Formula Management

### DO:
```python
# Use formulas for calculations
ws['D2'] = "=B2*C2"  # Quantity * Price
ws['E10'] = "=SUM(E2:E9)"  # Total

# Use named ranges for clarity
wb.define_name('TotalSales', f'{ws.title}!$E$10')
ws['G2'] = "=TotalSales*0.1"  # 10% commission
```

### DON'T:
```python
# Don't calculate in Python when Excel can do it
total = sum([cell.value for cell in ws['E2:E9']])  # Bad
ws['E10'] = total  # This won't update if source values change
```

## Performance Optimization

### DO:
```python
# For large datasets, write rows in bulk
data = [[f'Row {i}', i*100] for i in range(1000)]
for row_data in data:
    ws.append(row_data)

# Or use pandas for very large datasets
df = pd.DataFrame(data)
df.to_excel('large_file.xlsx', index=False)
```

### DON'T:
```python
# Don't read cell-by-cell in loops
for row in range(1, 10000):
    for col in range(1, 50):
        value = ws.cell(row, col).value  # Very slow!
```

## Memory Management

### DO:
```python
# Use read_only mode for reading large files
wb = load_workbook('large_file.xlsx', read_only=True)
for row in ws.rows:
    # Process row
    pass
wb.close()

# Use write_only mode for writing large files
wb = Workbook(write_only=True)
ws = wb.create_sheet()
for row_data in large_dataset:
    ws.append(row_data)
wb.save('output.xlsx')
```

### DON'T:
```python
# Don't load entire large files into memory
wb = load_workbook('huge_file.xlsx')  # May cause memory error
all_data = list(ws.values)  # Loads everything into RAM
```

## Preserving Existing Formatting

### DO:
```python
# Load workbook without data_only to preserve formulas
wb = load_workbook('report.xlsx')

# When copying styles, use copy()
from copy import copy
new_cell.font = copy(old_cell.font)
new_cell.fill = copy(old_cell.fill)
```

### DON'T:
```python
# Don't use data_only if you need to preserve formulas
wb = load_workbook('report.xlsx', data_only=True)
ws['A1'] = ws['A1'].value  # This will replace formula with value!
```

## Error Handling

### DO:
```python
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

try:
    wb = load_workbook('data.xlsx')
    ws = wb.active

    # Validate data exists
    if ws.max_row < 2:
        raise ValueError("File contains no data rows")

    # Process data
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is not None:  # Check for empty cells
            # Process row
            pass

    wb.save('data.xlsx')

except FileNotFoundError:
    print("Error: File not found")
except InvalidFileException:
    print("Error: Invalid Excel file format")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    if 'wb' in locals():
        wb.close()
```

## Date and Time Handling

### DO:
```python
from datetime import datetime
from openpyxl.styles import numbers

# Write date with proper format
ws['A1'] = datetime(2024, 1, 15)
ws['A1'].number_format = numbers.FORMAT_DATE_XLSX14  # mm-dd-yy

# Or use string format
ws['A1'].number_format = 'dd/mm/yyyy'

# Read dates correctly
wb = load_workbook('file.xlsx')
date_value = ws['A1'].value  # Returns datetime object
```

### DON'T:
```python
# Don't write dates as strings
ws['A1'] = "2024-01-15"  # This is text, not a date
```

## Column Width Auto-adjustment

### DO:
```python
from openpyxl.utils import get_column_letter

def auto_adjust_column_width(ws):
    """Auto-adjust column widths based on content."""
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)

        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        adjusted_width = min(max_length + 2, 50)  # Cap at 50
        ws.column_dimensions[column_letter].width = adjusted_width

# Usage
auto_adjust_column_width(ws)
```

## Common Pitfalls and Solutions

### Pitfall 1: Formula Reference Errors

**Problem:**
```python
# This creates broken formula when copied
ws['B2'] = "=A2*10"
ws['B3'] = "=A2*10"  # Still references A2, not A3!
```

**Solution:**
```python
# Let openpyxl handle relative references
for row in range(2, 10):
    ws[f'B{row}'] = f"=A{row}*10"  # Correct relative reference
```

### Pitfall 2: Lost Formulas When Using data_only

**Problem:**
```python
wb = load_workbook('file.xlsx', data_only=True)
ws['A1'] = ws['A1'].value  # Replaces formula with calculated value
wb.save('file.xlsx')  # Formulas are lost!
```

**Solution:**
```python
# Don't use data_only if you need to preserve formulas
wb = load_workbook('file.xlsx')  # Keep formulas intact

# Or, read values separately if needed
wb_data = load_workbook('file.xlsx', data_only=True)
value = wb_data['Sheet1']['A1'].value

wb_formula = load_workbook('file.xlsx')
formula = wb_formula['Sheet1']['A1'].value
```

### Pitfall 3: Chart Data Range Errors

**Problem:**
```python
# Wrong: Includes header in categories
categories = Reference(ws, min_col=1, min_row=1, max_row=10)
```

**Solution:**
```python
# Correct: Separate headers from data
data = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=10)
categories = Reference(ws, min_col=1, min_row=2, max_row=10)  # Start at row 2

chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)
```

### Pitfall 4: Date Format Issues

**Problem:**
```python
# Dates appear as numbers (e.g., 44927)
ws['A1'] = datetime(2024, 1, 15)
# Excel shows: 44927
```

**Solution:**
```python
from openpyxl.styles import numbers

ws['A1'] = datetime(2024, 1, 15)
ws['A1'].number_format = numbers.FORMAT_DATE_XLSX14
# Excel now shows: 01-15-24
```

### Pitfall 5: Memory Issues with Large Files

**Problem:**
```python
wb = load_workbook('huge_file.xlsx')  # Loads entire file into memory
data = list(ws.values)  # Memory error!
```

**Solution:**
```python
# Use read_only mode
wb = load_workbook('huge_file.xlsx', read_only=True)
for row in ws.iter_rows(values_only=True):
    # Process one row at a time
    pass
wb.close()
```

### Pitfall 6: Merged Cells Confusion

**Problem:**
```python
ws.merge_cells('A1:C1')
print(ws['B1'].value)  # Returns None!
print(ws['C1'].value)  # Returns None!
```

**Solution:**
```python
ws.merge_cells('A1:C1')
ws['A1'] = "Merged Title"  # Only set value in top-left cell
print(ws['A1'].value)  # Returns "Merged Title"

# To unmerge
ws.unmerge_cells('A1:C1')
```

## Summary

Key principles for Excel automation:
- Use formulas instead of Python calculations when possible
- Load files in read_only/write_only mode for large datasets
- Preserve formulas by not using data_only when editing
- Handle dates with proper number formatting
- Check for empty cells before processing
- Auto-adjust column widths for better presentation
- Use try/except blocks for robust error handling
