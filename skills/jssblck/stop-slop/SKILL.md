---
name: stop-slop
description: "Use for durable prose artifacts: docs, README, release notes, UI copy, comments, commit messages, PR/issue text. Skip ordinary chat replies."
---

# Stop slop

Use this skill only for durable prose: text that will be saved, shipped,
published, committed, or pasted outside chat. Do not use it for ordinary
assistant replies, progress updates, or final answers unless that response
contains a durable artifact; then apply it only to the artifact.

"Slop" is prose that reads as machine-written. A banned-word list catches
"delve", "tapestry", and "in today's landscape", but it misses problems with
rhythm and rhetorical scaffolding. Most useful signals are structural.

Avoid two failure modes:

1. Slop uses constant rhetorical framing. It reassures the reader and resolves
   each thought into a balanced contrast or tidy maxim.
2. Over-correction makes every sentence flat and informational. Uniform rhythm
   is also a machine-written signal.

Write plain, specific, varied prose that explains concrete mechanisms. One
brief expression of personality per section is fine.

## The core test

After an edit, ask whether every fact is still present. A shorter version that
keeps every fact removed slop. A rewrite that drops information changes the
content rather than its style.

## The structural tells

Scan for these. `references/structures.md` covers each in depth with kill/keep
tests; this is the working list.

1. **Virtue or character framing.** Delete claims that a subject is honest,
   trustworthy, principled, or humble. State what it does and let the mechanism
   show its character.
2. **Manufactured antithesis.** Remove "X, not Y" when Y is a strawman or mood.
   Keep it when both sides name real and distinct facts.
3. **Aphorism openers and closers.** Cut tidy maxims that repeat the surrounding
   facts.
4. **Decorative groups of three.** Keep a three-item list only when the content
   has exactly three real items.
5. **Dramatic setup and payoff.** State the information directly instead of
   staging it for suspense.
6. **Uniform clipped headers.** Vary the structure and use plain noun phrases
   where they fit.
7. **Uniform rhythm.** Allow some sentences to be flat and informational.
   Natural prose varies in length and emphasis.

## Discriminate, do not carpet-bomb

The "X, not Y" structure is frequent and easy to remove too broadly. Examine
what each side contributes:

- KILL: "a gate you govern, not a bot you tolerate" (the second half is a
  strawman invented for cadence).
- KEEP: "gates block, advisors comment" and "gates fail closed, advisors fail
  open" (both halves name real, distinct, opposed behaviors).

Apply the same test to fragments and short sentences. Remove manufactured ones,
but keep useful variation.

## Voice anchor (highest leverage)

A target voice is more useful than the instruction "remove AI tells". Read two
or three representative paragraphs before editing. Match their sentence length,
comment density, and idiom. Without a sample, write like the engineer who built
the system and respects the reader's time.

## Workflow

1. Read a voice anchor from the same author or product when one exists.
2. Read for meaning. Mark sentences that add rhetoric without adding facts.
3. Rewrite each marked sentence. Keep every fact while removing unnecessary
   framing.
4. Keep real contrasts and occasional personality. Do not flatten useful
   variation.
5. Preserve code, commands, data, tables, and quoted third-party material.
6. Read the result from start to finish. Restore variation if every sentence
   has the same rhythm.

## Mechanics

Follow ASD-STE100 Simplified Technical English in spirit. Do not enforce its
controlled dictionary unless the user asks for strict compliance.

- Plain ASCII only. No em dashes, no en dashes, and no literal `--` used as a
  dash in prose. Recast with a comma, a colon, parentheses, or two sentences.
  Leave `--flag` forms inside commands and code alone.
- Use one term for each concept.
- Prefer active voice and direct commands.
- Keep each paragraph on one topic.
- Put one action in each procedural step. Keep procedural sentences to 20 words
  or fewer when practical.

## References

- `references/structures.md`: the structural tells in depth, each with a
  kill-or-keep test and a rewrite.
- `references/phrases.md`: the lexical tells (a lower-priority backstop; the
  structure matters more than the vocabulary).
- `references/examples.md`: before and after rewrites from a real landing page.
