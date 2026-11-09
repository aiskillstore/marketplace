# Design quality for one-sentence decks

Read before choosing a DeckKit for any new deck, including Express. A short prompt delegates design
judgment; it does not lower the visual bar or require a style interview. Infer a sensible audience
and purpose, state material assumptions, and continue. Preserve a pinned brand, reference, era or
restrained aesthetic. Do not force every deck into a loud, dark or colorful style.

This guide adapts Impeccable's audience modes, committed art direction, craft floor and rendered
criticism to slides. It is self-contained: no Impeccable installation, browser, concept lottery,
extra approval, or web-specific styling bans are required. A deck is not a website; page chrome,
serif type, section labels and native diagrams remain valid when they serve its visual system.

## Decide before filling slots

1. Choose the viewer's success: `persuade` (product/sales/decision), `read` (understand evidence),
   `operate` (follow a procedure) or `experience` (engage with the work). Classify the presentation,
   not the product: a developer tool's introduction is usually persuade, not operate.
2. Record `deck_lock.artDirection`: audience, mode, one content-led visual idea, an actual visual
   anchor, and intentional restraint. “Modern / premium / clean” is not a direction. For a document
   engine, “one editable document opens into three product surfaces” suggests a visual mechanism;
   “technology = dark background with boxes” does not. Facts still come from sources.
3. Run selection with `--brief '<user brief>'` or a meaningful `--scenario`, plus language/density.
   Treat the ranked result as a shortlist. No recognized scenario means no evidence of aesthetic fit.
   Open the leading eligible kits' committed `contact-sheet.webp` examples, then read the chosen
   `intent.md` and slots. Compare visual hierarchy, density and proof-object coverage, not kit names.
   Explicit user style outranks inferred scenario. Missing examples are disclosed, not invented.
4. Choose one visual system. Use the selected kit's actual fonts/colors in the lock. Do not mix one
   kit's cover, another's chrome and improvised card shapes. If its slots can carry only tiny prose
   or placeholders instead of the required demonstration, choose another eligible kit or extend it.

For a long deck or an unfamiliar kit, resolve a representative cover, proof page and dense page
before expanding all content. Review an existing matching golden/example when it already proves
those responsibilities; otherwise render a small pilot. Reuse it as design evidence, not as a
second final render. The standard runner still owns the final full-deck canonical render once.

## Craft floor

- **Hierarchy:** every ordinary slide has a clear first and second read. Give the actual product,
  comparison, process or evidence the main stage. A title, a small paragraph and a mostly unused
  canvas is unfinished unless it is a deliberate, strong chapter/statement page.
- **Composition:** align to a real grid; proximity should explain grouping. Whitespace frames a
  substantial subject. Avoid filling the space with boxes, contour rings, rules or a gigantic
  generic icon. A symbol is not proof of privacy, quality or product capability.
- **Typography:** design for projected viewing as well as reading on a laptop. Main body often
  needs 18–24pt; dense evidence can be smaller with clear hierarchy. The existing technical font
  minimum is a safety bound, not a design target. If the kit's real-size example looks timid for
  this task, change the composition/kit or extend it; do not break validated constants locally.
  Check Chinese/Latin weight, punctuation, wrap and line height in the actual render.
- **Color:** commit to an intentional palette with readable contrast and a clear accent role.
  Calm and monochrome can be excellent; washed-out text across every slide is not restraint.
  Do not assign a different accent to every peer or confuse a color with a business meaning.
- **Specificity:** show the mechanism. Use sourced product imagery when available, or an honest
  native diagram, real input/output excerpt or comparison. Native diagrams need connected,
  purposeful relationships and clear hierarchy; generic equal boxes with arrow characters are a
  wireframe, not a finished platform map. Never invent a screenshot, logo, metric or testimonial.
- **Rhythm:** vary macro-composition and density across the contact sheet, not only slide-type
  names. Long stretches of tiny text on the same empty surface fail. A persuasive deck needs a
  memorable content-led moment: a strong reveal, visual transformation, comparison or typographic
  assertion. It need not animate. Quiet evidence reports do not need manufactured spectacle.
- **Icons and motion:** use a coherent licensed icon family at a supporting scale. “CLI / PDF”
  inside a circle and Unicode arrows are labels, not a drawn icon system. Add animation/Morph only
  within the user's request and capability contract, with one clear explanatory purpose. Motion
  never compensates for a weak static composition; continue separate playback verification.

