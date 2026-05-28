---
name: ensembl-database
description: Access Ensembl REST API for vertebrate genomic data; use when you need gene/ID lookups, sequence retrieval, variant effect prediction (VEP), or homology/assembly coordinate mapping.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Ensembl Database Skill

## When to Use

- Use this skill when you need access ensembl rest api for vertebrate genomic data; use when you need gene/id lookups, sequence retrieval, variant effect prediction (vep), or homology/assembly coordinate mapping in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/query_ensembl.py` is the most direct path to complete the request.
- Use this skill when you need the `ensembl-database` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Access Ensembl REST API for vertebrate genomic data; use when you need gene/ID lookups, sequence retrieval, variant effect prediction (VEP), or homology/assembly coordinate mapping.
- Packaged executable path(s): `scripts/query_ensembl.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/ensembl-database"
python -m py_compile scripts/query_ensembl.py
python scripts/query_ensembl.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/query_ensembl.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/query_ensembl.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

- **Gene-centric queries**: When you need to resolve a gene symbol or region to Ensembl identifiers and basic annotations (e.g., `BRCA2` in human).
- **Sequence extraction**: When you need DNA/cDNA/protein sequences for a known Ensembl gene/transcript/protein ID in FASTA or JSON.
- **Variant interpretation**: When you need to predict functional consequences of variants using **VEP** from HGVS notation.
- **Comparative genomics**: When you need ortholog/paralog relationships across vertebrate species.
- **Assembly/coordinate mapping**: When you need to map coordinates between assemblies (e.g., GRCh37 ↔ GRCh38).

## 2. Key Features

- Query Ensembl REST endpoints for:
  - **Gene lookup** by symbol, Ensembl ID, or genomic region
  - **Sequence retrieval** (DNA, cDNA, protein) in FASTA/JSON
  - **Variant Effect Predictor (VEP)** analysis from HGVS inputs
  - **Homology** retrieval (orthologs/paralogs)
  - **Assembly/coordinate mapping** between common human assemblies
- CLI helper script for repeatable queries:
  - `scripts/query_ensembl.py` (wrapper around an `ensembl_rest` client)
- Reference documentation for endpoints:
  - `references/api_endpoints.md`
  - Ensembl REST base URL: https://rest.ensembl.org

## 3. Dependencies

- Python `>=3.8`
- `ensembl_rest` (Python client; version depends on your environment)
- Network access to `https://rest.ensembl.org`

## 4. Example Usage

### CLI: Gene lookup by symbol

```bash
python scripts/query_ensembl.py --action lookup --species human --symbol BRCA2
```

### CLI: Retrieve sequence by Ensembl ID

```bash
python scripts/query_ensembl.py --action sequence --id ENSG00000139618
```

### CLI: Variant effect prediction (VEP) by HGVS

```bash
python scripts/query_ensembl.py --action vep --species human --hgvs "ENST00000380152.8:c.68_69delAG"
```

## 5. Implementation Details

### Script entry point

- **Tool**: `scripts/query_ensembl.py`
- **Purpose**: Provide a simple command-line interface that dispatches to Ensembl REST calls via an `ensembl_rest` client.

### Core parameters

- `--action`: Operation selector.
  - Supported values: `lookup`, `sequence`, `vep`
- `--species`: Target species name used by Ensembl REST (e.g., `human`).
- `--symbol`: Gene symbol used for lookup actions (e.g., `BRCA2`).
- `--id`: Ensembl stable ID used for sequence retrieval (e.g., `ENSG...`, `ENST...`, `ENSP...`).
- `--hgvs`: HGVS notation string used for VEP (e.g., `ENST...:c.123A>G`).

### Data types and outputs

- **Lookup**: Returns gene/transcript metadata as provided by Ensembl REST.
- **Sequence**: Returns DNA/cDNA/protein sequence; format depends on the endpoint/options (commonly FASTA or JSON).
- **VEP**: Returns consequence annotations and (when available) population frequency fields as provided by Ensembl VEP REST responses.

### Endpoint reference

For the exact REST paths, required parameters, and response schemas, see:
- `references/api_endpoints.md`
- https://rest.ensembl.org
