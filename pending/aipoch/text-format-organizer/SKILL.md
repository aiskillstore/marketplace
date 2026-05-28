---
name: text-format-organizer
description: A local text formatting organizer for biomedical/academic writing; use it when you need to clean whitespace/line endings while preserving Markdown structures or when normalizing .docx/.md/.txt before submission or proofreading.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/init_run.py --help
```

## When to Use

- Cleaning biomedical manuscripts where extra blank lines, trailing spaces, or mixed line endings break journal templates.
- Normalizing Markdown notes (lists/tables/code blocks) before converting to PDF/Word.
- Formatting clinical research reports or protocol records exported from multiple editors (Windows/macOS/Linux).
- Pre-processing `.docx` drafts before running downstream proofreading/QA tools (e.g., `academic-proofreader`).
- Preparing theses/dissertations to enforce consistent indentation and whitespace rules across chapters.

## Key Features

- **Intelligent cleaning**
  - Removes redundant empty lines while keeping paragraph boundaries.
  - Strips trailing whitespace while preserving leading indentation.
  - Unifies line endings (`unix`, `windows`, `mac`).
  - Converts tabs to spaces (configurable indentation size).
- **Structure protection**
  - Preserves Markdown list structures (`-`, `*`, `1.`).
  - Keeps fenced code blocks (``` ... ```) unchanged.
  - Preserves Markdown table formatting.
- **Multi-format I/O**
  - Supports `.txt`, `.md`, and `.docx` input/output.

## Dependencies

- `python >= 3.8`
- `python-docx >= 1.0.0`

## Example Usage

### 1) Format a Markdown or text file

```bash
python scripts/init_run.py --input input.md --output output.md
```

### 2) Format a Word document

```bash
python scripts/init_run.py -i paper.docx -o paper_clean.docx
```

### 3) Preview changes without writing output

```bash
python scripts/init_run.py -i input.md --preview
```

### 4) Programmatic usage (core module)

```python
from scripts.text_formatter import TextFormatter, FormatOptions

text = "Line with trailing spaces   \n\n\n- item 1\n\t- item 2\n"
options = FormatOptions(
    line_ending="unix",
    indent="spaces",
    indent_size=4,
)

formatter = TextFormatter(options=options)
formatted = formatter.format(text)
print(formatted)
```

### 5) Workflow with an academic proofreading tool

```bash
# Step 1: Format organization
python scripts/init_run.py -i paper.docx -o paper_clean.docx

# Step 2: Content/format checking (separate project)
cd ../academic-proofreader
python scripts/init_run.py -i paper_clean.docx
```

## Implementation Details

### CLI parameters

| Parameter | Description | Default |
|---|---|---|
| `--input` / `-i` | Input file path (`.txt` / `.md` / `.docx`) | Required |
| `--output` / `-o` | Output file path | Auto-generated |
| `--line-ending` | Line ending: `unix` / `windows` / `mac` | `unix` |
| `--indent` | Indentation type: `spaces` / `tabs` | `spaces` |
| `--indent-size` | Number of spaces per indent level | `4` |
| `--preview` | Preview mode (no output written) | `false` |
| `--docx-font` | Font used for Word output | `Times New Roman` |
| `--docx-size` | Font size used for Word output | `12` |

### Formatting rules (high level)

- **Whitespace normalization**
  - Collapses excessive blank lines while preserving paragraph separation.
  - Removes trailing spaces at line ends; does not remove leading indentation.
- **Line ending normalization**
  - Converts all line endings to the selected target (`unix`/`windows`/`mac`).
- **Indentation normalization**
  - Converts tab characters to spaces when `indent=spaces`, using `indent_size`.
- **Markdown-safe processing**
  - Skips transformations inside fenced code blocks.
  - Preserves list markers and table pipes/alignment to avoid structural breakage.
- **DOCX handling**
  - Reads `.docx`, applies the same normalization at the text/paragraph level, then writes a new `.docx` using the configured font and size.

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
- If a file is produced, prefer a deterministic output name such as `text_format_organizer_result.md` unless the skill documentation defines a better convention.
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
python scripts/init_run.py --help
```

Expected output format:

```text
Result file: text_format_organizer_result.md
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
