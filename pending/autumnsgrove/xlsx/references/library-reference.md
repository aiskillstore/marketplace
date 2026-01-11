# Python Library Reference for Excel Operations

## Primary: openpyxl

The main library for reading and writing Excel 2010 xlsx/xlsm files.

```bash
# Installation
pip install openpyxl

# Or with uv
uv pip install openpyxl
```

### Key Features
- Full read/write support for .xlsx files
- Formula preservation and creation
- Chart creation and editing
- Formatting and styling
- Multiple worksheet support

### Basic Imports
```python
# Core imports
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.chart import LineChart, BarChart, PieChart, Reference
from openpyxl.utils import get_column_letter
from openpyxl.data_validation import DataValidation
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, IconSetRule
```

## Secondary: pandas

Excellent for data analysis and CSV operations.

```bash
pip install pandas openpyxl
```

### Key Features
- High-performance data manipulation
- Easy CSV to Excel conversion
- DataFrame to Excel export
- Excel to DataFrame import with formulas evaluated

### Basic Usage
```python
import pandas as pd

# Read Excel file into DataFrame
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# Write DataFrame to Excel
df.to_excel('output.xlsx', sheet_name='Results', index=False)

# Write multiple sheets
with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    df1.to_excel(writer, sheet_name='Sheet1', index=False)
    df2.to_excel(writer, sheet_name='Sheet2', index=False)
```

## Alternative: xlsxwriter

Focused on writing Excel files with rich formatting.

```bash
pip install xlsxwriter
```

**Note**: xlsxwriter cannot read or edit existing files, only create new ones.

### Basic Usage
```python
import xlsxwriter

# Create workbook
workbook = xlsxwriter.Workbook('output.xlsx')
worksheet = workbook.add_worksheet()

# Write with formatting
bold = workbook.add_format({'bold': True})
worksheet.write('A1', 'Hello', bold)
workbook.close()
```

## Quick Reference Commands

```python
# Installation
pip install openpyxl pandas

# Create workbook
from openpyxl import Workbook
wb = Workbook()
ws = wb.active

# Load workbook
from openpyxl import load_workbook
wb = load_workbook('file.xlsx')
ws = wb.active

# Read cell
value = ws['A1'].value
value = ws.cell(row=1, column=1).value

# Write cell
ws['A1'] = "Hello"
ws.cell(row=1, column=1, value="Hello")

# Write formula
ws['C1'] = "=A1+B1"

# Add row
ws.append([1, 2, 3])

# Save
wb.save('output.xlsx')

# Close
wb.close()
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'openpyxl'"
```bash
pip install openpyxl
# Or
uv pip install openpyxl
```

### Issue: "InvalidFileException: openpyxl does not support .xls files"
Solution: Convert .xls to .xlsx first, or use `xlrd` library for old format.

### Issue: Formulas showing as text
Solution: Don't prefix with quotes. Use `ws['A1'] = "=SUM(B1:B10)"` not `ws['A1'] = "'=SUM(B1:B10)"`

### Issue: Charts not appearing
Solution: Ensure data references are correct and save file after adding chart.

### Issue: Date showing as numbers
Solution: Apply date format: `ws['A1'].number_format = 'mm/dd/yyyy'`

## Additional Resources

- **openpyxl Documentation**: https://openpyxl.readthedocs.io/
- **pandas Excel Support**: https://pandas.pydata.org/docs/reference/io.html#excel
- **Excel Formula Reference**: https://support.microsoft.com/en-us/excel
- **Chart Examples**: https://openpyxl.readthedocs.io/en/stable/charts/introduction.html
