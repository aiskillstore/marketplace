# Crawl4AI CLI Guide
<!-- Reference: Tier 2 - Command-line interface for Crawl4AI -->

## Table of Contents
<!-- Lines 1-20 -->

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Configuration](#configuration)
  - [Browser Configuration](#browser-configuration)
  - [Crawler Configuration](#crawler-configuration)
  - [Extraction Configuration](#extraction-configuration)
  - [Content Filtering](#content-filtering)
- [Advanced Features](#advanced-features)
  - [LLM Q&A](#llm-qa)
  - [Structured Data Extraction](#structured-data-extraction)
  - [Content Filtering](#content-filtering-1)
- [Output Formats](#output-formats)
- [Examples](#examples)
- [Best Practices & Tips](#best-practices--tips)

---

## Installation
<!-- Lines 21-25 -->

The Crawl4AI CLI (`crwl`) is installed automatically with the library:

```bash
pip install crawl4ai
crawl4ai-setup
```

---

## Basic Usage
<!-- Lines 26-50 -->

The `crwl` command provides a simple interface to the Crawl4AI library:

```bash
# Basic crawling - returns markdown
crwl https://example.com

# Specify output format
crwl https://example.com -o markdown

# Verbose JSON output with cache bypass
crwl https://example.com -o json -v --bypass-cache

# See usage examples
crwl --example
```

**Quick Example - Advanced Usage:**

```bash
# Extract structured data using CSS schema
crwl "https://www.infoq.com/ai-ml-data-eng/" \
    -e docs/examples/cli/extract_css.yml \
    -s docs/examples/cli/css_schema.json \
    -o json
```

---

## Configuration
<!-- Lines 51-160 -->

### Browser Configuration
<!-- Lines 51-75 -->

Browser settings via YAML file or command line:

```yaml
# browser.yml
headless: true
viewport_width: 1280
user_agent_mode: "random"
verbose: true
ignore_https_errors: true
```

```bash
# Using config file
crwl https://example.com -B browser.yml

# Using direct parameters
crwl https://example.com -b "headless=true,viewport_width=1280,user_agent_mode=random"
```

**Key Parameters:**
| Parameter | Description |
|-----------|-------------|
| `headless` | Run without GUI (true/false) |
| `viewport_width` | Browser width in pixels |
| `viewport_height` | Browser height in pixels |
| `user_agent_mode` | "random" or specific UA string |

For all browser parameters: [BrowserConfig Reference](complete-sdk-reference.md#1-browserconfig--controlling-the-browser) (lines 1977-2020)

### Crawler Configuration
<!-- Lines 76-110 -->

Control crawling behavior:

```yaml
# crawler.yml
cache_mode: "bypass"
wait_until: "networkidle"
page_timeout: 30000
delay_before_return_html: 0.5
word_count_threshold: 100
scan_full_page: true
scroll_delay: 0.3
process_iframes: false
remove_overlay_elements: true
magic: true
verbose: true
```

```bash
# Using config file
crwl https://example.com -C crawler.yml

# Using direct parameters
crwl https://example.com -c "css_selector=#main,delay_before_return_html=2,scan_full_page=true"
```

**Key Parameters:**
| Parameter | Description |
|-----------|-------------|
| `cache_mode` | bypass, enabled, disabled |
| `wait_until` | networkidle, domcontentloaded |
| `page_timeout` | Max page load time (ms) |
| `css_selector` | Focus on specific element |
| `scan_full_page` | Enable infinite scroll handling |

For all crawler parameters: [CrawlerRunConfig Reference](complete-sdk-reference.md#2-crawlerrunconfig--controlling-each-crawl) (lines 2020-2330)

### Extraction Configuration
<!-- Lines 111-160 -->

Two extraction types supported:

**1. CSS/XPath-based extraction:**

```yaml
# extract_css.yml
type: "json-css"
params:
  verbose: true
```

```json
// css_schema.json
{
  "name": "ArticleExtractor",
  "baseSelector": ".article",
  "fields": [
    {
      "name": "title",
      "selector": "h1.title",
      "type": "text"
    },
    {
      "name": "link",
      "selector": "a.read-more",
      "type": "attribute",
      "attribute": "href"
    }
  ]
}
```

**2. LLM-based extraction:**

```yaml
# extract_llm.yml
type: "llm"
provider: "openai/gpt-4"
instruction: "Extract all articles with their titles and links"
api_token: "your-token"
params:
  temperature: 0.3
  max_tokens: 1000
```

For extraction strategies: [Extraction Strategies](complete-sdk-reference.md#extraction-strategies) (lines 4522-5429)

---

## Advanced Features
<!-- Lines 161-230 -->

### LLM Q&A
<!-- Lines 161-190 -->

Ask questions about crawled content:

```bash
# Simple question
crwl https://example.com -q "What is the main topic discussed?"

# View content then ask questions
crwl https://example.com -o markdown  # See content first
crwl https://example.com -q "Summarize the key points"
crwl https://example.com -q "What are the conclusions?"

# Combined with advanced crawling
crwl https://example.com \
    -B browser.yml \
    -c "css_selector=article,scan_full_page=true" \
    -q "What are the pros and cons mentioned?"
```

**First-time setup:**
- Prompts for LLM provider and API token
- Saves configuration in `~/.crawl4ai/global.yml`
- Supports: openai/gpt-4, anthropic/claude-3-sonnet, ollama (no token needed)
- See [LiteLLM Providers](https://docs.litellm.ai/docs/providers) for full list

### Structured Data Extraction
<!-- Lines 191-210 -->

```bash
# CSS-based extraction
crwl https://example.com \
    -e extract_css.yml \
    -s css_schema.json \
    -o json

# LLM-based extraction
crwl https://example.com \
    -e extract_llm.yml \
    -s llm_schema.json \
    -o json
```

### Content Filtering
<!-- Lines 211-230 -->

Filter content for relevance:

```yaml
# filter_bm25.yml (relevance-based)
type: "bm25"
query: "target content"
threshold: 1.0

# filter_pruning.yml (quality-based)
type: "pruning"
query: "focus topic"
threshold: 0.48
```

```bash
crwl https://example.com -f filter_bm25.yml -o markdown-fit
```

For content filtering: [Content Processing](complete-sdk-reference.md#content-processing) (lines 2481-3101)

---

## Output Formats
<!-- Lines 231-240 -->

| Format | Flag | Description |
|--------|------|-------------|
| `all` | `-o all` | Full crawl result including metadata |
| `json` | `-o json` | Extracted structured data |
| `markdown` | `-o markdown` or `-o md` | Raw markdown output |
| `markdown-fit` | `-o markdown-fit` or `-o md-fit` | Filtered markdown |

---

## Complete Examples
<!-- Lines 241-280 -->

**1. Basic Extraction:**
```bash
crwl https://example.com \
    -B browser.yml \
    -C crawler.yml \
    -o json
```

**2. Structured Data Extraction:**
```bash
crwl https://example.com \
    -e extract_css.yml \
    -s css_schema.json \
    -o json \
    -v
```

**3. LLM Extraction with Filtering:**
```bash
crwl https://example.com \
    -B browser.yml \
    -e extract_llm.yml \
    -s llm_schema.json \
    -f filter_bm25.yml \
    -o json
```

**4. Interactive Q&A:**
```bash
# First crawl and view
crwl https://example.com -o markdown

# Then ask questions
crwl https://example.com -q "What are the main points?"
crwl https://example.com -q "Summarize the conclusions"
```

---

## Best Practices & Tips
<!-- Lines 281-310 -->

1. **Configuration Management:**
   - Keep common configurations in YAML files
   - Use CLI parameters for quick overrides
   - Store sensitive data (API tokens) in `~/.crawl4ai/global.yml`

2. **Performance Optimization:**
   - Use `--bypass-cache` for fresh content
   - Enable `scan_full_page` for infinite scroll pages
   - Adjust `delay_before_return_html` for dynamic content

3. **Content Extraction:**
   - Use CSS extraction for structured content (faster, no API costs)
   - Use LLM extraction for unstructured content
   - Combine with filters for focused results

4. **Q&A Workflow:**
   - View content first with `-o markdown`
   - Ask specific questions
   - Use broader context with appropriate selectors

---

## Recap

The Crawl4AI CLI provides:
- Flexible configuration via files and parameters
- Multiple extraction strategies (CSS, XPath, LLM)
- Content filtering and optimization
- Interactive Q&A capabilities
- Various output formats

---

## See Also

- [Python SDK Guide](sdk-guide.md) - Programmatic Python interface
- [Complete SDK Reference](complete-sdk-reference.md) - Full API documentation
