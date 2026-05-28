# OCR Troubleshooting

## Common Checks

- Confirm the input image path exists and is readable.
- Confirm `tesseract` is installed and callable from the configured path.
- Confirm the requested language pack is installed locally.
- Confirm the image format is supported by Pillow.

## Failure Recovery

- If OCR returns empty text, retry with the correct `lang` value.
- If Tesseract is not on `PATH`, set `tesseract_cmd` explicitly.
- If the image is low quality, warn that preprocessing may be required.
- If the config is incomplete, return the exact missing field before execution.
