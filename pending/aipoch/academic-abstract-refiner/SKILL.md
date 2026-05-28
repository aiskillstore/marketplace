---
name: academic-abstract-refiner
description: Refines long medical academic texts into SCI-style unstructured Chinese and English abstracts; use when you need to condense drafts/reports/summaries into bilingual abstracts and generate Summary_Report.md.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/refine_abstract.py --help
```

# academic-abstract-refiner

## When to Use

- Converting a long medical review draft into a concise, SCI-style unstructured abstract (single paragraph).
- Summarizing experimental or clinical study reports into bilingual (Chinese/English) abstracts for submission or internal review.
- Condensing multi-paper literature notes or evidence syntheses into a publication-ready abstract without section headers.
- Producing a standardized Markdown deliverable (`Summary_Report.md`) that contains both Chinese and English abstracts.
- Ensuring the abstract content strictly reflects the source text (no invented data, outcomes, or conclusions).

## Key Features

- Generates **unstructured** (single-paragraph) abstracts in **Chinese and English**.
- Enforces an **academic, formal tone** aligned with SCI journal abstract conventions.
- Produces a single Markdown report: **`Summary_Report.md`**.
- Script-based rendering that **does not call any model APIs** and **requires no API key**.
- Supports input as long plain text (e.g., `.txt` content or pasted text) and outputs a clean report.

## Dependencies

- Python `>=3.8`

## Example Usage

Generate the final report after you already have the refined abstracts (produced by the agent):

```bash
python scripts/refine_abstract.py \
  --abstract-zh "（、）。" \
  --abstract-en "Paste the English abstract here (single paragraph, no subheadings)." \
  --output Summary_Report.md
```

Expected output:

- `Summary_Report.md` containing:
  - Chinese abstract
  - English abstract

## Implementation Details

- **Input/Output contract**
  - Inputs are two strings: `--abstract-zh` and `--abstract-en`.
  - Output is a Markdown file path via `--output` (default: `Summary_Report.md`).

- **Abstract format constraints**
  - Both abstracts must be **unstructured**: a **single paragraph** without fixed templates such as *Objective/Methods/Results/Conclusion*.
  - Language should remain **formal and academic**, consistent with SCI abstract style.

- **Content integrity rules**
  - The abstracts must be derived **only from the original source text**.
  - Do **not** fabricate numerical results, experimental details, or conclusions not present in the source.

- **Execution model**
  - The rendering script is a local formatter/writer: it **does not invoke any LLM** and **does not require API credentials**.
  - All abstract generation/refinement is assumed to be completed by the agent prior to running the script.

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
- If a file is produced, prefer a deterministic output name such as `academic_abstract_refiner_result.md` unless the skill documentation defines a better convention.
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
python scripts/refine_abstract.py --help
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
