# Reading workflow

Run these six steps for any paper-reading job. Steps 1-2 build the source map, 3-5 produce the artifact, 6 covers follow-up questions.

## 1. Identify the source and paper type

The source-format fragment loaded for this job covers how to extract from the specific input. At a high level, also identify the paper type so you know how tightly to couple text, figures, and captions:

- discovery or mechanism paper
- methods or algorithm paper
- resource or dataset paper
- conference paper
- review or perspective

## 2. Build a full-document source map before translating

If the user provides a full paper, process the entire document. Do not stop at the abstract, introduction, or a few representative pages unless the user explicitly asks for a preview.

Create stable IDs for source blocks:

- `S001`, `S002`, ... for body text
- `C001`, `C002`, ... for captions
- `F001`, `F002`, ... for figures
- `T001`, `T002`, ... for tables

For each block, capture: page number, block type, original text, translation, reading-order index, nearby figure or table references, first substantive figure/table mention when applicable, and confidence level when extraction is uncertain.

Keep the source map stable so later questions can point back to the same IDs. For long papers, add a page index so the reader can jump across the whole document without losing location.

## 3. Translate conservatively

Translate every extractable substantive block with these rules:

- preserve technical terms unless a standard Chinese equivalent is clearly better
- keep gene names, protein names, formulas, model names, and symbols intact
- keep citations, superscripts, subscripts, and numeric values unchanged
- do not collapse methods details into vague prose
- keep paragraph order and section order unless the user asks for restructuring
- mark uncertain text instead of guessing when OCR or layout extraction is weak
- keep the source's paragraph form; do not convert dense prose into bullet-point keywords
- do not silently skip Methods, limitations, data availability, code availability, competing interests, or extended captions
- if the paper is too long for one pass, write `paper.md` incrementally by page/section and mark pending blocks rather than switching to summary mode

If a sentence contains multiple claims, keep the translation readable but do not split away the original evidence chain. Build the Terminology Ledger (`../../../_shared/core/terminology-ledger.md`) as you translate so recurring terms stay consistent across the whole document.

## 4. Extract and place figures and tables near the relevant discussion

Crop each figure/table into `assets/` and place it near its first substantive mention, keeping the caption attached with both original and Chinese caption text. For the full placement and tight-crop rules, and the figure/table block shape, open `references/figure-extraction.md`.

## 5. Generate the Markdown file

Default output is a single full-paper `paper.md` file. It must include:

- metadata header
- a short page/section index
- page-level or section-level divisions for long papers
- paragraph-level original/Chinese pairs for all extractable substantive text
- figure and table blocks placed near the relevant discussion
- source anchors on every substantive text, figure, caption, and table block
- a terminology table for recurring technical terms (from the Terminology Ledger)
- a short `阅读提示` / `critical reading notes` section only after the bilingual body, not as a replacement for it
- short uncertainty notes only when extraction is weak

Do not add an interactive Q&A panel or follow-up widget in the Markdown deliverable. If a browser preview is explicitly requested, a companion `reader.html` can be generated as a secondary artifact, but the Markdown file remains the primary output.

## 6. Answer follow-up questions with source grounding

When the user asks a question after the file is created, answer from the paper, not from memory, and cite exact block IDs and page numbers. For the full grounding rules, open `references/grounding-rules.md`.
