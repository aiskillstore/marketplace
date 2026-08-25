# SOW/PWS DOCX Validation Gates

Run every gate against the final file, then rerun after any change.

## Structural audit

Run:

```text
python scripts/validate_docx.py output.docx --document-type pws
```

The validator checks:

- The file is a valid DOCX ZIP.
- Core sections exist and appear in order.
- Heading paragraphs use real Word heading styles.
- A document with more than eight main sections contains a dynamic TOC field and update-fields-on-open setting.
- No staffing, SOC, IGCE, CLIN, pricing, or skill-chain leakage appears in document text.
- PWS documents contain measurable performance language and a QASP Summary.
- SOW documents contain Inspection and Acceptance.
- Forbidden FAR 37.102(d) hours claims and FAR 52.237-2 key-personnel citations are absent.
- CPARS rating labels are not tied to QASP content.

## Text and semantic audit

Extract all document text and verify:

- Every requirement maps to a deliverable or performance standard.
- Every deliverable has a trigger or due date and acceptance criteria.
- Place, period, security, Government-furnished resources, and transition are consistent.
- `[DEFAULT]` assumptions identify required owner action.
- No prompt text, local path, internal citation token, test instruction, or TOC-refresh instruction leaked into the file.
- No vague standalone `support`, undefined `as needed`, or untestable `best practices` requirement remains.

## Render audit

Render the latest DOCX to page PNGs with a real office engine and inspect every page at 100% zoom. Check:

- No clipping, overlap, broken glyphs, or orphaned headings.
- Tables fit the page, repeat headers, wrap correctly, and use readable widths.
- Header, footer, and page numbers are aligned.
- TOC placement is correct. If the dynamic field is not populated, retain it and disclose the Word refresh step in chat.
- No large blank gaps or accidental blank pages.

## Target application

LibreOffice rendering is not proof of Microsoft Word behavior. When Word is available, verify the final file in Word, refresh fields, and save. Record the exact surface in `test.md`.

## Separation fault injection

At minimum, confirm the validator rejects test copies containing:

1. `STAFFING HANDOFF TABLE`.
2. `SOC Code` or an FTE staffing table.
3. `CLIN HANDOFF TABLE` or a Section B pricing table.
4. `FAR 37.102(d)` as the basis for results-versus-hours language.
5. `FAR 52.237-2` as a key-personnel clause.
6. A PWS missing QASP Summary or measurable standards.

Document the exact automated and manual tests in `test.md`.
