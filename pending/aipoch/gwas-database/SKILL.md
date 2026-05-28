---
name: gwas-database
description: Query the NHGRI-EBI GWAS Catalog to retrieve SNP–trait associations, study metadata, and (when available) summary statistics when you need evidence for a variant, trait/disease, gene, or genomic region.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

1. **Look up a specific variant (rsID)** to see all reported trait/disease associations and their p-values/effect sizes.
2. **Find variants associated with a trait/disease** (via free text or an EFO trait ID) for downstream interpretation or reporting.
3. **Perform gene-centric exploration** to identify GWAS hits within/near a gene of interest.
4. **Retrieve study-level metadata** (GCST accession, PMID, cohorts, ancestry, sample size) to assess evidence quality and applicability.
5. **Access or filter summary statistics** (when available) for genome-wide analyses (e.g., fine-mapping, colocalization, PRS development).

## Key Features

- **Multiple query entry points**: rsID, EFO trait ID, gene symbol, chromosomal region, GCST accession, PMID.
- **Structured entities**: studies, associations, variants (SNPs), and traits (EFO-mapped).
- **Programmatic access** via:
  - GWAS Catalog REST API: `https://www.ebi.ac.uk/gwas/rest/api`
  - Summary Statistics API: `https://www.ebi.ac.uk/gwas/summary-statistics/api`
- **Association-level fields** commonly used in analysis: p-value, strongest allele, odds ratio/beta, mapped trait labels.
- **Pagination support** for bulk extraction (`page`, `size`, and `_links` navigation).

## Dependencies

- Python **3.9+**
- `requests` **>= 2.31.0**
- `pandas` **>= 2.0.0** (optional; for tabular outputs)

## Example Usage

The following script is a complete, runnable example that:
1) fetches associations for an EFO trait,  
2) filters by genome-wide significance,  
3) returns a tidy table.

```python
import time
import requests
import pandas as pd

GWAS_REST_BASE = "https://www.ebi.ac.uk/gwas/rest/api"

def fetch_trait_associations(efo_id: str, page_size: int = 100, max_pages: int = 50):
    """
    Fetch associations for a given EFO trait ID from the GWAS Catalog REST API.
    Returns a list of association JSON objects.
    """
    url = f"{GWAS_REST_BASE}/efoTraits/{efo_id}/associations"
    headers = {"Accept": "application/json"}

    all_assocs = []
    for page in range(max_pages):
        params = {"page": page, "size": page_size}
        r = requests.get(url, params=params, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()

        assocs = data.get("_embedded", {}).get("associations", [])
        if not assocs:
            break

        all_assocs.extend(assocs)
        time.sleep(0.1)  # be polite to the public API

    return all_assocs

def to_table(assocs, p_threshold: float = 5e-8) -> pd.DataFrame:
    rows = []
    for a in assocs:
        p = a.get("pvalue")
        try:
            p_float = float(p) if p is not None else None
        except (TypeError, ValueError):
            p_float = None

        if p_float is None or p_float > p_threshold:
            continue

        rows.append({
            "rsId": a.get("rsId"),
            "trait": a.get("efoTrait") or a.get("mappedLabel"),
            "pvalue": p_float,
            "strongestAllele": a.get("strongestAllele"),
            "orPerCopyNum": a.get("orPerCopyNum"),
            "betaNum": a.get("betaNum"),
            "pubmedId": a.get("pubmedId"),
            "studyAccession": a.get("studyAccession"),
        })

    df = pd.DataFrame(rows).drop_duplicates()
    if not df.empty:
        df = df.sort_values("pvalue", ascending=True).reset_index(drop=True)
    return df

if __name__ == "__main__":
    # Example: Type 2 diabetes (EFO_0001360)
    efo_id = "EFO_0001360"

    assocs = fetch_trait_associations(efo_id)
    df = to_table(assocs, p_threshold=5e-8)

    print(df.head(20).to_string(index=False))
    print(f"\nSignificant associations: {len(df)}")
    if not df.empty:
        print(f"Unique variants: {df['rsId'].nunique()}")
```

## Implementation Details

### Data Model and Identifiers
- **Study accession**: `GCST...` (e.g., `GCST001234`)
- **Variant identifier**: `rs...` (e.g., `rs7903146`)
- **Trait identifier**: **EFO** term (e.g., `EFO_0001360`)
- **Gene symbol**: HGNC-approved symbol (e.g., `APOE`, `TCF7L2`)

### Core Endpoints (REST API)
- Study details: `GET /studies/{GCST}`
- Variant details: `GET /singleNucleotidePolymorphisms/{rsId}`
- Variant associations: `GET /singleNucleotidePolymorphisms/{rsId}/associations`
- Trait associations: `GET /efoTraits/{EFO}/associations`

### Pagination Strategy
- Most list endpoints are paginated.
- Use query parameters:
  - `size`: number of records per page (commonly 20–100)
  - `page`: zero-based page index
- Stop conditions:
  - `_embedded.associations` is empty, or
  - you reach a predefined `max_pages` safety limit.

### Significance Thresholds and Filtering
- A common GWAS threshold is **p ≤ 5×10⁻⁸** (genome-wide significance).
- Filtering should be applied after parsing `pvalue` into a numeric type; handle missing or non-numeric values safely.

### Summary Statistics Access (when available)
- Summary Statistics API base: `https://www.ebi.ac.uk/gwas/summary-statistics/api`
- Typical filters include chromosome/position ranges and p-value bounds (endpoint availability and parameters may vary by resource version).
- For bulk downloads, the Catalog also provides an FTP directory:
  - `http://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/`

### Practical Notes for Robust Use
- Respect public API usage (add small delays; cache results for iterative workflows).
- Always interpret associations in context:
  - ancestry/cohort metadata,
  - sample size,
  - replication status,
  - effect size harmonization needs across studies.