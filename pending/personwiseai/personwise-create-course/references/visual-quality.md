# Capability-aware visual quality

## Decide whether visual review is possible

Claim visual review only when `image review-sheet` succeeds and the current Agent can actually
understand the downloaded image. A structured unsupported response stops only visual review;
command success, filenames, dimensions, generation state, and an asset reference do not prove
visual quality.

Record one honest result:

- `completed`: every required slide and serious presenter candidate was inspected and resolved;
- `partial`: only part of the required set was inspectable;
- `not_performed`: the Agent could not consume visual content.

This is completion evidence, not publication permission. Missing vision alone is not a publish
blocker.

## Review the complete deck

At canonical image readiness, download ordered review sheets with at most six zero-based slide
indexes per command and a new bounded destination:

```text
personwise --account <alias> image review-sheet --project-id <project-id> \
  --slides <indexes> --dest <new-path> --json
```

Zoom or crop locally when detail is needed. Cover every slide; sampling is insufficient. Keep a
ledger with slide index/title, intended visual job, text fidelity, semantics/facts, layout,
reference expectation, finding, correction, regeneration identity, and recheck.

Inspect:

- alignment with title, key points, page text, narration, and sources;
- visible text spelling, hierarchy, size, overlap, clipping, and table legibility;
- whether the visual explains the intended mechanism, process, comparison, evidence, or idea;
- deck-level continuity and useful variation without repeated template composition;
- invented numbers, charts, quotations, maps, artifacts, customers, logos, UI, workflow states,
  or source-looking material;
- unsafe advice, inappropriate imagery, watermarks, and intellectual-property problems;
- approved reference influence and any required subject preservation;
- presenter placement and mobile-scale readability.

Treat icons and composition as claims: a checkmark implies success, a lock implies security, a
rising chart implies growth, a dashboard implies observed UI/data, and an archival treatment
implies a real artifact. Reject unsupported implications.

## Correct and regenerate

Fix factual/content causes first:

1. Read a fresh `course snapshot`.
2. Apply the smallest aligned revision-bound `course update` batch.
3. Read the new revision.
4. Put the complete failed subset and concrete per-slide instructions into one
   `image regenerate` command.
5. Use bounded `run wait`/`run get` until each target is canonically complete.
6. Download a new review sheet for the changed subset and inspect again.

Do not split one failed subset into prompt-lottery calls or regenerate based on imagined defects.
After an ambiguous response, read authoritative state before another mutation.

## Use local replacements narrowly

Only a human or vision-capable Agent that genuinely reviewed the exact bounded PNG/JPEG/WebP may
attach it as a reviewed reference/replacement. Correct the lesson first, verify 4:3 composition and
every visible claim, fetch the current revision, upload through the CLI's bounded image command,
then request a fresh review sheet. Transfer success alone is not a visual pass.

## Review presenter candidates

Use `presenter list` to establish exact language/voice readiness. With vision, use
`presenter preview --presenter-id <id> --dest <new-path> --json` for serious candidates and inspect
observable formality, warmth/authority, energy, expression, clothing, framing, and teaching fit.

These are casting observations, not identity or biography. Appearance does not establish
nationality, ethnicity, profession, personality, or history. Select a complete compatible
presenter/voice pair.

## Non-vision path

When vision is unavailable:

- require canonical completed image state for every slide;
- do not claim text, layout, semantics, variety, or reference influence passed;
- do not regenerate or upload a supposedly reviewed image from fabricated findings;
- use only structured presenter/language/voice compatibility and the deliberate default;
- make no appearance or cultural-fit claim;
- record `visual_review_status=not_performed` with the real reason;
- continue the authorized workflow from structured state.
