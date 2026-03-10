---
name: libreoffice-calc
description: Use when creating, editing, formatting, or extracting LibreOffice Calc (.ods) spreadsheets via UNO, including cell operations, formulas, formatting, charts, named ranges, and data validation.
---

# LibreOffice Calc

## Overview
Use the `calc` modules to create and edit Calc spreadsheets
with UNO-backed operations. Prefer the high-level functions in these modules
instead of raw UNO calls or a CLI.

## Quick Reference
- `core.create_spreadsheet(path)`
- `core.export_spreadsheet(path, output_path, format)`
- `cells.get_cell(path, sheet, row, col)`
- `cells.set_cell(path, sheet, row, col, value, type)`
- `ranges.get_range(path, sheet, start_row, start_col, end_row, end_col)`
- `ranges.set_range(path, sheet, start_row, start_col, data)`
- `sheets.add_sheet(path, name, index=None)`
- `formatting.apply_format(path, sheet, row, col, format)`
- `charts.create_chart(path, sheet, data_range, chart_type, anchor, size, title=None)`
- `named_ranges.define_named_range(path, name, sheet, start_row, start_col, end_row=None, end_col=None)`
- `validation.add_validation(path, sheet, start_row, start_col, end_row, end_col, rule)`
- `snapshot.snapshot_area(doc_path, output_path, sheet="Sheet1", row=0, col=0, width=None, height=None, dpi=150)`
- `colors.resolve_color(color)`

## Usage Notes
- Use absolute file paths for spreadsheets.
- Ensure the bundled modules are on `PYTHONPATH`.
  The modules are bundled under `scripts/` in this skill directory. Set:
  `PYTHONPATH=<skill_base_dir>/scripts` where `<skill_base_dir>` is the base
  directory reported when this skill was loaded (e.g. the path shown as
  "Base directory" in the skill output).
- R1C1 addressing (row, col) is primary and zero-based.
- Use explicit `type` in examples ("number", "text", "date", "formula").
- `create_chart`: `anchor=(row, col)` is the zero-based cell that pins
  the chart's top-left corner. `size=(width, height)` sets chart dimensions
  in 1/100 mm (UNO native units). Example: `size=(10000, 7000)` produces a
  10 cm x 7 cm chart.
- Color fields accept either a `0xRRGGBB` integer or a CSS color name string.

## Example: Create a Summary Sheet
```python
from pathlib import Path

from calc.core import create_spreadsheet
from calc.cells import set_cell
from calc.formatting import apply_format
from calc.charts import create_chart

output = Path("test-output/summary.ods").resolve()
create_spreadsheet(str(output))

set_cell(str(output), 0, 0, 0, "Revenue", type="text")
set_cell(str(output), 0, 1, 0, 100, type="number")
set_cell(str(output), 0, 2, 0, 200, type="number")

apply_format(str(output), 0, 1, 0, {"number_format": "currency"})

create_chart(
    str(output),
    0,
    (0, 0, 2, 0),
    "line",
    anchor=(5, 0),      # chart top-left at row 5, col 0
    size=(5000, 3000),  # 5 cm x 3 cm (1/100 mm units)
    title="Revenue Trend",
)
```

## Common Mistakes
- Forgetting to create the spreadsheet before writing cells.
- Passing relative paths (UNO loads absolute URLs).
- Mixing A1 and R1C1 coordinates without conversion.
- Passing chart positions as raw tuples without converting to UNO rectangles.

## Visual Snapshots

Use `snapshot.snapshot_area()` to capture a cell-anchored area as PNG for
layout verification (especially after chart placement).

```python
from calc.snapshot import snapshot_area

result = snapshot_area(
    str(doc_path), "/tmp/chart_area.png",
    sheet="DataFinal", row=0, col=0, dpi=150,
)
# result.file_path, result.width, result.height, result.dpi
```

**Parameters:**
- `doc_path`: Absolute path to the Calc spreadsheet.
- `output_path`: File path for the PNG output.
- `sheet`: Sheet name (default: "Sheet1").
- `row`, `col`: Zero-based cell anchor for capture origin (default: 0, 0).
- `width`, `height`: Pixel dimensions (None for default extent).
- `dpi`: Export resolution (default: 150).

**When to snapshot:**
- After inserting charts to verify placement and sizing.
- After applying formatting to confirm visual layout.
- Before delivering a spreadsheet to verify chart/data alignment.

**Cleanup:** Remove snapshot PNGs after verification. Do not let temporary
images accumulate.

```python
Path(result.file_path).unlink(missing_ok=True)
```

**Visual Red Flags:**
- Charts overlapping data cells.
- Cut-off chart titles or axis labels.
- Misaligned chart anchors (chart not at expected position).
- Data cells hidden behind chart objects.
- Inconsistent formatting visible in the snapshot.
