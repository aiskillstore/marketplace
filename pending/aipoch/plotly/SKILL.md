---
name: plotly
description: Interactive visualization library for Python. Use it when you need hover tooltips, zoom/pan, selection, animations, or charts embeddable in web pages (e.g., dashboards, exploratory analysis, presentations).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Plotly

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Interactive visualization library for Python. Use it when you need hover tooltips, zoom/pan, selection, animations, or charts embeddable in web pages (e.g., dashboards, exploratory analysis, presentations).
- Documentation-first workflow with no packaged script requirement.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```text
Skill directory: 20260316/scientific-skills/Others/plotly
No packaged executable script was detected.
Use the documented workflow in SKILL.md together with the references/assets in this folder.
```

Example run plan:
1. Read the skill instructions and collect the required inputs.
2. Follow the documented workflow exactly.
3. Use packaged references/assets from this folder when the task needs templates or rules.
4. Return a structured result tied to the requested deliverable.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: instruction-only workflow in `SKILL.md`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use Plotly when you need interactive, shareable visualizations, especially in these scenarios:

- **Exploratory data analysis (EDA):** quickly inspect distributions, relationships, and outliers with hover and selection.
- **Dashboards and web embedding:** publish interactive charts to HTML pages or integrate into web apps (e.g., Dash).
- **Time-series monitoring:** use range sliders, zooming, and pan for dense temporal data.
- **Presentations and stakeholder reviews:** interactive tooltips and legend toggling help explain results live.
- **Complex multi-panel figures:** build subplots and multi-trace figures with fine-grained layout control.

If you only need static publication figures, consider Matplotlib or other scientific visualization tools.

## 2. Key Features

- **Two APIs**
  - **Plotly Express (`plotly.express`, `px`)**: high-level, concise API for common charts from DataFrames.
  - **Graph Objects (`plotly.graph_objects`, `go`)**: low-level building blocks for full control and custom figures.
  - Plotly Express returns a **Graph Objects `Figure`**, so you can mix both styles.
- **40+ chart types** across statistical, scientific, financial, geospatial, and 3D categories.
- **Interactivity by default**
  - hover tooltips, zoom/pan, legend toggling
  - box/lasso selection
  - range sliders (time series)
  - buttons/dropdowns and animations
- **Layout and styling**
  - subplots (`make_subplots`)
  - templates (e.g., `plotly_dark`, `plotly_white`)
  - annotations, shapes, axes/legend control
- **Export**
  - interactive HTML (`write_html`)
  - static images via Kaleido (`write_image`)

Reference guides (optional reading):
- Plotly Express: `reference/plotly-express.md`
- Graph Objects: `reference/graph-objects.md`
- Chart catalog: `reference/chart-types.md`
- Layout & styling: `reference/layouts-styling.md`
- Export & interactivity: `reference/export-interactivity.md`

## 3. Dependencies

- `plotly>=5.0`
- `pandas>=1.5` (recommended for DataFrame-based workflows)
- `kaleido>=0.2` (optional, required for static image export: PNG/SVG/PDF)
- `dash>=2.0` (optional, for building interactive web apps)

## 4. Example Usage

A complete runnable example demonstrating: Plotly Express + Graph Objects updates, hover customization, subplots, and export.

### Install

```bash
uv pip install "plotly>=5.0" "pandas>=1.5" "kaleido>=0.2"
```

### Run

```python
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def main():
    # Sample dataset
    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5],
            "y": [10, 11, 12, 11.5, 13],
            "group": ["A", "A", "B", "B", "B"],
        }
    )

    # 1) Quick chart with Plotly Express
    fig_scatter = px.scatter(
        df,
        x="x",
        y="y",
        color="group",
        title="Scatter (px) + Graph Objects Updates",
        template="plotly_white",
    )

    # 2) Use Graph Objects methods on a px figure
    fig_scatter.update_traces(
        hovertemplate="x=%{x}<br>y=%{y:.2f}<br>group=%{marker.color}<extra></extra>"
    )
    fig_scatter.add_hline(y=11, line_dash="dash", line_color="gray")

    # 3) Build a small dashboard-like layout with subplots
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Interactive Scatter", "Group Means (Bar)"),
        specs=[[{"type": "scatter"}, {"type": "bar"}]],
    )

    # Left: reuse traces from the px figure
    for tr in fig_scatter.data:
        fig.add_trace(tr, row=1, col=1)

    # Right: bar chart with group means
    means = df.groupby("group", as_index=False)["y"].mean()
    fig.add_trace(
        go.Bar(x=means["group"], y=means["y"], name="mean(y)"),
        row=1,
        col=2,
    )

    fig.update_layout(
        title="Plotly End-to-End Example",
        height=450,
        legend_title_text="Group",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    # Show interactively (notebook or supported environment)
    fig.show()

    # Export
    fig.write_html("plotly_example.html", include_plotlyjs="cdn")
    fig.write_image("plotly_example.png")  # requires kaleido

if __name__ == "__main__":
    main()
```

## 5. Implementation Details

### API choice: `px` vs `go`
- **Use `plotly.express` (`px`)** when:
  - your data is in a Pandas DataFrame,
  - you want fast defaults and concise code,
  - you need standard charts (scatter/line/bar/histogram/box/violin, etc.).
- **Use `plotly.graph_objects` (`go`)** when:
  - you need precise control over traces, axes, annotations, shapes, or multi-trace composition,
  - you are building uncommon chart types or highly customized figures.
- **Mixing is standard**: `px.*` returns a `go.Figure`, so `fig.update_layout(...)`, `fig.add_trace(...)`, `fig.add_hline(...)`, etc. work seamlessly.

### Interactivity configuration
- **Hover formatting**: customize per-trace with `hovertemplate` to control text and numeric formatting.
- **Time-series navigation**: enable range sliders via:
  - `fig.update_xaxes(rangeslider_visible=True)`
- **Selection tools**: box/lasso selection is available by default in many chart types; you can further configure selection behavior via trace/layout options.

### Export behavior
- **HTML export** (`write_html`) preserves full interactivity.
  - `include_plotlyjs="cdn"` reduces file size but requires internet access to load Plotly JS.
- **Static export** (`write_image`) requires **Kaleido** and produces PNG/SVG/PDF suitable for reports.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `plotly_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: plotly_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
