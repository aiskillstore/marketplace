# Create Express Mode

Read this file for simple prompt-to-PPTX requests, "make it quickly" requests,
and cases where the user gives a concise topic or rough outline without asking
for detailed control.

Express mode is still delivery-quality by default. It has less ceremony, not
lower quality.

## Load Order

For Express creation read:

1. `../common-workflow.md`
2. `deckkit-mode.md`
3. This file
   and `design-quality.md` for the design floor and evidence-based kit selection
4. `narrative-quality.md` when the deck has 6+ slides, a persuasive audience,
   or needs roadshow / customer / strategy polish
5. `express-mode.md` when you need the full golden path details

Read `../content/recipes.md` only for recipe-only drafts or tiny hand-authored pages. Read
`../edit/patch-ops-cheatsheet.md` only when DeckKit cannot express a required local
change.

## Default Behavior

Use reasonable assumptions and continue without blocking when:

- the user gives only a short prompt
- the user asks for speed
- the output is an internal draft or normal business deck
- the topic, audience, page count, and style can be inferred safely

Still create `outline.json` and `deck_lock.json` in the run directory. List the
main assumptions in the final summary.

## Minimal Express Pipeline

1. Create run directory and check final output collision; for DeckKit-first runs prefer
   `cli/runtime/init-run.mjs`.
2. Generate or normalize `outline.json`.
3. Generate `deck_lock.json` with canvas, DeckKit, theme/style, font, color,
   language, page-type decisions, and for persuasive decks the lightweight
   narrative fields from `narrative-quality.md`.
4. Select a production/default DeckKit through `deckkit-mode.md`, with a meaningful scenario/brief
   and actual rendered examples. Record `artDirection` using `design-quality.md`.
5. Write `content.json`.
6. Validate content in delivery mode.
7. Build patch with the selected DeckKit.
8. Run `cli/create/run.mjs` to execute check-lock, dry-run, apply,
   vision-check and canonical PDF/PNG evidence while keeping the intermediate artifacts.
9. Review the exact canonical PNGs, write `design_review.json` and record it through
   `visual-review.mjs --design-review` in `visual_review.json`, then repeat the
   Create command with `--finalize --visual-review <path>` to publish that same
   candidate without rebuilding or rendering. Follow `create-runner.md` for the
   required review checks and finalization binding, then write the completion summary.

If no production/default DeckKit fits, do not silently build a huge one-off
patch. Either ask for approval to use a candidate/draft path, or create/extend a
DeckKit following `deck-generator-workflow.md`.

## When To Pause

Even in Express, pause for user input when:

- the requested final output path already exists
- the prompt is too ambiguous to infer audience or purpose
- required data, brand assets, or source files are missing
- the request is legally/brand sensitive and assumptions would be risky
- the user explicitly asks to approve the outline first

## Output Quality

Create workflows must satisfy the common gates. `vision-check` high/medium must
be 0 before delivery. PNG/contact-sheet review is still required for generated
decks because static checks do not catch all font rendering, contrast, and
visual rhythm problems.

For quick decks, do not over-document. The minimum narrative bar is:

- use short claim-like display titles/subtitles when the source supports them,
  while keeping complete claims in `deck_lock.claimTitle` when needed
- avoid sentence-ending periods in display titles and subtitles
- preserve user-specified outline titles/subtitles exactly unless they create a
  hard fit problem; mark their source in `deck_lock`
- avoid repeated card grids dominating the contact sheet
- avoid invented facts
- make each non-appendix slide carry one visible proof object or clear purpose

The [design floor](design-quality.md) also applies below six slides. Sparse copy, a generic icon
and passing static checks do not establish presentation quality. Infer and execute the design
without turning a one-sentence request into a mandatory approval workshop.
