# Output contract

Prefer these outputs:

- `paper.md` for the full-paper Markdown artifact
- `source_map.json` for stable source anchors
- `translation_notes.md` for terminology, uncertainty, and layout notes
- `assets/` for extracted figures or cropped snippets when needed
- `reader.html` only when the user explicitly wants a browser preview

Do not hide missing information. If the source is incomplete, label the output as draft mode.

## Pre-response verification

Before final response, verify:

- `paper.md` contains `**Original:**` and `**中文:**` block pairs
- every image/table link used in `paper.md` exists under `assets/`
- every figure/table in `assets/` has a corresponding Markdown block and source pointer
- `source_map.json` parses as JSON and includes source block IDs
- `translation_notes.md` records skipped, uncertain, or draft-mode content

## Tooling guidance

- If the input is a PDF, load the `pdf` skill first for extraction and OCR guidance.
- If the user asks for a richer browser view, use `web-artifacts-builder` or `frontend-design` only as a preview layer on top of the Markdown workflow.
- If the user wants citation-level grounding to original text, keep the source map explicit and do not lose the page or block IDs.
