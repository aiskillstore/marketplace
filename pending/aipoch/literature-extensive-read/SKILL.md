---
name: literature-extensive-read
description: Rapidly skim and summarize academic papers (default:PDF-to-Markdown full text with `## Page XX` pagination and image references) and output a structured extensive-reading summary in Markdown when you need to quickly understand research questions, methods, key results, conclusions, and decide whether intensive reading is worthwhile.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a paper converted from PDF to Markdown and need a fast, structured overview before deciding to read it deeply.
- You need to extract the research question, methodology, main findings, and conclusions for literature triage.
- You are reviewing many papers and want consistent summaries using a fixed template.
- You want a quick interpretation of figures/tables referenced as images in the Markdown (only based on what is explicitly shown/described).
- You need to produce a UTF-8 Markdown summary file saved to a standard output directory for later review.

## Key Features

- Rapid extensive reading workflow: prioritize title/abstract/conclusion, then scan methods and results.
- Structured output using a predefined Markdown template.
- Supports PDF-to-Markdown inputs that include `## Page XX` pagination headers.
- Allows using embedded image references (e.g., `![page-01](...)`) to briefly describe charts/tables when explicitly interpretable.
- Strictly summarizes only explicit content from the provided text (no speculation); missing items are marked as **“Not specified”**.
- Standardized output location: saves results to `outputs/` (created if missing).

## Dependencies

- `pdf-extract` (version: Not specified) — used only when the input is PDF and must be converted to Markdown first.
- `securityclaw` (version: Not specified) — optional security audit report saved alongside outputs.

## Example Usage

### Input

Assume you have one of the following:

1) A PDF-to-Markdown file (recommended):
- `paper.md` (contains full text, may include `## Page XX` and image references)

2) Only a PDF:
- `paper.pdf` (convert it first using `pdf-extract`)

### Steps

1) **(Optional) Convert PDF to Markdown**
```bash
pdf-extract paper.pdf > paper.md
```

2) **Read and summarize using the template**
- Read `paper.md`, prioritizing: **Title → Abstract → Conclusion**, then scan **Methods** and **Results**.
- Follow requirements and quality checks in:
  - `references/guide.md`
- Fill the output template:
  - `assets/rapid_summary_template.md`
- If any field cannot be found in the text, write: **Not specified**.

3) **Save output**
- Save the completed summary as a UTF-8 encoded Markdown file to:
  - `outputs/rapid_summary.md`

4) **(Optional) Save security audit report**
- If generated, save the `securityclaw` report to:
  - `outputs/`

## Implementation Details

- **Input format**
  - Default input is full-text Markdown converted from PDF.
  - Pagination headers like `## Page XX` may appear and should be treated as page markers, not section headings.
  - Image references (e.g., `![page-01](...)`) may be used to support brief figure/table descriptions **only when the content is explicitly interpretable**.

- **Reading strategy (algorithm)**
  1. Extract bibliographic and high-level intent from **Title/Abstract**.
  2. Identify the **research question(s)** and scope.
  3. Scan **Methods** to capture: data, experimental setup, models, baselines, evaluation metrics, and key parameters (only if explicitly stated).
  4. Scan **Results** to capture the main quantitative/qualitative findings and comparisons.
  5. Read **Conclusion/Discussion** to capture claims, limitations, and future work.
  6. Produce an **intensive-reading recommendation** based on the paper’s stated contributions, clarity of evidence, and relevance to the user’s goal (when provided).

- **Output rules**
  - Use `assets/rapid_summary_template.md` as the sole structure for the final summary.
  - If information is missing or unclear in the source text, write **Not specified** (do not infer).
  - Output must be Markdown (`.md`) and saved in **UTF-8** to avoid encoding issues.
  - Default output language is Chinese unless the user explicitly requests another language.