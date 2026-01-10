---
name: ascii-preview-generate
description: Use AI to create ASCII text-based preview of PDF page layout. Transforms visual and extracted data into structured ASCII representation for HTML generation.
---

# ASCII Preview Generate Skill

## Purpose

This skill uses **AI to create a meaningful ASCII text-based representation** of the PDF page layout. The AI:
- Analyzes both the PDF page image and extracted text data
- Creates a structured ASCII preview showing page organization
- Represents heading hierarchy, paragraphs, lists, and tables visually
- Provides clear structural context for downstream HTML generation

The ASCII preview serves as a **structured representation of page layout**, enabling the downstream AI-HTML generator to understand both visual layout and content structure.

## What to Do

1. **Load input files**
   - Read `02_page_XX.png` (visual reference)
   - Read `01_rich_extraction.json` (text spans with metadata)
   - Verify all required fields present

2. **Invoke AI to analyze and represent**
   - Send PNG image to Claude (visual reference)
   - Include extracted text data (JSON)
   - Request ASCII layout representation
   - AI determines structure and relationships

3. **AI generates ASCII preview**
   - AI analyzes heading hierarchy from extraction data
   - AI identifies paragraphs and their relationships
   - AI represents lists with proper formatting
   - AI shows table layouts if present
   - AI creates visual representation using ASCII characters

4. **Validate ASCII output**
   - Verify output is readable text
   - Check that all content elements represented
   - Confirm structure is clear and logical

5. **Save to persistent file**
   - Save to: `output/chapter_XX/page_artifacts/page_YY/03_page_XX_ascii.txt`
   - Include metadata (page number, chapter, timestamp)

## Input Parameters

```
rich_extraction_file: <str>  - Path to 01_rich_extraction.json
page_png: <str>               - Path to 02_page_XX.png (optional, for visual validation)
output_file: <str>            - Path to save ASCII preview
book_page: <int>              - Book page number (for display)
chapter: <int>                - Chapter number (for display)
```

## Output Format

### ASCII Preview Structure

The ASCII preview uses this structure:

```
================================================================================
                        PAGE XX ASCII LAYOUT PREVIEW
================================================================================
Book Page: YY | Chapter: Z | PDF Index: XX | Dimensions: 612x792px
--------------------------------------------------------------------------------

[PAGE CONTENT WITH ASCII ART AND ANNOTATIONS]

STRUCTURE SUMMARY:
[Element counts and types]

================================================================================
```

### Example Output

