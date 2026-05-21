---
name: image-to-text-pdf
description: Convert a finished raster image, especially a generated poster or visual resume, into an image-based PDF with an additional selectable, copyable, searchable text layer. Use when the image is the final visual layout, when recreating that layout in PPT, HTML, or LaTeX would be fragile, and when the user needs both a final invisible-text PDF and a visible inspection PDF for checking OCR or text-layer placement.
---

# Image to Text PDF

Turn a finished raster image into a PDF while preserving the image exactly and adding a transparent text layer for selection, copying, and search.

## Workflow

1. Get the complete image.
- Treat the image as the visual source of truth.
- Keep the original image dimensions; the layout coordinates should use the same pixel coordinate space whenever possible.

2. Build a text-layer layout JSON.
- Prefer OCR or a vision model that returns text boxes over trying to infer positions manually.
- Use the user's source text to correct OCR transcription. OCR boxes determine position; the source text determines final copyable content.
- Read `references/ocr-alignment.md` when you need guidance for extracting, correcting, or prompting for box-level text.
- Read `references/layout-json.md` for the exact JSON schema.

3. Generate both PDFs.

```bash
python scripts/compose_image_text_pdf.py \
  --image /path/to/image.png \
  --layout /path/to/layout.json \
  --output /path/to/image-text.pdf \
  --debug-output /path/to/image-text-check.pdf
```

For CJK or other non-Latin text, pass a Unicode font:

```bash
python scripts/compose_image_text_pdf.py \
  --image /path/to/image.png \
  --layout /path/to/layout.json \
  --output /path/to/image-text.pdf \
  --debug-output /path/to/image-text-check.pdf \
  --font-file /path/to/NotoSansCJK-Regular.ttc
```

4. Inspect the debug PDF before delivering.
- The final PDF should look like the image-only source.
- The debug PDF should show highlighted text boxes and visible text where the hidden layer will be placed.
- If a highlighted box is shifted, fix the layout JSON, not the image.
- If copy/paste text is wrong, fix the `text` field in layout JSON, not the OCR image.

## OCR Word Conversion

When an OCR tool returns word-level boxes, convert them to line-level layout items:

```bash
python scripts/ocr_words_to_layout.py \
  --ocr /path/to/ocr.json \
  --output /path/to/layout.json \
  --image-width 1536 \
  --image-height 2048 \
  --source-text /path/to/source.txt
```

The converter accepts common JSON shapes containing `words`, `items`, `textAnnotations`, or nested page/line/word objects. It groups nearby words into lines and can replace OCR text with the closest line from the source text when the match is strong.

## Practical Rules

- Keep text boxes line-level unless a paragraph must be selected as one unit. Line-level boxes are easier to position and debug.
- Do not try to match the rasterized font exactly. The hidden layer only needs close geometry and correct text.
- Use the visible inspection PDF as the validation artifact. It should make every embedded text span obvious.
- For generated images, ask the image-generation step to keep text in large, separated blocks. Dense tiny text is harder for OCR and manual correction.
- Preserve the image as the background instead of rebuilding the layout in presentation or web formats.
