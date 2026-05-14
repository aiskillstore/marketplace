# Quality Gates

Use these gates before delivering a redesigned PDF.

## Gate 1: Source Evidence

The agent should collect source evidence before designing:

- Extract text when possible.
- Render each page to an image.
- Extract embedded QR codes, barcodes, seals, stamps, signatures, and logos when possible.
- Build a preservation list for IDs, dates, times, amounts, names, labels, table values, notes, and machine-readable assets.

Optional helper:

```bash
python scripts/pdf_guardrails.py input.pdf --out /tmp/prettify-pdf-check
```

## Gate 2: Exact Preservation

Locked values must match the source:

- Same spelling and capitalization.
- Same punctuation and separators.
- Same timestamp precision.
- Same amount display unless a secondary explanatory display is clearly added beside the exact value.
- Same label meaning.
- Same barcode/QR/seal/signature/logo source assets when extractable.

Do not infer relationships from layout. If the source places two lines under `Applicant Name`, keep both under `Applicant Name` unless the source explicitly labels one line as a parent, guardian, owner, or other role.

## Gate 3: Rendered Visual QA

Text extraction is not enough. Render the final PDF and inspect it.

Fail the output if any of these are visible:

- Names, IDs, amounts, dates, or timestamps clipped or overwritten.
- Icons overlapping values.
- A seal, watermark, or barcode sitting on top of critical text.
- A barcode or QR code recreated instead of preserved.
- Values squeezed into boxes too narrow to read confidently.
- Tables with amount columns colliding.
- Headers or notes that changed legal or operational meaning.

## Gate 4: Source-vs-Final Audit

Compare source and final renders side by side.

Ask the active vision-capable model, a separate reviewer, or the user to check:

- Names and labels.
- Receipt/invoice/application/reference IDs.
- Dates and times.
- Amounts, subtotals, totals, and amount-in-words.
- Transaction references and bank references.
- Line-item descriptions and fees.
- Required actions, warnings, and notes.
- Barcode/QR/seal/signature/logo visibility.

Do not deliver until the visual audit has no source-data mismatches and no layout collisions.

## Gate 5: Delivery Note

The final response should state:

- Output PDF path.
- Source or render artifacts, if useful.
- Critical fields checked.
- Any limitations, such as missing OCR, unreadable scan, or barcode decoding not performed.
