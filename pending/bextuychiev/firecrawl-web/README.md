# Firecrawl Web Skill for Claude Code

A Claude Code skill that adds web scraping capabilities using [Firecrawl](https://firecrawl.dev). This skill gives Claude Code reliable web access for fetching page content, taking screenshots, extracting structured data, searching the web, and crawling documentation sites.

## Features

- **Markdown extraction** - Fetch any webpage as clean, LLM-ready markdown
- **Screenshots** - Capture full-page screenshots of any URL
- **Structured data extraction** - Extract specific fields using JSON schemas
- **Web search** - Search the web and get full content from results
- **Documentation crawling** - Crawl entire doc sites to learn new frameworks

## Installation

1. Clone this repo into your Claude Code skills directory:

```bash
git clone https://github.com/bexgboost/firecrawl-claude-code-skill.git ~/.claude/skills/firecrawl-web
```

2. Install dependencies:

```bash
pip install firecrawl python-dotenv
```

3. Get your Firecrawl API key from [firecrawl.dev](https://firecrawl.dev) and add it to your environment:

```bash
echo 'FIRECRAWL_API_KEY=fc-your-key-here' >> ~/.env
```

4. Restart Claude Code to load the skill.

## Usage

The skill triggers automatically when you ask Claude Code to:
- "Get the markdown from this URL"
- "Take a screenshot of this page"
- "Extract the price and title from this product page"
- "Search the web for Python 3.13 features"
- "Crawl the Optuna documentation"

You can also use the script directly:

```bash
# Fetch markdown
python3 ~/.claude/skills/firecrawl-web/fc.py markdown "https://example.com"

# Take screenshot
python3 ~/.claude/skills/firecrawl-web/fc.py screenshot "https://example.com" -o page.png

# Search the web
python3 ~/.claude/skills/firecrawl-web/fc.py search "your query" --limit 5

# Crawl docs
python3 ~/.claude/skills/firecrawl-web/fc.py crawl "https://docs.example.com" --limit 30
```

## Firecrawl Credits

- Free tier: 500 credits
- Scrape/screenshot/extract: 1 credit per URL
- Search: 1 credit per query
- Crawl: 1 credit per page

## Learn More

This skill was built as part of the tutorial: [How to Create a Claude Code Skill: A Web Scraping Example with Firecrawl](https://firecrawl.dev/blog/claude-code-skill)

## License

MIT
