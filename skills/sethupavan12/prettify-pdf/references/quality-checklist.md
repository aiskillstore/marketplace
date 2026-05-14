# Quality Checklist

Use this reference before delivering a redesigned PDF, especially when the source is a receipt, invoice, appointment confirmation, ticket, government form, legal form, medical document, or any document with machine-readable assets.

## Preservation

- Confirm names, dates, times, totals, company/office names, invoice numbers, application numbers, UID/reference values, addresses, transaction IDs, and contact details match the source.
- Confirm label-to-value meaning matches the source. Do not upgrade ambiguous adjacent text into a relationship or role that the source does not explicitly state.
- Confirm locked text preserves source capitalization, punctuation, separators, and spacing, including document titles, vehicle classes, amount displays, and timestamps.
- Confirm QR codes, barcodes, verification codes, official logos, seals, signatures, and stamps are preserved as original source images when available.
- Confirm friendly explanations do not replace original values. Example: keep `10.00AM-11.00AM`; add `1 hour appointment window` only as secondary text.
- For receipts and invoices, manually compare line items, fees, fines, totals, and amount-in-words.
- For appointment or test confirmations, verify the reader can quickly find date, time, location, applicant, reference number, required documents, and arrival/action instructions.
- For resumes, ensure roles, dates, employers, skills, degrees, and outcomes are not invented or upgraded.
- For proposals/reports, ensure scope, timeline, pricing, responsibilities, terms, and claims remain faithful.

## Information Hierarchy

- Put the most important facts in a priority card or top summary strip.
- Use direct labels: `Test date`, `Appointment window`, `Amount paid`, `Receipt no`, `Application no`, `Test address`, `Required action`.
- Highlight required actions and deadlines with restrained color.
- Do not bury the reason the document exists in paragraphs or dense tables.
- Avoid making the reader infer meaning from layout alone.

## Visual And Print QA

- Render final pages to images and inspect them.
- Compare the rendered source page and rendered final page side by side. Look for visual truth, not only extracted text.
- Check A4/Letter sizing as appropriate, margins, page breaks, line wrapping, and table widths.
- Check that no numbers, timestamps, names, icons, labels, seals, or barcode captions collide or sit too close to be read confidently.
- Check that headers do not orphan at the bottom of a page.
- Check all body text remains legible in grayscale.
- Use semantic colors: identity/header, success/paid/total, warning/action/deadline, neutral text.
- Pair icons with visible text labels.
- Avoid clipped text, overlaps, fake watermarks, illegible stamps, broken glyphs, and low-contrast values.

## Source Evidence

- Keep temporary evidence organized: extracted text, rendered page images, and extracted machine-readable images.
- If a helper script is available, generate a manifest and compare against it.
- If a field cannot be verified from extraction, inspect the rendered source page visually.
- If extraction says a value is present but the rendered page clips, overlaps, or visually mislabels it, fail the output and regenerate.
- If OCR is required, state that OCR may be imperfect and verify visually.

## Delivery

- Provide the final PDF path.
- Provide source HTML or intermediate source if useful.
- Summarize verification in one or two lines.
- Mention any limitation clearly: missing OCR, unreadable barcode, no page renderer, or source image not extractable.
