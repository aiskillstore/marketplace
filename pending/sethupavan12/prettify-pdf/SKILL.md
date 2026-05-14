---
name: prettify-pdf
description: Redesign or QA PDFs for clarity while preserving IDs, dates, amounts, barcodes, QR codes, seals, signatures, labels, and meaning. Use for receipts, invoices, forms, tickets, resumes, reports.
license: MIT
metadata:
  openclaw:
    homepage: https://github.com/sethupavan12/prettify-pdf
---

# Prettify PDF

## Core Idea

Redesign the PDF around what the reader needs to notice first, while treating the source PDF as evidence. The work is not "make it pretty"; it is "make it easier to use without changing what it means."

This skill has no hosted service, API key, or model-provider requirement. Use whatever local PDF, image, HTML, or document tools are available in the current environment.

## Compatibility

This is a pure Agent Skill. It should work in any agent environment that can read `SKILL.md` and optionally run local scripts. No OpenAI, Anthropic, hosted model, API key, MCP server, web app, or cloud service is required.

## Workflow

1. Inspect the source PDF before designing.
   - Extract text when possible.
   - Render pages to images and visually inspect layout.
   - Extract embedded images when possible, especially QR codes, barcodes, logos, seals, stamps, and signatures.
   - If `scripts/pdf_guardrails.py` is available and PyMuPDF is installed, run it to create a source manifest.

2. Build a preservation list.
   - Lock identifiers: application numbers, receipt numbers, invoice numbers, UID values, transaction IDs, bank references, booking IDs, license numbers, tax IDs.
   - Lock operational facts: dates, times, deadlines, amounts, totals, addresses, locations, required documents, eligibility rules, legal notes.
   - Lock personal and organization facts: names, parent names, company names, offices, contact details, titles, certifications.
   - Lock machine-readable assets as source images: QR codes, barcodes, verification marks, seals, signatures, stamps, official logos.
   - Preserve source labels unless the mapping is unambiguous. If the source puts two name lines under `Applicant Name`, keep both under `Applicant Name`; do not infer `Father`, `Guardian`, `Owner`, or another relationship from position alone.
   - Preserve capitalization, punctuation, separators, and spacing inside locked values. Do not add currency prefixes, normalize comma spacing, title-case text, or otherwise "clean up" a locked field unless the source already contains that form.

3. Design the reader path.
   - Put the most important facts in a top summary strip or priority cards.
   - For appointments: show date, time, place, required arrival/action, applicant, and reference number first.
   - For receipts/invoices: show amount, receipt/invoice number, date, payee/office, transaction references, and fee/line-item breakdown first.
   - For resumes: show name, target role, contact, strongest proof points, skills, and recent experience first.
   - For proposals/reports: show title, client/audience, objective, decision points, timeline, and next action first.

4. Redesign conservatively.
   - Copy locked values exactly. If a friendlier interpretation helps, add it next to the original value instead of replacing it.
   - Keep original headers and issuing-agency text visible unless the user explicitly asks to remove them.
   - Never let icons, labels, captions, seals, or decorative elements share the same visual space as values. Give every ID, date, time, amount, and name its own stable box or row with enough width for the longest expected value.
   - Preserve QR/barcode/logo/seal/signature/stamp images exactly. Do not recreate, recolor, crop, filter, blur, or trace them.
   - Use clear labels so the reader does not infer meaning from raw tables.
   - Use color semantically: strong header color for identity, green or similar for paid/success/total, amber for warnings/arrival/deadlines, neutral body text.
   - Use small icons only as scanning aids, never as a replacement for visible text labels.
   - Keep typography readable and print-safe. Use stable page dimensions, margins, and spacing.

5. Validate before delivery.
   - Render the final PDF to images and inspect every page.
   - Check all locked values from the preservation list are present exactly.
   - Confirm machine-readable assets are visible and unchanged from the source.
   - Confirm no text is clipped, overlapping, too low contrast, or ambiguous.
   - Compare a rendered image of the source and a rendered image of the final PDF visually. Ask the active vision-capable model, a reviewer, or the user-facing LLM view to identify any discrepancy in names, IDs, dates, times, amounts, table values, barcode/QR visibility, and label meaning.
   - Treat any collision, clipped value, ambiguous relabeling, or missing machine-readable asset as a blocking failure even when text extraction says the value is present.
   - Read `references/quality-checklist.md` for a fuller final pass on sensitive PDFs.

## Output Expectations

Deliver a final redesigned PDF when the user asks for a transformed file. If helpful, also provide the HTML/source artifact used to render it.

In the final response, include:

- The final PDF path.
- Any supporting source path, if created.
- A short verification note naming the critical fields and machine-readable assets checked.
- A clear limitation if OCR, barcode decoding, or visual rendering could not be performed.

## Optional Helper

Use `scripts/pdf_guardrails.py` when you want a deterministic source manifest:

```bash
python scripts/pdf_guardrails.py input.pdf --out /tmp/prettify-pdf-check
```

It writes extracted text, critical-fact candidates, embedded image assets, and page renders. The script is optional and local-only; it does not call an external service.

## Design Rules

- Preserve exact source values before improving wording.
- Add helpful context without replacing original text: `10.00AM-11.00AM` can be paired with `1 hour appointment window`; keep both.
- Use summary cards for high-value fields, not for every field.
- Keep tables for line items, totals, transaction references, or structured data.
- Prefer system fonts unless the user provides a brand/type direction.
- Keep icons small, simple, and paired with text.
- Avoid decorative effects that reduce trust: heavy gradients, low-contrast text, blurred backgrounds, fake stamps, fake signatures, fake QR codes.
- Never invent missing fields. Omit unknown values or mark them only if the source explicitly marks them.

## Common Pitfalls

- A visually nicer PDF that loses the barcode is worse than the original.
- Reformatting IDs can break verification. Copy them exactly.
- "Cleaning up" timestamps, names, totals, or addresses can change meaning. Add a friendly hint beside the exact value instead.
- Relabeling an adjacent value can change identity. If the source label is unclear, keep the original label/value grouping instead of inventing a better-sounding label.
- Text extraction can pass while the PDF is visually wrong. Final acceptance depends on rendered-page inspection, not extraction alone.
- A beautiful hierarchy that hides the next action fails the task.
- If the source is scanned, OCR may be incomplete. Say so and visually verify the final result.
