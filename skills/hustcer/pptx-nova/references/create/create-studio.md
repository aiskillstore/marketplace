# Create Studio Mode

Read this file for investor/customer/board decks, brand-sensitive work,
high-risk content, "Studio" requests, or any request where the user asks for
precise control over narrative, style, resources, or page structure.

Studio mode adds confirmation and design locking. It does not replace the
DeckKit-first production path.

## Load Order

For Studio creation read:

1. `../common-workflow.md`
2. `deckkit-mode.md`
3. `design-lock-and-assets.md`
4. `narrative-quality.md`
5. This file
6. `../review/visual-qa-and-asset-slots.md` when images/assets are involved
7. `rich-deck-patterns.md` only if no suitable DeckKit exists or a DeckKit must
   be extended for a richer pattern

Read `../content/formulas.md`, `../content/charts.md`, or `../content/tables.md` only when the deck actually
contains those structures.

## Confirmation Strategy

If the user already provides a clear outline, preserve it. Only propose changes
when the sequence is contradictory, cannot fit, misses required information, or
the user asks for structure improvement.
If that outline explicitly fixes slide titles or subtitles, treat those display
texts as user-specified and preserve them ahead of claim-title/style preferences.
Use `claimTitle` separately for the internal narrative claim.

If the user has not provided a confirmed outline, pause before content/patch
generation and ask for confirmation of:

- page sequence and purpose for each slide
- primary deck profile and the claim/proof spine for formal persuasive decks
- canvas and page count
- audience and decision goal
- style and density
- brand colors and typography
- formula policy if math appears
- chart/table/icon strategy, including data source and semantic validation needs
- image/logo/third-party asset strategy
- whether to continue in the same session or split after the lock

Keep confirmation short: page titles plus one-line purpose, not full copy. The
confirmation should settle decisions that materially affect quality or control;
do not add a design interview for choices that can be safely inferred.

## Design Lock

Write `deck_lock.json` after outline confirmation. It should freeze:

- output and canvas
- `deckProfile` and per-slide `claimTitle` / `proofObject` / `rhythm` /
  `layoutIntent` / `visualDensity` for formal persuasive decks
- DeckKit/theme/style decisions
- colors and typography
- formula policy
- icons/charts/tables, including source data and validation expectations
- image/logo/resource policy
- page types and per-slide rhythm
- template or reference deck fusion decisions

Any later change to theme, DeckKit, fonts, resource policy, or page type should
update the lock before changing content or patch.

Use `assets_manifest.json` only when resources exist. Do not create empty asset
manifests for pure native-shape decks.

## Split / Resume

For long decks, high-risk decks, long source materials, many resources, or
formal customer/investor/board work, offer split mode after `outline.json`,
`deck_lock.json`, and necessary `assets_manifest.json` are complete.

If the user chooses split, write `resume_manifest.json` and stop. Do not write
`content.json`, do not dry-run, and do not generate `.pptx` before the resume.

When resuming, read `../runtime/resume-split-mode.md`, verify run-dir sanity, then continue
from content/patch generation.

## Studio Production Path

After confirmation and lock, return to the common DeckKit-first path:

```text
outline.json -> deck_lock.json -> content.json -> DeckKit -> patch -> check-lock
  -> dry-run -> apply -> vision-check -> final inspect -> high-risk evidence
  -> PNG/contact-sheet review
  -> narrative_quality_review.json
```

After `vision.json` is clean, run the shared finalizer with
`--mode studio-create`. It writes `layout-final.json` and
`evidence-summary.json` from the final inspect report before PNG review. Layout
warnings are review evidence, not automatic failures; merely undisclosed inspect
fields are counted separately. Do not add this finalizer to Express or Micro
Edit merely because it exists.

If a DeckKit lacks needed page types or visual structure, extend/create the
DeckKit following `deck-generator-workflow.md`. Avoid local one-off patches for
large delivery decks unless the task is explicitly a small local edit.

## Quality Bar

Studio decks must preserve readable typography:

- core body text should generally be at least `10.5pt`
- labels, badges, chart/table text should generally be at least `9pt`
- footer/source text may be `8.5-9pt` only when it is non-critical
- numbers, units, percentages, and short labels must not split awkwardly
- circle/square badges need centered readable labels
- arrows, connectors, and center markers must be derived from real geometry
- claim titles should survive the noun-swap test; if the title works after
  replacing the product/company name, sharpen the proof or weaken the claim
- display titles and subtitles should be shorter than the full claim when the
  claim would wrap poorly or dominate the slide; avoid sentence-ending periods
  in both fields unless a question/exclamation is intentional

If text does not fit, first delete copy, change layout, split slides, or enlarge
containers. Do not keep shrinking font sizes to force content into a fixed box.
