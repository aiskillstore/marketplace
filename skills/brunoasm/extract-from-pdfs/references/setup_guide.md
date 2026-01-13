# Setup Guide for PDF Data Extraction

## Installation

### Using Conda (Recommended)

Create a dedicated environment for the extraction pipeline:

```bash
conda env create -f environment.yml
conda activate pdf_extraction
```

### Using pip

```bash
pip install -r requirements.txt
```

## Required Dependencies

### Core Dependencies
- `anthropic>=0.40.0` - Anthropic API client
- `pybtex>=0.24.0` - BibTeX file handling
- `rispy>=0.6.0` - RIS file handling
- `json-repair>=0.25.0` - JSON repair and validation
- `jsonschema>=4.20.0` - JSON schema validation
- `pandas>=2.0.0` - Data processing
- `requests>=2.31.0` - HTTP requests for APIs

### Export Dependencies
- `openpyxl>=3.1.0` - Excel export
- `pyreadr>=0.5.0` - R RDS export

## API Keys Setup

### Anthropic API Key (Required for Claude backends)

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Add to your shell profile (~/.bashrc, ~/.zshrc) for persistence:

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### GeoNames Username (Optional - for geographic validation)

1. Register at https://www.geonames.org/login
2. Enable web services in your account
3. Set environment variable:

```bash
export GEONAMES_USERNAME='your-username'
```

## Local Model Setup (Ollama)

For free, private, offline abstract filtering:

### Installation

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### Pulling Models

```bash
# Recommended models
ollama pull llama3.1:8b      # Good balance (8GB RAM)
ollama pull mistral:7b       # Fast, simple filtering
ollama pull qwen2.5:7b       # Multilingual support
ollama pull llama3.1:70b     # Best accuracy (64GB RAM)
```

### Starting Ollama Server

Usually auto-starts, but can be manually started:

```bash
ollama serve
```

The server runs at http://localhost:11434 by default.

## Verifying Installation

Test that all components are properly installed:

```bash
# Test Python dependencies
python -c "import anthropic, pybtex, rispy, json_repair, pandas; print('All dependencies OK')"

# Test Anthropic API
python -c "import os; from anthropic import Anthropic; client = Anthropic(); print('API key valid')"

# Test Ollama (if using)
curl http://localhost:11434/api/tags
```

## Directory Structure

The skill will work with PDFs and metadata organized in various ways:

### Option A: Reference Manager Export
```
project/
├── library.bib              # BibTeX export
└── pdfs/
    ├── Smith2020.pdf
    ├── Jones2021.pdf
    └── ...
```

### Option B: Simple Directory
```
project/
└── pdfs/
    ├── paper1.pdf
    ├── paper2.pdf
    └── ...
```

### Option C: DOI List
```
project/
└── dois.txt                 # One DOI per line
```

## Next Steps

After installation, proceed to the workflow guide to start extracting data from your PDFs.

See: `references/workflow_guide.md`
