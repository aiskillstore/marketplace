# MCP tools and shared modules

Multi-source literature search, citation verification, citation format conversion, and reference management via MCP tools.

## MCP tools

### Core search

| Tool | Source | Best For |
|------|--------|----------|
| `search_papers` | academic-search MCP | Default concurrent search across CrossRef, PubMed, arXiv; accepts opt-in Scopus / ScienceDirect sources |
| `get_paper_by_id` | academic-search MCP | DOI / PMID / arXiv ID details |
| `get_citation` | academic-search MCP | DOI-based formatted citation |
| `lookup_mesh` | academic-search MCP | MeSH term exploration |

### Scopus / ScienceDirect tools

| Tool | Source | Best For |
|------|--------|----------|
| `search_scopus` | academic-search MCP | Scopus advanced document search |
| `get_scopus_abstract` | academic-search MCP | Scopus abstract and document metadata |
| `get_scopus_citation_overview` | academic-search MCP | Scopus citation overview |
| `search_scopus_authors` / `get_scopus_author` | academic-search MCP | Author profile search and retrieval |
| `search_scopus_affiliations` / `get_scopus_affiliation` | academic-search MCP | Affiliation search and retrieval |
| `search_scopus_serial_titles` / `get_scopus_serial_title` | academic-search MCP | Journal/source metadata |
| `get_scopus_plumx_metrics` | academic-search MCP | PlumX metrics |
| `search_sciencedirect` | academic-search MCP | ScienceDirect article search |
| `get_sciencedirect_article_metadata` | academic-search MCP | ScienceDirect article metadata |

### Extended search

| Tool | Source | Best For |
|------|--------|----------|
| `search_google_scholar` | paper-search MCP | Broad academic search (scraped) |
| `search_semantic_scholar` | paper-search MCP | Citation graph, field-of-study filters |
| `search_biorxiv` | paper-search MCP | Biology preprints |
| `search_medrxiv` | paper-search MCP | Medical preprints |
| `search_webofscience` | paper-search MCP | Curated index, citation reports |
| `search_scopus` | paper-search MCP | Broad scholarly database |

### PubMed utilities

| Tool | Purpose |
|------|---------|
| `pubmed_fetch_articles` | Full metadata by PMID |
| `pubmed_find_related` | Related article discovery |
| `pubmed_format_citations` | APA / MLA / BibTeX / RIS formatting |
| `pubmed_convert_ids` | DOI ↔ PMID ↔ PMCID conversion |
| `pubmed_lookup_mesh` | MeSH term exploration and hierarchy |
| `pubmed_lookup_citation` | Bibliographic citation → PMID lookup |

## Shared modules

| Module | Purpose |
|--------|---------|
| [Dedup Engine](../../references/dedup-engine.md) | Unified deduplication (WFs 1, 2, 5a) |
| [Citation Parser](../../references/citation-parser.md) | Extract citations from documents (WF 2) |
| [Search Strategy](../../references/search-strategy.md) | Query construction, source selection, ranking |
| [RIS/BibTeX Format](../../references/ris-bibtex-format.md) | Format specifications and field mappings |
| [Format Converter](../../scripts/format-converter.py) | Multi-source .nbib/.ris/.bib downloader |
