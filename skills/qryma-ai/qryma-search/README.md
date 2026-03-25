# Qryma Agent Skills

Qryma Ai web search API with Markdown/JSON/Brave formats. Generous free tier covers most daily needs.

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
| `--detail` | Enable detailed results (default: False) |
| `--format` | Output format: raw \| brave \| md (default: raw) |

## Workflow

Start simple, escalate when needed:

1. **Basic Search** — `python main_claw.py --query "how to learn python" --format md`
2. **JSON Output** — `python main_claw.py --query "latest AI trends" --format raw`
3. **Multiple Results** — `python main_claw.py --query "ai ethics" --max-results 10`