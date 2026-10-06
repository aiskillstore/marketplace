---
name: tech-writing-proofread
description: Proofreads English technical writing for typos, grammar slips, punctuation, terminology consistency, jargon, and structure; returns an itemized Original → Suggestion → Reason list without rewriting the whole document. Use when the user asks to proofread, polish, or review an English technical doc, README, or blog draft.
license: MIT
---

# Technical Writing Proofreading

Take an English technical document from "understandable" to "publishable." Proofread only — never rewrite content. Flag suspected factual errors; do not silently fix them.

## Workflow

1. **Read for tone first**: Read the whole document and identify its type (tutorial / API reference / blog post / README). Tutorials tolerate a conversational voice; API references must be precise.
2. **Build a terminology list**: Scan for key terms (e.g. "callback" vs "callback function", "sign in" vs "log in") and check whether one concept is named several ways. Standardize on the most frequent form and note it in the checklist.
3. **Check paragraph by paragraph**, but only for these six categories — do not drift into "is this paragraph well written":
   - Typos and spelling: transposed letters, doubled words ("the the"), commonly confused pairs ("affect/effect", "its/it's", "complement/compliment").
   - Grammar: subject-verb agreement, verb tense consistency within a procedure, dangling modifiers, missing articles before singular countable nouns.
   - Punctuation: consistent serial (Oxford) comma usage; hyphens in compound adjectives ("command-line tool"); no double spaces after periods; consistent use of em dashes vs parentheses.
   - Inline code and proper nouns: inline code, commands, file names, and paths in backticks; proper nouns in their official casing (`GitHub`, not `github`; `JavaScript`, not `Javascript`).
   - Sentence style: prefer active voice ("The system calls the function" over "The function is called by the system"); cut filler ("basically", "simply", "just", "very"); one idea per sentence.
   - Structure: headings in parallel form; lists use parallel items; steps in a procedure are imperative and numbered; acronyms are expanded on first use.
4. **Output the checklist**: list items as "Original → Suggestion → Reason", with line numbers or short quotes. Mark uncertain items `[verify]` instead of forcing a change.
5. **Close with statistics**: N items total, of which typos x, grammar y, terminology z, style w — so the author sees the distribution at a glance.

## Rules

- Fix language, not facts. A suspected factual error becomes `[verify] This contradicts the usual definition — please confirm`, never a silent "correction."
- Do not rewrite whole paragraphs. Even a wordy paragraph gets only specific, fixable sentences flagged; keep the author's voice.
- One pass only. Do not keep "polishing another round" — the deliverable is a "no-defects" checklist, not a perfect text.

## Minimal example

Input snippet:

```text
This function will be called by the system after the data is ready, you can use it to basically handle the registration of the callback, the timeout is 5 s, examples on github can be referenced.
```

Output checklist:

```text
1. [Style] "will be called by the system" → "the system calls" (passive → active)
2. [Style] "basically handle" → "handle" (cut filler word)
3. [Terminology] "callback" — if written elsewhere as "callback function", unify on one form (most frequent wins)
4. [Grammar] run-on sentence: split after "ready." into two sentences
5. [Proper noun] "github" → "GitHub" (official casing)

Statistics: 5 items — style 2, terminology 1, grammar 1, proper noun 1.
```

## Anti-patterns

- ❌ Turning proofreading into rewriting: tearing a paragraph down so the author's voice and structure are lost.
- ❌ Hallucinated "corrections": changing an uncertain technical statement as if it were a typo, introducing a factual error.
- ❌ Typos-only checks: inconsistent terminology and sloppy structure are the real defects in technical docs.
- ❌ Endless iteration: the user says "polish it once more" and it never ends — the deliverable is the checklist, not a perfect text.
