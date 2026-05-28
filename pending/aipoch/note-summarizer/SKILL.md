---
name: note-summarizer
description: Organize study notes into a structured knowledge-point outline and export to a .docx summary when you need a shareable, hierarchical document from Word/PPT/Text/Markdown inputs.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Note Summarizer

## When to Use

- Use this skill when you need organize study notes into a structured knowledge-point outline and export to a .docx summary when you need a shareable, hierarchical document from word/ppt/text/markdown inputs in a reproducible workflow.
- Use this skill when a others task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/note_summarizer.py` is the most direct path to complete the request.
- Use this skill when you need the `note-summarizer` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Organize study notes into a structured knowledge-point outline and export to a .docx summary when you need a shareable, hierarchical document from Word/PPT/Text/Markdown inputs.
- Packaged executable path(s): `scripts/note_summarizer.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/note-summarizer"
python -m py_compile scripts/note_summarizer.py
python scripts/note_summarizer.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/note_summarizer.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/note_summarizer.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use
- When you have class notes (Word/Markdown/text) and need a clean outline with key takeaways per section.
- When you need to merge notes from multiple sources (e.g., Word + PPT + Markdown) into one unified study summary.
- When you want to preserve the original heading hierarchy (H1/H2/H3) while summarizing content into bullet points.
- When you need to include images from the source materials in the corresponding sections of the exported Word document.
- When you need an offline, local-file-only summarization workflow for study materials.

## 2. Key Features
- Multi-format input support: **.docx**, **.pptx**, **.txt**, **.md**.
- Exports a **Word (.docx)** document with a structured outline (Heading 1/2/3).
- Generates **key-point bullet summaries** per section with a configurable limit.
- Optional **heading hierarchy preservation** to keep the original structure.
- Optional **image handling**: copy images into the output or skip them.
- Local-only processing (no network access) and minimal logging of user content.

## 3. Dependencies
- Python (recommended): **3.9+**
- Python packages:
  - **python-docx** (latest compatible)
  - **python-pptx** (latest compatible)
  - **Pillow** (latest compatible)

Install:
```bash
python -m pip install python-docx python-pptx pillow
```

## 4. Example Usage

### Interactive run
```bash
python scripts/note_summarizer.py
```

### Run with a JSON config (recommended)
1) Create `input.json`:
```json
{
  "inputs": ["notes.docx", "slides.pptx", "notes.md"],
  "output": "summary.docx",
  "keep_headings": true,
  "max_bullets_per_section": 6,
  "image_mode": "copy",
  "max_image_long_edge": 1600
}
```

2) Execute:
```bash
python scripts/note_summarizer.py --json input.json
```

## 5. Implementation Details

### Input schema
**Required**
- `inputs`: array of input file paths (Word/PPT/Text/Markdown)
- `output`: output `.docx` file path

**Optional**
- `keep_headings` (boolean, default: `true`): attempts to preserve heading hierarchy from source documents.
- `max_bullets_per_section` (int, default: `6`): maximum number of summary bullets generated per section.
- `image_mode` (`"copy"` | `"skip"`, default: `"copy"`): whether to copy images into the output document.
- `max_image_long_edge` (int, default: `1600`): maximum pixel size for the long edge when copying images.

### Output structure
- A Word document containing:
  - Heading levels (Heading 1/2/3) representing the outline
  - Bullet lists of key points under each section
  - Images copied into the relevant sections when `image_mode: "copy"`

### Security / compliance notes
- Processes **local files only** and does not access the network.
- Reads only user-provided paths and writes only to the specified output path.
- Avoids logging or emitting sensitive content from user files into logs.

### Basic verification
```bash
python scripts/note_summarizer.py --json examples/example.json
```

Success criteria:
- The output `.docx` exists and opens successfully.
- The heading hierarchy and per-section key points are present and correctly structured.
