---
name: uspto-database
description: Access USPTO data (Patent Search, PEDS, TSDR, assignments) when you need to query patents/trademarks and retrieve prosecution or status information programmatically.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Find relevant US patents by keyword, inventor, assignee, CPC/IPC class, or date range for prior-art screening.
- Retrieve patent application/prosecution history (PEDS) to understand office actions, events, and timeline status.
- Check trademark status and documents via TSDR for clearance, monitoring, or portfolio review.
- Validate patent lifecycle signals such as maintenance-fee-related status or expiration indicators as part of diligence.
- Pull assignment/ownership-related information to support chain-of-title checks.

## Key Features

- Patent search client for querying USPTO/PatentsView-style endpoints and returning matching patent identifiers/records.
- PEDS client for fetching examination history and event data for applications.
- TSDR access for trademark status and document retrieval.
- Script-oriented workflow designed for automation (batch queries, pipelines, and integration into internal tools).

## Dependencies

- Python `>=3.9`
- `requests >=2.31.0`
- `uspto-opendata-python >=0.3.0`

## Example Usage

```python
# Example: search patents by abstract text and print results
# Prerequisite: set required API keys in environment variables as expected by your scripts/clients.
# For example (names may vary by implementation):
#   export USPTO_API_KEY="..."
#   export PATENTSVIEW_API_KEY="..."

from scripts.patent_search import PatentSearchClient

def main():
    client = PatentSearchClient()

    # Query example: search for patents whose abstract contains "AI"
    query = {"_text_all": {"patent_abstract": "AI"}}

    results = client.search_patents(query)
    print(results)

if __name__ == "__main__":
    main()
```

## Implementation Details

- **Workflow**
  1. **Search**: Use `scripts/patent_search.py` to locate relevant patent numbers/records from a text or fielded query.
  2. **History**: Use `scripts/peds_client.py` to retrieve prosecution/examination history (events, dates, and status signals).
  3. **Status checks**: Use retrieved metadata to assess maintenance-fee/expiration-related status where available.

- **Query model**
  - Patent search is driven by a JSON query object (e.g., full-text constraints such as `"_text_all"` over fields like `patent_abstract`).
  - Returned results are intended to be fed into downstream steps (e.g., PEDS lookups by application/patent identifiers).

- **Authentication**
  - API keys for USPTO and/or PatentsView are required and should be provided via environment variables or configuration used by the clients.

- **Networking**
  - HTTP requests are performed via `requests`; ensure timeouts/retries are configured in the underlying clients if running large batches.