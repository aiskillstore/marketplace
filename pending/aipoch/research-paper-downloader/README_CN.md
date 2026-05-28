# Research Paper Downloader

Academic Paper Downloader - Download research papers from open access databases

## Directory Structure

```
research-paper-downloader/
├── SKILL.md              # Main skill document
├── config.json           # Configuration file
├── scripts/
│   └── download.py       # Download script
└── references/
    └── apis.md           # API reference documentation
```

## Quick Start

### Install Dependencies

```bash
pip install requests
```

### Basic Usage

```bash
# Download by DOI
python scripts/download.py --doi "10.1038/nature12345"

# Download by arXiv ID
python scripts/download.py --arxiv "2310.12345"

# Search and download by keywords
python scripts/download.py --search "machine learning" --max-results 5

# View configuration
python scripts/download.py --config

# View data sources
python scripts/download.py --list-sources
```

## Configuration Instructions

Edit `config.json` for custom settings:

| Parameter | Description | Default Value |
|------|------|--------|
| `output_dir` | Download directory | `~/Downloads/ResearchPapers` |
| `timeout` | API timeout (seconds) | 30 |
| `max_retries` | Maximum retries | 3 |
| `download_timeout` | Download timeout (seconds) | 120 |
| `preferred_sources` | Data source priority | See config.json |

## Data Sources

1. **Semantic Scholar** - Open access paper API
2. **OpenAlex** - Open academic graph
3. **Unpaywall** - Open access lookup
4. **arXiv** - Preprint server
5. **PubMed** - Biomedical literature
6. **Crossref** - DOI registration agency

## Security Constraints

- Path restrictions: Only allowed to download to the configured output directory
- No code execution: Only downloads files, does not execute external code
- Timeout control: All requests have timeout limits
- Error handling: Friendly error messages, does not expose technical details

## Troubleshooting

**Download failed**
- Check if the DOI format is correct
- Confirm if the paper is open access
- Try other data sources

**Timeout error**
- Increase the `timeout` configuration value
- Check network connection

## Dependencies

- Python 3.8+
- requests library