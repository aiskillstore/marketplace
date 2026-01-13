# Extract Structured Data from Scientific PDFs

A comprehensive pipeline for extracting standardized data from scientific literature PDFs using Claude AI.

## Overview

This skill provides an end-to-end workflow for:
- Organizing PDF literature and metadata from various sources
- Filtering relevant papers based on abstract content (optional)
- Extracting structured data from full PDFs using Claude's vision capabilities
- Repairing and validating JSON outputs
- Enriching data with external scientific databases
- Exporting to multiple analysis formats (Python, R, Excel, CSV, SQLite)

## Quick Start

### 1. Installation

Create a conda environment:

```bash
conda env create -f environment.yml
conda activate pdf_extraction
```

Or install with pip:

```bash
pip install -r requirements.txt
```

### 2. Setup API Keys

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

For geographic validation (optional):
```bash
export GEONAMES_USERNAME='your-geonames-username'
```

### 3. Run the Skill

The easiest way is to use the skill through Claude Code:

```bash
claude-code
```

Then activate the skill by mentioning it in your conversation. The skill will guide you through an interactive setup process.

## Documentation

The skill includes comprehensive reference documentation:

- `references/setup_guide.md` - Installation and configuration
- `references/workflow_guide.md` - Complete step-by-step workflow with examples
- `references/validation_guide.md` - Validation methodology and metrics interpretation
- `references/api_reference.md` - External API integration details

## Manual Workflow

You can also run the scripts manually:

### Step 1: Organize Metadata

```bash
python scripts/01_organize_metadata.py \
  --source-type bibtex \
  --source path/to/library.bib \
  --pdf-dir path/to/pdfs \
  --organize-pdfs \
  --output metadata.json
```

### Step 2: Filter Papers (Optional)

First, customize the filtering prompt in `scripts/02_filter_abstracts.py` for your use case.

**Option A: Claude Haiku (Fast & Cheap - ~$0.25/M tokens)**
```bash
python scripts/02_filter_abstracts.py \
  --metadata metadata.json \
  --backend anthropic-haiku \
  --use-batches \
  --output filtered_papers.json
```

**Option B: Local Model via Ollama (FREE)**
```bash
# One-time setup:
# 1. Install Ollama from https://ollama.com
# 2. Pull model: ollama pull llama3.1:8b
# 3. Start server: ollama serve

python scripts/02_filter_abstracts.py \
  --metadata metadata.json \
  --backend ollama \
  --ollama-model llama3.1:8b \
  --output filtered_papers.json
```

Recommended Ollama models:
- `llama3.1:8b` - Good balance (8GB RAM)
- `mistral:7b` - Fast, good for simple filtering
- `qwen2.5:7b` - Good multilingual support
- `llama3.1:70b` - Better accuracy (64GB RAM)

### Step 3: Extract Data from PDFs

First, create your extraction schema by copying and customizing `assets/schema_template.json`.

```bash
python scripts/03_extract_from_pdfs.py \
  --metadata filtered_papers.json \
  --schema my_schema.json \
  --method batches \
  --output extracted_data.json
```

### Step 4: Repair JSON

```bash
python scripts/04_repair_json.py \
  --input extracted_data.json \
  --schema my_schema.json \
  --output cleaned_data.json
```

### Step 5: Validate with APIs

First, create your API configuration by copying and customizing `assets/api_config_template.json`.

```bash
python scripts/05_validate_with_apis.py \
  --input cleaned_data.json \
  --apis my_api_config.json \
  --output validated_data.json
```

### Step 6: Export

```bash
# For Python/pandas
python scripts/06_export_database.py \
  --input validated_data.json \
  --format python \
  --flatten \
  --output results

# For R
python scripts/06_export_database.py \
  --input validated_data.json \
  --format r \
  --flatten \
  --output results

# For CSV
python scripts/06_export_database.py \
  --input validated_data.json \
  --format csv \
  --flatten \
  --output results.csv
```

### Validation & Quality Assurance (Optional but Recommended)

Validate extraction quality using precision and recall metrics:

