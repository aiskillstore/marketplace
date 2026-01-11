# Complete Workflow Guide

This guide provides step-by-step instructions for the complete PDF extraction pipeline.

## Overview

The pipeline consists of 6 main steps plus optional validation:

1. **Organize Metadata** - Standardize PDF and metadata organization
2. **Filter Papers** - Identify relevant papers by abstract (optional)
3. **Extract Data** - Extract structured data from PDFs
4. **Repair JSON** - Validate and repair JSON outputs
5. **Validate with APIs** - Enrich with external databases
6. **Export** - Convert to analysis format

**Optional:** Steps 7-9 for quality validation

## Step 1: Organize Metadata

Standardize PDF organization and metadata from various sources.

### From BibTeX (Zotero, JabRef, etc.)

```bash
python scripts/01_organize_metadata.py \
  --source-type bibtex \
  --source path/to/library.bib \
  --pdf-dir path/to/pdfs \
  --organize-pdfs \
  --output metadata.json
```

### From RIS (Mendeley, EndNote, etc.)

```bash
python scripts/01_organize_metadata.py \
  --source-type ris \
  --source path/to/library.ris \
  --pdf-dir path/to/pdfs \
  --organize-pdfs \
  --output metadata.json
```

### From PDF Directory

```bash
python scripts/01_organize_metadata.py \
  --source-type directory \
  --source path/to/pdfs \
  --output metadata.json
```

### From DOI List

```bash
python scripts/01_organize_metadata.py \
  --source-type doi_list \
  --source dois.txt \
  --output metadata.json
```

**Outputs:**
- `metadata.json` - Standardized metadata file
- `organized_pdfs/` - Renamed PDFs (if --organize-pdfs used)

## Step 2: Filter Papers (Optional but Recommended)

Filter papers by analyzing abstracts to reduce PDF processing costs.

### Backend Selection

**Option A: Claude Haiku (Fast & Cheap)**
- Cost: ~$0.25 per million input tokens
- Speed: Very fast with batches API
- Accuracy: Good for most filtering tasks

```bash
python scripts/02_filter_abstracts.py \
  --metadata metadata.json \
  --backend anthropic-haiku \
  --use-batches \
  --output filtered_papers.json
```

**Option B: Claude Sonnet (More Accurate)**
- Cost: ~$3 per million input tokens
- Speed: Fast with batches API
- Accuracy: Higher for complex criteria

```bash
python scripts/02_filter_abstracts.py \
  --metadata metadata.json \
  --backend anthropic-sonnet \
  --use-batches \
  --output filtered_papers.json
```

**Option C: Local Ollama (FREE & Private)**
- Cost: $0 (runs locally)
- Speed: Depends on hardware
- Accuracy: Good with llama3.1:8b or better

```bash
python scripts/02_filter_abstracts.py \
  --metadata metadata.json \
  --backend ollama \
  --ollama-model llama3.1:8b \
  --output filtered_papers.json
```

**Before running:** Customize the filtering prompt in `scripts/02_filter_abstracts.py` (line 74) to match your criteria.

**Outputs:**
- `filtered_papers.json` - Papers marked as relevant/irrelevant

## Step 3: Extract Data from PDFs

Extract structured data using Claude's PDF vision capabilities.

### Schema Preparation

1. Copy schema template:
```bash
cp assets/schema_template.json my_schema.json
```

2. Customize for your domain:
   - Update `objective` with your extraction goal
   - Define `output_schema` structure
   - Add domain-specific `instructions`
   - Provide an `output_example`

See `assets/example_flower_visitors_schema.json` for a real-world example.

### Run Extraction

```bash
python scripts/03_extract_from_pdfs.py \
  --metadata filtered_papers.json \
  --schema my_schema.json \
  --method batches \
  --output extracted_data.json
```

**Processing methods:**
- `batches` - Most efficient for many PDFs
- `base64` - Sequential processing

**Optional flags:**
- `--filter-results filtered_papers.json` - Only process relevant papers
- `--test` - Process only 3 PDFs for testing
- `--model claude-3-5-sonnet-20241022` - Change model

**Outputs:**
- `extracted_data.json` - Raw extraction results with token counts

## Step 4: Repair and Validate JSON

