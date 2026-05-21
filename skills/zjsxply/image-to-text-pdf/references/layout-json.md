# Layout JSON

Use one layout JSON per source image. Coordinates are top-left origin image pixels unless `units` says otherwise.

## Minimal Schema

```json
{
  "image_width": 1536,
  "image_height": 2048,
  "units": "px",
  "items": [
    {
      "text": "Main title",
      "bbox": [120, 96, 1416, 210],
      "font_size": 72,
      "align": "center"
    }
  ]
}
```

## Fields

- `image_width`, `image_height`: source image dimensions. If omitted, `compose_image_text_pdf.py` reads them from the image file.
- `units`: `px` is the default. `relative` means bbox values are fractions from 0 to 1.
- `items`: text spans to embed.
- `text`: exact copyable text.
- `bbox`: `[x0, y0, x1, y1]`.
- `x`, `y`, `width`, `height`: accepted alternative to `bbox`.
- `polygon`: accepted alternative; the script uses the polygon's bounding rectangle.
- `font_size`: optional. If omitted, the script estimates a size that fits the box.
- `align`: optional `left`, `center`, or `right`.

## Recommended Granularity

Use one item per visual line for most images. Paragraph-level items are acceptable only when the paragraph is not tightly typeset and the selection region does not need line precision.

## OCR Correction Pattern

Keep OCR output and corrected layout separate:

- OCR text is evidence for position.
- Source text is evidence for final wording.
- The layout JSON should contain corrected final text.

This separation avoids embedding OCR mistakes even when the image itself contains stylized or imperfect generated text.
