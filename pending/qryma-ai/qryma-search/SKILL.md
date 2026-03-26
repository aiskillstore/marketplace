---
name: qryma-search
description: Search the web with multiple output formats using the Qryma API. Use this skill when the user wants to search the web, find information on a specific topic, says "search", "look up", "find information", "web search", or needs quick answers from the internet. Supports Markdown format for readability, JSON for structured data, and Brave search-like format.
---

# qryma search

Search the web with Qryma search engine. Supports multiple output formats including Markdown, JSON, and Brave search-like format.

## Quick start

### Basic search (Markdown format)
```bash
python main_claw.py --query "how to learn python" --max-results 3 --format md
```

### JSON format output
```bash
python main_claw.py --query "latest AI trends 2024" --format raw
```

### Advanced search
```bash
python main_claw.py --query "artificial intelligence ethics" --max-results 10 --format brave
```

## Options

Option | Description
--- | ---
--api-key | Qryma API key
--query | **Required** Search query (e.g. "machine learning basics")
--max-results | Maximum number of results to return (default: 5)
--lang | Language code (default: en) - [See available languages](https://developers.google.com/custom-search/docs/xml_results_appendices#interfaceLanguages)
--start | Start offset (default: 0)
--safe | Enable safe search (default: False)
--detail | Enable detailed results (default: False)
--format | Output format: raw \| brave \| md (default: raw)

## Configuration

### Environment variable
```bash
export QRYMA_API_KEY="ak-your-api-key-here"
```

### Configuration file
Create `.env` file:
```bash
QRYMA_API_KEY=ak-your-api-key-here
```
