---
name: ai-html-generate
description: Use AI to recreate PDF page as semantic HTML. Consumes three inputs (PNG image, parsed text, ASCII preview) for complete contextual understanding and accurate generation.
---

# AI HTML Generate Skill

## Purpose

This skill leverages **AI's probabilistic generation capabilities** to recreate PDF pages as semantic HTML. The AI receives three complementary inputs that together provide complete context:

1. **Visual reference** (PNG image) - Page layout and visual hierarchy
2. **Text data** (rich_extraction.json) - Accurate text content and formatting metadata
3. **Structural preview** (ASCII text) - Logical layout and element relationships

This **three-input approach** ensures the AI understands not just what text to include, but how it should be structured semantically in HTML.

The output is **probabilistic** (AI-generated), but will be made **deterministic** by validation gates in subsequent skills.

## What to Do

1. **Prepare three input files**
   - Load `02_page_XX.png` (image file)
   - Load `01_rich_extraction.json` (text spans with metadata)
   - Load `03_page_XX_ascii.txt` (structure preview)

2. **Construct AI prompt**
   - Attach PNG image as visual reference
   - Include extracted text data (JSON)
   - Include ASCII preview (text representation)
   - Provide specific generation requirements

3. **Invoke Claude API** with complete context
   - Send multi-modal prompt (text + image)
   - Request semantic HTML5 output
   - Specify CSS classes and structure requirements

4. **Parse and save generated HTML**
   - Extract HTML from AI response
   - Validate basic well-formedness
   - Save to persistent file with metadata

5. **Log generation metadata**
   - Record AI model used
   - Timestamp generation
   - List input files used
   - Store any confidence indicators from AI

## Input Files (From Previous Skills)

### Input 1: Rendered PDF Page (PNG)
**File**: `output/chapter_XX/page_artifacts/page_YY/02_page_XX.png`
- High-resolution rendering of PDF page
- 300+ DPI for visual clarity
- Shows actual page appearance
- Used for visual layout understanding

### Input 2: Rich Extraction Data (JSON)
**File**: `output/chapter_XX/page_artifacts/page_YY/01_rich_extraction.json`
- Text spans with complete metadata
- Font names, sizes, bold/italic flags
- Position information (bounding boxes)
- Sequence and relationships

### Input 3: ASCII Preview (Text)
**File**: `output/chapter_XX/page_artifacts/page_YY/03_page_XX_ascii.txt`
- Text-based structural representation
- Heading hierarchy marked
- Lists and bullets identified
- Paragraph flow documented
- Element types annotated

## AI Prompt Template

The prompt sent to Claude:

