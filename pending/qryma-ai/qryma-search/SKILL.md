---
name: qryma-search
description: Search the web with multiple output formats using the Qryma API. Use this skill when the user wants to search the web, find information on a specific topic, says "search", "look up", "find information", "web search", or needs quick answers from the internet. Supports Markdown format for readability, JSON for structured data, and Brave search-like format.
---

# qryma search

Qryma AI Web Search SKILL, The World's Fastest and Cheapest Search API for LLM and AI Agents.

Search the web with Qryma search engine. Supports multiple output formats including Markdown, JSON, and Brave search-like format.

Start free now. Get your free key now [qryma.com](https://qryma.com/).

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
--mode | Search mode: fulltext (detailed) | snippet (concise) (default: fulltext)
--format | Output format: raw \| brave \| md (default: raw)

## Authenticate

Get your free QRYMA_API_KEY from [qryma.com](https://qryma.com/). Chat with your AI assistant and ask it to help you complete the configuration.

```test
 Please configure qryma search with the QRYMA_API_KEY set to ak-your-api-key-here.
 ```

从 [qryma.com](https://qryma.com/) 获取免费的 QRYMA_API_KEY，直接发送给你的 AI 助手，让他帮你自动配置。

```text
请帮我配置好 qryma search，设置 QRYMA_API_KEY 为 ak-your-api-key-here
```

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
