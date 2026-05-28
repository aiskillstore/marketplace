# Research Paper Downloader - API Reference

## Semantic Scholar API
Endpoint: `https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}`

Fields:
- `title`: Paper title
- `authors`: List of author objects
- `year`: Publication year
- `openAccessPdf`: Object with `url` and `status` fields

Rate Limit: 100 requests per 5 minutes (free tier)

---

## OpenAlex API
Endpoint: `https://api.openalex.org/works/doi:{doi}`

Response includes:
- `open_access.is_oa`: Boolean flag
- `locations[].url_for_pdf`: Direct PDF link

---

## Unpaywall API
Endpoint: `https://api.unpaywall.org/v2/{doi}`

Parameters:
- `email`: Required (use a valid email for better results)

Response:
- `is_oa`: Boolean
- `best_oa_location.url_for_pdf`: Best PDF URL

---

## arXiv API
Search API: `http://export.arxiv.org/api/query?search_query=all:{query}&max_results={n}`

Direct PDF: `https://arxiv.org/pdf/{id}.pdf`

Alternative: `https://ar5iv.org/pdf/{id}.pdf`

---

## Crossref API
Endpoint: `https://api.crossref.org/works/{doi}`

Response includes `link[]` with PDF URLs if available

---

## Error Codes
- 404: Paper not found
- 403: Rate limited or forbidden
- 500: Server error
