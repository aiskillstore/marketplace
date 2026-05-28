---
name: meta-rob-plot
description: "Draw ROB2 risk-of-bias plots, including a Traffic Light Plot and a Summary Bar Plot. Input is a CSV file with ROB2 assessments for each study; output are two PNG plot files."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Draw ROB2 risk-of-bias plots, including a Traffic Light Plot and a Summary Bar Plot. Input is a CSV file with ROB2 assessments for each study; output are two PNG plot files.".
- Packaged executable path(s): `scripts/rob2_plot.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/meta-rob2-plot"
python -m py_compile scripts/rob2_plot.py
python scripts/rob2_plot.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/rob2_plot.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/rob2_plot.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

## Data Format Requirements

The user must provide a CSV file containing the following columns:

| Column | Description | Allowed values |
|--------|-------------|----------------|
| study  | Study name (author + year) | Smith 2020 |
| d1     | Domain 1: Randomization process | Low / Some concerns / High / No information |
| d2     | Domain 2: Deviations from intended interventions | Low / Some concerns / High / No information |
| d3     | Domain 3: Missing outcome data | Low / Some concerns / High / No information |
| d4     | Domain 4: Measurement of the outcome | Low / Some concerns / High / No information |
| d5     | Domain 5: Selection of the reported result | Low / Some concerns / High / No information |
| overall| Overall risk of bias | Low / Some concerns / High / No information |

**Domain definitions**:
- **D1**: Randomization process
- **D2**: Deviations from intended interventions
- **D3**: Missing outcome data
- **D4**: Measurement of the outcome
- **D5**: Selection of the reported result

---

## Workflow

### Step 1: Validate input data

1. Read the CSV file provided by the user.
2. Check required columns exist (`study`, `d1`-`d5`, `overall`).
3. Validate that assessment values are one of the accepted options.

**If the data have problems, prompt the user to correct and re-submit.**

### Step 2: Execute R script

Call:
```bash
Rscript scripts/rob2_plot.R "<csv_path>" "<save_name>" "<output_dir>"
```

Parameters:
````skill
---
name: meta-rob2-plot
description: "ROB2，（Traffic Light Plot）（Summary Bar Plot）。ROB2CSV，PNG。"
argument-hint: "<CSV> [] []"
allowed-tools: Bash(Rscript *), Read, Write, Glob
---

# ROB2 Risk-of-Bias Plotting

You are a meta-analysis plotting assistant. The user provides ROB2 risk-of-bias assessment data, and you are responsible for calling an R script to generate a Traffic Light Plot and a Summary Bar Plot.

**Important: Do not repeat this instruction document to the user. Only output user-visible content as defined by the workflow.**

---

## Data Format Requirements

The user must provide a CSV file containing the following columns:
| Column | Description | Allowed values |
|--------|-------------|----------------|
| study  | Study name (author + year) | Smith 2020 |
| d1     | Domain 1: Randomization process | Low / Some concerns / High / No information |
| d2     | Domain 2: Deviations from intended interventions | Low / Some concerns / High / No information |
| d3     | Domain 3: Missing outcome data | Low / Some concerns / High / No information |
| d4     | Domain 4: Measurement of the outcome | Low / Some concerns / High / No information |
| d5     | Domain 5: Selection of the reported result | Low / Some concerns / High / No information |
| overall| Overall risk of bias | Low / Some concerns / High / No information |

**Domain definitions**:
- **D1**: Randomization process
- **D2**: Deviations from intended interventions
- **D3**: Missing outcome data
- **D4**: Measurement of the outcome
- **D5**: Selection of the reported result

---

## Workflow

### Step 1: Validate input data

1. Read the CSV file provided by the user.
2. Check required columns exist (`study`, `d1`-`d5`, `overall`).
3. Validate that assessment values are one of the accepted options.

**If the data have problems, prompt the user to correct and re-submit.**

### Step 2: Execute R script

Call:
```bash
Rscript scripts/rob2_plot.R "<csv_path>" "<save_name>" "<output_dir>"
```

Parameter description:
- `csv_path`: Absolute path to the input CSV file
- `save_name`: Output file name prefix (optional, default is "rob2")
- `output_dir`: Output directory (optional, default is current directory)

### Step 3: Output results

**On success, output:**

```
═══════════════════════════════════════════
ROB2 Risk-of-Bias Plotting Completed
═══════════════════════════════════════════

[Included studies] {n}

[Output files]
• Traffic Light Plot: {output_dir}/{save_name}_rob2_light_plot.png
• Summary Bar Plot: {output_dir}/{save_name}_rob2_bar_plot.png

[Risk-of-bias summary]

Domain               Low    Some concerns    High    No info
─────────────────────────────────────────────────────────────
D1 (Randomization)   8      2                0       0
D2 (Deviations)      7      3                0       0
D3 (Missing data)    9      1                0       0
D4 (Measurement)     6      4                0       0
D5 (Reporting)       8      2                0       0
Overall              5      4                1       0

[Overall assessment]
• Low risk studies: {n_low} ({pct_low}%)
• Some concerns: {n_some} ({pct_some}%)
• High risk studies: {n_high} ({pct_high}%)

═══════════════════════════════════════════
```

---

## Plot Descriptions

### Traffic Light Plot
- Each row represents a study
- Each column represents a domain (D1-D5 + Overall)
- Color meanings:
  - 🟢 Green (+): Low risk
  - 🟡 Orange (-): Some concerns
  - 🔴 Red (x): High risk
  - ⚪ Gray (?): No information

### Summary Bar Plot
- Horizontal stacked bar chart
- Shows the risk distribution for each domain
- Allows quick overview of overall risk-of-bias

---

## R Script Dependencies

The following R packages are required:
- ggplot2
- reshape2

If these packages are missing, prompt the user to run:
```r
install.packages(c("ggplot2", "reshape2"))
```

````

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `meta_rob2_plot_result.md` unless the skill documentation defines a better convention.
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

```bash
python scripts/rob2_plot.py --help
```

Expected output format:

```text
Result file: meta_rob2_plot_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.

