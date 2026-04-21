---
name: url-citation-search
description: Find papers and preprints that cite a given URL, especially blogs, docs pages, project pages, or other web content that standard citation indexes often miss. Use when the user provides a URL and wants confirmed citing works, evidence from PDF or HTML references, DOI or arXiv links, BibTeX, or a deduplicated citation report.
---

# URL Citation Search

## Use this skill for

- A user gives a URL and asks which papers cited it.
- The target is a blog post, documentation page, project page, demo, GitHub page, or other web content rather than a standard paper.
- The user wants confirmed citations, not just likely matches from search results.

## Workflow

1. Resolve the target page.
- Fetch the page and record the visible title.
- Extract the canonical URL if present.
- Keep obvious variants: `http/https`, `www/non-www`, trailing slash, moved domains, and mirrored or cross-posted URLs.
- Keep direct-URL variants separate from mirror URLs. The final report should distinguish `direct citation` from `mirror citation`.
- Record author and date only when they help disambiguate the page.

2. Build search keys.
- Exact full URL.
- Host plus path without protocol.
- Stable slug or final path segment.
- Exact page title.
- Title variants exposed by the page metadata or mirror pages.

3. Search in this order.
- Exact full URL and protocol-less URL in a general web search.
- Exact title and slug in a general web search.
- Site-restricted searches on academic sources such as `arxiv.org`, `openreview.net`, `aclanthology.org`, `proceedings.neurips.cc`, `proceedings.mlr.press`, `dl.acm.org`, `ieeexplore.ieee.org`, `nature.com`, `link.springer.com`, and `ceur-ws.org`.
- Mirror or cross-post URLs too. Papers often cite the mirror instead of the current canonical URL.
- If direct URL or title search is sparse, build a topical candidate pool and batch-scan likely papers. This is especially useful on arXiv when full-text search misses exact quoted strings.

4. Verify every candidate.
- Keep a work only if its PDF, HTML reference list, or in-text bibliography contains the target URL, title, slug, or a verified mirror URL.
- Search snippets alone are not enough.
- PDF-only evidence is acceptable when the exact URL appears in extracted text or PDF link annotations.
- Publisher article pages may expose references in HTML metadata such as `citation_reference` or dedicated bibliography pages. Use those before scraping PDFs.
- arXiv HTML bibliography entries may hide the real target inside `External Links` even when the visible text omits the URL. Inspect the underlying href, not just the rendered text.
- Bibliography pages, project pages, and search indexes are candidate finders, not final proof, unless they expose the actual reference entry for the citing work.

5. Deduplicate and normalize.
- If the same work exists as both a preprint and a published paper, prefer the published version in the main list and keep the preprint as an access fallback.
- Keep genuine preprints when no formal version exists.
- Do not assume the published version preserves a web citation seen in the preprint. Verify each version separately.
- Keep official same-site variants separate from mirrors. Examples: `/engineering/...` versus `/research/...`, renamed official paths, or root-versus-`/home` pages on the same site.
- Separate `confirmed` from `candidate` when verification is incomplete.

## Output

Choose the lightest format that matches the user's ask.

- Brief list: title, year, type, and landing link.
- Citation report: title, link, DOI or arXiv ID, evidence note, and whether it is published or a preprint.
- When useful, distinguish `direct`, `official variant`, and `mirror` citation.
- Bib mode: return BibTeX for the citing papers. Return BibTeX for the target URL only if the user explicitly asks for it.

## Heuristics That Matter

- Standard citation indexes often miss web pages, so reverse search on URL, title, and slug is usually more reliable than `cited by` counts.
- arXiv full-text search misses some quoted strings. If it returns nothing, switch back to general search and inspect candidate PDFs or HTML directly.
- On arXiv, broad topic searches plus batch inspection of candidate HTML reference lists can recover citations that exact-string full-text search misses.
- Moved domains and cross-posts are common. Check canonical tags and obvious mirrors before concluding that nothing cites the page.
- Official variants are common too. A paper may cite a renamed or migrated first-party URL rather than the exact URL from the seed paper.
- PDF text extraction is lossy. If the visible citation text is missing, inspect PDF link annotations or raw extracted strings for the URL.
- Publisher HTML can be better than PDF for verification because references may already be normalized into page metadata.
- Reject false positives aggressively: a paper on the same topic is not a citation unless the reference is visible.
