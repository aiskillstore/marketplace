# OCR and Source-Text Alignment

Use this guide when converting a generated image plus known source text into a reliable text-layer layout.

## Recommended Process

1. Run OCR or a vision model on the final image.
2. Ask for line-level or word-level boxes in image pixel coordinates.
3. Compare OCR text against the source text supplied by the user.
4. Correct the `text` values while preserving the OCR-derived boxes.
5. Compose the final and debug PDFs.
6. Inspect the debug PDF and iterate on boxes or text.

## Vision/OCR Prompt Pattern

Ask for machine-readable output:

```text
Return JSON only. Extract all visible text from this image.
Use image pixel coordinates with top-left origin.
Return:
{
  "image_width": <number>,
  "image_height": <number>,
  "items": [
    {"text": "...", "bbox": [x0, y0, x1, y1]}
  ]
}
Prefer one item per visual text line. Do not summarize or translate text.
```

If the image was generated from known source text, add:

```text
The source text below is authoritative. Use it to correct OCR typos, but keep the boxes aligned to the image.
```

## Alignment Heuristics

- Keep headings, labels, and bullets as separate layout items.
- Merge words into a line when their vertical centers are close and their horizontal gap is normal for the line.
- Preserve user-facing punctuation from the source text, even if OCR drops it.
- For CJK text, remove OCR-inserted spaces between adjacent CJK characters.
- If generated image text differs materially from source text, embed the intended source text only if the user wants copy/paste fidelity over visual fidelity. Otherwise ask which text should be authoritative.
- If OCR misses a region, add a manual `bbox` item after visual inspection.

## Common Failure Modes

- Tiny decorative text is often not worth embedding unless the user explicitly needs it.
- Rotated or curved text may require several smaller boxes.
- Text generated as distorted artwork may not visually match the embedded text. Use the debug PDF to make this tradeoff explicit.
- Reusing slide, HTML, or LaTeX layout after image generation often changes spacing. Keep the generated image as the visual layer and add only the PDF text layer.