```
================================================================================
                        PAGE 16 ASCII LAYOUT PREVIEW
================================================================================
Book Page: 17 | Chapter: 2 | PDF Index: 16 | Dimensions: 612x792px
--------------------------------------------------------------------------------

┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  [H1 Heading - 27pt Bold]                                              │
│  ████████████████████████████████                                      │
│  █ Rights in Real Estate █                                             │
│  ████████████████████████████████                                      │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────     │
│  [Divider]                                                              │
│                                                                         │
│  [H2 Section Heading - 11pt Bold All-Caps]                             │
│  REAL PROPERTY RIGHTS                                                  │
│                                                                         │
│  [Paragraph 1 - 11pt Regular]                                          │
│  Real property consists of physical land and the legal rights          │
│  associated with ownership. These rights form what is commonly         │
│  referred to as the "bundle of rights."                                │
│                                                                         │
│  [H4 Subsection - 11pt Bold]                                           │
│  Physical characteristics.                                             │
│                                                                         │
│  [Paragraph 2 - 11pt Regular]                                          │
│  Land has unique physical characteristics that distinguish it from    │
│  other types of assets. The most important characteristics include:   │
│                                                                         │
│  [Bullet List - 3 items]                                               │
│    ▶ Immobility - Land cannot be moved from one location to           │
│      another. This fact has significant legal and economic            │
│      implications.                                                     │
│    ▶ Indestructibility - Land is permanent and cannot be              │
│      destroyed. Although structures on land can be destroyed,          │
│      the land itself endures.                                          │
│    ▶ Uniqueness - Each parcel of land is unique due to its            │
│      location. "Not two parcels of land are exactly alike due to       │
│      their geographic location."                                       │
│                                                                         │
│  [H4 Subsection - 11pt Bold]                                           │
│  Interdependence.                                                      │
│                                                                         │
│  [Paragraph 3 - 11pt Regular]                                          │
│  All land exists in relation to other land. Therefore, the value      │
│  of land is dependent on the land around it...                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

STRUCTURE SUMMARY:
─────────────────
Page Type: Chapter Continuation
Total Elements: 12

Headings (3):
  • H1: 1 instance (27pt, bold) - "Rights in Real Estate"
  • H2: 1 instance (11pt, bold, all-caps) - "REAL PROPERTY RIGHTS"
  • H4: 2 instances (11pt, bold) - "Physical characteristics", "Interdependence"

Paragraphs (3):
  • Body text: 3 paragraphs total
  • Average paragraph length: ~45 words
  • Text flow: Top to bottom, left to right

Lists (1):
  • Bullet list with 3 items
  • Indentation: 2em from left margin
  • Separator: "▶" character

Tables: 0

Images: 0

Font Summary:
  • 27pt: 1 instance (heading)
  • 11pt: 7 instances (body, subsections, lists)
  • Total unique fonts: 2 (Arial-Bold, Times-Regular)

Confidence Assessment:
  • Heading hierarchy: 100% confident
  • Element types: 95% confident
  • Content flow: 90% confident
  • (Lower confidence = ambiguous or unusual formatting)

================================================================================
```

## AI Prompt Template

The prompt sent to Claude to generate ASCII preview:

```
You are creating an ASCII text-based layout preview of a PDF page.

VISUAL REFERENCE (PDF Page):
[PNG Image Attached]

EXTRACTED TEXT DATA:
[JSON Attached]

TASK:
Generate an ASCII text representation of this page's layout and structure.

REQUIREMENTS:

1. ASCII Format:
   - Use box drawing characters for visual clarity (┌─┐│└┘)
   - Show page boundaries
   - Use spacing to represent actual layout

2. Element Representation:
   - Headings: Show in ASCII, mark with [H1], [H2], [H3], [H4]
   - Paragraphs: Show first line, indicate continuation
   - Lists: Use ▶ or • characters, maintain structure
   - Tables: Show column alignment and structure
   - Spacing: Represent actual gaps between elements

3. Annotations:
   - Label each element type [Heading], [Paragraph], [List], etc.
   - Show font size context (11pt, 27pt, etc.)
   - Note text styling (Bold, All-Caps, etc.)

4. Summary Statistics:
   - Count headings by level (h1, h2, h3, h4)
   - Count paragraphs
   - Count lists and items
   - Note any tables or images

5. Readability:
   - Keep lines under 80 characters
   - Use clear visual separation
   - Make structure obvious at a glance

OUTPUT:

```
================================================================================
                        PAGE XX ASCII LAYOUT PREVIEW
================================================================================
Book Page: YY | Chapter: Z | PDF Index: XX
--------------------------------------------------------------------------------

[ASCII representation with visual structure]

STRUCTURE SUMMARY:
[Element counts and types]
================================================================================
```

VALIDATION:
- ASCII must be readable text
- All major content elements must be represented
- Structure must be clear and logical
- Total elements count must match data
```

## AI Generation Process

1. **Load inputs**
   - `02_page_XX.png` - Visual reference
   - `01_rich_extraction.json` - Text spans with metadata

2. **Invoke Claude API**
   - Send image as multi-modal input
   - Include extracted data in prompt
   - Request ASCII layout preview

3. **Extract and validate output**
   - Parse ASCII from response
   - Verify readability
   - Check element representation

4. **Save to file**
   - Write to `output/chapter_XX/page_artifacts/page_YY/03_page_XX_ascii.txt`

