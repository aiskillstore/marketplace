---
name: academic-poster-generator
description: Complete workflow for generating academic research posters from PDF literature; use when you need to extract paper content from PDFs and produce a LaTeX-based poster (beamerposter/tikzposter/baposter) with mandatory figure generation and a final rendered HTML deliverable.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have one or more research paper PDFs and need a conference-style poster draft with standard sections (Intro/Methods/Results/Conclusions).
- You want to automatically extract title/authors/abstract/sections from a PDF and restructure them into concise poster bullet points.
- You need a LaTeX poster scaffold using **beamerposter**, **tikzposter**, or **baposter**, with standard poster sizes (A0/A1/36×48").
- You must ensure posters are **visual-first** (at least 2–3 generated figures) and pass an automated quality gate before delivery.
- You want a **browser-viewable final output** (`poster.rendered.html`) rather than a compiled PDF (PDF compilation is optional).

## Key Features

- **End-to-end pipeline**: PDF → metadata extraction → content structuring → figure generation → LaTeX poster assembly → HTML base conversion → agent rendering → final HTML.
- **Scripted PDF processing**:
  - Convert PDF pages to images for reference.
  - Extract metadata (title, authors, abstract, section structure).
  - Structure content into poster-ready bullet points with word limits.
- **Mandatory figure workflow**:
  - Generate at least **2–3 figures** (schematics/flowcharts/mechanisms/comparison charts).
  - Insert figures into LaTeX templates automatically or via config.
- **Template support**:
  - `assets/templates/beamerposter-template.tex`
  - `assets/templates/tikzposter-template.tex`
  - `assets/templates/baposter-template.tex`
- **HTML-first delivery policy**:
  - Final deliverables: `poster.rendered.html` + `figures/`
  - Intermediate artifacts are temporary and must not be returned.
- **Quality control**:
  - Automated checks for HTML/LaTeX outputs.
  - Manual checklist reference: `references/poster_quality_checklist.md`
- **Design guidance**:
  - Poster design principles: `references/design_principles.md`

## Dependencies

### Python (recommended)
- Python `>=3.8`
- `pypdf` (version not pinned)
- `pdfplumber` (version not pinned)
- `pdf2image` (version not pinned)
- `pytesseract` (version not pinned; required for OCR on scanned PDFs)
- `pandas` (version not pinned; optional for table handling)
- `Pillow` (version not pinned)
- `matplotlib` (version not pinned)

Install (example):
```bash
pip install pypdf pdfplumber pdf2image pytesseract pandas pillow matplotlib
```

### System tools
- `tesseract-ocr` (for OCR; required only for scanned PDFs)
- Poppler utilities (commonly required by `pdf2image`, e.g., `pdftoppm`)

### LaTeX (optional, only if compiling PDF)
- TeX Live / MiKTeX / MacTeX
- TeX packages (via `tlmgr`, names may vary by distribution):
  - `beamerposter`
  - `tikzposter`
  - `baposter`
  - `qrcode`
  - `xcolor`
  - `tcolorbox`
  - `subcaption`
  - `graphics`

Example:
```bash
tlmgr install beamerposter tikzposter baposter qrcode xcolor tcolorbox subcaption graphics
```

### HTML conversion
- `pandoc` (required for `--html-only` base HTML generation)
- `pdf2htmlEX` (optional; only if doing PDF → HTML rendering)

## Example Usage

### 1) Run the end-to-end pipeline (recommended)

Creates a timestamped directory under `output/` and supports HTML-only mode.

```bash
python scripts/run_poster_pipeline.py paper.pdf --html-only
```

Expected final structure:
```text
output/YYYYMMDD_HHMMSS/
├── poster.rendered.html
└── figures/
    ├── mechanism.png
    ├── process_flowchart.png
    └── comparison_chart.png
```

### 2) Run stages manually (fully reproducible)

#### Stage A — Extract metadata and structure content (temporary artifacts)
```bash
python scripts/extract_metadata.py paper.pdf metadata.json
python scripts/structure_content.py paper.pdf --json poster_content.json --latex content.tex --max-words 800
python scripts/convert_pdf_to_images.py paper.pdf paper_images/ --dpi 600
```

#### Stage B — Generate figures (mandatory)
At least **2–3** figures are required.

```bash
python scripts/generate_figures.py schematic "Cell signaling pathway" mechanism.png
python scripts/generate_figures.py flowchart "Step 1;Step 2;Step 3" process_flowchart.png
python scripts/generate_figures.py comparison '{"Control":[65],"Our Method":[87]}' comparison_chart.png
```

Or generate from a config:
```bash
python scripts/generate_figures.py config figures_config.json
```

#### Stage C — Create poster LaTeX from a template (temporary artifact)
```bash
cp assets/templates/beamerposter-template.tex poster.tex
# (Edit poster.tex: title/authors/institute + paste structured content)
```

#### Stage D — Insert figures into LaTeX (temporary artifact)
```bash
python scripts/insert_figures.py poster.tex --all
# or:
python scripts/insert_figures.py poster.tex --config figures_config.json
```

#### Stage E — Convert to base HTML and render final HTML (final artifact)
```bash
python scripts/convert_poster.py poster.tex --html-only
# Agent step: read poster.html, validate <img> paths, inject CSS/layout, output poster.rendered.html
```

#### Stage F — Quality control (mandatory)
```bash
python scripts/check_poster_quality.py poster.rendered.html
```

## Implementation Details

### Pipeline and file policy

All generated files must be placed under `output/` (preferably a timestamped subdirectory). Only the following are considered **final deliverables**:

- `poster.rendered.html`
- `figures/` directory (PNG figures)

All other files are **intermediate/temporary** and must not be returned to the user, including (non-exhaustive):
- `poster.tex`, `poster.html`
- `metadata.json`, `poster_content.json`, `figures_config.json`, `figures.json`
- LaTeX auxiliary files (`.aux`, `.log`, `.out`, etc.)

Conceptual flow:
```text
PDF → metadata extraction (temp) → content structuring (temp) → figure generation (final figures/)
→ LaTeX poster (temp) → base HTML (temp) → agent rendering → poster.rendered.html (final)
```

### PDF extraction approach

- Text and tables are extracted via `pdfplumber`.
- For scanned PDFs, OCR is performed by converting pages to images (`pdf2image`) and running `pytesseract`.

Typical extraction targets:
- Title/authors (first-page patterns)
- Abstract (from “Abstract” header to next section)
- Section blocks (Introduction/Methods/Results/Conclusion)
- Tables (converted to summaries for poster bullets)

### Content structuring rules

- Convert paragraphs to bullet points suitable for poster blocks.
- Enforce a poster-friendly word budget (commonly **600–800 words** total).
- Prefer 3–6 key visuals; summarize tables into a small set of metrics.

### Figure requirements (mandatory)

- Every poster must include **at least 2–3 generated figures**.
- Target **40–50%** of poster area as visual content.
- Figures should be **≥300 DPI**, with clear labels and concise captions.

Supported figure categories:
- Schematics (systems, pathways, conceptual diagrams)
- Flowcharts (procedures, pipelines, algorithms)
- Mechanism diagrams (biological/chemical processes)
- Comparison charts (bar charts, benchmarks)

### LaTeX package selection

Use one of the supported poster packages depending on style needs:

- **beamerposter** (traditional academic)
- **tikzposter** (modern, colorful)
- **baposter** (multi-column layouts)

Templates are provided in `assets/templates/`.

### HTML rendering requirements (agent step)

After `pandoc` produces `poster.html`, the renderer must:
1. Verify all `<img>` references exist and paths resolve to `figures/`.
2. Apply poster-grade CSS (grid columns, typography, spacing, captions).
3. Ensure accessibility: **WCAG AA contrast ≥ 4.5:1**.
4. Output `poster.rendered.html` as the only final HTML artifact.

Minimum layout expectations:
- 2–3 column grid on desktop; single column on narrow screens.
- Clear hierarchy: title/authors/institution, section headers, bullet lists, figure blocks with captions.

### Quality control requirements (mandatory)

Run `scripts/check_poster_quality.py` on the final output:
- Validate that images exist and render correctly.
- Confirm layout integrity (columns/blocks).
- Ensure readability (font sizes, spacing).
- Confirm contrast compliance (≥ 4.5:1).
- Confirm figure count (≥ 2–3) and that no placeholder text remains.

References:
- Design principles: `references/design_principles.md`
- Manual checklist: `references/poster_quality_checklist.md`