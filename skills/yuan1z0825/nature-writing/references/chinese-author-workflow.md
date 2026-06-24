# Chinese Author Workflow

Deep reference for Chinese, mixed Chinese-English, or lab-note input.

This extends `static/fragments/language/zh-to-en.md`. That fragment already holds
the base rule (**translate intent, not syntax** — split each note into claim /
evidence / condition / comparison / implication / limitation, then reorder for
the section) and the common-repair table. Do not repeat those here. Open this
file only when the fragment is not enough: for the drafting sequence below and
the edge-case repairs.

## Drafting from author notes

Use this sequence:

1. Summarize the author's intended claim in Chinese.
2. Identify missing evidence or boundary.
3. Draft the English paragraph.
4. Add short Chinese notes explaining any structural changes.

Do not make the English sound like a literal translation. Make it sound like a
Nature-style manuscript paragraph supported by the user's facts.

## Edge-case repairs (beyond the fragment table)

These patterns come from Chinese having no tense, no obligatory plural, and a
topic-comment structure. They are the ones the base table does not cover.

| Chinese-draft pattern | Repair |
|---|---|
| No tense marking | Choose tense explicitly: past for what was done/found, present for established facts and what the figure shows |
| No obligatory plural | Decide singular vs plural per noun; do not leave bare count nouns (`sample` → `samples` / `each sample`) |
| Stacked `的…的` nested modifiers | Break into a relative clause or a separate sentence; do not pile modifiers before the head noun |
| Topic-comment opener (`关于X，…`) | Rewrite as subject-verb-object; make the topic the grammatical subject or drop it |
| Every sentence opening with `本文 / 我们` | Vary openings; lead some sentences with the result or the object, not the agent |
