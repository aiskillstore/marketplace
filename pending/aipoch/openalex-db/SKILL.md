---
name: openalex-db
description: Access the OpenAlex database (240M+ scholarly works) for bibliometric analysis, literature search, and citation tracking; use when you need to query works/authors/institutions/concepts without an API key.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to search scholarly **works** by keyword and filter by properties (e.g., open access, year, venue).
- You want to look up **authors** and analyze their publication output and citation impact.
- You need to retrieve and compare **institutions** (e.g., affiliation-based exploration or benchmarking).
- You want to explore **concepts/topics** and track trends across time.
- You need lightweight **bibliometric workflows** (citation tracking, publication trends) without managing API keys.

## Key Features

- Query OpenAlex entities: **works, authors, institutions, concepts**.
- Keyword search with **filtering** support.
- Designed for bibliometric tasks such as **citation tracking** and **trend exploration**.
- No API key required; supports providing an email for OpenAlex **Polite Pool** (higher rate limits).
- Simple Python client wrapper via `scripts/openalex_client.py`.

## Dependencies

- `requests` (version not pinned; install via `uv pip install requests`)

## Example Usage

```python
from scripts.openalex_client import OpenAlexClient

def main():
    # Provide an email to use OpenAlex "Polite Pool" (recommended for better rate limits)
    client = OpenAlexClient(email="user@example.com")

    # Search for open-access works related to CRISPR
    works = client.search_works(
        search="CRISPR",
        filter_params={"is_oa": "true"},
    )

    print(f"Found {len(works)} works")
    if works:
        first = works[0]
        # Field names depend on OpenAlex response schema
        print("First result:")
        print(f"  id: {first.get('id')}")
        print(f"  title: {first.get('title')}")
        print(f"  publication_year: {first.get('publication_year')}")
        print(f"  cited_by_count: {first.get('cited_by_count')}")

if __name__ == "__main__":
    main()
```

## Implementation Details

- **Client entry point:** `scripts/openalex_client.py` provides the main API wrapper (`OpenAlexClient`).
- **Polite Pool:** Supplying an `email` is recommended to receive higher rate limits from OpenAlex.
- **Search + filters:** Work queries accept a free-text `search` string plus `filter_params` (key/value pairs) that map to OpenAlex API filters (e.g., `{"is_oa": "true"}`).
- **Pagination and schema:** For supported filters, pagination behavior, and response fields, refer to `references/api_guide.md`.