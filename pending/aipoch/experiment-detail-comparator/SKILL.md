---
name: experiment-detail-comparator
description: Compare experimental method details between two Zotero PDF papers, identify protocol differences (ratios, dosages, timing, conditions), search supporting literature to explain why they differ, and generate an HTML report. Use when you need a parameter-level comparison of two methods and evidence-backed reasons for discrepancies.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/compare_methods.py --help
```

# Experiment Detail Comparator

## When to Use

Use this skill when you need to:

1. Compare two papers that apply the *same or highly similar* experimental method (e.g., CRISPR editing, ELISA, Western blot, synthesis protocol).
2. Identify parameter-level differences in protocols (concentration, ratio, dosage, temperature, duration, incubation, buffer composition, instrument settings).
3. Explain *why* protocols differ by searching additional references and extracting evidence-backed rationales.
4. Produce a structured, shareable **HTML comparison report** for collaborators, lab records, or reproducibility audits.
5. Standardize method extraction into machine-readable JSON for downstream analysis (QA, meta-analysis, protocol harmonization).

## Key Features

- **Zotero-first retrieval**: locate items by title/author/DOI, then resolve PDF attachments.
- **PDF → Markdown conversion** via the `mistral-pdf-to-markdown` workflow for robust text extraction.
- **Comprehensive method extraction** including:
  - reagents, concentrations, ratios, volumes
  - temperatures, durations, timing
  - organisms/cell lines, sample handling, ethics/consent (when present)
  - equipment models and settings
  - experimental design (controls, replicates, randomization/blinding when stated)
  - stepwise procedure structure
- **Optional table extraction** from PDFs to capture dense parameter tables.
- **Protocol comparison engine** producing a structured diff and a human-readable comparison table.
- **Literature-backed explanations**: query PubMed/Europe PMC/Semantic Scholar for each major difference.
- **Evidence grading** (High/Medium/Low) for each explanation.
- **HTML report generation** with citations, highlighted differences, and graded rationale sections.

## Dependencies

### Runtime (Python)

- Python `>=3.10`

### Core libraries / modules

- `json` (stdlib)
- `subprocess` (stdlib)
- `pathlib` (stdlib)
- `re` (stdlib)

### Optional but recommended

- `pdfplumber >=0.10.0` (PDF table extraction)
- `PyPDF2 >=3.0.0` (PDF text extraction / parsing support)
- `requests >=2.31.0` (download PDFs from URLs)

Install optional dependencies:

```bash
pip install "pdfplumber>=0.10.0" "PyPDF2>=3.0.0" "requests>=2.31.0"
```

### External tools / services

- Zotero MCP tools: `mcp__zotero__*`
- `mistral-pdf-to-markdown` skill (requires `MISTRAL_API_KEY`)
- Literature search tools (as available in your environment):
  - PubMed
  - Europe PMC
  - Semantic Scholar
- Optional: **EDirect** for PubMed CLI workflows  
  https://www.ncbi.nlm.nih.gov/books/NBK179288/

### Environment variables (recommended)

Set in `Notes/.env`:

- `ZOTERO_API_KEY` (required for Zotero web library access; optional for local-only)
- `ZOTERO_LIBRARY_TYPE` (`user` or `group`)
- `ZOTERO_LIBRARY_ID` (your Zotero library ID)
- `MISTRAL_API_KEY` (required for best PDF→Markdown conversion)

## Example Usage

### End-to-end run (recommended)

Compare two papers by Zotero search terms:

```bash
python run_comparison.py \
  "CRISPR-Cas9 knockout in HeLa cells" \
  "Efficient genome editing in HEK293 cells" \
  ./output
```

Compare two papers by Zotero attachment keys:

```bash
python run_comparison.py \
  ABCDEFGHIJKLMNOPQRSTUVWXYZ123456 \
  ZYXWVUTSRQPONMLKJIHGFEDCBA654321 \
  ./output
```

Compare two local PDFs:

```bash
python run_comparison.py \
  ./paper1.pdf \
  ./paper2.pdf \
  ./output
```

Expected outputs (in `./output`):

- `comparison_report.html`
- `method_details.json`
- `explanations.json`

### Manual workflow (script-by-script)

1) **Find items in Zotero and resolve PDF attachments**

```python
result1 = mcp__zotero__zotero_search_items(query="paper 1 title or author", limit=5)
item_key1 = result1[0]["key"]

result2 = mcp__zotero__zotero_search_items(query="paper 2 title or author", limit=5)
item_key2 = result2[0]["key"]

children1 = mcp__zotero__zotero_get_item_children(item_key=item_key1)
attachment_key1 = [c for c in children1 if c.get("type") == "application/pdf"][0]["key"]

