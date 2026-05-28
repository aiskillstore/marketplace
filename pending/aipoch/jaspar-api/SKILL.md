---
name: jaspar-api
description: Access JASPAR database for transcription factor binding profiles (matrices), collections, and species via REST API. Use when user wants to search for transcription factors, retrieve matrix details (PFM/PWM), infer profiles from protein sequences, or explore JASPAR collections.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# JASPAR API

This skill provides access to the JASPAR database (https://jaspar.elixir.no/).

## When to Use

- Use this skill when you need access jaspar database for transcription factor binding profiles (matrices), collections, and species via rest api. use when user wants to search for transcription factors, retrieve matrix details (pfm/pwm), infer profiles from protein sequences, or explore jaspar collections in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/jaspar_client.py` is the most direct path to complete the request.
- Use this skill when you need the `jaspar-api` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Access JASPAR database for transcription factor binding profiles (matrices), collections, and species via REST API. Use when user wants to search for transcription factors, retrieve matrix details (PFM/PWM), infer profiles from protein sequences, or explore JASPAR collections.
- Packaged executable path(s): `scripts/jaspar_client.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Evidence Insight/jaspar-api"
python -m py_compile scripts/jaspar_client.py
python scripts/jaspar_client.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/jaspar_client.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/jaspar_client.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Usage

### 1. Search Matrices (Profiles)

Search for transcription factor binding profiles.

```bash
python scripts/jaspar_client.py matrix_list --search "SMAD3" --tax_group "Vertebrates"
```

Supported parameters:
- `--search`: Search term
- `--collection`: e.g., CORE, CNE
- `--tax_group`: e.g., Vertebrates, Plants
- `--tax_id`: e.g., 9606 (Human)
- `--tf_class`: Transcription factor class
- `--version`: `latest` (default) or specific
- `--page_size`: Results per page

### 2. Get Matrix Details

Retrieve details for a specific matrix ID (e.g., MA0001.1).

```bash
python scripts/jaspar_client.py matrix_read MA0001.1
```

### 3. Infer Profile from Sequence

Infer matrix profiles given a protein sequence.

```bash
python scripts/jaspar_client.py infer "SEQUENCE_STRING"
```

### 4. Collections and Species

List collections:
```bash
python scripts/jaspar_client.py collections_list
```

Get details for a species (by tax_id):
```bash
python scripts/jaspar_client.py species_read 9606
```

## References

See `references/api_docs.md` for full parameter lists and endpoint details.
