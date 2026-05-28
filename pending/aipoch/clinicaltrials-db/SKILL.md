---
name: clinicaltrials-db
description: Query the ClinicalTrials.gov API v2 to search for clinical trials, retrieve detailed study protocols, and analyze recruitment status; use when you need to find trials by condition/drug, export results, or verify study details by NCT ID.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to find clinical trials for a specific condition (e.g., “cancer”) and filter by recruitment status (e.g., Recruiting).
- You want to locate trials involving a particular intervention (drug/biologic/device) and quickly review matching studies.
- You need to retrieve full study protocol details (including eligibility criteria) for a known NCT identifier.
- You want to export or programmatically process trial metadata for downstream analysis or reporting.
- You need to validate study status and key fields (phase, locations, sponsor) from the authoritative ClinicalTrials.gov source.

## Key Features

- Search studies via ClinicalTrials.gov API v2 using common filters (condition, intervention, recruitment status, result limits).
- Retrieve detailed study information by NCT ID, including protocol and eligibility criteria.
- Simple Python interface for integrating trial search and retrieval into scripts and pipelines.
- Reference documentation for advanced query parameters and field definitions (see `references/api_reference.md`).

## Dependencies

- Python 3.9+
- `requests` >= 2.28

## Example Usage

```python
from scripts.query_clinicaltrials import search_studies, get_study_details

def main():
    # 1) Search studies (example: recruiting cancer studies)
    results = search_studies(
        condition="cancer",
        status="RECRUITING",
        limit=10,
    )

    print("Search results:")
    for i, item in enumerate(results, start=1):
        # The exact keys depend on the API fields returned by the implementation.
        # Print the raw item to keep this example runnable across field selections.
        print(f"\n[{i}] {item}")

    # 2) Get study details by NCT ID
    nct_id = "NCT01234567"
    study = get_study_details(nct_id)

    print(f"\n\nStudy details for {nct_id}:")
    print(study)

if __name__ == "__main__":
    main()
```

## Implementation Details

- **API Backend**: Uses ClinicalTrials.gov API v2 endpoints to query study records and fetch study details.
- **Search Parameters**:
  - `condition`: Condition/disease term used to match relevant studies.
  - `status`: Recruitment status filter (e.g., `RECRUITING`).
  - `limit`: Maximum number of records to return.
- **Study Detail Retrieval**:
  - `get_study_details(nct_id)` fetches the full record for a single study identified by its NCT ID and returns the protocol-level information (including eligibility criteria when available).
- **Advanced Queries / Field Definitions**:
  - For additional query parameters, response fields, and definitions, refer to `references/api_reference.md`.