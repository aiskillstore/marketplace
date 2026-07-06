# image-to-code — implement the reference boards faithfully (Phase 3)

The boards are the specification. The #1 failure mode of image-grounded builds
is **design drift**: strong references, generic code. This file is the
discipline that prevents it.

## Deep board analysis (per section, BEFORE coding it)

Read the board image again at build time — do not code from memory. Extract,
per board:

- **Text:** exact headline/sub/CTA wording visible (adapt, don't lorem);
  line count and wrapping behavior; alignment logic.
- **Typography:** size relationships between display/heading/body (ratios,
  not px guesses); weight contrast; tracking feel; serif/sans behavior;
  calm vs aggressive register.
- **Spacing:** headline↔sub distance, text↔CTA distance, card gaps, section
  top/bottom padding, side gutters, image↔text distance, overall cadence.
  Goal: faithful spacing LOGIC, not pixel OCR. Never collapse a generous
  board into default tight spacing.
- **Color:** background, panel, accent placement, text hierarchy colors,
  border/shadow color mood, image tint/grade. Preserve the palette logic —
  never sub in generic web defaults.
- **Components:** button size/shape/radius/fill-vs-outline and hierarchy;
  card structure; badges; dividers; borders; shadows. If a detail is too
  small to read, generate a closer detail image rather than guessing.
- **Rhythm:** repeated motifs that define the design language (hairlines,
  numerals, crop frames, rail notes) — these carry the concept spine.

## Anti-drift rules (during implementation)

- Do not simplify distinctive sections into generic rows.
- Do not compress generous spacing into dense layout.
- Do not flatten strong typography into a default hierarchy.
- Do not merge different section systems into one repeating pattern.
- Do not swap the board's palette for tokens you're used to.
- When your habit disagrees with the board, **the board wins.**
- The coded page must feel like the same website as the boards. After each
  section, glance board ↔ code and name one thing you kept faithful.

## Ambiguity resolution (in order)

1. Preserve the visible design language.
2. Preserve layout + spacing logic.
3. Preserve the component family.
4. Preserve mood/polish level.
5. Generate an extra detail image of the unclear region.
6. Regenerate that section's board fresh.
7. Only then pick the most implementation-friendly faithful reading.

Never fill ambiguity with a generic default first.

## Bespoke chrome (hard rule, gate-checked)

**Page chrome inside a section board is non-normative.** Board generators
often render a nav bar, footer, or sibling-section fragments inside a single
section's mockup. Only the section's OWN content is binding; do not copy
board-invented nav items, footer chrome, or adjacent-section slivers into a
section that doesn't own them.

**Board-drawn eyebrows beyond the budget are also non-normative.** Boards
love uppercase kickers and will draw one on nearly every section; the page's
eyebrow ceiling (ceil(sections/3)) wins. Keep the budgeted ones where the
board placed them; drop the rest without treating it as drift.

**The generated icon set is exempt from the "don't add micro-UI" rule** when
it annotates real content (spec rows, facts tables, feature labels) — the
icons come from the asset plan, not board improvisation. Don't scatter them
decoratively where nothing needs annotating.

**Board vs. brief precedence for CTAs:** the board wins for composition and
placement; the brief's CTA inventory wins for the CTA's garment and
interaction identity (boards often render generic default buttons — that part
of the board is not authoritative). Distinct intents (e.g. "book" vs.
"walk in") may carry distinct labels; the one-label rule collapses only
same-intent duplicates.

**Garment catalog — stop reinventing the same three buttons.** Recent builds
converged on the same trio (drawing underline, hover flood-fill, framed
block). Those three are now RATIONED: at most ONE of them per page, and zero
overlap with the previous build's garment set (anti-convergence ledger,
`wow-catalog.md`). Pick or derive the rest from garments like these — always
re-expressed through the brief's material world, not copied literally:

- text link whose arrow travels along a drawn path (route, circuit, seam)
- label that splits/slides apart revealing the destination underneath
- CTA embedded in an image cutout (button IS a photographed object/tag)
- stamp/press: :active physically imprints (skew + texture shift)
- ticket/coupon with perforation that "tears" on hover
- mono readout that types/decodes the label on hover
- circular badge that spins/unrolls; text-on-a-path
- magnetic pill with inertia (only if nothing else on the page is a pill)
- underline that is a waveform/route/thread, animating like the motif
- swatch/chip that flips like a material sample
- oversized numeral or glyph as the hit area, label as its caption
- row/band CTA where the entire strip shears or shifts grade on hover
- corner-bracket target that closes around the label (viewfinder)
- toggle/switch metaphor for binary intents (listen/read, light/dark)

The test: cover the label — could you still tell which site this button
belongs to? If it could live on any site, it's not done.

No shared button/CTA style stamped across the page. Each CTA is designed in
the component that owns it, with its own interaction identity — examples:

- Hero: oversized underlined text-link, underline draws in, magnetic pull.
- Work row: whole-row hover reveals a preview crop + sliding index digit.
- Contact: framed block that fills on hover with a clipped text swap.
- Nav: links with sliding digits or a moving hairline, not pill buttons.

Same voice, different garments. Also: no site-wide `.btn-primary`-style
utility classes in the global CSS; style CTAs where they live. Two builds (or
two sections) sharing the same nav/CTA shape is a failure even if the palette
differs.

## Structural hygiene

- **Anti-nested-box:** don't wrap content in card-inside-panel-inside-frame
  stacks the board doesn't show. Boards usually get their depth from ONE
  surface change — mirror that.
- **Micro-UI clutter:** don't add badges, dots, tag pills, version chips, or
  icon confetti the board doesn't show. Every small element must exist on the
  board or serve real content.
- Copy discipline: adapt the board's visible wording into real, specific copy
  (design-recipe.md §5 rules apply — no filler verbs, no em-dashes, no fake
  numbers).
