---
name: file-search
description: Perform fast file name and content searches with ripgrep (rg); use it when you need to locate files by glob/regex, find keywords across directories, or replace common find/grep workflows.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to list files matching a pattern (e.g., `*.rs`, `*.md`) across a project quickly.
- You want to find occurrences of a keyword/regex (e.g., `TODO|FIXME`) across one or more directories.
- You need contextual matches (lines before/after) to understand how a symbol or string is used.
- You want a faster, simpler replacement for typical `find` + `grep` pipelines.
- You need to narrow searches by file type (e.g., Rust-only) while scanning large repositories.

## Key Features

- File name discovery via `rg --files` combined with `--glob` filters.
- Content search using regex patterns with high performance.
- Context output around matches (e.g., `-C 3`) for quick inspection.
- Optional type filtering (e.g., `--type rust`) to reduce noise.
- Simple pre-check workflow to ensure `rg` is available before running searches.

## Dependencies

- ripgrep (rg) >= 13.0.0
- Python >= 3.8 (only required to run `scripts/test_skill.py`)

## Example Usage

```bash
# 1) Pre-check: ensure ripgrep is installed
rg --version

# 2) (Optional) Run the skill self-check script
python scripts/test_skill.py

# 3) Search by file name (list Rust files under a directory)
rg --files --glob "*.rs" /path/to/projects

# 4) Search by content (regex search across a directory)
rg "TODO|FIXME" /path/to/projects

# 5) Search by content with context and type filtering
rg -C 3 "fn main" /path/to/projects --type rust
```

## Implementation Details

- **File name search**: uses `rg --files` to enumerate files, then applies `--glob` to include/exclude paths (e.g., `--glob "*.rs"`).
- **Content search**: `rg PATTERN PATH` performs a regex search; patterns like `TODO|FIXME` use alternation.
- **Context control**: `-C N` prints `N` lines of leading and trailing context around each match to aid quick review.
- **Type filtering**: `--type <name>` restricts scanning to known file type definitions (e.g., `rust`), reducing irrelevant matches.
- **Pre-check behavior**: if `rg` is not available, prompt to install ripgrep before proceeding with any search commands.

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
- If a file is produced, prefer a deterministic output name such as `file_search_result.md` unless the skill documentation defines a better convention.
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
Result file: file_search_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Perform fast file name and content searches with ripgrep (rg); use it when you need to locate files by glob/regex, find keywords across directories, or replace common find/grep workflows.
