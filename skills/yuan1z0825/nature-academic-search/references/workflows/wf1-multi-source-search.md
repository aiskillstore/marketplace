# Workflow 1: Multi-Source Literature Search

**Purpose:** Search multiple academic databases in parallel, deduplicate, merge, and rank results.

**Prerequisites:** MCP tools available (PubMed, CrossRef, arXiv, and optionally Semantic Scholar / Google Scholar).

**Uses:** [Dedup Engine](../dedup-engine.md) — deduplication and merge preference logic.

## Procedure

1. **Analyze topic** — identify domain, consult [source routing](../search-strategy.md#source-selection).
2. **Select sources by tier** — follow [Source Tiers](../source-tiers.md). Always try T1 first; escalate to T2 only if T1 insufficient; use T3 as last resort with explicit user warning.
3. **Search in parallel** — call all relevant MCP search tools simultaneously:
   - Biomedical → `pubmed_search_articles`
   - Cross-disciplinary → `search_crossref`
   - Preprints → `search_arxiv` / `search_biorxiv` / `search_medrxiv`
   - Exhaustive → add `search_semantic_scholar` / `search_webofscience` / `search_scopus`
4. **Deduplicate** — apply [Dedup Engine](../dedup-engine.md) to merged result list.
5. **Merge and rank** — sort by relevance, date, or citation count per user preference. See [Result Ranking](../search-strategy.md#result-ranking).
6. **Present results** — unified table with source labels, metadata, and abstract snippets.

## Output Format

```
**Title**: [Paper Title]
**Authors**: [Author list]
**Journal**: [Journal name]
**Year**: [Year]  |  **DOI**: [DOI]  |  **PMID**: [PMID]
**Citations**: [count if available]
**Abstract**: [First 200 characters...]
```

## Error Modes

- **MCP tool unavailable:** report specific failure, continue with remaining tools.
- **No results:** broaden terms per [Query Construction](../search-strategy.md#query-construction), try alternative sources, suggest user refine query.
- **All sources empty:** suggest MeSH strategy (Workflow 3) or manual query refinement.
