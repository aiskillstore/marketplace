# Grounding Rules

## Answering questions

When the user asks a follow-up question about the paper:

1. Find the most relevant source blocks.
2. Answer from those blocks first.
3. Cite the exact page and block IDs.
4. Include the figure or table if it is part of the evidence.
5. Say `原文未明确说明` if the paper does not support the claim.

## Good answer pattern

- `结论`
- `原文依据: p.5 S014-S016, Fig. 3 caption`
- `补充说明: 这是译文中的概括，不是原文逐字表述`

## Bad answer pattern

- vague paraphrase without source IDs
- answer based only on the title or abstract when the question needs body text
- claiming support from a figure without citing the figure or caption
- inventing missing detail when OCR or extraction is uncertain

## Translation rules

- Keep specialized terms stable.
- Keep equations, units, symbols, and citations unchanged.
- Do not over-simplify method steps.
- If a term has no clear Chinese equivalent, keep the original term and add a short note.
- Preserve paragraph-level original/Chinese alignment in `paper.md`.
- Do not convert a full-paper translation request into a Chinese-only summary or critique.
- If a full English paragraph cannot be included because of source restrictions or extraction failure, keep the block anchor and explain the limitation in `translation_notes.md`.

## Figure and table rules

- Cite the caption when explaining a figure.
- Cite the relevant table row or table block when explaining a table.
- If the claim relies on both text and figure, cite both.
- If figure placement is uncertain, mark it as a layout approximation.
- Extract figures/tables to `assets/` whenever possible.
- Place each figure/table card near the first substantive mention in the bilingual text.
- Include original caption, Chinese caption translation, and a short reading note.
- Do not use whole-page screenshots as figure/table replacements unless no tighter crop is possible; mark those as approximate.
