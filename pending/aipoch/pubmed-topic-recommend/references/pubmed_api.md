# PubMed E-utilities Quick Reference

## Basic Information

- Base URL: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- Common Endpoints: `esearch.fcgi`, `esummary.fcgi`, `efetch.fcgi`
- Rate Limits: 3 req/s without an API key, up to 10 req/s with an API key

## Common Parameters

- `db=pubmed`: Specify PubMed database
- `term=`: Search query
- `retmax=`: Maximum number of records returned
- `sort=`: Sorting (`relevance`, `pub+date`, etc.)
- `mindate` / `maxdate`: Date range (recommended to use with `datetype=pdat`)
- `retmode=`: Return format (`json` or `xml`)
- `tool` / `email` / `api_key`: Optional identity information

## Query Syntax Highlights

- Logical Combinations: `(keyword1[Title/Abstract] OR keyword2[Title/Abstract]) AND review[Publication Type]`
- MeSH Terms: `"Diabetes Mellitus"[MeSH Terms]`
- Exclusion Terms: `NOT (animal[Title/Abstract])`
- Common Fields:
  - `Title/Abstract`
  - `MeSH Terms`
  - `Publication Type`

## Recommended Workflow

1. Use `esearch` to get `IdList`
2. Use `esummary` to get summary information such as title, authors, source, and year
3. Use `efetch` to get abstracts or more complete information when necessary

## Official Documentation (Internet access required)

- `https://www.ncbi.nlm.nih.gov/books/NBK25500/`