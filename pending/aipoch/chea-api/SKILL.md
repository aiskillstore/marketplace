---
name: chea-api
description: Access ChEA3 and Harmonizome ChEA data for transcription factor enrichment analysis and metadata retrieval. Use when the user needs to perform ChEA3 enrichment analysis on a gene set, get metadata about the ChEA dataset, or retrieve information about a specific transcription factor (attribute).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# ChEA API Skill

This skill provides programmatic access to the ChEA3 enrichment analysis API and Harmonizome ChEA dataset metadata.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Access ChEA3 and Harmonizome ChEA data for transcription factor enrichment analysis and metadata retrieval. Use when the user needs to perform ChEA3 enrichment analysis on a gene set, get metadata about the ChEA dataset, or retrieve information about a specific transcription factor (attribute).
- Packaged executable path(s): `scripts/chea_client.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Evidence Insight/chea-api"
python -m py_compile scripts/chea_client.py
python scripts/chea_client.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/chea_client.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/chea_client.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Usage

### 1. Enrichment Analysis

Perform enrichment analysis on a list of genes to identify associated transcription factors.

**Script**: `scripts/chea_client.py`
**Command**: `enrich`

```python
import json
import sys

# Add scripts directory to path if needed, or run as subprocess
sys.path.append('scripts')
from chea_client import enrich

genes = ["FOXM1", "SMAD9", "MYC", "SMAD3", "STAT1", "STAT3"]
results = enrich(genes, query_name="my_analysis")
print(json.dumps(results, indent=2))
```

### 2. Get Dataset Metadata

Retrieve metadata for the ChEA dataset from Harmonizome.

**Script**: `scripts/chea_client.py`
**Command**: `metadata`

```python
from chea_client import get_dataset_metadata

metadata = get_dataset_metadata()
print(json.dumps(metadata, indent=2))
```

### 3. Get Attribute (Transcription Factor) Info

Get details about a specific transcription factor (Attribute) from Harmonizome.

**Script**: `scripts/chea_client.py`
**Command**: `attribute`

```python
from chea_client import get_attribute_info

# Example: Get info for CREB1
info = get_attribute_info("CREB1")
print(json.dumps(info, indent=2))
```

## CLI Usage

You can also run the script directly from the command line:

```bash

# Enrichment
python scripts/chea_client.py enrich FOXM1 SMAD9 MYC

# Metadata
python scripts/chea_client.py metadata

# Attribute Info
python scripts/chea_client.py attribute CREB1
```

## Requirements

- Python 3
- `requests` library (`pip install requests`)

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
- If a file is produced, prefer a deterministic output name such as `chea_api_result.md` unless the skill documentation defines a better convention.
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
python scripts/chea_client.py --help
```

Expected output format:

```text
Result file: chea_api_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
