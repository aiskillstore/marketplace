---
name: semantic-scholar-database
description: Access the Semantic Scholar Graph API to search papers and retrieve paper/author/citation data when you need literature discovery or citation graph exploration.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to find relevant papers by keyword, title, or known identifiers (e.g., Semantic Scholar Paper ID).
- You want to fetch detailed metadata for a paper (abstract, venue, year, fields of study, etc.).
- You need author-centric information such as an author profile and their publications.
- You want to explore a citation network by traversing references or citations for a given paper.
- You are building a literature review workflow that requires programmatic access to scholarly graph data.

## Key Features

- Paper search via the Semantic Scholar Graph API.
- Paper details retrieval (e.g., abstract, venue, citations-related fields depending on requested fields).
- Author details retrieval (author profile and associated papers depending on requested fields).
- Citation graph traversal:
  - Fetch papers that cite a target paper (`citations`)
  - Fetch papers referenced by a target paper (`references`)
- Optional API key support for higher rate limits via environment variable.

## Dependencies

- Python `>=3.9`
- `requests >=2.25.0`

## Example Usage

```python
import os
from scripts.client import (
    search_papers,
    get_paper_details,
    get_author_details,
    get_citations,
)

# Optional: set for higher rate limits
# os.environ["S2_API_KEY"] = "YOUR_API_KEY"

def main():
    # 1) Search papers
    results = search_papers(query="Attention Is All You Need", limit=5)
    print("Search results (top 5):")
    for i, p in enumerate(results, 1):
        # The exact keys depend on the fields requested by the client implementation.
        print(f"{i}. {p.get('title')} ({p.get('year')}) - paperId={p.get('paperId')}")

    # 2) Get paper details
    paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
    paper = get_paper_details(paper_id=paper_id)
    print("\nPaper details:")
    print("Title:", paper.get("title"))
    print("Venue:", paper.get("venue"))
    print("Year:", paper.get("year"))
    print("Abstract:", (paper.get("abstract") or "")[:300], "...")

    # 3) Get author details
    author_id = "1741101"
    author = get_author_details(author_id=author_id)
    print("\nAuthor details:")
    print("Name:", author.get("name"))
    print("AuthorId:", author.get("authorId"))

    # 4) Traverse citations / references
    citing = get_citations(paper_id=paper_id, method="citations")
    refs = get_citations(paper_id=paper_id, method="references")
    print("\nCitation traversal:")
    print("Citations count:", len(citing) if isinstance(citing, list) else "N/A")
    print("References count:", len(refs) if isinstance(refs, list) else "N/A")

if __name__ == "__main__":
    main()
```

## Implementation Details

- **API Endpoint**: The skill communicates with the Semantic Scholar Graph API:
  - Base URL: `https://api.semanticscholar.org/graph/v1/`
- **HTTP Client**: Uses `requests` to perform REST calls.
- **Authentication / Rate Limits**:
  - If `S2_API_KEY` is set in the environment, requests should include it (typically via an `x-api-key` header) to obtain higher rate limits.
  - Without an API key, the API may enforce stricter rate limiting.
- **Core Operations** (as implemented in `scripts/client.py`):
  - `search_papers(query, limit=...)`: queries the search endpoint and returns a list of matching papers.
  - `get_paper_details(paper_id)`: fetches metadata for a specific paper ID.
  - `get_author_details(author_id)`: fetches metadata for a specific author ID.
  - `get_citations(paper_id, method="citations"|"references")`: traverses the citation graph by selecting either inbound citations or outbound references.
- **Parameters**:
  - `limit`: controls the maximum number of results returned by search.
  - `method`: must be either `"citations"` or `"references"` to select traversal direction.