---
name: ai-chapter-consolidate
description: Use AI to merge individual page HTML files into a unified chapter document. Creates continuous document format for improved reading experience and semantic consistency.
---

# AI Chapter Consolidate Skill

## Purpose

This skill uses AI to **intelligently merge individual page HTML files** into a single, continuous chapter document. Rather than simple concatenation, the AI:

- Removes duplicate headers/footers from continuation pages
- Ensures consistent heading hierarchy across pages
- Maintains semantic structure throughout
- Preserves all content without loss or repetition
- Creates smooth content flow (no page breaks)

The result is a **unified chapter document** in the continuous format (single `page-container`, single `page-content`).

## What to Do

1. **Collect all page HTML files for chapter**
   - Gather `04_page_XX.html` files for all pages in chapter
   - Verify all files exist and are valid
   - Sort by page number (ascending)

2. **Extract content from each page**
   - Load each HTML file
   - Extract main content from `<main class="page-content">`
   - Preserve semantic classes and structure

3. **Prepare consolidation inputs for AI**
   - Page 1: Full content including chapter header
   - Pages 2+: Extract content sections, remove chapter header/nav
   - Preserve all text and structure
   - Note any special sections (exhibits, tables, etc.)

4. **Invoke AI consolidation**
   - Send all page contents to Claude
   - Request merging into single continuous document
   - Specify structural requirements
   - Request heading hierarchy normalization

5. **Process AI output**
   - Extract consolidated HTML from response
   - Verify structure integrity
   - Ensure all pages represented
   - Check heading hierarchy

6. **Save consolidated document**
   - Save to: `output/chapter_XX/chapter_artifacts/chapter_XX.html`
   - Create metadata/log file
   - Calculate statistics

## Input Files

**Per-page HTML files** (validated by previous gate):
- `output/chapter_XX/page_artifacts/page_16/04_page_16.html` (Chapter opening)
- `output/chapter_XX/page_artifacts/page_17/04_page_17.html` (Continuation)
- `output/chapter_XX/page_artifacts/page_18/04_page_18.html` (Continuation)
- ... (all pages in chapter)

**Chapter metadata** (from analysis):
- Page range (first and last page of chapter)
- Chapter number
- Chapter title
- Expected page count

## AI Consolidation Prompt

The prompt sent to Claude:

```
You are merging individual page HTML documents into a single, continuous chapter.

INPUT PAGES:

Page 1 (Opening - include chapter header):
[HTML content from page 1]

Page 2 (Continuation):
[HTML content from page 2]

Page 3 (Continuation):
[HTML content from page 3]

... (all pages)

TASK:
Merge these pages into a single HTML document that reads as one continuous chapter.

REQUIREMENTS:

1. Structure:
   - Create single <div class="page-container"> wrapping everything
   - Create single <main class="page-content"> for all content
   - Remove page-break indicators or comments
   - Create truly continuous document (no paginated elements)

2. Chapter Header:
   - Keep chapter header from Page 1 (chapter number, title)
   - Remove chapter headers/titles from continuation pages
   - Keep section navigation if present on Page 1
   - Remove duplicate navigation from other pages

3. Content Preservation:
   - Include ALL text content from all pages
   - Preserve exact wording (no paraphrasing)
   - Maintain all lists, paragraphs, tables
   - Include all semantic classes
   - Keep all HTML structure

4. Heading Hierarchy:
   - Normalize heading levels across merged pages
   - Page 1 h1 = Chapter title (stays as h1)
   - First section in each page = h2 (main sections)
   - Sub-sections = h3 or h4 as needed
   - Ensure no hierarchy jumps (h1 → h3 without h2)
   - Number consecutive headings logically

5. Content Flow:
   - Remove page-specific headers/footers
   - Merge seamlessly so content flows naturally
   - No artificial breaks or transitions
   - Paragraphs continue logically
   - Lists maintain coherence

6. Exhibits and Images:
   - Preserve all tables and figures
   - Keep exhibit titles and captions
   - Include all images with proper paths
   - Maintain table of contents if present

7. CSS Classes:
   - Preserve all semantic classes (section-heading, paragraph, etc.)
   - Keep consistent class usage throughout
   - Ensure classes match chapter opening page style
   - Do not add or remove classes

8. Metadata:
   - Include title tag: "Chapter N: Title - Pages X-Y"
   - Keep meta charset and viewport
   - Link stylesheet: <link rel="stylesheet" href="../../styles/main.css">

OUTPUT:

Return ONLY a single, valid HTML5 document:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter [N]: [Title] - Pages [X-Y]</title>
    <link rel="stylesheet" href="../../styles/main.css">
</head>
<body>
    <div class="page-container">
        <main class="page-content">
            <!-- All content from all pages, merged seamlessly -->
        </main>
    </div>
</body>
</html>
```

