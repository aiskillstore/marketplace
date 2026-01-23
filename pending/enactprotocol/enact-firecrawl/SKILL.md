---
name: enact/firecrawl
version: 1.2.1
description: Scrape, crawl, search, and extract structured data from websites using Firecrawl API - converts web pages to LLM-ready markdown
enact: "2.0"

from: python:3.12-slim

build:
  - pip install requests

env:
  FIRECRAWL_API_KEY:
    description: Your Firecrawl API key from firecrawl.dev
    secret: true

command: python /workspace/firecrawl.py ${action} ${url} ${formats} ${limit} ${only_main_content} ${prompt} ${schema}

timeout: 300s

license: MIT

tags:
  - web-scraping
  - crawling
  - markdown
  - llm
  - ai
  - data-extraction
  - search
  - structured-data

annotations:
  readOnlyHint: true
  openWorldHint: true

inputSchema:
  type: object
  properties:
    action:
      type: string
      description: |
        The action to perform:
        - scrape: Extract content from a single URL
        - crawl: Discover and scrape all subpages of a website
        - map: Get all URLs from a website (fast discovery)
        - search: Search the web and get scraped results
        - extract: Extract structured data using AI
      enum:
        - scrape
        - crawl
        - map
        - search
        - extract
      default: scrape
    url:
      type: string
      description: The URL to process (for scrape, crawl, map, extract) or search query (for search action)
    formats:
      type: string
      description: Comma-separated output formats (markdown, html, links, screenshot). Used by scrape and crawl actions.
      default: markdown
    limit:
      type: integer
      description: Maximum number of pages to crawl (crawl action) or search results to return (search action)
      default: 10
    only_main_content:
      type: boolean
      description: Extract only the main content, excluding headers, navs, footers (scrape action)
      default: true
    prompt:
      type: string
      description: |
        Multi-purpose field:
        - For map: Search query to filter URLs
        - For extract: Natural language instruction for what to extract
      default: ""
    schema:
      type: string
      description: JSON schema string for structured extraction (extract action only). Define the shape of data you want to extract.
      default: ""
  required:
    - url

outputSchema:
  type: object
  properties:
    success:
      type: boolean
      description: Whether the operation succeeded
    action:
      type: string
      description: The action that was performed
    url:
      type: string
      description: The URL or query that was processed
    data:
      type: object
      description: The scraped/crawled/extracted data including markdown, metadata, and structured content
    error:
      type: string
      description: Error message if the operation failed

examples:
  - input:
      url: "https://example.com"
      action: "scrape"
    description: Scrape a single page and get markdown
  - input:
      url: "https://docs.example.com"
      action: "crawl"
      limit: 5
    description: Crawl a documentation site (up to 5 pages)
  - input:
      url: "https://example.com"
      action: "map"
    description: Get all URLs from a website
  - input:
      url: "latest AI news"
      action: "search"
      limit: 5
    description: Search the web and get scraped results
  - input:
      url: "https://news.ycombinator.com"
      action: "extract"
      prompt: "Extract the top 5 news headlines with their URLs and point counts"
    description: Extract structured data from a page using AI
---

# Firecrawl Web Scraping Tool

A powerful web scraping tool that uses the [Firecrawl API](https://firecrawl.dev) to convert websites into clean, LLM-ready markdown and extract structured data.

## Features

- **Scrape**: Extract content from a single URL as markdown, HTML, or with screenshots
- **Crawl**: Automatically discover and scrape all accessible subpages of a website
- **Map**: Get a list of all URLs from a website without scraping content (extremely fast)
- **Search**: Search the web and get full scraped content from results
- **Extract**: Use AI to extract structured data from pages with natural language prompts

## Setup

1. Get an API key from [firecrawl.dev](https://firecrawl.dev)
2. Set your API key as a secret:
   ```bash
   enact env set FIRECRAWL_API_KEY <your-api-key> --secret --namespace enact
   ```

This stores your API key securely in your OS keyring (macOS Keychain, Windows Credential Manager, or Linux Secret Service).

## Usage Examples

### CLI

#### Scrape a single page
```bash
enact run enact/firecrawl -a '{"url": "https://example.com", "action": "scrape"}'
```

#### Crawl an entire documentation site
```bash
enact run enact/firecrawl -a '{"url": "https://docs.example.com", "action": "crawl", "limit": 20}'
```

#### Map all URLs on a website
```bash
enact run enact/firecrawl -a '{"url": "https://example.com", "action": "map"}'
```

#### Search the web
```bash
enact run enact/firecrawl -a '{"url": "latest AI developments 2024", "action": "search", "limit": 5}'
```

#### Extract structured data with AI
```bash
enact run enact/firecrawl -a '{"url": "https://news.ycombinator.com", "action": "extract", "prompt": "Extract the top 10 news headlines with their URLs"}'
```

#### Extract with a JSON schema
```bash
enact run enact/firecrawl -a '{
  "url": "https://example.com/pricing",
  "action": "extract",
  "prompt": "Extract pricing information",
  "schema": "{\"type\":\"object\",\"properties\":{\"plans\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"name\":{\"type\":\"string\"},\"price\":{\"type\":\"string\"}}}}}}"
}'
```

### MCP (for LLMs/Agents)

When using this tool via MCP, call `enact__firecrawl` with these parameters:

#### Scrape a single page
Call with `url` set to the target URL and `action` set to `"scrape"`.

#### Crawl a documentation site
Call with `url`, `action` set to `"crawl"`, and `limit` to control the maximum number of pages.

#### Map all URLs on a website
Call with `url` and `action` set to `"map"` to discover all URLs without scraping content.

#### Search the web
Call with `url` set to your search query (e.g., "latest AI news") and `action` set to `"search"`. Use `limit` to control result count.

#### Extract structured data with AI
Call with `url`, `action` set to `"extract"`, and `prompt` describing what data to extract. Optionally provide a `schema` for structured output.

## Output

The tool returns JSON with:
- **markdown**: Clean, LLM-ready content
- **metadata**: Title, description, language, source URL
- **extract**: Structured data (for extract action)
- **links**: Discovered URLs (for map action)

## API Features

Firecrawl handles the hard parts of web scraping:
- Anti-bot mechanisms
- Dynamic JavaScript content
- Proxies and rate limiting
- PDF and document parsing
- Screenshot capture