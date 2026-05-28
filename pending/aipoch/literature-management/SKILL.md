---
name: literature-management
description: Import local literature into a managed library; trigger when you need offline deduplication, tagging, and a searchable index.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a batch of locally downloaded papers (PDF/BibTeX/RIS/CSV/TXT) that must be organized into a consistent library structure.
- You need **offline** deduplication using DOI or normalized *Title + Year* to avoid repeated entries.
- You want to apply **manual tags** at import time and also derive tags from available metadata keywords.
- You need a local, appendable **search index** (`index.jsonl`) for later retrieval and filtering.
- You must operate in an environment where **network access is not allowed** and all processing must remain local.

## Key Features

- Local-only import into a managed literature library directory.
- Deterministic deduplication with clear priority rules (DOI → Title+Year → file hash).
- Tagging support:
  - manual tags via CLI flags
  - automatic tags from metadata keywords (when present)
- Searchable index generation and maintenance via `index.jsonl` (one JSON object per line).
- Predictable file organization by year and journal, with safe handling of naming conflicts.
- Security/compliance-friendly behavior: no external APIs, no credentials, no network calls.

## Dependencies

- Python **3.9+**
- Python packages (install via requirements file):
  - `pip install -r scripts/requirements.txt`

## Example Usage

```bash
# 1) Choose a source directory containing local literature files
SOURCE_DIR="/path/to/downloads"

# 2) Choose (or create) a target library directory managed by this skill
LIBRARY_DIR="/path/to/literature-library"

# 3) Import with optional manual tags (repeatable)
python scripts/import_library.py \
  --source-dir "$SOURCE_DIR" \
  --library-dir "$LIBRARY_DIR" \
  --tag "survey" \
  --tag "to-read"
```

After running, verify:

- Organized files under:
  - `"$LIBRARY_DIR/files/<Year>/<Journal>/..."`
- Index file:
  - `"$LIBRARY_DIR/index.jsonl"`
- The import/deduplication/error summary printed by the script.

Additional examples may be available in: `references/examples.md`.

## Implementation Details

### Inputs

- **Source directory**: contains one or more of `.pdf`, `.bib`, `.ris`, `.csv`, `.txt`
- **Target library directory**: the managed library root
- **Manual tags** (optional): provided via repeated `--tag "<tag>"`

### Outputs

- Organized literature files written into the target library directory
- `index.jsonl` created/appended in the library root
- A summary of imported items, deduplicated items, and errors

### Index Data Model (`index.jsonl`)

Each line is a single JSON record with (at minimum) the following fields:

- `id`, `title`, `year`, `journal`, `authors`, `keywords`, `doi`, `tags`
- `source_type`, `source_path`, `file_path`
- `dedup_key`, `dedup_rule`, `imported_at`

### Deduplication Algorithm

Deduplication is applied in the following priority order:

1. **DOI** (primary)
   - Case-insensitive comparison after normalization.
2. **Title + Year** (secondary)
   - Title is normalized (e.g., whitespace/case normalization) and combined with year.
3. **File hash** (fallback)
   - Used only when DOI and Title+Year are unavailable.

The chosen rule is recorded in `dedup_rule`, and the computed key is stored in `dedup_key`.

### Tagging Rules

- All `--tag` values are **always applied** to imported records.
- If metadata includes `keywords`, they are converted into tags and merged with manual tags.

### File Organization Rules

- Target path pattern:
  - `<library>/files/<Year>/<Journal>/`
- Unknown values are mapped to:
  - `UnknownYear`, `UnknownJournal`
- Filenames are preserved when possible; if a conflict occurs, a suffix is appended to avoid overwriting.

### Security / Compliance Constraints

- No network access is used or required.
- No external APIs or credentials are used.
- The tool only reads from the specified `--source-dir`.
- The tool only writes within the specified `--library-dir` (no writes outside the library root).

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
- If a file is produced, prefer a deterministic output name such as `literature_management_result.md` unless the skill documentation defines a better convention.
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
python scripts/import_library.py --help
```

Expected output format:

```text
Result file: literature_management_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
