# Offline PDF Parsing Workflow (No API)

Use this workflow to extract text, figure legends, and images from a PDF using local tools only.

## Tools

- GROBID: structure extraction for academic PDFs (title, authors, sections, references).
- PyMuPDF (fitz): page text blocks, image extraction, and page-level screenshots.
- pdfplumber or pdfminer.six: supplemental text extraction when GROBID output is incomplete.
- OCRmyPDF + Tesseract: only for scanned PDFs (image-only).

## Output Contract

Create a local working folder per paper containing:

- `extracted_text.txt` (cleaned, readable text)
- `figure_legends.txt` (grouped by Figure number)
- `Figure_1.jpg`, `Figure_2.jpg`, ...
- `Graphical abstract.jpg` (if present)
- `explication.json` (draft JSON aligned to figure order)

## Step 0: Detect scan vs. text PDF

- If most pages have no selectable text, run OCRmyPDF first.
- Otherwise, skip OCR.

## Step 1: Extract structure and metadata

- Run GROBID to extract title, journal/date, abstract, and section headings.
- If GROBID is not available, fallback to PyMuPDF text blocks.

## Step 2: Extract figure legends

- Parse text for "Figure X." blocks.
- Group contiguous legend lines until the next "Figure Y." marker.
- Remove obvious page headers/footers.
- Save as `figure_legends.txt`.

## Step 3: Extract figure images

- Use PyMuPDF to locate image blocks near each figure caption.
- If figures are vector or multi-panel, fallback to a page-level raster crop:
  - Crop the region above the caption on the same page.
  - Save as `Figure_X.jpg`.
- If a graphical abstract label is detected, extract it as `Graphical abstract.jpg`.

## Step 4: Build explication.json (draft)

- Use the title and journal/date from Step 1.
- For each figure legend, create an item entry:
  - `item_id`: `Figure_X`
  - `item_name`: `Figure_X.jpg`
  - `title_en`: legend heading
  - `type`: `results`
  - `content`: leave as a placeholder or fill with a first-pass interpretation.
- Keep figures in Results order.

## Step 5: Manual sanity checks

- Verify each `Figure_X.jpg` matches the correct legend.
- Fix any mismatched or missing figures before PPT generation.

## Notes

- Avoid external APIs.
- Prefer deterministic local parsing even if the first pass needs manual cleanup.