children2 = mcp__zotero__zotero_get_item_children(item_key=item_key2)
attachment_key2 = [c for c in children2 if c.get("type") == "application/pdf"][0]["key"]
```

2) **Retrieve PDFs (local cache first, download if needed)**

```bash
python scripts/get_zotero_pdf.py "$ATTACHMENT_KEY1"
python scripts/get_zotero_pdf.py "$ATTACHMENT_KEY2"
```

3) **Convert PDFs to Markdown**

```bash
python scripts/convert_pdf_to_markdown.py "PATH_TO_PDF1" "temp/paper1.md"
python scripts/convert_pdf_to_markdown.py "PATH_TO_PDF2" "temp/paper2.md"
```

4) **Extract comprehensive method details to JSON**

```bash
python scripts/extract_method_section.py temp/paper1.md temp/paper1_method.json
python scripts/extract_method_section.py temp/paper2.md temp/paper2_method.json
```

5) **Compare extracted methods**

```bash
python scripts/compare_methods.py temp/paper1_method.json temp/paper2_method.json output/comparison.json
```

6) **Search literature for explanations (per major difference)**

```bash
python scripts/search_explanations.py output/comparison.json output/explanations.json
```

7) **Generate HTML report**

```bash
python scripts/generate_html_report.py \
  temp/paper1_method.json \
  temp/paper2_method.json \
  output/comparison.json \
  output/explanations.json \
  output/comparison_report.html
```

## Implementation Details

### 1) Method extraction schema (what is captured)

The extraction step aims to produce a structured JSON object per paper with:

- **Basic parameters**
  - method name (if inferable)
  - reagents and materials
  - concentrations, ratios, dosages, volumes
  - temperatures, durations, timing
  - organisms/cell lines
  - equipment list

- **Experimental design**
  - control vs experimental groups
  - replicates (technical/biological; e.g., *n=3*)
  - sample size statements
  - randomization/blinding (only if explicitly stated)
  - block design cues (if present)

- **Materials detail**
  - chemicals (supplier/manufacturer, catalog/batch when present)
  - kits and manufacturers
  - media/buffers and compositions (when listed)
  - solvents

- **Equipment detail**
  - instrument model/manufacturer
  - instrument settings (e.g., centrifuge speed, wavelength, incubation conditions)

- **Sample information**
  - source and handling (fresh/frozen/fixed/dried)
  - storage conditions
  - ethics approval / consent statements (when present)

- **Key steps**
  - step sequence (numbered when possible)
  - step type tags (preparation / reaction / purification / detection)

### 2) Optional enhancements

#### A) Extract tables directly from PDF

Use when parameters are primarily in tables (common in materials lists, primer tables, buffer recipes):

```bash
python scripts/extract_pdf_tables.py paper.pdf output/tables.json
```

Output includes detected table types (e.g., materials/parameters/results) and normalized JSON rows.

#### B) Download and parse full PDFs (URL or local)

Use when you need full-text parsing, DOI detection, or multi-language handling:

```bash
python scripts/download_full_pdf.py https://example.com/paper.pdf ./downloads
# or
python scripts/download_full_pdf.py ./local/paper.pdf ./parsed
```

Features:
- automatic language detection (e.g., English/CJK/Russian)
- DOI extraction
- JSON metadata + plain text output

### 3) Comparison logic (protocol diff)

`compare_methods(...)` identifies differences across normalized fields and produces:

- a **parameter comparison table** (Paper 1 vs Paper 2)
- a list of **significant differences** (heuristics typically prioritize:
  - large numeric deltas (e.g., 2× concentration, 10°C shift)
  - categorical changes (different reagent, cell line, instrument)
  - timing/sequence changes that affect outcomes)

Example comparison table structure:

| Parameter | Paper 1 | Paper 2 | Difference |
|---|---|---|---|
| Reagent concentration | 10 mM | 20 mM | 2× higher in Paper 2 |
| Temperature | 37°C | 25°C | 12°C lower in Paper 2 |
| Duration | 2 h | 4 h | 2× longer in Paper 2 |

### 4) Literature search and explanation synthesis

For each significant difference, the skill builds targeted queries such as:

- `{method_name} {parameter} optimization`
- `{parameter} effect on yield`
- `{reagent} concentration protocol comparison`

Supported sources (depending on your toolchain availability):

- PubMed
- Europe PMC (including full-text term extraction when available)
- Semantic Scholar (including PDF snippet retrieval when available)

The output is an explanation object per parameter with:
- summary rationale
- citations
- extracted supporting snippets (when available)

### 5) Evidence grading rubric

Each explanation is graded:

- **High**: direct mechanistic or comparative experimental evidence supporting the parameter choice.
- **Medium**: empirical optimization/functional evidence without strong mechanistic validation.
- **Low**: review-level mention, indirect rationale, or anecdotal protocol statements.

### 6) HTML report generation

The report includes:

- paper metadata blocks
- a comparison table with highlighted differences
- per-parameter explanation sections with evidence grade styling
- references list

Primary output file:

- `comparison_report.html` (shareable, human-readable)

Supporting outputs:

- `method_details.json` (structured extraction for both papers)
- `explanations.json` (search results + graded rationales)

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `experiment_detail_comparator_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```bash
python scripts/compare_methods.py --help
```

Expected output format:

```text
Result file: experiment_detail_comparator_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
