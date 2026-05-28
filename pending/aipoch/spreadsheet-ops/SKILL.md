---
name: spreadsheet-ops
description: Spreadsheet processing and analysis for CSV/Excel; trigger when users ask to merge/clean tabular data, run statistics, add/edit Excel formulas, apply formatting, generate charts, or force workbook recalculation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to merge multiple CSV/Excel files into a single dataset and align columns.
- You need to clean tabular data (normalize headers, deduplicate rows, resolve conflicts) before downstream use.
- You need to perform data analysis/statistics on CSV/Excel (summaries, distributions, group-by metrics).
- You need to add or edit formulas in an Excel workbook (including applying formulas across ranges).
- You need to apply Excel formatting (including conditional formatting), generate charts, or force formula recalculation.

## Key Features

- **CSV/Excel merge & cleaning**: combine files, normalize column names, deduplicate, and resolve conflicts.
- **CSV/Excel analysis**: compute descriptive statistics and analysis reports.
- **Excel-only formula operations**: create/edit formulas and apply them to specified ranges.
- **Excel-only formatting**: apply cell styles and conditional formatting rules.
- **Excel-only visualization**: build charts from worksheet ranges.
- **Excel-only recalculation**: set workbook to full recalculation (recalc flag) to ensure formulas update.

## Dependencies

- Python **3.x**
- Project Python dependencies are defined by the repository environment (e.g., `requirements.txt` / lockfile if present).  
  *(No explicit versions were provided in the source document.)*

## Example Usage

> The following commands assume you are in the repository root and have a Python environment available.

### 1) Merge files (CSV/Excel)

```bash
python scripts/merge_files.py
```

### 2) Analyze data (CSV/Excel)

```bash
python scripts/analyze_data.py
```

### 3) Apply formulas (Excel only)

```bash
python scripts/apply_formulas.py
```

### 4) Apply formatting (Excel only)

```bash
python scripts/apply_formatting.py
```

### 5) Build charts (Excel only)

```bash
python scripts/build_charts.py
```

### 6) Force workbook recalculation (Excel only)

```bash
python scripts/recalc_workbook.py
```

## Implementation Details

- **Workflow**
  1. Confirm inputs/outputs: file paths, file formats (CSV vs Excel), worksheet names, and target ranges.
  2. Choose the task type: merge, analysis, formula, formatting, chart, or recalculation.
  3. Run the corresponding script and configure parameters in `CONFIG` (as used by the scripts).
  4. Produce output files and any generated reports.

- **Task boundaries**
  - **CSV/Excel supported**: merging/cleaning, data analysis.
  - **Excel only**: formula creation/editing, formatting, chart visualization, and recalculation.

- **Key parameters to clarify (priority)**
  - Input type: CSV or Excel; single file or multiple files.
  - Worksheet names and cell ranges to operate on (Excel).
  - Whether formulas/formatting/charts must preserve original styles.
  - Desired output format: CSV / Excel / JSON / Parquet.

- **Standards / constraints**
  - Python file I/O must explicitly specify `encoding='utf-8'`.
  - `json.dump(...)` must set `ensure_ascii=False`.

- **Reference documentation (optional)**
  - Column name matching & normalization: `references/column-matching.md`
  - Deduplication & conflict resolution: `references/dedup-conflict.md`
  - Large files & performance: `references/large-files.md`
  - Formula design & ranges: `references/formulas.md`
  - Formatting & conditional formatting: `references/formatting.md`
  - Data analysis & statistics: `references/analysis.md`
  - Charts & visualization: `references/visualization.md`
  - Formula recalculation: `references/recalc.md`