```
You are recreating a PDF textbook page as semantic HTML5.

You have three pieces of information about this page:
1. A visual rendering (PNG image) - to understand layout
2. Parsed text data (JSON) - to ensure accuracy
3. An ASCII structure preview (text) - to understand element relationships

VISUAL REFERENCE:
[PNG Image Attached]

PARSED TEXT DATA:
[JSON Attached]

STRUCTURAL PREVIEW:
[ASCII Text Attached]

TASK:
Generate semantic HTML5 that accurately recreates this page.

REQUIREMENTS:

1. HTML5 Structure:
   - Proper DOCTYPE, html, head, body tags
   - Meta charset="UTF-8"
   - Meta viewport for responsive design
   - Title tag with descriptive text

2. Content Wrapper:
   - Single <div class="page-container"> wrapper
   - Single <main class="page-content"> for all content
   - No page breaks or paginated structure

3. Semantic HTML Elements:
   - Use proper heading tags (h1-h6) based on hierarchy
   - Use <p> for paragraphs
   - Use <ul> and <li> for bullet lists
   - Use <table> if data tables present
   - Use <figure> and <figcaption> for images/exhibits

4. Semantic CSS Classes:
   Apply these classes based on detected element types:

   Page Structure:
   - page-container (main wrapper)
   - page-content (content area)
   - chapter-header (chapter opening section)
   - chapter-number (numeric chapter marker)
   - chapter-title (chapter main title)

   Content Elements:
   - section-heading (major section, h2)
   - subsection-heading (minor section, h3-h4)
   - paragraph (body text, p)
   - bullet-list (ul)
   - bullet-item (li)

   Navigation & Structure:
   - section-navigation (list of topics/sections)
   - nav-item (individual nav item)
   - section-divider (hr divider line)

   Special Elements:
   - exhibit (table or figure)
   - exhibit-table (actual table)
   - exhibit-title (figure/table caption)
   - image-placeholder (for embedded images)

5. Content Preservation & Boundary Integrity:
   - Include ALL text content from the parsed data
   - Preserve exact text (no paraphrasing or edits)
   - Maintain original structure and relationships
   - Do not omit or skip sections

   CRITICAL - PAGE BOUNDARY RULES:
   - Start page content EXACTLY where JSON starts it
   - End page content EXACTLY where JSON ends it
   - NEVER add bridging text, connectors, or completing phrases
   - NEVER invent transitional words or sentences
   - NEVER synthesize content to "smooth" page transitions
   - Pages may start or end mid-sentence - this is EXPECTED and CORRECT
   - If a sentence seems incomplete, that is the accurate page boundary
   - Every single word in your HTML MUST exist in the source JSON

6. Heading Hierarchy:
   - Follow logical hierarchy (h1 → h2 → h3 → h4)
   - No skipped levels (don't jump from h1 to h4)
   - Chapter title is h1 (if present)
   - Main sections are h2
   - Subsections are h3 or h4 as appropriate

7. List Formatting:
   - Wrap in <ul class="bullet-list">
   - Each item in <li class="bullet-item">
   - Preserve item order and grouping
   - Include all bullet text exactly

8. CSS Stylesheet Link:
   - Include: <link rel="stylesheet" href="../../styles/main.css">
   - Use relative path (two levels up to root)
   - This stylesheet provides all styling

9. Special Handling:
   - Bold text within paragraphs: Use <strong> tags
   - Italic text: Use <em> tags
   - Embedded images: Use <img> tags with src path and alt text
   - Exhibits/tables: Preserve structure and captions

OUTPUT FORMAT:

Return ONLY valid HTML5. Do not include explanations.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    ...
</head>
<body>
    ...
</body>
</html>
```

VALIDATION:
- HTML must be valid HTML5
- All opening tags must have closing tags
- Class attributes must use correct class names
- All text content from JSON MUST be included
- NO TEXT MAY BE ADDED that doesn't exist in the source JSON extraction
- Coverage must be 99-100% (>100% indicates invented content = FAIL)
- Every single word must come from the extraction data
```

## Process Flow

```
┌─ Load Input Files ─────────────────────┐
│ • 02_page_XX.png (image)               │
│ • 01_rich_extraction.json (text data)  │
│ • 03_page_XX_ascii.txt (structure)     │
└────────┬────────────────────────────────┘
         │
         ▼
┌─ Construct Prompt ─────────────────────┐
│ • Attach PNG image                     │
│ • Include JSON data                    │
│ • Include ASCII preview                │
│ • Add generation requirements          │
└────────┬────────────────────────────────┘
         │
         ▼
┌─ Invoke Claude API ────────────────────┐
│ • Multi-modal prompt                   │
│ • Vision + Text understanding          │
│ • Deterministic system instructions    │
└────────┬────────────────────────────────┘
         │
         ▼
┌─ Extract & Save HTML ──────────────────┐
│ • Parse AI response                    │
│ • Extract HTML block                   │
│ • Basic validation (tag closure)       │
│ • Save to 04_page_XX.html              │
└────────┬────────────────────────────────┘
         │
         ▼
┌─ Log Generation Metadata ──────────────┐
│ • Model name and version               │
│ • Input file references                │
│ • Timestamp                            │
│ • Save to 05_generation_metadata.json  │
└────────┬────────────────────────────────┘
         │
         ▼
