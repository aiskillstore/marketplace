# Qryma Agent Skills

Qryma AI Web Search SKILL, The World's Fastest and Cheapest Search API for LLM and AI Agents.

Start free now. Get your free key now [qryma.com](https://qryma.com/).

## Installation

### Install Skills
```bash
# Agent skills (Claude Code, Cursor, etc.)
npx skills add https://github.com/qryma-ai/skills

# Manual installation
git clone https://github.com/qryma-ai/skills.git qryma-search
cd qryma-search
pip install -r requirements.txt
```

### Authenticate
Get your free QRYMA_API_KEY from [qryma.com](https://qryma.com/). Chat with your AI assistant and ask it to help you complete the configuration.

```test
Please configure qryma search with the QRYMA_API_KEY set to ak-your-api-key-here.
```

从[qryma.com](https://qryma.com/) 获取免费的QRYMA_API_KEY，直接发送给你的AI助手，让他帮你自动配置。

```text
请帮我配置好qryma search，设置QRYMA_API_KEY为ak-your-api-key-here
```

Via the command line:

```bash
# Method 1: Environment variable
export QRYMA_API_KEY="ak-your-api-key-here"

# Method 2: Create .env file
echo 'QRYMA_API_KEY=ak-your-api-key-here' > .env

# Method 3: API key in command line
python main_claw.py --query "test" --api-key "ak-your-api-key"
```

Get an API key from your Qryma service provider.

## Available Skills

| Skill | Description |
|-------|-------------|
| `qryma-search` | Search the web with LLM-optimized results. Supports multiple output formats (Markdown, JSON, Brave-style). |

## Options

| Option | Description |
|--------|-------------|
| `--api-key` | Qryma API key |
| `--query` | **Required** Search query (e.g. "machine learning") |
| `--max-results` | Maximum number of results (default: 5) |
| `--lang` | Language code (default: en) - [See available languages](https://developers.google.com/custom-search/docs/xml_results_appendices#interfaceLanguages) |
| `--start` | Start offset (default: 0) |
| `--safe` | Enable safe search (default: False) |
| `--mode` | Search mode: fulltext (detailed) | snippet (concise) (default: fulltext) |
| `--format` | Output format: raw \| brave \| md (default: raw) |

## Workflow

Start simple, escalate when needed:

1. **Basic Search** — `python main_claw.py --query "how to learn python" --format md`
2. **JSON Output** — `python main_claw.py --query "latest AI trends" --format raw`
3. **Multiple Results** — `python main_claw.py --query "ai ethics" --max-results 5`
