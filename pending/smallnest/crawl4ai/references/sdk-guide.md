# Crawl4AI Python SDK Guide
<!-- Reference: Tier 2 - Python SDK interface for Crawl4AI -->

## Quick Start
<!-- Lines 1-60 -->

### Installation

```bash
pip install crawl4ai
crawl4ai-setup
```

### Basic First Crawl

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:500])

asyncio.run(main())
```

### With Configuration

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

browser_config = BrowserConfig(
    headless=True,
    viewport_width=1920,
    viewport_height=1080
)

crawler_config = CrawlerRunConfig(
    page_timeout=30000,
    screenshot=True,
    remove_overlay_elements=True
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(
        url="https://example.com",
        config=crawler_config
    )
    print(f"Success: {result.success}")
    print(f"Markdown length: {len(result.markdown)}")
```

For complete API reference: [AsyncWebCrawler](complete-sdk-reference.md#asyncwebcrawler) (lines 517-778)

---

## Configuration
<!-- Lines 61-150 -->

### BrowserConfig

Controls the browser instance (global settings):

```python
from crawl4ai import BrowserConfig

browser_config = BrowserConfig(
    browser_type="chromium",    # chromium, firefox, webkit
    headless=True,              # Run without GUI
    viewport_width=1280,
    viewport_height=720,
    user_agent="custom-agent",  # Custom user agent
    proxy_config={              # Proxy settings
        "server": "http://proxy:8080",
        "username": "user",
        "password": "pass"
    }
)
```

**Key Parameters:**
| Parameter | Description |
|-----------|-------------|
| `headless` | Run with/without GUI |
| `viewport_width/height` | Browser dimensions |
| `user_agent` | Custom user agent string |
| `cookies` | Pre-set cookies |
| `headers` | Custom HTTP headers |
| `proxy_config` | Proxy server settings |

For all parameters: [BrowserConfig Reference](complete-sdk-reference.md#1-browserconfig--controlling-the-browser) (lines 1977-2020)

### CrawlerRunConfig

Controls each crawl operation (per-crawl settings):

```python
from crawl4ai import CrawlerRunConfig, CacheMode

config = CrawlerRunConfig(
    # Timing
    page_timeout=30000,         # Max page load time (ms)
    wait_for="css:.content",    # Wait for element
    delay_before_return_html=0.5,

    # Content selection
    css_selector=".main-content",
    excluded_tags=["nav", "footer"],

    # Caching
    cache_mode=CacheMode.BYPASS,

    # JavaScript
    js_code="window.scrollTo(0, document.body.scrollHeight);",

    # Output
    screenshot=True,
    pdf=True
)
```

**Key Parameters:**
| Parameter | Description |
|-----------|-------------|
| `page_timeout` | Max page load/JS time (ms) |
| `wait_for` | CSS selector or JS condition |
| `cache_mode` | ENABLED, BYPASS, DISABLED |
| `js_code` | JavaScript to execute |
| `session_id` | Persist session across crawls |
| `screenshot` | Capture screenshot |

For all parameters: [CrawlerRunConfig Reference](complete-sdk-reference.md#2-crawlerrunconfig--controlling-each-crawl) (lines 2020-2330)

---

## CrawlResult
<!-- Lines 151-200 -->

Every `arun()` call returns a `CrawlResult`:

```python
result = await crawler.arun(url, config=config)

# Status
result.success          # bool - crawl succeeded
result.status_code      # HTTP status code
result.error_message    # Error details if failed

# Content
result.html             # Raw HTML
result.cleaned_html     # Sanitized HTML
result.markdown         # MarkdownGenerationResult object
result.markdown.raw_markdown    # Full markdown
result.markdown.fit_markdown    # Filtered markdown (if filter used)

# Media & Links
result.media["images"]  # List of images
result.media["videos"]  # List of videos
result.links["internal"] # Internal links
result.links["external"] # External links

# Extras
result.screenshot       # Base64 screenshot (if requested)
result.pdf              # PDF bytes (if requested)
result.metadata         # Page metadata (title, description)
```

For complete fields: [CrawlResult Reference](complete-sdk-reference.md#crawlresult-reference) (lines 1224-1612)

---

## Content Processing
<!-- Lines 201-280 -->

### Markdown Generation

```python
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

md_generator = DefaultMarkdownGenerator(
    options={
        "ignore_links": False,
        "ignore_images": False,
        "body_width": 80
    }
)

config = CrawlerRunConfig(markdown_generator=md_generator)
```

### Content Filtering

Filter content for relevance before markdown generation:

```python
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Option 1: Pruning (removes low-quality content)
pruning_filter = PruningContentFilter(
    threshold=0.4,
    threshold_type="fixed"
)

# Option 2: BM25 (relevance-based)
bm25_filter = BM25ContentFilter(
    user_query="machine learning tutorials",
    bm25_threshold=1.0
)

md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
config = CrawlerRunConfig(markdown_generator=md_generator)

result = await crawler.arun(url, config=config)
print(result.markdown.fit_markdown)  # Filtered content
print(result.markdown.raw_markdown)  # Original content
```

For filters and generators: [Content Processing](complete-sdk-reference.md#content-processing) (lines 2481-3101)

---

## Data Extraction
<!-- Lines 281-360 -->

### CSS-Based Extraction (No LLM)

Fast, deterministic extraction using CSS selectors:

```python
from crawl4ai import JsonCssExtractionStrategy

schema = {
    "name": "articles",
    "baseSelector": "article.post",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "date", "selector": ".date", "type": "text"},
        {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
    ]
}

extraction_strategy = JsonCssExtractionStrategy(schema=schema)
config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

result = await crawler.arun(url, config=config)
data = json.loads(result.extracted_content)
```

### LLM-Based Extraction

For complex or irregular content:

```python
from crawl4ai import LLMExtractionStrategy, LLMConfig
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(description="Product name")
    price: str = Field(description="Product price")

extraction_strategy = LLMExtractionStrategy(
    llm_config=LLMConfig(
        provider="openai/gpt-4o-mini",
        api_token="your-token"
    ),
    schema=Product.model_json_schema(),
    extraction_type="schema",
    instruction="Extract product information"
)

config = CrawlerRunConfig(extraction_strategy=extraction_strategy)
```

For extraction strategies: [Extraction Strategies](complete-sdk-reference.md#extraction-strategies) (lines 4522-5429)

---

## Multi-URL Crawling
<!-- Lines 361-420 -->

### Concurrent Processing with arun_many()

```python
urls = ["https://site1.com", "https://site2.com", "https://site3.com"]

config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    stream=True  # Enable streaming
)

async with AsyncWebCrawler() as crawler:
    # Streaming mode - process as they complete
    async for result in await crawler.arun_many(urls, config=config):
        if result.success:
            print(f"Completed: {result.url}")

    # Batch mode - wait for all
    config = config.clone(stream=False)
    results = await crawler.arun_many(urls, config=config)
```

### URL-Specific Configurations

```python
from crawl4ai import CrawlerRunConfig, MatchMode

# Different configs for different URL patterns
pdf_config = CrawlerRunConfig(
    url_matcher="*.pdf",
    # PDF-specific settings
)

blog_config = CrawlerRunConfig(
    url_matcher=["*/blog/*", "*/article/*"],
    match_mode=MatchMode.OR
)

default_config = CrawlerRunConfig()  # Fallback

results = await crawler.arun_many(
    urls=urls,
    config=[pdf_config, blog_config, default_config]
)
```

For dispatchers and advanced: [arun_many() Reference](complete-sdk-reference.md#arunmany-reference) (lines 1057-1224)

---

## Session Management
<!-- Lines 421-480 -->

### Persistent Sessions

```python
# First crawl - establish session
login_config = CrawlerRunConfig(
    session_id="user_session",
    js_code="""
    document.querySelector('#username').value = 'myuser';
    document.querySelector('#password').value = 'mypass';
    document.querySelector('#submit').click();
    """,
    wait_for="css:.dashboard"
)

await crawler.arun("https://site.com/login", config=login_config)

# Subsequent crawls - reuse session
config = CrawlerRunConfig(session_id="user_session")
await crawler.arun("https://site.com/protected", config=config)

# Clean up
await crawler.crawler_strategy.kill_session("user_session")
```

### Dynamic Content Handling

```python
config = CrawlerRunConfig(
    wait_for="css:.ajax-content",
    js_code="""
    window.scrollTo(0, document.body.scrollHeight);
    document.querySelector('.load-more')?.click();
    """,
    page_timeout=60000
)
```

For session patterns: [Advanced Features - Session Management](complete-sdk-reference.md#advanced-features) (lines 5429-5940)

---

## Best Practices

1. **Use context managers** - `async with AsyncWebCrawler()` ensures cleanup
2. **Enable caching during development** - `cache_mode=CacheMode.ENABLED`
3. **Set appropriate timeouts** - 30s normal, 60s+ for JS-heavy sites
4. **Prefer CSS extraction** over LLM - 10-100x more efficient
5. **Use clone() for config variants** - `config.clone(screenshot=True)`
6. **Respect rate limits** - Use delays between requests

---

## See Also

- [CLI Guide](cli-guide.md) - Command-line interface alternative
- [Complete SDK Reference](complete-sdk-reference.md) - Full API documentation
