# Source Tiers & Reliability

Every academic data source is classified by reliability tier to guide automated fallback routing.

## Tier Definitions

| Tier | Label | API Quality | Fallback Behavior |
|------|-------|-------------|-------------------|
| **T1** | API-backed, structured | Official REST/XML API, stable schema | Use first. If fails → next T1 source. |
| **T2** | API-backed, limited | Official API but narrow coverage or low rate limits | Use when T1 exhausted or insufficient. |
| **T3** | Scraped, unstable | Web scraping, no contract on response format | Last resort. Always warn user: "results may be incomplete or stale". |

## Source Classification

### T1 — API-backed, Structured

| Source | API | Rate Limit | Notes |
|--------|-----|------------|-------|
| PubMed | E-utilities (XML/JSON) | 3 req/s (10 with API key) | Biomedical + life sciences, MeSH indexing |
| CrossRef | REST API (JSON) | 50 req/s (no key needed) | Cross-disciplinary, citation counts |
| arXiv | OAI-PMH Atom XML | 1 req/3s | Preprints: physics, math, CS, biology |

### T2 — API-backed, Limited

| Source | API | Rate Limit | Notes |
|--------|-----|------------|-------|
| Semantic Scholar | REST API (JSON) | 1 req/s (100 with API key) | Citation graph, field-of-study filters |
| bioRxiv | API | Limited metadata | Biology preprints only |
| medRxiv | API | Limited metadata | Medical preprints only |

### T3 — Scraped, Unstable

| Source | Method | Risk |
|--------|--------|------|
| Google Scholar | HTML scrape | CAPTCHA blocks, IP bans |
| Web of Science | Institution proxy required | Access varies |
| Scopus | Institution proxy required | Access varies |
| CNKI / 万方 | No programmatic access | Chinese only, manual download |

## Fallback Routing Rules

For every literature search or citation verification:

```
1. SELECT T1 sources matching the query domain
2. SEARCH all selected T1 sources in parallel
3. If (result found AND relevance > threshold) → ACCEPT
4. If T1 exhausted or insufficient → ESCALATE to T2
5. If T1+T2 exhausted → ESCALATE to T3 + WARN USER
6. If all exhausted → return partial results + suggest query refinement
```

### Domain → Tier Mapping

| Domain | T1 | T2 | T3 (if needed) |
|--------|-----|-----|-----------------|
| Medical / clinical | PubMed | Semantic Scholar | Google Scholar |
| Cross-disciplinary | CrossRef | Semantic Scholar | Scopus |
| Preprints / CS / physics | arXiv | bioRxiv / medRxiv | Google Scholar |
| Exhaustive review | PubMed + CrossRef + arXiv | Semantic Scholar + bioRxiv/medRxiv | WoS / Scopus |
| Citation verification | CrossRef (DOI) → PubMed (PMID) | Semantic Scholar | Google Scholar |
| Chinese literature | — | — | CNKI / 万方 (manual) |
