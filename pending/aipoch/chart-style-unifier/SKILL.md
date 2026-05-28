---
name: chart-style-unifier
description: Batch-unify typography (font family, size, italics) for Word table cells and embedded charts; use when you need consistent formatting across theses/reports without changing body text.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Chart Style Unifier

## When to Use

- Use this skill when you need batch-unify typography (font family, size, italics) for word table cells and embedded charts; use when you need consistent formatting across theses/reports without changing body text in a reproducible workflow.
- Use this skill when a others task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/change_table_font.py` is the most direct path to complete the request.
- Use this skill when you need the `chart-style-unifier` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Batch-unify typography (font family, size, italics) for Word table cells and embedded charts; use when you need consistent formatting across theses/reports without changing body text.
- Packaged executable path(s): `scripts/change_table_font.py` plus 2 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/chart-style-unifier"
python -m py_compile scripts/change_table_font.py
python scripts/change_table_font.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/change_table_font.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/change_table_font.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

- You need to normalize **table cell fonts** across a Word document (e.g., thesis tables must use SimSun 10pt).
- You have many **embedded Word charts** and want consistent typography (title/axis/ticks/legend/data labels) without manual editing.
- You are preparing a **final submission/export (PDF/print)** and want to eliminate inconsistent chart/table styling.
- Your document contains **mixed chart types** (with/without titles/legends) and you need a robust batch operation that won’t fail on missing elements.
- You have **linked charts** and want a safe workflow: unify styles in the Excel sources first, then refresh in Word.

## 2. Key Features

- **Word table-only processing**: updates typography inside **table cells only**; does **not** modify body text styles.
- **Embedded chart typography normalization (VBA)**:
  - Chart area base font
  - Chart title
  - Axis titles
  - Tick labels
  - Legend
  - Data labels
- **Config-driven Python workflow**: initialize a run directory, edit a generated `config.json`, then execute.
- **Run isolation**: outputs are written to `outputs/runs/<timestamp>/` for traceability.
- **Linked chart guidance**: highlights that Word-side changes can be overwritten by Excel link refresh.

## 3. Dependencies

| Dependency | Version | Purpose | Notes |
|---|---:|---|---|
| python-docx | >= 0.8.11 | Modify Word table cell runs/fonts | Used by `scripts/change_table_font.py` |
| pywin32 | >= 306 | Word/Excel COM automation for chart macros | Windows-only; required for COM-based operations |

Installation:

```bash
pip install python-docx pywin32
```

Optional (mirror):

```bash
pip install -i https://mirrors.aliyun.com/pypi/simple python-docx pywin32
```

## 4. Example Usage

### 4.1 Unify Word Table Cell Fonts (Python, runnable)

```bash

# 1) Initialize a run directory for table processing
python scripts/init_run.py --table

# 2) Edit the generated config:

# outputs/runs/<timestamp>/config.json

# 3) Execute the table font unification
python scripts/change_table_font.py
```

Example `outputs/runs/<timestamp>/config.json`:

```json
{
  "target_doc_path": "C:/Users/xxx/Desktop/document.docx",
  "font_name": "SimSun",
  "font_size": 10,
  "target_type": "table",
  "italic_numbers": false,
  "italic_chinese": false,
  "lowercase_letters": false,
  "status": "pending"
}
```

### 4.2 Unify Embedded Chart Typography (Word VBA, runnable)

Paste into **Word VBA Editor** (Alt+F11) and run `NormalizeChartTypography`:

```vba
Option Explicit

Public Sub NormalizeChartTypography()
    Dim fontName As String
    Dim baseSize As Single, titleSize As Single
    Dim axisTitleSize As Single, tickLabelSize As Single
    Dim legendSize As Single, dataLabelSize As Single

    fontName = InputBox("Font Name", "Unify Chart Fonts", "Times New Roman")
    baseSize = CSng(InputBox("Base Size (ChartArea)", "Unify Chart Fonts", "9"))
    titleSize = CSng(InputBox("Chart Title Size", "Unify Chart Fonts", "11"))
    axisTitleSize = CSng(InputBox("Axis Title Size", "Unify Chart Fonts", "9"))
    tickLabelSize = CSng(InputBox("Tick Label Size", "Unify Chart Fonts", "8"))
    legendSize = CSng(InputBox("Legend Size", "Unify Chart Fonts", "10"))
    dataLabelSize = CSng(InputBox("Data Label Size", "Unify Chart Fonts", "8"))

    Application.ScreenUpdating = False

    Dim ish As InlineShape, shp As Shape
    For Each ish In ActiveDocument.InlineShapes
        If ish.HasChart Then
            ApplyChartTypography ish.Chart, fontName, baseSize, titleSize, axisTitleSize, tickLabelSize, legendSize, dataLabelSize
        End If
    Next ish

    For Each shp In ActiveDocument.Shapes
        If shp.HasChart Then
            ApplyChartTypography shp.Chart, fontName, baseSize, titleSize, axisTitleSize, tickLabelSize, legendSize, dataLabelSize
        End If
    Next shp

    Application.ScreenUpdating = True
End Sub

