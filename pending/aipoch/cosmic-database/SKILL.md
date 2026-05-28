---
name: cosmic-database
description: Access COSMIC to download mutation datasets, query Cancer Gene Census, and retrieve mutational signatures when your genomic analysis requires curated somatic mutation resources.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# COSMIC Database Skill

## When to Use

- Use this skill when you need access cosmic to download mutation datasets, query cancer gene census, and retrieve mutational signatures when your genomic analysis requires curated somatic mutation resources in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/download_cosmic.py` is the most direct path to complete the request.
- Use this skill when you need the `cosmic-database` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Access COSMIC to download mutation datasets, query Cancer Gene Census, and retrieve mutational signatures when your genomic analysis requires curated somatic mutation resources.
- Packaged executable path(s): `scripts/download_cosmic.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/cosmic-database"
python -m py_compile scripts/download_cosmic.py
python scripts/download_cosmic.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/download_cosmic.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/download_cosmic.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill when you need COSMIC data for tasks such as:

- Downloading COSMIC mutation exports (TSV/VCF) for cohort or sample-level variant analysis.
- Retrieving Cancer Gene Census (CGC) gene lists for oncogene/tumor suppressor annotation and prioritization.
- Working with COSMIC mutational signatures (SBS/DBS/ID) for signature attribution or comparative studies.
- Accessing additional COSMIC genomics datasets (e.g., copy number, fusions, expression) for multi-omics integration.
- Building reproducible pipelines that programmatically fetch the latest COSMIC releases.

## 2. Key Features

- **Authenticated downloads** of COSMIC files (e.g., TSV/VCF; often GZIP-compressed).
- **Cancer Gene Census access** for curated cancer gene information.
- **Mutational signature retrieval** including **SBS**, **DBS**, and **ID** signatures.
- **Support for multiple COSMIC dataset types**, such as mutation, copy number, fusion, and expression resources.
- **Pandas-friendly workflow** for loading and filtering downloaded tables.

## 3. Dependencies

- Python **3.9+**
- `pandas` **>= 1.5**
- `requests` **>= 2.28**

External requirements:

- A registered COSMIC account at https://cancer.sanger.ac.uk/cosmic
- Valid COSMIC login credentials (email + password)

## 4. Example Usage

The following example downloads a COSMIC file and loads it into a pandas DataFrame.

```python
from scripts.download_cosmic import download_cosmic_file
import pandas as pd

# 1) Download a COSMIC dataset (example path; adjust to your target release/build)
download_cosmic_file(
    email="user@email.com",
    password="pwd",
    filepath="GRCh38/cosmic/latest/CosmicMutantExport.tsv.gz"
)

# 2) Load the downloaded GZIP-compressed TSV
df = pd.read_csv(
    "CosmicMutantExport.tsv.gz",
    sep="\t",
    compression="gzip"
)

# 3) Example analysis: filter by gene symbol (column name depends on the dataset)

# df_gene = df[df["Gene name"] == "TP53"]
```

For dataset field definitions and COSMIC file specifics, see: `references/cosmic_data_reference.md`.

## 5. Implementation Details

- **Authentication**: Downloads require COSMIC account credentials (email/password) and are performed via an authenticated HTTP session.
- **File targeting**: The `filepath` parameter specifies the COSMIC resource path (e.g., genome build such as `GRCh38`, release channel such as `latest`, and the target filename).
- **Data format**: Many COSMIC exports are distributed as **GZIP-compressed TSV** (and sometimes **VCF**). Use `pandas.read_csv(..., sep="\t", compression="gzip")` for TSV `.gz` files.
- **Typical workflow**:
  1. Download the desired COSMIC export.
  2. Load into a DataFrame (or parse VCF with an appropriate library if needed).
  3. Filter/aggregate by gene, tumor type, sample, or signature depending on the analysis goal.
