---
name: firecrawl-web
description: "Fetch web content, take screenshots, extract structured data, search the web, and crawl documentation sites. Use when the user needs current web information, asks to scrape a URL, wants a screenshot, needs to extract specific data from a page, or wants to learn about a framework or library."
allowed-tools: ["Bash", "Read", "Write"]
---

# Firecrawl Web Skill

This skill provides web access through Firecrawl's API.

## Script Location

All commands use the bundled script:
~/.claude/skills/firecrawl-web/fc.py

## Getting Page Content

Fetch any webpage as clean markdown:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py markdown "https://example.com"
```

For cleaner output without navigation and footers:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py markdown "https://example.com" --main-only
```

## Taking Screenshots

Capture a full-page screenshot:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py screenshot "https://example.com" -o page.png
```

## Extracting Structured Data

Extract specific data using a JSON schema. Create a schema file first:

```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "price": {"type": "number"},
    "features": {"type": "array", "items": {"type": "string"}}
  }
}
```

Then extract:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py extract "https://example.com/product" --schema schema.json
```

Add a prompt for better accuracy:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py extract "https://example.com/product" --schema schema.json --prompt "Extract the main product details"
```

## Searching the Web

Search for current information:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py search "Python 3.13 new features"
```

Limit results:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py search "latest React documentation" --limit 3
```

## Crawling Documentation

Crawl a documentation site to learn about a new framework:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py crawl "https://docs.newframework.dev" --limit 30
```

Save pages to a directory:

```bash
python3 ~/.claude/skills/firecrawl-web/fc.py crawl "https://docs.example.com" --limit 50 --output ./docs
```

Each page costs one credit. Set a reasonable limit to avoid burning through your quota.