#### Step 7: Prepare Validation Set

```bash
python scripts/07_prepare_validation_set.py \
  --extraction-results cleaned_data.json \
  --schema my_schema.json \
  --sample-size 20 \
  --strategy stratified \
  --output validation_set.json
```

Sampling strategies:
- `random` - Random sample
- `stratified` - Sample by extraction characteristics
- `diverse` - Maximize diversity

#### Step 8: Manual Annotation

1. Open `validation_set.json`
2. For each sampled paper:
   - Read the PDF
   - Fill in `ground_truth` field with correct extraction
   - Add `annotator` name and `annotation_date`
   - Use `notes` for ambiguous cases
3. Save the file

#### Step 9: Calculate Metrics

```bash
python scripts/08_calculate_validation_metrics.py \
  --annotations validation_set.json \
  --output validation_metrics.json \
  --report validation_report.txt
```

This produces:
- **Precision**: % of extracted items that are correct
- **Recall**: % of true items that were extracted
- **F1 Score**: Harmonic mean of precision and recall
- **Per-field metrics**: Accuracy by field type

Use these metrics to:
- Identify weak points in extraction prompts
- Compare models (Haiku vs Sonnet vs Ollama)
- Iterate and improve schema
- Report quality in publications

## Customization

### Creating Your Extraction Schema

1. Copy `assets/schema_template.json` to `my_schema.json`
2. Customize the following sections:
   - `objective`: What you're extracting
   - `system_context`: Your scientific domain
   - `instructions`: Step-by-step guidance for Claude
   - `output_schema`: JSON schema defining your data structure
   - `output_example`: Example of desired output

See `assets/example_flower_visitors_schema.json` for a real-world example.

### Configuring API Validation

1. Copy `assets/api_config_template.json` to `my_api_config.json`
2. Map your schema fields to appropriate validation APIs
3. See available APIs in `scripts/05_validate_with_apis.py` and `references/api_reference.md`

See `assets/example_api_config_ecology.json` for an ecology example.

## Cost Estimation

PDF processing costs approximately 1,500-3,000 tokens per page:

- 10-page paper: ~20,000-30,000 tokens
- 100 papers: ~2-3M tokens
- With Sonnet 4.5: ~$6-9 for 100 papers

Tips to reduce costs:
- Use abstract filtering (Step 2) to reduce full PDF processing
- Enable prompt caching with `--use-caching`
- Use batch processing (`--method batches`)
- Consider using Haiku for simpler extractions

## Supported Data Sources

### Bibliography Formats
- BibTeX (Zotero, JabRef, etc.)
- RIS (Mendeley, EndNote, etc.)
- Directory of PDFs
- List of DOIs

### Output Formats
- Python (pandas DataFrame pickle)
- R (RDS file)
- CSV
- JSON
- Excel
- SQLite database

### Validation APIs
- **Biology**: GBIF, World Flora Online, NCBI Gene
- **Geography**: GeoNames, OpenStreetMap Nominatim
- **Chemistry**: PubChem
- **Medicine**: (extensible - add your own)

## Examples

See the [beetle flower visitors repository](https://github.com/brunoasm/ARE_2026_beetle_flower_visitors) for a real-world example of this workflow in action.

## Troubleshooting

### PDF Size Limits
- Maximum file size: 32MB
- Maximum pages: 100
- Solution: Use chunked processing for larger PDFs

### JSON Parsing Errors
- The `json-repair` library handles most common issues
- Check your schema validation
- Review Claude's analysis output for clues

### API Rate Limits
- Add delays between requests (implemented in scripts)
- Use batch processing when available
- Check specific API documentation for limits

## Contributing

To add support for additional validation APIs:
1. Add validator function to `scripts/05_validate_with_apis.py`
2. Register in `API_VALIDATORS` dictionary
3. Update `api_config_template.json` with examples

## Citation

If you use this skill in your research, please cite:

```bibtex
@software{pdf_extraction_skill,
  title = {Extract Structured Data from Scientific PDFs},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/your-repo}
}
```

## License

MIT License - see LICENSE file for details
