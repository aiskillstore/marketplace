---
name: pdf-page-extract
description: Extract rich data from PDF pages including text spans with metadata, rendered PNG images, and page mapping. Creates persistent artifacts for downstream processing.
---

# PDF Page Extract Skill

## Purpose

This skill extracts all necessary data from PDF pages to enable accurate AI-driven HTML generation. It produces three critical artifacts:
1. **Rich extraction data** - Text spans with font metadata (sizes, styles, positions)
2. **Rendered PNG image** - Visual reference for AI to understand page layout
3. **Page mapping** - Authoritative mapping of PDF indices to book pages

This is the **deterministic, Python-based foundation** for the entire pipeline. All extracted data is saved to persistent files for traceability and future processing.

## What to Do

1. **Validate input parameters**
   - Check PDF file exists and is readable
   - Verify page range (PDF indices or book pages)
   - Confirm output directory structure

2. **Establish page mapping** (if not already done)
   - Run: `python3 Calypso/tools/read_page_footers.py`
   - Scans page footers to establish PDF index → book page mapping
   - Saves to: `analysis/page_mapping.json`

3. **Extract rich page data** using PyMuPDF and pdfplumber
   - Run: `python3 Calypso/tools/rich_extractor.py`
   - Extracts text spans with font metadata:
     - Font name and size
     - Bold/italic flags
     - Position (bounding box)
     - Color information
   - Analyzes page structure to identify:
     - Likely headings (by size and style)
     - Paragraphs (regular text)
     - Potential lists
   - Detects tables using pdfplumber
   - Saves to: `analysis/chapter_XX/rich_extraction.json`

4. **Render PDF page to PNG**
   - Convert page to high-resolution PNG image (300+ DPI)
   - Maintains visual fidelity for AI reference
   - Saves to: `output/chapter_XX/page_artifacts/page_YY/02_page_XX.png`

5. **Extract embedded images** (if present)
   - Run: `python3 Calypso/tools/extract_images.py`
   - Extracts all images from page
   - Saves: `output/chapter_XX/images/page_YY_image_*.png`
   - Creates metadata: `page_YY_images.json`

6. **Validate extraction completeness**
   - Verify all files saved correctly
   - Check JSON files are valid
   - Confirm PNG image is readable
   - Validate page mapping consistency

## Input Parameters

```
chapter: <int>           - Chapter number (1-8)
start_page: <int>        - Starting PDF index (0-based) or page range
end_page: <int>          - Ending PDF index (optional if single page)
pdf_path: <str>          - Path to PDF file (default: Calypso/PREP-AL 4th Ed 9-26-25.pdf)
output_base: <str>       - Output directory (default: Calypso/output)
mapping_file: <str>      - Page mapping file (default: Calypso/analysis/page_mapping.json)
```

## Output Structure

### Artifact Files Saved

**Per-page artifacts** (in `output/chapter_XX/page_artifacts/page_YY/`):
- `01_rich_extraction.json` - Text spans with metadata
- `02_page_XX.png` - Rendered PDF page image
- `page_mapping.json` - Shared mapping file (symlink or copy)

**Extraction data** (in `analysis/chapter_XX/`):
- `rich_extraction.json` - Full extraction for all pages in chapter
- `page_6_pattern_analysis.json` - (Optional) Pattern analysis for specific pages

**Images** (in `output/chapter_XX/images/chapter_XX/`):
- `page_XX_image_*.png` - Embedded images from page
- `page_XX_images.json` - Metadata for embedded images

### Rich Extraction JSON Format

```json
{
  "page_number": 16,
  "pdf_index": 15,
  "book_page": 17,
  "chapter": 2,
  "dimensions": {
    "width": 612,
    "height": 792
  },
  "text_spans": [
    {
      "text": "Rights in Real Estate",
      "font": "Arial-BoldMT",
      "size": 27.04,
      "bold": true,
      "italic": false,
      "bbox": {
        "x0": 72,
        "y0": 150,
        "x1": 400,
        "y1": 177
      },
      "color": 0,
      "sequence": 1
    }
  ],
  "analysis": {
    "font_sizes": {
      "27.04": 1,
      "11.04": 45
    },
    "font_styles": {
      "bold_27.04": 1,
      "regular_11.04": 45
    },
    "likely_headings": [
      {
        "text": "Rights in Real Estate",
        "level": 1,
        "confidence": 0.95
      }
    ],
    "likely_paragraphs": [
      {
        "text": "Real property consists of...",
        "type": "body_text"
      }
    ]
  },
  "extraction_timestamp": "2025-11-08T14:30:00Z",
  "extraction_tool": "rich_extractor.py v1.0"
}
```

