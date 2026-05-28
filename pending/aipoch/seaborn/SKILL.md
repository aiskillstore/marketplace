---
name: seaborn
description: Statistical visualization library integrated with pandas; use it when you need fast EDA of distributions, relationships, and categorical comparisons (e.g., box/violin/pair plots and heatmaps) with strong default aesthetics on top of matplotlib.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Exploring relationships between variables in a DataFrame (e.g., scatter/line plots with `hue`, `size`, `style`).
- Comparing distributions across categories (e.g., box/violin/swarm plots for groups).
- Inspecting univariate/bivariate distributions (histograms, KDE, ECDF; joint and pairwise views).
- Visualizing correlation matrices or other rectangular data (heatmaps, clustered heatmaps).
- Building faceted "small multiples" quickly (split by `row`/`col` using figure-level APIs).

## Key Features

- **DataFrame-first API**: Works naturally with pandas "long-form/tidy" data and named columns.
- **Semantic mappings**: Encode extra dimensions via `hue`, `size`, `style`, and faceting (`row`, `col`).
- **Statistical awareness**: Built-in aggregation and uncertainty display (e.g., confidence intervals / error bars).
- **High-quality defaults**: Themes, contexts, and curated palettes for readable statistical graphics.
- **Two interfaces**:
  - **Axes-level** functions (return a matplotlib `Axes`, accept `ax=`) for custom layouts.
  - **Figure-level** functions (return Grid objects) for faceting and consistent multi-panel figures.
- **Matplotlib compatibility**: Fine-tune labels, annotations, and layout using matplotlib when needed.

## Dependencies

- `seaborn>=0.13`
- `matplotlib>=3.7`
- `pandas>=2.0`
- `numpy>=1.24`

## Example Usage

```python
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    # Built-in example dataset (requires internet on first use in some environments)
    df = sns.load_dataset("tips")

    sns.set_theme(style="whitegrid", palette="colorblind")

    # 1) Relationship exploration with semantic mapping
    ax = sns.scatterplot(
        data=df,
        x="total_bill",
        y="tip",
        hue="day",
        style="sex",
        size="size",
        sizes=(30, 200),
        alpha=0.8,
    )
    ax.set(title="Tips: Total Bill vs Tip", xlabel="Total bill ($)", ylabel="Tip ($)")
    plt.tight_layout()
    plt.show()

    # 2) Faceted categorical comparison (figure-level)
    g = sns.catplot(
        data=df,
        x="day",
        y="total_bill",
        col="time",
        kind="violin",
        inner="quartile",
        height=3.5,
        aspect=1.1,
    )
    g.set_axis_labels("Day", "Total bill ($)")
    g.set_titles("{col_name}")
    plt.tight_layout()
    plt.show()

    # 3) Correlation heatmap (matrix plot)
    corr = df.select_dtypes("number").corr(numeric_only=True)
    plt.figure(figsize=(5.5, 4.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True)
    plt.title("Numeric Correlations (tips)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
```

## Implementation Details

- **Axes-level vs Figure-level**
  - *Axes-level* (e.g., `scatterplot`, `histplot`, `boxplot`, `regplot`, `heatmap`) draw onto one matplotlib `Axes`, accept `ax=`, and are best for custom subplot grids.
  - *Figure-level* (e.g., `relplot`, `displot`, `catplot`, `lmplot`, `jointplot`, `pairplot`) manage the full figure and faceting; they return Grid objects (e.g., `FacetGrid`, `JointGrid`, `PairGrid`) and are not designed to be embedded into an existing matplotlib figure.

- **Data shape expectations**
  - Prefer **long-form (tidy)** data: one column per variable, one row per observation. This maximizes compatibility with semantic mappings and faceting.
  - **Wide-form** data is supported for some plots (notably matrix-like inputs such as heatmaps), but may require reshaping via `pandas.melt()` for general-purpose plotting.

- **Statistical estimation controls**
  - Many functions compute summaries automatically (e.g., `lineplot` aggregates and can display uncertainty bands; `barplot` estimates a central tendency with error bars).
  - Key parameters to control estimation/uncertainty include `estimator=`, `errorbar=` (or legacy `ci=`), and for KDE smoothing `bw_adjust=`.

- **Distribution and smoothing parameters**
  - Histograms: `bins=` / `binwidth=`, `stat=` (`"count"`, `"frequency"`, `"probability"`, `"density"`), and `multiple=` for hue handling (`"layer"`, `"stack"`, `"dodge"`, `"fill"`).
  - KDE: `bw_adjust` (higher = smoother), `fill=True`, `levels=` for contour density plots.

- **Color and theme system**
  - Palettes: qualitative (categorical), sequential (ordered), diverging (centered at a reference via `center=` in heatmaps).
  - Global styling: `sns.set_theme(style=..., context=..., palette=...)`; use matplotlib calls for final layout (`plt.tight_layout()`) and export (`savefig(dpi=300, bbox_inches="tight")`).

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

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `seaborn_result.md` unless the skill documentation defines a better convention.
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

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: seaborn_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Statistical visualization library integrated with pandas; use it when you need fast EDA of distributions, relationships, and categorical comparisons (e.g., box/violin/pair plots and heatmaps) with strong default aesthetics on top of matplotlib.
