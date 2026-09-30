---
name: pangolinfo-amazon-scraper
description: >
  Programmatic Amazon scraping via Pangolinfo APIs (products, keywords,
  categories, best sellers, etc.). Use when you need structured results (JSON)
  for pipelines/agents. Requires PANGOLIN_TOKEN or PANGOLIN_EMAIL +
  PANGOLIN_PASSWORD.
homepage: https://www.pangolinfo.com/amazon-scraper-skill/
license: MIT
metadata:
  openclaw:
    emoji: "🛒"
    os: ["darwin", "linux"]
    requires:
      env: ["PANGOLIN_TOKEN"]
      notes: "Auth: set PANGOLIN_TOKEN (recommended) OR set PANGOLIN_EMAIL + PANGOLIN_PASSWORD"
---

# Pangolinfo Amazon Scraper

Scrape Amazon programmatically via **Pangolinfo** APIs.
Supports product detail pages, keyword search, category listings, seller pages, best sellers, and more.

## Prerequisites

- **Python 3.6+** (standard library only)
- A **Pangolinfo account**: https://tool.pangolinfo.com/
- Auth env vars (choose one):
  - `PANGOLIN_TOKEN` (recommended)
  - or `PANGOLIN_EMAIL` + `PANGOLIN_PASSWORD`

```bash
export PANGOLIN_TOKEN="..."
# or
export PANGOLIN_EMAIL="..."
export PANGOLIN_PASSWORD="..."
```

## Minimal examples

Product detail:

```bash
python3 scripts/pangolinfo.py --url "https://www.amazon.com/dp/B0DYTF8L2W" --parser amzProductDetail
```

Keyword search:

```bash
python3 scripts/pangolinfo.py --q "wireless mouse" --parser amzKeyword
```

## Usage

```
--q QUERY          Keyword query (builds an Amazon search URL)
--url URL          Target Amazon URL (product/category/seller/etc.)
--parser PARSER    Parser name (default: amzProductDetail)
--zipcode CODE     Zipcode for localized pricing (default: 10041)
--format FMT       json (default) | rawHtml | markdown
--auth-only        Authenticate and show token info
--raw              Output raw API response instead of extracted data
```

### Amazon parsers

- `amzProductDetail` (default)
- `amzKeyword`
- `amzProductOfCategory`
- `amzProductOfSeller`
- `amzBestSellers`
- `amzNewReleases`
- `amzFollowSeller`

## Links

- Product: https://www.pangolinfo.com/amazon-scraper-skill/
- Amazon Scraper API: https://www.pangolinfo.com/amazon-scraper-api/
- Amazon Scrape API documentation: https://docs.pangolinfo.com/en-api-reference/amazonApi/amazonScrapeAPI
- Amazon Reviews API documentation: https://docs.pangolinfo.com/en-api-reference/amazonReviewAPI/amazonReviewAPI
- Source: https://github.com/Pangolin-spg/openclaw-skills/tree/main/pangolinfo-amazon-scraper

## References

- [references/amazon-api.md](references/amazon-api.md)
- [references/error-codes.md](references/error-codes.md)