Private Sub ApplyChartTypography(cht As Object, fontName As String, baseSize As Single, _
                                 titleSize As Single, axisTitleSize As Single, tickLabelSize As Single, _
                                 legendSize As Single, dataLabelSize As Single)
    On Error Resume Next

    With cht.ChartArea.Format.TextFrame2.TextRange.Font
        .Name = fontName
        .Size = baseSize
    End With

    If cht.HasTitle Then
        With cht.ChartTitle.Format.TextFrame2.TextRange.Font
            .Name = fontName
            .Size = titleSize
        End With
    End If

    If cht.HasLegend Then
        With cht.Legend.Format.TextFrame2.TextRange.Font
            .Name = fontName
            .Size = legendSize
        End With
    End If

    Dim axType As Variant, axGroup As Variant, ax As Object
    For Each axType In Array(1, 2) ' 1=xlCategory, 2=xlValue
        For Each axGroup In Array(1, 2) ' 1=xlPrimary, 2=xlSecondary
            Set ax = Nothing
            Set ax = cht.Axes(axType, axGroup)
            If Not ax Is Nothing Then
                ax.TickLabels.Font.Name = fontName
                ax.TickLabels.Font.Size = tickLabelSize
                If ax.HasTitle Then
                    ax.AxisTitle.Format.TextFrame2.TextRange.Font.Name = fontName
                    ax.AxisTitle.Format.TextFrame2.TextRange.Font.Size = axisTitleSize
                End If
            End If
        Next axGroup
    Next axType

    Dim s As Object
    For Each s In cht.SeriesCollection
        If s.HasDataLabels Then
            s.DataLabels.Font.Name = fontName
            s.DataLabels.Font.Size = dataLabelSize
        End If
    Next s

    On Error GoTo 0
End Sub
```

### 4.3 Unify Linked Chart Source Files (Excel VBA, runnable)

Run in Excel on the **source workbook(s)** before refreshing links in Word:

```vba
Option Explicit

Public Sub NormalizeLinkedChartTypography()
    Dim fontName As String
    Dim baseSize As Single, titleSize As Single
    Dim axisTitleSize As Single, tickLabelSize As Single
    Dim legendSize As Single, dataLabelSize As Single

    fontName = InputBox("Font Name", "Unify Chart Fonts", "Times New Roman")
    baseSize = CSng(InputBox("Base Size (ChartArea)", "Unify Chart Fonts", "9"))
    titleSize = CSng(InputBox("Chart Title Size", "Unify Chart Fonts", "11"))
    axisTitleSize = CSng(InputBox("Axis Title Size", "Unify Chart Fonts", "9"))
    tickLabelSize = CSng(InputBox("Tick Label Size", "Unify Chart Fonts", "8"))
    legendSize = CSng(InputBox("Legend Size", "Unify Chart Fonts", "10"))
    dataLabelSize = CSng(InputBox("Data Label Size", "Unify Chart Fonts", "8"))

    Application.ScreenUpdating = False

    Dim ws As Worksheet, co As ChartObject
    For Each ws In ActiveWorkbook.Worksheets
        For Each co In ws.ChartObjects
            ApplyChartTypography co.Chart, fontName, baseSize, titleSize, axisTitleSize, tickLabelSize, legendSize, dataLabelSize
        Next co
    Next ws

    Application.ScreenUpdating = True
End Sub
```

## 5. Implementation Details

### 5.1 Processing Scope and Constraints

- **Allowed input**: only the Word document path explicitly provided by the user (`target_doc_path`).
- **Output directory**: `outputs/runs/<timestamp>/`.
- **Disallowed access**: parent traversal (`../`) and sensitive system directories.
- **No network usage**: local-only operations; no external APIs; no credentials.

### 5.2 Python Table Unification Logic (Conceptual)

- Reads `outputs/runs/<timestamp>/config.json`.
- Opens the `.docx` and iterates **tables → rows → cells → paragraphs → runs**.
- Applies:
  - `font_name` and `font_size` to runs inside table cells.
  - Optional toggles (if enabled in config): italics rules for numbers/Chinese/lowercase letters.
- Saves results into the run output directory (implementation-dependent).

### 5.3 Chart Typography Tokens (What Gets Normalized)

Recommended parameter mapping (used by the VBA macros):

| Element | VBA Target | Parameter |
|---|---|---|
| Chart area base | `Chart.ChartArea` | `baseSize` |
| Chart title | `Chart.ChartTitle` | `titleSize` |
| Axis titles | `Axes(...).AxisTitle` | `axisTitleSize` |
| Tick labels | `Axes(...).TickLabels` | `tickLabelSize` |
| Legend | `Chart.Legend` | `legendSize` |
| Data labels | `Series.DataLabels` | `dataLabelSize` |

### 5.4 Linked Charts: Overwrite Behavior

- If a chart in Word is **linked** to Excel, refreshing the link can overwrite Word-side formatting.
- Safe workflow:
  1. Normalize chart typography in the **Excel source files** (Excel VBA).
  2. Refresh/update links in Word.
  3. Only use Word VBA for charts that are truly **embedded** (not linked).

### 5.5 Repository Entry Points

| Script | Purpose |
|---|---|
| `scripts/init_run.py` | Create `outputs/runs/<timestamp>/` and a starter `config.json` |
| `scripts/generate_style_pack.py` | Generate matplotlib/plotly style packs from a unified config |
| `scripts/change_table_font.py` | Apply table cell font normalization based on `config.json` |

### 5.6 References

- Test cases: `tests/test_table_font.py`
- Evaluation checklist: `references/style-apply-checklist.md`
- Style specification template: `references/style-spec-template.md`