## Review the render, then repair

Look at all canonical PNGs at presentation size and the deck overview. Review quality before
consulting a green machine report; static geometry checks cannot judge taste. Compare the actual
result to the visual anchor and to the brief. Ask:

- What does a viewer see first in three seconds, and why does it deserve that attention?
- If names were swapped, would this still look like the same generic presentation?
- Does the cover promise a compelling story, and do the interior pages deliver it?
- Which slide is weakest, and what concrete change would make it worth presenting?

Batch the fixes revealed by one review. Repair content/layout/kit at its source, rerender changed
pages as needed, then produce a fresh final candidate when inputs changed. Do not inflate scores,
rename repetitive layouts, add decorative icons, or shrink text to make the evidence pass. A
craft failure needs repair; a user's explicit minimal/reference style is not a failure.

## Recorded design judgment

After actual PNG review, write `design_review.json`. Use the exact candidate and canonical manifest
SHA-256 values from `captureVisualBinding()` or the files themselves. This is a human/Agent judgment
record; the validator checks completeness, binding and unresolved findings, not whether an image
is beautiful. All six observations must refer to actual slides; bare `pass`, invented visual
observations and a copied example are not review. State remaining external limitations separately.

```json
{
  "schemaVersion": "pptx-nova-design-review/v1",
  "candidateSha256": "<current candidate SHA-256>",
  "manifestSha256": "<current visual-evidence/manifest.json SHA-256>",
  "mode": "persuade",
  "direction": {
    "audience": "Developers evaluating document integration",
    "idea": "One document expands into three product surfaces",
    "visualAnchor": "<actual example/contact sheet inspected, and relevant qualities>",
    "intentionalRestraint": "No invented UI, decorative 3D or unsupported business metrics"
  },
  "criteria": [
    {
      "id": "hierarchy",
      "verdict": "pass",
      "slides": [1],
      "observation": "<what leads the eye and why>"
    },
    {
      "id": "composition",
      "verdict": "pass",
      "slides": [2],
      "observation": "<subject scale, grid and purposeful whitespace>"
    },
    {
      "id": "typography",
      "verdict": "pass",
      "slides": [3],
      "observation": "<real-size readability and CJK/Latin wrapping>"
    },
    {
      "id": "color",
      "verdict": "pass",
      "slides": [1, 2],
      "observation": "<contrast and consistent accent meaning>"
    },
    {
      "id": "specificity",
      "verdict": "pass",
      "slides": [2],
      "observation": "<visible product mechanism/evidence>"
    },
    {
      "id": "rhythm",
      "verdict": "pass",
      "slides": [1, 2, 3],
      "observation": "<actual macro-layout and density changes>"
    }
  ],
  "weakestSlide": { "slide": 3, "observation": "<honest weakest-page assessment after repair>" },
  "signatureMoment": {
    "slide": 2,
    "description": "<content-led memorable moment; required for persuade/experience>"
  },
  "unresolvedIssues": []
}
```

Pass it as `--design-review <run-dir>/design_review.json` to `cli/review/visual-review.mjs` with
`--mode create`, candidate/manifest binding and the ordinary visual checks. Its complete judgment is
embedded in `visual_review.json`; both the helper and final canonical consumer reject missing,
stale, failed or unresolved design reviews. This applies to short decks and Express too. Narrative
review remains an additional claim/proof check for formal decks. Neither record substitutes for
actually looking, and neither claims universal aesthetic approval or PowerPoint fidelity.

Final Create authorization also requires a valid `deck_lock.artDirection.mode` and rejects a review
whose `mode` differs from that locked mode. The locked mode determines whether `signatureMoment` is
required; changing a review to `read` cannot relax a `persuade` or `experience` design. The standard
runner verifies the lock's existing input binding before checking its mode. When using the standalone
visual-evidence gate, supply the same run lock with `--lock <run-dir>/deck_lock.json`.

An older Create review without this record needs a new actual design review before finalization.
If candidate and canonical evidence bytes are unchanged, record the missing judgment against those
bytes; do not rebuild, rerender, or manufacture an old passing record just to migrate the report.
If the bound lock has no valid `artDirection.mode`, regenerate in a fresh run with the intended mode
locked before candidate creation. Do not rewrite the already bound lock to make finalization pass.
