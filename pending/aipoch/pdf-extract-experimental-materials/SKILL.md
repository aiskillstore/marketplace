---
name: pdf-extract-experimental-materials
description: Extract experimental materials and instrument information from PDFs (or PDF-derived text/Markdown) into three CSV tables; use when a paper/report contains sections like Materials and Methods, Key Resources Table, Reagents, Antibodies, Consumables, Software, Equipment, Instruments, or Reagent Preparation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

## When to Use

- You need to build a structured inventory of **reagents/antibodies/consumables** from a paper's *Materials and Methods* section.
- A document includes a **Key Resources Table** and you want to convert it into clean CSV outputs.
- You want to extract **instrument/equipment** details (brand + model) from methods text or tables.
- You need to capture **software and versions** mentioned in methods (e.g., analysis pipelines, imaging software).
- You want to standardize **reagent preparation** instructions (buffers/solutions, concentrations, temperatures, steps) into a table.

## Key Features

- Accepts **PDF-derived Markdown/text** as primary input; falls back to PDF text extraction when needed.
- **Table-first parsing**: prioritizes structured tables (e.g., Key Resources Table) before scanning prose sections.
- Extracts and outputs **three normalized CSV tables** with fixed schemas:
  - Main reagents (including antibodies/consumables/software versions)
  - Main instruments
  - Reagent preparation methods
- Uses **section heading + keyword targeting** to locate relevant regions and fill gaps.
- Enforces **non-hallucination rules**: unknown brand/model/catalog/version fields remain blank.

## Dependencies

- Python 3.10+
- pdfplumber >= 0.10.0 (recommended for text-based PDFs)
- OCR engine (only for scanned PDFs), e.g.:
  - pytesseract >= 0.3.10
  - Tesseract OCR >= 5.0

## Example Usage

### 1) Convert PDF to Markdown (preferred)
Reuse the existing script to generate parseable Markdown; only use OCR for scanned PDFs.

```bash
python d:\SKILL\project\pdf-extract\scripts\extract_pdf.py -i input.pdf -o out.md
```

### 2) Extract and write CSV outputs
After you have PDF-derived text/Markdown, extract the target fields and write exactly these three files:

- `main_reagents.csv`
- `main_instruments.csv`
- `reagent_preparation.csv`

CSV schemas (must match exactly):

`main_reagents.csv`
```csv
name,brand,catalog_number
```

`main_instruments.csv`
```csv
instrument,brand,model
```

`reagent_preparation.csv`
```csv
reagent,preparation_method
```

## Implementation Details

### 1) Input decision logic
- If **Markdown/text is available and structured**, parse tables and sections directly.
- If only **PDF** is available:
  - Prefer **pdfplumber** for text-based PDFs.
  - Use **OCR** only when the PDF is scanned (image-only).

### 2) Target region detection (table-first)
Prioritize extraction in this order:
1. **Key Resources Table** (or any structured materials table)
2. **Materials and Methods** tables
3. Prose sections identified by headings/keywords, such as:
   - *Key resources table*, *Materials and Methods*, *Reagents*, *Antibodies*, *Consumables*, *Software*, *Equipment*, *Instruments*, *Reagent preparation*, *Buffers*, *Solutions*

When a table exists, parse it first; then scan prose to fill missing items.

### 3) Field extraction rules
**A. Main reagents (`name, brand, catalog_number`)**
- Include: reagents, antibodies, consumables, and software versions.
- Software mapping:
  - `name` = software name
  - `brand` = vendor/project/organization (if explicitly stated)
  - `catalog_number` = version/release (if explicitly stated)
- If `brand` or `catalog_number` is not present, leave it blank (do not infer).

**B. Main instruments (`instrument, brand, model`)**
- `instrument` = instrument/equipment name (e.g., "confocal microscope")
- `brand` = manufacturer/vendor (only if stated)
- `model` = model identifier string (often alphanumeric; only if stated)

**C. Reagent preparation (`reagent, preparation_method`)**
- `reagent` = buffer/solution/reagent being prepared
- `preparation_method` = preparation text, including any explicitly stated:
  - concentration, solvent, ratios, steps, incubation/temperature/time, pH adjustments

### 4) Output constraints and quality checks
- Write **three CSV files** with the exact column names shown above.
- **Deduplicate** entries by primary name (e.g., reagent name or instrument name) and keep the **most complete** row.
- Preserve **original casing and punctuation** from the source.
- Perform a **spot check of at least three items** against the PDF source to confirm correctness.

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
- If a file is produced, prefer a deterministic output name such as `pdf_extract_experimental_materials_result.md` unless the skill documentation defines a better convention.
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

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: pdf_extract_experimental_materials_result.md
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
