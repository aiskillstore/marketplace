---
name: singlecell-portal
description: Programmatically query public single-cell study metadata from the Broad Institute Single Cell Portal REST API when you need to search and filter datasets by organism, tissue, disease, or cell type without an API key.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to **discover relevant public single-cell studies** by filtering on organism (e.g., human/mouse) and tissue (e.g., lung/brain).
- You want to **quickly retrieve study-level metadata** (e.g., study name, accession, cell counts) for downstream curation or reporting.
- You are building a script or tool that needs **no authentication** and should work reliably on **Windows** with minimal setup.
- You want to **inspect available filter facets** (what tissues/diseases/cell types exist in the index) before constructing queries.
- You need a lightweight way to **validate that a study exists** and fetch its details by accession.

## Key Features

- Direct REST access to the official Single Cell Portal API (`/single_cell/api/v1/*`)
- No API key required (public endpoints)
- Faceted search for studies (organism, tissue, disease, cell type, etc.)
- Retrieve facet dictionaries to build valid filters
- Retrieve study details by accession
- Minimal dependency footprint (only `requests`)
- Windows-friendly behavior (optional SSL verification disablement for certificate issues)

## Dependencies

- `requests==2.31.0`

## Example Usage

```python
import requests

BASE_URL = "https://singlecell.broadinstitute.org/single_cell/api/v1"

def scp_get(path: str, params=None, verify_ssl: bool = True, timeout: int = 30):
    """
    Minimal helper for Single Cell Portal API calls.

    Security note:
    - Only call official endpoints under:
      https://singlecell.broadinstitute.org/single_cell/api/v1/*
    - If you encounter Windows certificate issues, set verify_ssl=False.
    """
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, params=params or {}, timeout=timeout, verify=verify_ssl)
    resp.raise_for_status()
    return resp.json()

def search_studies(facets: str, size: int = 5):
    return scp_get("/search", params={"facets": facets, "size": size})

def get_facets():
    return scp_get("/search/facets")

def get_study(accession: str):
    return scp_get(f"/studies/{accession}")

if __name__ == "__main__":
    # 1) Search: human lung studies
    results = search_studies("organism:human,tissue:lung", size=5)
    studies = results.get("studies", [])
    print("Top matches:")
    for s in studies:
        print(f"- {s.get('name')} | accession={s.get('accession')} | cells={s.get('cell_count')}")

    # 2) Inspect available facet values (useful to build valid filters)
    facet_info = get_facets()
    print("\nFacet keys available:", ", ".join(sorted(facet_info.keys())))

    # 3) Fetch details for the first returned study (if any)
    if studies and studies[0].get("accession"):
        acc = studies[0]["accession"]
        detail = get_study(acc)
        print(f"\nStudy detail for {acc}:")
        print("Name:", detail.get("name"))
        print("Description:", detail.get("description"))
```

## Implementation Details

- **Base endpoint constraint**: All network requests must target  
  `https://singlecell.broadinstitute.org/single_cell/api/v1/*`  
  (no third-party URLs).
- **Core endpoints**:
  - `GET /search`: returns study search results (metadata)
  - `GET /search/facets`: returns available facet keys/values for filtering
  - `GET /studies/{accession}`: returns details for a specific study
- **Facet filtering (`facets` parameter)**:
  - Format: comma-separated `key:value` pairs, e.g. `organism:human,tissue:lung`
  - Common facet keys include: `organism`, `tissue`, `disease`, `cell_type`
  - Some values may be multi-word (e.g., `T cell`); pass them as-is in the string.
- **Pagination / result size**:
  - `size` controls the number of returned studies (default behavior depends on the API; set explicitly for deterministic results).
- **SSL handling on Windows**:
  - If certificate verification fails in certain environments, you may set `verify=False` in `requests.get(...)`.
  - Prefer `verify=True` when possible; disabling verification reduces transport security.
- **Error handling**:
  - Use `response.raise_for_status()` to surface HTTP errors.
  - Treat missing keys defensively (`dict.get`) because response shapes may evolve.
- **Data scope**:
  - The API primarily returns **metadata**; raw data downloads typically occur via the portal’s dataset pages and are not covered by these endpoints.