## Quality Checks

Before declaring ASCII preview complete:

1. **File output**
   - [ ] Output file created and readable
   - [ ] File is valid text (UTF-8 encoding)
   - [ ] File size meaningful (> 500 bytes)

2. **Content representation**
   - [ ] All major page elements represented
   - [ ] Heading hierarchy shown clearly
   - [ ] Paragraphs indicated and readable
   - [ ] Lists properly formatted with bullets/markers
   - [ ] Tables (if present) shown with alignment

3. **Accuracy against source data**
   - [ ] Structure matches rich_extraction.json
   - [ ] Element counts reasonable
   - [ ] Text content accurate (no changes)
   - [ ] Layout represents visual (PNG) appearance

4. **Readability and format**
   - [ ] ASCII art is clear and clean
   - [ ] Line length reasonable (< 100 chars)
   - [ ] Box drawing characters render properly
   - [ ] Annotations are clear and helpful
   - [ ] Summary section present and accurate

## Output Metadata

```json
{
  "preview_file": "03_page_16_ascii.txt",
  "page": 16,
  "book_page": 17,
  "chapter": 2,
  "generated_at": "2025-11-08T14:31:00Z",
  "source_file": "01_rich_extraction.json",
  "elements_detected": {
    "headings": 4,
    "paragraphs": 3,
    "lists": 1,
    "tables": 0,
    "images": 0
  },
  "confidence_scores": {
    "overall": 0.93,
    "heading_hierarchy": 1.0,
    "element_types": 0.95,
    "content_flow": 0.90
  }
}
```

## Use in Downstream Processing

The ASCII preview is used by **Skill 3 (ai-html-generate)** as one of three inputs:

1. `02_page_XX.png` - Visual reference (pixel data)
2. `01_rich_extraction.json` - Parsed text with metadata
3. `03_page_XX_ascii.txt` - **Structural representation** ← This skill creates

Together, these three inputs give the AI complete context for accurate HTML generation.

## Error Handling

**If PNG image fails to load:**
- Fall back to text-only analysis using rich_extraction.json
- AI still generates ASCII but without visual reference
- Note in metadata: "Image unavailable"
- Proceed (text data is sufficient for structure)

**If rich_extraction.json is invalid:**
- Use PNG image and AI visual analysis
- Attempt ASCII generation from visual alone
- Log warning about missing text data
- Proceed with AI best judgment

**If AI response is not valid text:**
- Validate encoding and line breaks
- Retry request if necessary
- Escalate if repeated failures

**If ASCII structure seems incomplete:**
- AI may have missed elements due to image quality
- Downstream HTML generation has visual reference for verification
- Quality gates will catch if output is insufficient

## Success Criteria

✓ ASCII preview file created successfully
✓ File contains all page elements in structured format
✓ Heading hierarchy is clear and logical
✓ All text content included and readable
✓ Summary statistics accurate
✓ File is well-formatted and unambiguous
✓ Ready for AI HTML generation with complete context

## Next Steps

Once ASCII preview is complete:
1. **Skill 3** (ai-html-generate) uses this + PNG + extraction for HTML
2. AI has maximum context: visual (PNG) + text (extraction) + structure (ASCII)
3. Result is accurate, semantically correct HTML

## Troubleshooting

**ASCII preview is incomplete**: Check source rich_extraction.json has all text spans
**Heading hierarchy looks wrong**: Verify font sizes in extraction data
**Lists not detected**: Check for bullet character encoding issues
**Spacing is off**: Ensure coordinate system matches PDF (top-left origin)

## Design Notes

- This skill is **AI-powered** (probabilistic generation)
- Output is **human-readable** (for debugging and validation)
- Output is **machine-parseable** (for downstream processing)
- Input is **multi-modal** (visual image + structured text data)
- AI understands context to create meaningful layout preview
- Critical bridge between visual and textual representations
- Enables downstream HTML generation with complete context
