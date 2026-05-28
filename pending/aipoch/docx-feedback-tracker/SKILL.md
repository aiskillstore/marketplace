---
name: docx-feedback-tracker
description: Automatically detect DOCX track-changes history, version rounds, and author feedback to generate a Markdown modification explanation file when you run it on one or more DOCX versions.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# DOCX Feedback Tracker

## When to Use

- You receive a DOCX with **Track Changes** and/or **Comments** enabled and need a consolidated change log by author.
- You have multiple DOCX versions (e.g., `-v1`, `-v2`, `-v3`) and want to reconstruct **round-based** modifications into a single report.
- A document has **no Track Changes**, but you still need **added/deleted** content via version-to-version text diffs.
- You want to generate a **Markdown modification explanation** automatically and save it next to the original DOCX files.
- You need to batch-process a folder of DOCX files and group them by topic into one change-log output per topic series.

## Key Features

- Detect and attribute changes to **track-changes authors** and **comment authors**.
- Extract **insertions** and **deletions** from DOCX OOXML (`w:ins` / `w:del`) and comments.
- Fallback to **version diffs** when track changes are absent (changes are then not attributable to specific authors).
- Group files by **topic series** and generate only one `<topic>-change-log.md` per series.
- Write output Markdown to the **same directory** as the inspected DOCX file(s).

## Dependencies

- Python 3.x
- No additional pinned third-party dependencies are specified in the provided documentation.

## Example Usage

### Single DOCX file

```bash
python script/docx_feedback_tracker.py "path\file.docx"
```

### Multiple DOCX versions (ordered rounds)

```bash
python script/docx_feedback_tracker.py "path\file-v1.docx" "path\file-v2.docx" "path\file-v3.docx"
```

### Batch process a directory

```bash
python script/docx_feedback_tracker.py --dir "path" --pattern "*.docx"
```

### Output

- **Grouping rule**: for the same topic series, only one Markdown file is generated:
  - `<topic>-change-log.md`
- **Output location**: the generated Markdown is saved in the **same directory** as the DOCX file(s).

## Implementation Details

- Entry script: `script/docx_feedback_tracker.py`
- Topic grouping and version-round ordering:
  - Files are grouped by the same base topic name.
  - Unmarked versions are treated as **v0**.
  - Version suffixes supported:
    - `-vN` (e.g., `report-v2.docx`)
    - `-N` (e.g., `report-2.docx`) — only applied when a same-name base exists.
  - If suffix-based ordering cannot be determined, files are sorted by **file timestamp**.
- Track changes and comments parsing:
  - Extract OOXML change nodes from:
    - `document.xml`
    - `comments.xml`
  - Primary markers:
    - `w:ins` for inserted content
    - `w:del` for deleted content
- Diff fallback when no track changes exist:
  - Perform text diffs between versions to compute added/deleted content.
  - Changes from diffs are **not attributable** to specific authors.
  - Before diffing, text is normalized to reduce false positives:
    - remove link tags
    - merge/normalize whitespace
- Output generation:
  - Produce a Markdown "modification explanation" and merge all rounds into a single file per topic series.
  - Template reference: `assets/change-log-template.md`
- OOXML reference for tracked changes:
  - `references/docx-tracked-changes.md`

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
- If a file is produced, prefer a deterministic output name such as `docx_feedback_tracker_result.md` unless the skill documentation defines a better convention.
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
Result file: docx_feedback_tracker_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
