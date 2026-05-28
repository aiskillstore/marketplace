---
name: cohort-study-quality-assessment-nos
description: Evaluates the quality of cohort studies using the Newcastle-Ottawa Scale (NOS). Use when the user provides a cohort study article or text and needs a quality assessment report.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Cohort Study Quality Assessment (NOS)

This skill evaluates the quality of a cohort study based on the Newcastle-Ottawa Scale (NOS). It analyzes Selection, Comparability, and Outcome categories and generates a scored report.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Evaluates the quality of cohort studies using the Newcastle-Ottawa Scale (NOS). Use when the user provides a cohort study article or text and needs a quality assessment report.
- Packaged executable path(s): `scripts/calculate_nos_score.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Data Analytics/cohort-study-quality-assessment-nos"
python -m py_compile scripts/calculate_nos_score.py
python scripts/calculate_nos_score.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/calculate_nos_score.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/calculate_nos_score.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Prerequisites

- Python 3.x
- PyPDF2 library (`pip install PyPDF2`)
- Access to `references/nos_criteria.md` for detailed evaluation criteria

## Usage

### Method 1: Direct Text Input

1.  **Input**: The full text of the cohort study article (copy-pasted or provided by user).
2.  **Process**:
    *   Extract study metadata (Author, Year).
    *   Evaluate the study against NOS criteria (Selection, Comparability, Outcome).
    *   Calculate the total score (number of stars).
3.  **Output**: A Markdown table summarizing the assessment for each criterion and the overall score.

### Method 2: PDF File Input

1.  **Input**: Path to a PDF file containing the cohort study.
2.  **Process**:
    *   Use `scripts/extract_pdf.py` to extract text from the PDF.
    *   Review the extracted text for completeness.
    *   Proceed with Method 1 steps.
3.  **Output**: Same as Method 1.

## Workflow

### Step 1: Extract Content

**If input is PDF:**
```bash
cd "D:\helix\test record\\262\skills_\skills\cohort-study-quality-assessment-nos"
python scripts/extract_pdf.py "path/to/your/file.pdf"
```

**Note**: The extracted text will be saved to `extracted_text.txt` in the current directory.

### Step 2: Analyze the Text

You must analyze the input text to extract information and evaluate it against the criteria defined in `references/nos_criteria.md`.

**1. Extract Metadata:**
*   **Study**: First Author, Year (e.g., "Wang, 2018").

**2. Evaluate Selection (4 items):**
*   **D1**: Representativeness of the Exposed Cohort (* or -)
    - Look for: study design (retrospective/prospective), data source (hospital registry/population-based), inclusion/exclusion criteria clarity
    - Give star if: representative sample from a defined population with clear criteria
*   **D2**: Selection of the Non-Exposed Cohort (* or -)
    - Look for: comparison group source (same community/hospital/different source)
    - Give star if: drawn from the same source as exposed cohort
*   **D3**: Ascertainment of Exposure (* or -)
    - Look for: how exposure was determined (medical records/interview/self-report)
    - Give star if: secure record (surgical records, pharmacy records, EMR) or structured interview
*   **D4**: Outcome not present at start (* or -)
    - Look for: exclusion of patients with outcome at baseline
    - Give star if: demonstrated that outcome was not present at study start

**3. Evaluate Comparability (2 items):**
*   **D5**: Age comparability (* or -)
    - Look for: age matching or statistical adjustment for age
    - Give star if: matched in design OR adjusted in analysis (not just "no difference" statement)
*   **D6**: Additional comparability (* or -)
    - Look for: matching/adjustment for other key confounders (BMI, disease severity, comorbidities)
    - Give star if: matched in design OR adjusted in analysis for important factors beyond age

**4. Evaluate Outcome (3 items):**
*   **D7**: Assessment of Outcome (* or -)
    - Look for: outcome measurement method (blind assessment/secure records/self-report)
    - Give star if: independent blind assessment, secure records (lab results, imaging), or record linkage
*   **D8**: Enough follow-up (* or -)
    - Look for: duration of follow-up
    - Give star if: follow-up long enough for outcomes to occur (depends on disease/condition)
*   **D9**: Adequacy of follow up (* or -)
    - Look for: follow-up completion rate, description of losses
    - Give star if: complete follow-up OR ≥80% follow-up with description of losses
    - **Important**: If follow-up rate not reported or <80%, do NOT give star

For each item, determine if it meets the criteria for a star (*). If not, or if uncertain, mark as (-).

### Step 3: Format Data

Construct a JSON object with the results:

```json
{
  "Study": "Wang, 2018",
  "D1": "*",
  "D2": "-",
  "D3": "*",
  "D4": "*",
  "D5": "*",
  "D6": "-",
  "D7": "*",
  "D8": "*",
  "D9": "-"
}
```

**Scoring Notes:**
- Be conservative: If uncertain about meeting criteria, use "-"
- For D9 (follow-up adequacy): Common issue is lack of reported completion rate
- Document your reasoning for each item

### Step 4: Calculate Score and Generate Report

Run the python script to generate the final table:

```bash
python scripts/calculate_nos_score.py '<json_string>'
```

**Example:**
```bash
python scripts/calculate_nos_score.py "{\"Study\": \"Wei et al., 2026\", \"D1\": \"*\", \"D2\": \"*\", \"D3\": \"*\", \"D4\": \"*\", \"D5\": \"*\", \"D6\": \"*\", \"D7\": \"*\", \"D8\": \"*\", \"D9\": \"-\"}"
```

**Important**: JSON string must be properly escaped when passed via command line.

### Step 5: Generate Final Report

Return to user:
1. The generated Markdown table
2. Brief explanation of each scoring decision
3. Summary of study quality (High: ≥7 stars, Moderate: 4-6 stars, Low: <4 stars)
4. Key strengths and limitations

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `scripts/extract_pdf.py` to extract the text content before assessment:

**Features:**
- Extracts text from all pages
- Saves output to `extracted_text.txt`
- Handles path issues with spaces
- Provides progress feedback

**Usage:**
```bash
python scripts/extract_pdf.py "path/to/file.pdf"
```

**Output:**
- Console: Extraction progress and statistics
- File: `extracted_text.txt` in current working directory

## Quality Interpretation

| Score | Quality Level | Recommendation |
|-------|---------------|----------------|
| 9 stars | Excellent | Low risk of bias, high confidence |
| 7-8 stars | High quality | Acceptable for meta-analysis |
| 4-6 stars | Moderate quality | Consider in sensitivity analyses |
| <4 stars | Low quality | High risk of bias, use caution |

## Common Issues and Solutions

1. **PDF extraction fails**: Check if file exists and is not corrupted; try different PDF library (PyMuPDF)
2. **JSON parsing error**: Ensure proper escaping of quotes in command line
3. **Uncertain criteria**: When in doubt, be conservative and assign "-"
4. **Missing information**: Note in report that certain items could not be assessed

## References

- Detailed criteria: `references/nos_criteria.md`
- Wells GA, et al. The Newcastle-Ottawa Scale (NOS) for assessing the quality of nonrandomised studies in meta-analyses

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
- If a file is produced, prefer a deterministic output name such as `cohort_study_quality_assessment_nos_result.md` unless the skill documentation defines a better convention.
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
python scripts/calculate_nos_score.py --help
```

Expected output format:

```text
Result file: cohort_study_quality_assessment_nos_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