┌─ GATE 1: Verify Text Content ──────────┐
│ MANDATORY - DO NOT SKIP                │
│                                        │
│ Run per-page text verification:        │
│ python3 Calypso/tools/                 │
│   verify_text_content.py 1 <page>      │
│                                        │
│ Check coverage percentage:             │
│ • 99-100% = PASS, proceed to next page │
│ • 95-98% = WARNING, review content    │
│ • >100% = FAIL, REGENERATE (hallucin) │
│ • <85% = FAIL, REGENERATE PAGE        │
│                                        │
│ CRITICAL: Never consolidate pages     │
│ until all individual pages pass ✓      │
└────────┬─────────────────────────────┘
         │
         ▼
   ✓ Complete - Ready for Validation
```

## GATE 1: MANDATORY Per-Page Text Verification

**This is the fail-safe that prevents incorrect content from reaching consolidation.**

After generating each page's HTML with the AI prompt above:

1. **Immediately run verification:**
   ```bash
   python3 Calypso/tools/verify_text_content.py <chapter_num> <page_num>
   ```

2. **Interpret results:**
   - **99-100% coverage**: PASS ✅ - Text matches extraction JSON precisely, proceed to next page
   - **95-98% coverage**: WARNING ⚠️ - Minor text differences, review content manually to ensure no loss
   - **85-95% coverage**: WARNING ⚠️ - Some text missing/modified, review content manually
   - **>100% coverage**: FAIL ❌ - Extra content added not in original page (AI hallucination), REGENERATE IMMEDIATELY
   - **<85% coverage**: FAIL ❌ - Critical content missing, REGENERATE

3. **If verification FAILS (<85% coverage):**
   - Stop immediately
   - DO NOT proceed to next page
   - DO NOT consolidate chapter
   - Review the HTML - check if it contains:
     - Content from a DIFFERENT page (wrong page generated)
     - Missing sections or major text blocks
     - Corrupted or duplicate content
   - Regenerate the page with the AI prompt again
   - Re-run verification
   - Only proceed when coverage ≥95%

4. **Example of FAIL scenarios:**

   **Extra content (>100% - AI HALLUCINATION)**:
   ```
   Page 16 HTML contains 301 words
   Page 16 JSON should have 297 words
   Coverage: 101.2% = FAIL ❌ (>100%)
   → Extra 4 words = AI invented bridging text
   → Example: AI added "All land also includes" that doesn't exist in source
   → Regenerate page 16 immediately with strict boundary constraints
   ```

   **Missing content (<85%)**:
   ```
   Page X HTML contains 180 words
   Page X JSON should have 250 words
   Coverage: 72% = FAIL ❌ (<85%)
   → Missing 70 words from page X
   → Regenerate page X immediately
   ```

5. **CONSOLIDATION BLOCK:**
   - Do not run Skill 4 (consolidate) until all pages pass Gate 1
   - Consolidating pages with wrong content cascades the error to the entire chapter
   - Each page must verify individually first

## Output Files

### Generated HTML File
**Path**: `output/chapter_XX/page_artifacts/page_YY/04_page_XX.html`

**Content**: Complete HTML5 document with:
- DOCTYPE and proper tags
- Meta tags (charset, viewport)
- Title tag
- CSS stylesheet link
- Semantic structure with classes
- All extracted text content
- Proper heading hierarchy
- Lists and paragraphs formatted

**Example structure**:
```html
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
            <!-- Opening chapter only -->
            <div class="chapter-header">
                <span class="chapter-number">2</span>
                <h1 class="chapter-title">Rights in Real Estate</h1>
            </div>

            <!-- Navigation (opening pages only) -->
            <nav class="section-navigation">
                <div class="nav-item">Real Property Rights</div>
                <div class="nav-item">...</div>
            </nav>

            <hr class="section-divider">

            <!-- Main content -->
            <h2 class="section-heading">REAL PROPERTY RIGHTS</h2>

            <p class="paragraph">Real property consists of...</p>

            <h4 class="subsection-heading">Physical characteristics.</h4>

            <p class="paragraph">Land has unique physical characteristics...</p>

            <ul class="bullet-list">
                <li class="bullet-item">Immobility - Land cannot be moved...</li>
                <li class="bullet-item">Indestructibility - Land is permanent...</li>
                <li class="bullet-item">Uniqueness - Each parcel is unique...</li>
            </ul>

            <!-- More content... -->
        </main>
    </div>