## Python Commands to Execute

### Step 1: Establish Page Mapping

```bash
cd Calypso/tools
python3 read_page_footers.py \
  --start 15 \
  --end 28 \
  --pdf "../PREP-AL 4th Ed 9-26-25.pdf" \
  --output "../analysis/page_mapping.json"
```

**Success indicators:**
- Command exits with code 0
- Page mapping JSON created/updated
- All pages in range have entries

### Step 2: Extract Rich Data

```bash
cd Calypso/tools
python3 rich_extractor.py \
  --pdf "../PREP-AL 4th Ed 9-26-25.pdf" \
  --start 15 \
  --end 28 \
  --output "../analysis/chapter_02/rich_extraction.json"
```

**Success indicators:**
- Command exits with code 0
- JSON file created
- File contains text_spans array
- All pages in range represented

### Step 3: Render to PNG

```bash
cd Calypso/tools
python3 -c "
import fitz
pdf = fitz.open('../PREP-AL 4th Ed 9-26-25.pdf')
for page_idx in range(15, 29):
    page = pdf[page_idx]
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))  # 300% zoom for high-res
    pix.save(f'../output/chapter_02/page_artifacts/page_{page_idx:02d}/02_page_{page_idx}.png')
pdf.close()
"
```

### Step 4: Extract Images (if present)

```bash
cd Calypso/tools
# For each page with images
python3 extract_images.py \
  --page 17 \
  --pdf "../PREP-AL 4th Ed 9-26-25.pdf" \
  --output "../output" \
  --mapping "../analysis/page_mapping.json"
```

## Quality Checks

Before declaring extraction complete:

1. **File existence**
   - [ ] `01_rich_extraction.json` exists
   - [ ] `02_page_XX.png` exists and is valid
   - [ ] `page_mapping.json` exists

2. **JSON validity**
   - [ ] JSON files parse without errors
   - [ ] All required fields present
   - [ ] No null/undefined values in critical fields

3. **Data completeness**
   - [ ] All pages in range have text_spans
   - [ ] Text content is not empty
   - [ ] Font sizes are reasonable (> 0)
   - [ ] Bounding boxes are within page dimensions

4. **Image quality**
   - [ ] PNG files are readable
   - [ ] Image dimensions match PDF page size
   - [ ] No corrupted or blank images

## Error Handling

**If PDF file not found:**
- Exit with error message
- Do not create partial artifacts

**If page mapping fails:**
- Fall back to default indexing (PDF index = book page - 1)
- Log warning
- Continue extraction

**If rich extraction produces no text:**
- Check if page is image-only
- Mark in metadata: `"page_type": "image_only"`
- Continue (ASCII preview will handle image OCR)

**If PNG rendering fails:**
- Use fallback: save raw PDF page as PDF image
- Log warning
- Continue to next step

## Persistence & Traceability

All artifacts include metadata:
- Extraction timestamp
- Tool version
- Input parameters
- Processing status

This enables:
- Reproducibility (re-extract with same parameters)
- Debugging (trace what data was extracted)
- Auditing (track all changes to artifacts)
- Caching (skip re-extraction if unchanged)

## Success Criteria

✓ All required files created in correct directories
✓ Rich extraction JSON is valid and complete
✓ PNG image renders correctly
✓ Page mapping is accurate
✓ All data persisted and ready for next skill
✓ No extraction errors or warnings

## Next Steps

Once extraction completes successfully:
1. **Skill 2** will create ASCII preview from extracted data
2. **Skill 3** will use extraction + PNG + ASCII for HTML generation
3. All artifacts available for validation and debugging

## Troubleshooting

**PDF won't open**: Verify file path, ensure PDF is not corrupted
**No text extracted**: Page may be image-only (OCR needed)
**Wrong page numbers**: Check page_mapping.json for accuracy
**PNG images are blank**: Try increasing zoom factor (3x = 300 DPI)

## Implementation Notes

- This skill is **fully deterministic** - same inputs always produce same outputs
- Python tools ensure data quality and consistency
- All files saved to persistent storage for audit trail
- No AI involved at this stage - pure data extraction
- Ready to support later AI-based HTML generation with complete context