VALIDATION:
- Single HTML5 document
- All pages represented
- No page breaks or transitions
- Proper heading hierarchy
- All text preserved
```

## Page Content Extraction Logic

Before sending to AI, extract content strategically:

### Page 1 (Opening):
- **Include**: Entire page HTML content
- **Reason**: Contains chapter header, navigation, first section
- **Preserve**: All elements (header, nav, dividers, content)

### Pages 2-N (Continuation):
- **Extract**: Only content after chapter header
- **Skip**: Chapter number, chapter title, section navigation
- **Preserve**: Section headings, paragraphs, lists, exhibits
- **Include**: All semantic content sections

### Example extraction:
```html
<!-- Page 1: Keep everything -->
<div class="chapter-header">
    <span class="chapter-number">2</span>
    <h1 class="chapter-title">Rights in Real Estate</h1>
</div>
<nav class="section-navigation">...</nav>
<h2 class="section-heading">REAL PROPERTY RIGHTS</h2>
<p class="paragraph">...</p>

<!-- Page 2: Skip header, keep content -->
<!-- <div class="chapter-header">...</div> SKIPPED -->
<!-- <nav class="section-navigation">...</nav> SKIPPED -->
<h4 class="subsection-heading">Physical characteristics.</h4>
<p class="paragraph">...</p>
<ul class="bullet-list">...</ul>

<!-- Page 3: Continue same pattern -->
<h4 class="subsection-heading">Interdependence.</h4>
<p class="paragraph">...</p>
```

## Output File

### Consolidated Chapter HTML
**Path**: `output/chapter_XX/chapter_artifacts/chapter_XX.html`

**Structure**:
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter 2: Rights in Real Estate - Pages 16-29</title>
    <link rel="stylesheet" href="../../styles/main.css">
</head>
<body>
    <div class="page-container">
        <main class="page-content">
            <!-- Chapter header (from page 1) -->
            <div class="chapter-header">...</div>
            <nav class="section-navigation">...</nav>
            <hr class="section-divider">

            <!-- Page 1 content -->
            <h2 class="section-heading">REAL PROPERTY RIGHTS</h2>
            <p class="paragraph">...</p>

            <!-- Page 2 content (seamlessly merged) -->
            <h4 class="subsection-heading">Physical characteristics.</h4>
            <p class="paragraph">...</p>
            <ul class="bullet-list">...</ul>

            <!-- Page 3 content (continuing flow) -->
            <h4 class="subsection-heading">Interdependence.</h4>
            <p class="paragraph">...</p>

            <!-- ... more content from remaining pages ... -->

            <!-- Final page content -->
            <h2 class="section-heading">REGULATIONS AND LICENSING</h2>
            <p class="paragraph">...</p>
        </main>
    </div>
</body>
</html>
```

### Consolidation Log
**Path**: `output/chapter_XX/chapter_artifacts/consolidation_log.json`

