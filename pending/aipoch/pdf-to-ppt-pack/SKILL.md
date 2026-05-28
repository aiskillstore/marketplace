---
name: pdf-to-ppt-pack
description: Convert research paper PDFs into literature-report PPTX decks using a fully offline workflow (extract text/figures, map captions, summarize findings, and generate slides). Use when you need to turn a PDF into a presentation deck, especially for scientific articles with figures and tables.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Convert research paper PDFs into literature-report PPTX decks using a fully offline workflow (extract text/figures, map captions, summarize findings, and generate slides). Use when you need to turn a PDF into a presentation deck, especially for scientific articles with figures and tables.
- Packaged executable path(s): `scripts/validate_skill.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `python-pptx`: `>=0.6.21`. Declared in `ppt/requirements.txt`.
- `lxml`: `>=4.9.0`. Declared in `ppt/requirements.txt`.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/pdf-to-ppt-pack"
python -m py_compile scripts/validate_skill.py
python scripts/validate_skill.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/validate_skill.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/validate_skill.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# PDF To PPT Pack

## 1. When to Use

- You are asked to convert a research paper PDF into a PPTX presentation deck.
- You need an offline (local-only) workflow to extract figures and text and generate slides.
- You are preparing a journal club / literature report deck with one slide per figure plus interpretation.
- The paper contains many figures/tables and you need caption-to-image mapping to stay consistent.
- You want a repeatable pipeline where you can refine titles/mappings and regenerate the PPTX.

## 2. Key Features

- Offline PDF processing: no external services required.
- Extracts paper text and figure images from a PDF into a structured "offline directory".
- Captures figure-caption hits to help map captions/legends to extracted images.
- Builds a PPTX deck following predefined layout rules (title/overview/figure slides/summary).
- Supports iterative refinement: adjust figure titles and rerun generation.

## 3. Dependencies

- Python 3.10+ (recommended)
- Local scripts (repository-provided):
  - `tools/extract_pdf_figures.py`
  - `tools/build_cell_reports_ppt_offline.py`

## 4. Example Usage

### Step 1 — Extract figures and text

This generates (in the output directory):

- `Figure_*.jpg`
- `Graphical abstract.jpg` (if present)
- `extracted_text.txt`
- `figure_legend_hits.txt`

```powershell
python "tools/extract_pdf_figures.py" --pdf "D:/path/paper.pdf" --outdir "D:/path/offline_dir"
```

### Step 2 — Build the PPTX from the extracted directory

```powershell
python "tools/build_cell_reports_ppt_offline.py" --base-dir "D:/path/offline_dir" --output "D:/path/output.pptx"
```

### Step 3 — Validate and refine, then rerun if needed

- Confirm each slide title is short and readable.
- Verify each figure slide uses the correct image for the corresponding caption/legend.
- If a title is too long, edit `figure_titles_zh.txt` inside the offline directory and rerun Step 2.

## 5. Implementation Details

### Pipeline structure

1. **Extraction phase** (`tools/extract_pdf_figures.py`)
   - Reads the input PDF.
   - Exports figure images (e.g., `Figure_1.jpg`, `Figure_2.jpg`, …).
   - Exports a graphical abstract image if detected.
   - Writes extracted paper text to `extracted_text.txt`.
   - Produces `figure_legend_hits.txt` to assist with caption/legend matching.

2. **Deck generation phase** (`tools/build_cell_reports_ppt_offline.py`)
   - Consumes the "offline directory" produced by the extraction phase.
   - Builds a PPTX deck using the repository's layout framework.

### Expected slide structure

- **Slide 1**: Title, journal/date, presenter, report date.
- **Slide 2**: Overview (background + key findings) and graphical abstract (if available).
- **Middle slides**: One slide per figure, with concise interpretation aligned to the figure.
- **Final slide**: Summary and limitations.

### Repository resources

- `tools/`: extraction and PPT building scripts.
- `ppt/`: layout and animation framework.
- `PPTX/`: PPTX editing utilities and guidelines.
- `pdf-extract/`: PDF extraction helpers.

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
- If a file is produced, prefer a deterministic output name such as `pdf_to_ppt_pack_result.md` unless the skill documentation defines a better convention.
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
Result file: pdf_to_ppt_pack_result.md
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
