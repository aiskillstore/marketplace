---
name: clinpgx-database
description: Access ClinPGx pharmacogenomics data (successor to PharmGKB) when you need to query gene-drug interactions, CPIC guidelines, allele functions, and drug-label PGx content for precision medicine and genotype-guided dosing.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# ClinPGx Database

ClinPGx (Clinical Pharmacogenomics Database) is a curated pharmacogenomics resource and successor to PharmGKB. It integrates content from sources such as CPIC, DPWG, PharmCAT, and regulatory drug labels to support genotype-informed prescribing, safety screening, and evidence review via a REST API.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Access ClinPGx pharmacogenomics data (successor to PharmGKB) when you need to query gene-drug interactions, CPIC guidelines, allele functions, and drug-label PGx content for precision medicine and genotype-guided dosing.
- Packaged executable path(s): `scripts/query_clinpgx.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/clinpgx-database"
python -m py_compile scripts/query_clinpgx.py
python scripts/query_clinpgx.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/query_clinpgx.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/query_clinpgx.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill when you need to:

1. **Make genotype-guided prescribing decisions** (e.g., select therapy or adjust dose based on CPIC recommendations).
2. **Assess gene-drug interaction evidence** (e.g., determine whether a gene impacts efficacy/toxicity for a medication).
3. **Look up allele/variant function and phenotype mapping** (e.g., CYP star alleles, functional status, phenotype categories).
4. **Perform medication safety screening** (e.g., HLA risk alleles and severe adverse reaction associations; label warnings).
5. **Run research or population analyses** (e.g., compare allele frequencies across populations; review evidence levels and citations).

## 2. Key Features

- **Gene lookup**: retrieve pharmacogene metadata and related annotations.
- **Drug/chemical lookup**: search drugs and retrieve pharmacogenomics-relevant information.
- **Gene-drug pair queries**: access curated relationships and supporting sources (CPIC/DPWG/FDA/literature).
- **Guideline access**: retrieve CPIC guideline records and recommendation components.
- **Allele and variant queries**: star-allele function, defining variants, phenotype categories, and variant-level annotations.
- **Clinical annotations**: evidence-graded literature summaries (e.g., levels 1A-4).
- **Drug labels**: pharmacogenomic label content by regulatory source (e.g., FDA).
- **Pathways**: pharmacokinetic/pharmacodynamic pathway records for drugs.

## 3. Dependencies

- Python **3.10+**
- `requests` **>=2.31.0**

Install:

```bash
python -m pip install "requests>=2.31.0"
```

## 4. Example Usage

The following script is a complete, runnable example that:
- fetches a gene record,
- fetches a drug record by name,
- queries a gene-drug pair,
- retrieves matching CPIC guidelines,
- applies basic rate limiting and safe retries.

```python
import time
import requests

BASE_URL = "https://api.clinpgx.org/v1"
MAX_RPS_DELAY_SEC = 0.5  # 2 requests/sec

session = requests.Session()

def get_json(path, params=None, timeout=20, max_retries=4):
    """
    Safe GET with exponential backoff for HTTP 429 and transient failures.
    """
    url = f"{BASE_URL}{path}"
    for attempt in range(max_retries):
        try:
            resp = session.get(url, params=params, timeout=timeout)

            if resp.status_code == 200:
                time.sleep(MAX_RPS_DELAY_SEC)
                return resp.json()

            if resp.status_code == 429:
                backoff = 2 ** attempt
                time.sleep(backoff)
                continue

            resp.raise_for_status()

        except requests.RequestException:
            if attempt == max_retries - 1:
                raise
            time.sleep(1 + attempt)

def main():
    gene = "CYP2C19"
    drug_name = "clopidogrel"

    # 1) Gene details
    gene_data = get_json(f"/gene/{gene}")
    print("Gene:", gene_data.get("symbol", gene))

    # 2) Drug search by name (API may return a list)
    drugs = get_json("/chemical", params={"name": drug_name})
    if not drugs:
        raise RuntimeError(f"No drug found for name={drug_name!r}")

    drug = drugs[0]
    drug_id = drug.get("id")
    print("Drug:", drug.get("name", drug_name), "| id:", drug_id)

    # 3) Gene-drug pair query
    pair = get_json("/geneDrugPair", params={"gene": gene, "drug": drug_name})
    print("Gene-drug pair results:", len(pair) if isinstance(pair, list) else "1")

    # 4) CPIC guideline query (by gene+drug filter)
    guidelines = get_json("/guideline", params={"source": "CPIC", "gene": gene, "drug": drug_name})
    print("CPIC guidelines:", len(guidelines) if isinstance(guidelines, list) else "1")

    # 5) Drug labels (optional)
    labels = get_json("/drugLabel", params={"drug": drug_name, "source": "FDA"})
    print("FDA labels:", len(labels) if isinstance(labels, list) else "1")

if __name__ == "__main__":
    main()
```

## 5. Implementation Details

### API Base URL and request patterns
- Base URL:
  - `https://api.clinpgx.org/v1/`
- Common resource patterns:
  - `GET /gene/{symbol}` (e.g., `/gene/CYP2D6`)
  - `GET /gene?q=...` (search)
  - `GET /chemical?name=...` or `GET /chemical/{id}`
  - `GET /geneDrugPair?gene=...&drug=...`
  - `GET /guideline?source=CPIC&gene=...&drug=...` or `GET /guideline/{id}`
  - `GET /allele/{star_allele}` (e.g., `/allele/CYP2D6*4`)
  - `GET /variant/{rsid}` (e.g., `/variant/rs4244285`)
  - `GET /clinicalAnnotation?...` (filters such as `gene`, `drug`, `evidenceLevel`)
  - `GET /drugLabel?drug=...&source=FDA`
  - `GET /pathway/{id}` or `GET /pathway?drug=...`

### Rate limiting
- Limit: **2 requests/second**
- Recommended client behavior:
  - enforce a **0.5s delay** between requests in loops,
  - on HTTP **429**, apply **exponential backoff** (e.g., 1s, 2s, 4s, ...).

### Evidence levels (clinical annotations)
Clinical annotations may be graded from higher to lower strength, commonly:
- **1A**, **1B**, **2A**, **2B**, **3**, **4**

Use evidence filters (e.g., `evidenceLevel=1A`) when building clinical decision support or prioritizing literature review.

### Phenotype categories (typical metabolizer labels)
For many pharmacogenes, phenotype groupings may include:
- **Ultrarapid Metabolizer (UM)**
- **Normal Metabolizer (NM)**
- **Intermediate Metabolizer (IM)**
- **Poor Metabolizer (PM)**

### Notes on clinical use
- Always confirm **guideline version/date**, **evidence strength**, and **population context** (allele frequencies vary).
- Consider **phenoconversion** (drug-drug interactions altering enzyme activity) and non-genetic factors (age, organ function, comedications).
- If you need phenoconversion and multi-drug interpretation workflows, ClinPGx also provides the **PharmDOG** decision-support tool on the ClinPGx website.

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
- If a file is produced, prefer a deterministic output name such as `clinpgx_database_result.md` unless the skill documentation defines a better convention.
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

```bash
python scripts/query_clinpgx.py --help
```

Expected output format:

```text
Result file: clinpgx_database_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Access ClinPGx pharmacogenomics data (successor to PharmGKB) when you need to query gene-drug interactions, CPIC guidelines, allele functions, and drug-label PGx content for precision medicine and genotype-guided dosing.
