---
name: reference-finder
description: Automatically finds and ranks PubMed references for each sentence in scientific text; use when you need titles, DOIs, and brief recommendation reasons from the PubMed E-utilities API.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a scientific paragraph and want suggested PubMed papers for **each sentence**.
- You need **top-ranked references** with **title, DOI, PMID, year**, and a short **why recommended** explanation.
- You are drafting or reviewing a manuscript and want quick **literature grounding** for key claims.
- You want a lightweight reference matcher that uses **only the official PubMed E-utilities API** (no third-party services).
- You need a scriptable tool for batch or CLI workflows to generate candidate citations.

## Key Features

- Sentence-level reference matching for scientific text.
- Returns the **top N (default: 3)** most relevant PubMed records per sentence.
- Outputs structured fields: **title, DOI, PMID, year, recommendation reason**.
- Relevance ranking based on:
  - keyword overlap / match strength,
  - publication year preference,
  - citation-count signal (when available/derivable).
- Safety constraints:
  - Network access restricted to `eutils.ncbi.nlm.nih.gov`.
  - No local filesystem writes except to `outputs/` during execution.
  - Request timeout set to **30 seconds** with clear error messages.
- Supports Python API usage and CLI usage (including interactive mode).

## Dependencies

- Python **3.x** (standard library only; no third-party packages required)

## Example Usage

### Python (direct call)

```python
from reference_finder import find_references

text = "CRISPR-Cas9 gene editing has revolutionized biomedical research."

results = find_references(text)

for ref in results[:3]:
    print(f"- {ref['title']} ({ref['year']})")
    print(f"  DOI: {ref['doi']}")
    print(f"  PMID: {ref['pmid']}")
    print(f"  Reason: {ref['reason']}")
```

### CLI (single input)

```bash
python scripts/find_refs.py "CRISPR-Cas9 gene editing has revolutionized biomedical research."
```

### CLI (interactive mode)

```bash
python scripts/find_refs.py
```

### Example output (JSON)

```json
[
  {
    "pmid": "PMID:",
    "title": "A Programmable Dual-RNA-Guided DNA Endonuclease in Vitro",
    "doi": "10.1126/science.1225829",
    "year": 2012,
    "reason": "Highest keyword match for 'CRISPR-Cas9', foundational paper"
  }
]
```

## Implementation Details

### Data flow

1. **Sentence splitting**: The input text is split into sentences (implementation-defined; typically punctuation-based).
2. **PubMed search (ESearch)**: For each sentence, a query is sent to:
   - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
3. **Record retrieval (EFetch)**: The top candidate PMIDs are fetched via:
   - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`
4. **Field extraction**: Title, year, PMID, and DOI (when present) are extracted from the returned metadata.
5. **Ranking and selection**: Candidates are scored and the top **N** are returned with a short recommendation reason.

### Ranking signals

- **Keyword match**: Measures overlap between sentence terms and retrieved record metadata (e.g., title/abstract terms when available).
- **Publication year**: Used as a preference signal (e.g., favoring more recent work unless a classic/foundational match is strong).
- **Citation count**: Incorporated when available/derivable; otherwise treated as missing without failing the run.

### Operational constraints and safety

- **Allowed network host**: `eutils.ncbi.nlm.nih.gov` only.
- **Prohibited**: Any third-party URLs.
- **Filesystem**: Do not write outside `outputs/` during execution.
- **Rate limiting**: Use a reasonable request cadence (e.g., **~0.5s** between requests) to respect API limits.
- **Timeout**: **30 seconds** per request.
- **Error handling**: Return semantic, user-readable error messages for network/API/parse failures.

### Defaults

- **Top references per sentence**: 3
- **Endpoints**:
  - ESearch: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
  - EFetch: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`

### Related project files

- Main script: `scripts/find_refs.py`
- Tests: `tests/test_finder.py`
- Evaluation checklist: `references/evaluation-checklist.md`
- PubMed E-utilities documentation: https://www.ncbi.nlm.nih.gov/books/NBK25504/