Repair malformed JSON and validate against schema.

```bash
python scripts/04_repair_json.py \
  --input extracted_data.json \
  --schema my_schema.json \
  --output cleaned_data.json
```

**Optional flags:**
- `--strict` - Reject records that fail validation

**Outputs:**
- `cleaned_data.json` - Repaired and validated extractions

## Step 5: Validate with External APIs

Enrich data using external scientific databases.

### API Configuration

1. Copy API config template:
```bash
cp assets/api_config_template.json my_api_config.json
```

2. Map fields to validation APIs:
   - `gbif_taxonomy` - GBIF for biological taxonomy
   - `wfo_plants` - World Flora Online for plant names
   - `geonames` - GeoNames for locations (requires account)
   - `geocode` - OpenStreetMap for geocoding (free)
   - `pubchem` - PubChem for chemical compounds
   - `ncbi_gene` - NCBI Gene database

See `assets/example_api_config_ecology.json` for an ecology example.

### Run Validation

```bash
python scripts/05_validate_with_apis.py \
  --input cleaned_data.json \
  --apis my_api_config.json \
  --output validated_data.json
```

**Optional flags:**
- `--skip-validation` - Skip API calls, only structure data

**Outputs:**
- `validated_data.json` - Data enriched with validated taxonomy, geography, etc.

## Step 6: Export to Analysis Format

Convert to format for your analysis environment.

### Python (pandas)

```bash
python scripts/06_export_database.py \
  --input validated_data.json \
  --format python \
  --flatten \
  --output results
```

Outputs:
- `results.pkl` - pandas DataFrame
- `results.py` - Loading script

### R

```bash
python scripts/06_export_database.py \
  --input validated_data.json \
  --format r \
  --flatten \
  --output results
```

Outputs:
- `results.rds` - R data frame
- `results.R` - Loading script

### CSV

```bash
python scripts/06_export_database.py \
  --input validated_data.json \
  --format csv \
  --flatten \
  --output results.csv
```

### Excel

```bash
python scripts/06_export_database.py \
  --input validated_data.json \
  --format excel \
  --flatten \
  --output results.xlsx
```

### SQLite Database

```bash
python scripts/06_export_database.py \
  --input validated_data.json \
  --format sqlite \
  --flatten \
  --output results.db
```

Outputs:
- `results.db` - SQLite database
- `results.sql` - Example queries

**Flags:**
- `--flatten` - Flatten nested JSON for tabular format
- `--include-metadata` - Include paper metadata in output

## Cost Estimation

### Example: 100 papers, 10 pages each

**With Filtering (Recommended):**
1. Filter (Haiku): ~200 abstracts × 500 tokens × $0.25/M = **$0.03**
2. Extract (Sonnet): ~50 relevant papers × 10 pages × 2,500 tokens × $3/M = **$3.75**
3. **Total: ~$3.78**

**Without Filtering:**
1. Extract (Sonnet): 100 papers × 10 pages × 2,500 tokens × $3/M = **$7.50**

**With Local Ollama:**
1. Filter (Ollama): **$0**
2. Extract (Sonnet): ~50 papers × 10 pages × 2,500 tokens × $3/M = **$3.75**
3. **Total: ~$3.75**

### Token Usage by Step
- Abstract (~200 words): ~500 tokens
- PDF page (text-heavy): ~1,500-3,000 tokens
- Extraction prompt: ~500-1,000 tokens
- Schema/context: ~500-1,000 tokens

**Tips to reduce costs:**
- Use abstract filtering (Step 2)
- Use Haiku for filtering instead of Sonnet
- Use local Ollama for filtering (free)
- Enable prompt caching with `--use-caching`
- Process in batches with `--use-batches`

## Common Issues

### PDF Not Found
Check PDF paths in metadata.json match actual file locations.

### JSON Parsing Errors
Run Step 4 (repair JSON) - the json_repair library handles most issues.

### API Rate Limits
Scripts include delays, but check specific API documentation for limits.

### Ollama Connection Error
Ensure Ollama server is running: `ollama serve`

## Next Steps

For quality assurance, proceed to the validation workflow to calculate precision and recall metrics.

See: `references/validation_guide.md`
