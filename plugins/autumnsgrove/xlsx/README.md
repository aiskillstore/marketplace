# Excel (XLSX) Skill

Comprehensive Excel spreadsheet manipulation skill for Claude with support for formulas, formatting, charts, data analysis, and visualization.

## Installation

```bash
pip install openpyxl pandas
# Or with uv
uv pip install openpyxl pandas
```

## Files

- **SKILL.md** - Complete skill documentation with workflows and examples
- **scripts/excel_helper.py** - Python utility library with helper functions

## Quick Start

### Using the Skill

Reference this skill in your Claude conversation:

```
Use the xlsx skill to create a financial report with formulas and charts
```

### Using the Helper Script

```python
from scripts.excel_helper import create_workbook, apply_formatting, add_chart

# Create workbook with headers
wb, ws = create_workbook("Sales Report", headers=["Product", "Q1", "Q2"])

# Add formatting
apply_formatting(ws, "A1:B1", bold=True, bg_color="4472C4")

# Save
wb.save("report.xlsx")
```

## Key Capabilities

- Create/read/edit Excel files (.xlsx, .xlsm, .csv)
- Formula management (SUM, VLOOKUP, INDEX/MATCH, etc.)
- Cell formatting (colors, fonts, borders, number formats)
- Chart creation (line, bar, pie, scatter, combo)
- Data analysis and transformation
- Multi-worksheet operations
- Conditional formatting
- Data validation

## Examples

See SKILL.md for comprehensive examples including:
- Financial reports with formulas
- Data analysis with charts
- Conditional formatting
- Multi-sheet workbooks
- Dashboard creation
- CSV to Excel transformation

## Test

```bash
cd /Users/mini/Documents/Projects/ClaudeSkills/xlsx
uv run python scripts/excel_helper.py
```

This creates demo files to verify functionality.
