---
name: gene-info
description: "Retrieves comprehensive gene information including PubMed publication counts, NCBI summaries, and Ensembl transcript data. Supports batch processing and file input. Invoke when the user asks for gene details, publication statistics, or needs to analyze a list of genes."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Retrieves comprehensive gene information including PubMed publication counts, NCBI summaries, and Ensembl transcript data. Supports batch processing and file input. Invoke when the user asks for gene details, publication statistics, or needs to analyze a list of genes.".
- Packaged executable path(s): `scripts/fetch_gene_info.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Evidence Insight/gene-info"
python -m py_compile scripts/fetch_gene_info.py
python scripts/fetch_gene_info.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/fetch_gene_info.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/fetch_gene_info.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# Gene Information Tool

This skill retrieves detailed information for specific genes from authoritative databases (NCBI PubMed, NCBI Gene, Ensembl). It supports single-gene queries, batch processing, and file-based input.

## Capabilities

- **PubMed Statistics**: Retrieves total publication counts and counts for specific keywords.
- **Gene Summary**: Fetches official gene descriptions and summaries from NCBI.
- **Transcript Data**: Retrieves transcript counts and maximum amino acid sequence lengths from Ensembl.
- **Batch Processing**: Efficiently queries multiple genes in parallel.
- **File Input**: Supports reading gene lists from text files.
- **Data Export**: Supports saving results to JSON or CSV formats.

## Usage

To use this skill, run the provided Python script with gene symbols.

### Prerequisites

NCBI recommends providing an email address to contact you in case of excessive usage. You can also optionally provide an API key for higher rate limits.

Set the following environment variables (recommended):
- `NCBI_EMAIL`: Your email address (Recommended)
- `NCBI_API_KEY`: Your NCBI API Key (Optional)

Or provide them via command line arguments:
- `--email <your_email>` (Recommended)
- `--api-key <your_api_key>` (Optional)

### Basic Usage (Single Gene)

```bash
python .trae/skills/gene-info/scripts/fetch_gene_info.py BRCA1
```

### With Keyword Search (for PubMed)

```bash
python .trae/skills/gene-info/scripts/fetch_gene_info.py BRCA1 --keyword "breast cancer"
```

### Batch Processing (Multiple Genes)

```bash
python .trae/skills/gene-info/scripts/fetch_gene_info.py BRCA1 TP53 EGFR --keyword "mutation"
```

### File Input

Create a file containing a list of genes (supports multiple formats), then run:

**Supported Formats**:
- Plain text list (one per line)
- CSV/TSV files (automatically detects columns named "Gene" or "Symbol")
- Free text (comma, space, or semicolon separated)

Example `genes.txt`:
```text
BRCA1
TP53
EGFR
```

Command:
```bash
python .trae/skills/gene-info/scripts/fetch_gene_info.py --file genes.txt --keyword "cancer"
```

### Export Results

Save results to a CSV or JSON file:

```bash
python .trae/skills/gene-info/scripts/fetch_gene_info.py BRCA1 TP53 --output results.csv
```

## Output Format

The script outputs a JSON array containing objects with the following fields:
- `gene`: Gene symbol
- `totalPublications`: Total PubMed publications
- `keywordPublications`: Publications matching gene + keyword (if keyword provided)
- `summary`: Gene summary text
- `transcriptCount`: Number of transcripts
- `maxAminoAcids`: Maximum amino acid length
- `chromosome`: Chromosome location
- `organism`: Organism name
- `sequence`: Genomic sequence (if --include-sequence used)
- `orthologs`: List of orthologs (if --include-homology used)

## Advanced Features

### Include Genomic Sequence
Add `--include-sequence` to fetch the genomic sequence from Ensembl.

```bash
python .trae/skills/gene-info/scripts/fetch_gene_info.py BRCA1 --include-sequence
```

### Include Homology Data
Add `--include-homology` to fetch orthologs (e.g., mouse, rat homologs).

```bash
python .trae/skills/gene-info/scripts/fetch_gene_info.py BRCA1 --include-homology
```

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
- If a file is produced, prefer a deterministic output name such as `gene_info_result.md` unless the skill documentation defines a better convention.
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
python scripts/fetch_gene_info.py --help
```

Expected output format:

```text
Result file: gene_info_result.md
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
