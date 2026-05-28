---
name: study-design-scale-selector
description: Determines the appropriate Risk of Bias assessment scale for a medical study based on its design (RCT, Cohort, etc.), using PubMed metadata lookup or text analysis. Use when the user wants to know which quality assessment tool to use for a specific paper (given PMID or abstract).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Study Design Scale Selector

This skill helps identify the study design of a medical paper and selects the appropriate risk of bias assessment scale.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Determines the appropriate Risk of Bias assessment scale for a medical study based on its design (RCT, Cohort, etc.), using PubMed metadata lookup or text analysis. Use when the user wants to know which quality assessment tool to use for a specific paper (given PMID or abstract).
- Packaged executable path(s): `scripts/extract_pdf.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/study-design-scale-selector"
python -m py_compile scripts/extract_pdf.py
python scripts/extract_pdf.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/extract_pdf.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/extract_pdf.py` with additional helper scripts under `scripts/`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Workflow

### 1. Check Metadata (If PMID provided)

If the user provides a PMID, use the `selector.py` script to fetch study metadata from PubMed.

```bash
python scripts/selector.py "<PMID>"
```

**If the script returns a non-empty JSON with `study_design`:**
- Use the returned `study_design`.
- Skip to **Step 3**.

**If the script returns empty JSON `{}` or fails:**
- Proceed to **Step 2**.

### 2. Analyze Text (Fallback)

If metadata is unavailable or no PMID is provided, analyze the Title and Abstract provided by the user.

**Action:**
Identify the study design from the text. Look for keywords like:
- "Randomized controlled trial", "RCT"
- "Cohort study", "Longitudinal study"
- "Case-control study"
- "Cross-sectional study"

### 3. Select Scale

Using the identified `study_design`, consult [scale_rules.md](references/scale_rules.md) to select the correct assessment scale.

### 4. Output

Present the result in the following JSON format:

```json
{
  "study_design": "<Identified Design>",
  "scale": "<Selected Scale>"
}
```

## Helper Scripts

### PDF Text Extraction

When the user provides a PDF file path, use `extract_pdf.py` to extract the text content before assessment:

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
- If a file is produced, prefer a deterministic output name such as `study_design_scale_selector_result.md` unless the skill documentation defines a better convention.
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
python scripts/extract_pdf.py --help
```

Expected output format:

```text
Result file: study_design_scale_selector_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