</body>
</html>
```

### Generation Metadata
**Path**: `output/chapter_XX/page_artifacts/page_YY/05_generation_metadata.json`

```json
{
  "page": 16,
  "book_page": 17,
  "chapter": 2,
  "generated_at": "2025-11-08T14:33:00Z",
  "ai_model": "claude-3-5-sonnet-20241022",
  "inputs_used": [
    "02_page_16.png",
    "01_rich_extraction.json",
    "03_page_16_ascii.txt"
  ],
  "html_file": "04_page_16.html",
  "content_metrics": {
    "headings_count": 4,
    "paragraphs_count": 3,
    "lists_count": 1,
    "list_items_count": 3,
    "images_count": 0
  },
  "generation_notes": "Successfully generated with all three input sources",
  "estimated_accuracy": "90%"
}
```

## Implementation Notes

### Handling Different Page Types

**Chapter Opening Pages** (first page of chapter):
- Include chapter number (h1 or span.chapter-number)
- Include chapter title (h1.chapter-title)
- Include navigation list (nav.section-navigation)
- Include section divider (hr.section-divider)

**Continuation Pages** (middle of chapter):
- No chapter header
- Start with main content (h2.section-heading or similar)
- Maintain heading hierarchy across page boundaries

**Final Pages** (end of chapter):
- Continue content seamlessly
- Include any summary sections (if present)
- End naturally without special footer

**Pages with Images/Exhibits**:
- Include <figure> tags for exhibits
- Include <figcaption> tags for titles
- Use <table> for tabular data
- Embed image file references correctly

### AI Generation Best Practices

1. **Be specific about requirements** - AI responds better to detailed instructions
2. **Provide all three inputs** - Together they remove ambiguity
3. **Include examples** - Show AI what good output looks like
4. **Use structured prompts** - Numbered lists are clearer than prose
5. **Request validation** - Ask AI to validate its own output

## Quality Checks (Before Validation Gate)

Before passing to validation:

1. **File created**
   - [ ] HTML file exists and is readable
   - [ ] File size > 5KB (substantial content)

2. **Basic structure**
   - [ ] Contains `<!DOCTYPE html>`
   - [ ] Has `<html>` tags
   - [ ] Has `<head>` and `<body>`
   - [ ] Has `<main class="page-content">`

3. **Metadata**
   - [ ] Generation timestamp recorded
   - [ ] Input files listed
   - [ ] Model name recorded
   - [ ] All content metrics captured

## Success Criteria

✓ HTML file generated successfully
✓ All three inputs consumed (PNG, JSON, ASCII)
✓ HTML structure is valid (basic checks pass)
✓ All text content included (no omissions)
✓ Semantic classes applied correctly
✓ Heading hierarchy is logical
✓ Ready for deterministic validation gate

## Error Handling

**If AI refuses to generate**:
- Log error message from AI
- Check input files for corruption
- Retry with simplified prompt if needed

**If HTML is malformed**:
- Try to extract what's usable
- Log specific issues
- May fail validation gate (expected)

**If image fails to attach**:
- Fall back to text-only generation
- Note in metadata
- Proceed (visual context lost but text may be sufficient)

**If JSON data is incomplete**:
- Use text from ASCII preview as fallback
- Note in metadata
- Proceed with caution

## Next Steps

Once HTML is generated:
1. **Quality Gate 1** (html-structure-validate) checks basic structure
2. **Skill 4** (consolidate pages) for full chapter
3. **Quality Gate 2** (semantic-validate) checks classes and hierarchy
4. **Final validation** ensures quality standards met

## Key Principle

> **AI generates probabilistically. Python validates deterministically. Together they produce reliable, high-quality output.**

This skill provides the **probabilistic generation**, leveraging AI's understanding of context and structure. The validation gates that follow ensure the output meets quality standards.

## Testing the Skill

To test HTML generation on Chapter 1:

```bash
# Generate HTML for page 6 (Chapter 1 opening)
# Inputs: 02_page_6.png, 01_rich_extraction.json, 03_page_6_ascii.txt
# Output: 04_page_6.html
```

Expected result: Valid semantic HTML that accurately represents page 6 content.
