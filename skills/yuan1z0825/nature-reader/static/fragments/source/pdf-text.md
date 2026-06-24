# Source: selectable-text PDF

The PDF has an extractable text layer. Load the `pdf` skill first for extraction guidance.

- Extract the text layer directly; do not OCR text that is already selectable.
- Process the whole document, not just the first pages. Build the source map (step 2) across every page.
- Watch for multi-column layouts: recover natural reading order rather than top-to-bottom raw stream order.
- Keep ligatures, hyphenated line breaks, superscripts, subscripts, and math intact; rejoin words split across line breaks.
- Figures and tables are images embedded in the page — crop them per `references/figure-extraction.md`; do not paste the page text of a table where the table image belongs.
- If some pages have a text layer and others are scanned, treat the scanned pages with the `scanned-pdf` rules and mark them with a confidence note.