```json
{
  "chapter": 2,
  "title": "Rights in Real Estate",
  "book_pages": "16-29",
  "pdf_indices": "15-28",
  "consolidated_at": "2025-11-08T14:35:00Z",
  "pages_merged": 14,
  "pages_included": [
    {
      "page": 16,
      "book_page": 17,
      "status": "opening_chapter",
      "content_type": "header_navigation_content"
    },
    {
      "page": 17,
      "book_page": 18,
      "status": "continuation",
      "content_type": "subsections_paragraphs"
    },
    {
      "page": 18,
      "book_page": 19,
      "status": "continuation",
      "content_type": "subsections_paragraphs_list"
    }
    // ... all pages
  ],
  "content_statistics": {
    "total_headings": {
      "h1": 1,
      "h2": 4,
      "h3": 0,
      "h4": 12
    },
    "total_paragraphs": 156,
    "total_lists": 12,
    "total_list_items": 42,
    "total_tables": 3,
    "total_images": 5,
    "total_words": 12547
  },
  "ai_model": "claude-3-5-sonnet-20241022",
  "consolidation_notes": "Successfully merged 14 pages into continuous format"
}
```

## Implementation

Execute consolidation via Python wrapper:

```bash
cd Calypso/tools

# Run consolidation
python3 consolidate_chapter.py \
  --chapter 2 \
  --pages 15-28 \
  --output "../output" \
  --mapping "../analysis/page_mapping.json"

# Or invoke directly via Claude API:
# The orchestrator sends the AI prompt with all page contents
```

## Quality Checks

Before passing to next gate:

1. **File created**
   - [ ] `chapter_XX.html` exists
   - [ ] File is valid HTML (parseable)
   - [ ] File size reasonable (> 50KB typical)

2. **Structure validated**
   - [ ] Single `<div class="page-container">`
   - [ ] Single `<main class="page-content">`
   - [ ] All tags properly closed
   - [ ] No duplicate content

3. **Content completeness**
   - [ ] All pages represented
   - [ ] No missing sections
   - [ ] Paragraph/heading counts reasonable
   - [ ] All text content present

4. **Heading hierarchy**
   - [ ] Starts with h1 (chapter title)
   - [ ] h1 count = 1
   - [ ] h2 = major sections
   - [ ] h3/h4 = subsections
   - [ ] No hierarchy jumps

5. **Metadata logged**
   - [ ] Consolidation timestamp recorded
   - [ ] Pages merged count documented
   - [ ] Content statistics calculated
   - [ ] Log file saved

## Success Criteria

✓ All pages merged into single document
✓ Chapter header preserved from page 1
✓ Duplicate headers removed from continuation pages
✓ Content flows naturally (continuous format)
✓ Heading hierarchy is correct
✓ All text content preserved
✓ Semantic classes maintained
✓ Ready for semantic validation

## Error Handling

**If page HTML is incomplete**:
- Note in consolidation log
- Include whatever content is available
- Proceed to validation (validation will catch issues)

**If heading hierarchy is ambiguous**:
- AI makes best judgment
- Semantic validation gate will refine if needed
- Document decision in log

**If content appears duplicated**:
- AI deduplicates automatically
- Verify word count is reasonable
- Log any unusual content patterns

## Next Steps

Once consolidation completes:
1. **Quality Gate 2** (semantic-validate) checks semantic structure
2. **Skill 5** (quality-report-generate) generates final report
3. **Quality Gate 3** (visual-accuracy-check) validates appearance

## Design Notes

- This skill is **AI-powered** (uses probabilistic consolidation)
- Relies on AI's understanding of document structure
- Produces continuous format (no page breaks)
- Merges intelligently (not just concatenation)
- Output will be refined by validation gates

## Testing

To test consolidation on Chapter 2:

```bash
# Input: 14 individual page HTML files (pages 16-29)
# Process: AI merges into single continuous chapter
# Output: chapter_02.html (single, unified document)

# Verify:
# - File size is sum of all pages
# - Content flows logically
# - Heading hierarchy makes sense
# - No duplicate sections
```
