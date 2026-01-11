# Sitemap / Web Crawl Strategy

Discover and fetch documentation pages via sitemap.xml or link crawling.

## Overview

When llms.txt and GitHub raw aren't available, use sitemap or crawl to discover pages. Sitemap is preferred over blind crawling.

## Sitemap Detection

```bash
# Check for sitemap
curl -sI "https://docs.viperjuice.dev/sitemap.xml" | head -1

# Common sitemap locations
curl -sI "https://docs.viperjuice.dev/sitemap.xml"
curl -sI "https://docs.viperjuice.dev/sitemap_index.xml"
curl -sI "https://docs.viperjuice.dev/docs/sitemap.xml"
```

## Sitemap Fetch

```bash
# Fetch sitemap
curl -s "https://docs.viperjuice.dev/sitemap.xml"

# Extract URLs with xmllint
curl -s "https://docs.viperjuice.dev/sitemap.xml" | \
  xmllint --xpath "//*[local-name()='loc']/text()" - 2>/dev/null

# Filter to docs URLs
curl -s "https://docs.viperjuice.dev/sitemap.xml" | \
  grep -oP '(?<=<loc>)[^<]+' | \
  grep '/docs/'
```

## Sitemap Index

Some sites use sitemap index files:

```xml
<sitemapindex>
  <sitemap><loc>https://docs.viperjuice.dev/sitemap-docs.xml</loc></sitemap>
  <sitemap><loc>https://docs.viperjuice.dev/sitemap-blog.xml</loc></sitemap>
</sitemapindex>
```

```bash
# Extract sitemap URLs from index
curl -s "https://docs.viperjuice.dev/sitemap_index.xml" | \
  grep -oP '(?<=<loc>)[^<]+' | \
  xargs -I{} curl -s "{}" | grep -oP '(?<=<loc>)[^<]+'
```

## Web Crawl (Last Resort)

When no sitemap exists:

```bash
# Fetch homepage and extract links
curl -s "https://docs.viperjuice.dev/docs" | \
  grep -oP 'href="[^"]*"' | \
  grep -E '/docs/|/guide/|/api/' | \
  sed 's/href="//;s/"$//'
```

### Crawl Patterns to Match

| Pattern | Description |
|---------|-------------|
| `/docs/` | Documentation section |
| `/guide/` | Guides/tutorials |
| `/api/` | API reference |
| `/reference/` | Reference docs |
| `/learn/` | Learning resources |

## Page Content Fetch

```bash
# Fetch individual page
curl -s "https://docs.viperjuice.dev/docs/intro"

# Extract main content (basic)
curl -s "https://docs.viperjuice.dev/docs/intro" | \
  grep -oP '(?<=<main[^>]*>).*(?=</main>)'

# Better: Use readability or html2text
curl -s "https://docs.viperjuice.dev/docs/intro" | \
  python3 -c "import sys; from readability import Document; doc = Document(sys.stdin.read()); print(doc.summary())"
```

## Registry Configuration

### Sitemap

```json
{
  "example-docs": {
    "name": "Example Documentation",
    "strategy": "web_sitemap",
    "paths": {
      "homepage": "https://docs.viperjuice.dev/docs",
      "sitemap": "https://docs.viperjuice.dev/sitemap.xml"
    },
    "filters": {
      "include_patterns": ["/docs/", "/guide/"],
      "exclude_patterns": ["/blog/", "/changelog/"]
    }
  }
}
```

### Web Crawl

```json
{
  "example-docs": {
    "name": "Example Documentation",
    "strategy": "web_crawl",
    "paths": {
      "homepage": "https://docs.viperjuice.dev/docs"
    },
    "crawl": {
      "max_depth": 3,
      "include_patterns": ["/docs/"],
      "exclude_patterns": ["/blog/"]
    }
  }
}
```

## Advantages

- Works for most sites
- Sitemap shows all pages
- No framework detection needed

## Disadvantages

- May include non-doc pages
- No hierarchy information
- HTML parsing required
- Slower than raw content
- May be blocked or rate-limited

## When to Use Browser Instead

If curl returns:
- Less than 1KB response
- "Please enable JavaScript" message
- 403 Forbidden
- Framework markers only (`__NEXT_DATA__`, etc.)

Then use `cookbook/browser-strategy.md` instead.
