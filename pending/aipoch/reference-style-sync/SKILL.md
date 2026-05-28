---
name: reference-style-sync
description: One-click synchronization and standardization of reference formats in literature management tools, intelligently fixing metadata errors.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Reference Style Sync

One-click synchronization and standardization of reference formats in literature management tools, intelligently fixing metadata errors.

## When to Use

- Use this skill when the task needs One-click synchronization and standardization of reference formats in literature management tools, intelligently fixing metadata errors.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: One-click synchronization and standardization of reference formats in literature management tools, intelligently fixing metadata errors.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/reference-style-sync"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py -h
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

Reference Style Sync can:
- Automatically detect and fix erroneous metadata scraped in Zotero/EndNote
- Unify literature formats to standard citation styles (APA, MLA, AMA, Vancouver, etc.)
- Batch process entire literature libraries
- Intelligently complete missing fields (DOI, page numbers, volume/issue, etc.)
- Detect duplicate entries and merge them

## Supported Literature Management Tools

- **Zotero**: Supports RDF, BibTeX, CSL JSON, RIS format export
- **EndNote**: Supports XML, RIS, BibTeX format export
- **Universal Formats**: BibTeX, RIS, CSV, JSON

## Features

### 🔧 Metadata Repair
- Author name format standardization
- Journal name abbreviation/full name unification
- DOI format validation and completion
- Page number format normalization
- Date format unification

### 🎨 Format Sync
- Batch conversion to target citation format
- Field order standardization
- Punctuation unification
- Case normalization

### 🔍 Quality Check
- Missing field detection
- Duplicate entry identification
- Invalid DOI/URL marking
- Journal name spell checking

## Usage

### Command Line Interface

```text

# Process single file
python scripts/main.py --input library.bib --output fixed.bib --style apa

# Fix metadata and convert to AMA format
python scripts/main.py --input zotero.rdf --output fixed.ris --style ama --fix-metadata

# Batch processing and duplicate detection
python scripts/main.py --input library.json --output cleaned.json --deduplicate --style vancouver

# Quality check only
python scripts/main.py --input library.bib --check-only
```

### Python API

```python
from scripts.main import ReferenceSync

# Initialize
sync = ReferenceSync()

# Load library
sync.load('library.bib')

# Fix metadata
sync.fix_metadata()

# Convert to target format
sync.convert_style(target_style='apa')

# Export
sync.export('output.bib')
```

## Parameter Description

| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--input` | str | Required | Input file path (.bib, .ris, .json, .xml) |
| `--output` | str | Required | Output file path |
| `--style` | str | ama | Target format: apa, mla, ama, vancouver, chicago |
| `--fix-metadata` | bool | False | Enable metadata repair |
| `--deduplicate` | bool | False | Detect and merge duplicate entries |
| `--check-only` | bool | False | Check only, no output |
| `--format` | str | auto | Input format auto-detect or specify |

## Repair Rules

### Author Names
```python

# Before repair
Smith, John, Doe, Jane M.
Smith J., Doe J.M.

# After repair (AMA)
Smith J, Doe JM.
```

### Journal Names
```python

# Before repair
journal of the american medical association
J. Am. Med. Assoc.

# After repair
JAMA
```

### DOI
```python

# Before repair
www.doi.org/10.1234/example
doi:10.1234/example
10.1234/example

# After repair
doi:10.1234/example
```

### Page Numbers
```python

# Before repair
123-127
123 -- 127
123–127

# After repair
123-127
```

## Output Example

### Before Repair (Zotero Export)
```
@article{smith2020,
  author = {Smith, John and Doe, Jane M.},
  title = {A Study of Something},
  journal = {journal of clinical medicine},
  year = {2020},
  volume = {15},
  pages = {123-127},
  doi = {10.1234/example}
}
```

### After Repair (AMA Format)
```
@article{smith2020,
  author = {Smith J, Doe JM},
  title = {A Study of Something},
  journal = {J Clin Med},
  year = {2020},
  volume = {15},
  pages = {123-127},
  doi = {doi:10.1234/example}
}
```

## Technical Details

**Difficulty**: Medium  
**Dependencies**: Python 3.8+, regex, titlecase  
**Data Processing**: Supports 10000+ entries batch processing

## Supported Citation Formats

- **AMA**: American Medical Association (11th Edition)
- **APA**: American Psychological Association (7th Edition)
- **MLA**: Modern Language Association (9th Edition)
- **Vancouver**: ICMJE Recommended Format
- **Chicago**: Chicago Manual of Style (17th Edition)
- **IEEE**: Institute of Electrical and Electronics Engineers

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Notes

1. It is recommended to backup the original library before processing
2. Metadata repair is based on built-in rule library; complex cases may require manual review
3. Journal abbreviations follow ISO 4 standard
4. DOI validation uses regex patterns, does not actually resolve and verify

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited

## Prerequisites

```text

# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Input Validation

This skill accepts requests that match the documented purpose of `reference-style-sync` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `reference-style-sync` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References

- [references/audit-reference.md](references/audit-reference.md) - Supported scope, audit commands, and fallback boundaries

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
