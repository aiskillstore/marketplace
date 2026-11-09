# Narrative Quality

Use this file for customer, investor, board, roadshow, strategy, product, market,
or other formal create workflows where the deck must persuade rather than merely
format content. For tiny internal drafts, apply only the short checklist at the
end unless the user asks for polish.

This layer does not replace DeckKit, `content.json`, xdoc patching, dry-run, or
vision-check. It defines what the deck is trying to prove before DeckKit renders
it, then checks whether the rendered deck still proves it.

The separate [design floor](design-quality.md) applies to every Create, including short Express
decks. Narrative scores do not prove visual craft. Record actual observations, and do not copy the
example's all-4 scores into a report merely because machine gates passed.

## When It Is Required

Read and apply this file when any of these are true:

- The audience is external, executive, investor, customer, board, or sales.
- The deck is a roadshow, pitch, strategy narrative, product/platform story, or
  reference-quality deliverable.
- The deck has 6+ slides and the prompt expects more than a raw outline.
- A reference deck is supplied as a quality bar.
- The user asks for polish, high-end output, Studio mode, or precise narrative.

For Express drafts under 6 slides, do not add extra ceremony. Still avoid topic
titles and obvious card-grid repetition.

## Deck Profile

Choose one `deckProfile.primary` in `deck_lock.json`. Add `secondaryGates` only
when they materially affect proof requirements.

Common profiles:

| profile                | Use when                                         | Required proof bias                                          |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------ |
| `finance-ir`           | earnings, board, operating, investor metrics     | exact numbers, units, footnotes, bridges, tables             |
| `product-platform`     | SaaS, infra, workflow, developer, AI platform    | platform map, workflow, adoption/efficiency/business linkage |
| `gtm-growth`           | growth, marketing, sales, subscription, consumer | growth loop, segment/cohort proof, monetization bridge       |
| `engineering-platform` | technical architecture, security, data, AI infra | concrete system diagram, technical labels, metric linkage    |
| `strategy-leadership`  | market strategy, transformation, investor day    | thesis arc, market frame, strategic bets, roadmap            |
| `consumer-retail`      | brand, campaign, lifestyle, visual/product-led   | real assets/provenance, editorial hierarchy, image quality   |
| `appendix-heavy`       | dense tables, source packs, disclosures          | readable density, index markers, table grammar               |

If no profile fits, write `general-business` and keep the quality gates below.

## Claim Spine

For formal create workflows, every non-appendix slide in `deck_lock.slides[]`
should carry:

```json
{
  "title": "Product overview",
  "claimTitle": "A single PPTX engine now powers browser preview, PDF export, and AI-native workflows.",
  "purpose": "Show that the product is a system, not isolated features.",
  "proofObject": {
    "kind": "platform-map",
    "proves": "Shared parser/render core supports multiple commercial surfaces"
  },
  "source": "user brief / source_brief.md",
  "omissionNotes": ["No revenue or customer count provided; do not invent."],
  "rhythm": "anchor",
  "layoutIntent": "platform-map",
  "visualDensity": "medium"
}
```

Rules:

- `claimTitle` is the internal conclusion the slide must prove, not necessarily
  the exact on-slide title. Avoid topic-only claim titles such as
  `Product Overview`, `Market`, `Roadmap`, or `Competitors` unless the deck is
  intentionally a raw appendix.
- Display `title` and `subtitle` should be short, scannable, and compatible with
  the selected DeckKit slot. If the full claim is too long, keep it in
  `claimTitle` and split evidence or qualifiers into subtitle, callout, body, or
  `proofObject`. Do not make the page title long merely to sound conclusive.
- Display `title` and `subtitle` should not end with a period. Use `?` or `!`
  only when the page is intentionally framed as a question or emphatic call.
- User-specified outline titles/subtitles have priority over this style rule.
  Preserve them as display text, mark the source in `deck_lock`, and use
  `claimTitle` separately for the fuller conclusion.
- `proofObject.kind` should be concrete: `timeline`, `platform-map`,
  `workflow`, `comparison-table`, `customer-map`, `roadmap`, `metric-rail`,
  `bar-chart`, `matrix`, `source-table`, etc.
- Do not invent metrics, customers, competitors, market size, quotes, or source
  dates to make a slide feel stronger. Put missing facts in `omissionNotes` or
  `deck_lock.assumptions[]`.
- If a slide only has bullets, either convert it into a proof object or mark it
  as `appendix` / `transition` with a reason.

## Contact Sheet Plan

Before writing `content.json`, create either `contact_sheet_plan.json` or embed
equivalent fields in `deck_lock.slides[]`:

```json
{
  "index": 3,
  "rhythm": "anchor",
  "layoutIntent": "platform-map",
  "visualDensity": "medium",
  "macroLayout": "platform-map",
  "density": "medium",
  "proofObject": "shared-engine-flow"
}
```

Gates:

- No 3 consecutive slides should share the same `layoutIntent` / `macroLayout`.
- In a 10-slide formal deck, no more than 2 slides should be plain card grids.
- A repeated DeckKit slide type must vary rhythm, accent, density, title shape,
  or proof object.
- A slide can be visually sparse only when the claim is strong enough to carry
  the space.
- Boxes, arrows, badges, and icon marks must encode hierarchy, grouping,
  direction, or data. Remove decoration that only fills space.

## DeckKit Integration

Keep the DeckKit-first path. Do not hand-author a large coordinate patch just to
make one slide look bespoke.

Use the selected DeckKit's slots to express the claim spine:

- Derive the strongest title/headline slot from `claimTitle` only when it fits
  the layout; otherwise use a shorter display title/subtitle and keep the full
  claim in `deck_lock`.
- Map `proofObject` to a DeckKit-supported visual field such as chart data,
  table rows, stages, timeline items, map nodes, or comparison columns.
- Keep `purpose`, `source`, `omissionNotes`, `rhythm`, `layoutIntent`,
  `visualDensity`, and `macroLayout` in `deck_lock.json` even when the DeckKit
  schema does not expose those fields.
- If no production/default DeckKit can express the required proof object, extend
  a DeckKit instead of hiding the proof in generic bullets.

## Comeback Review

After `vision-check` and PNG/contact-sheet review, create
`narrative_quality_review.json` for formal decks:

```json
{
  "schemaVersion": "pptx-nova-narrative-review/v1",
  "deckProfile": "product-platform",
  "profileGate": "pass",
  "scores": {
    "story": 4,
    "specificity": 4,
    "rhythm": 4,
    "proof": 4,
    "typography": 4,
    "restraint": 4,
    "coherence": 4,
    "precision": 4
  },
  "weakestSlides": [5],
  "acceptedTradeoffs": ["No customer logos provided; used text categories only."]
}
```

Use 0-5 scoring. A formal deck should have no score below 4 before delivery.
If the score is lower, fix the weakest 1-3 slides first. Prefer rebuilding a
weak slide with a better proof object over cosmetic nudges.

Score definitions:

- `story`: sequence has a clear arc and each slide advances it.
- `specificity`: the slide would fail a generic noun-swap test.
- `rhythm`: contact sheet has distinct macro-layouts and density changes.
- `proof`: each claim has a visible proof object strong enough to carry it.
- `typography`: hierarchy is intentional and readable.
- `restraint`: no filler boxes, decorative arrows, or low-value badges.
- `coherence`: the deck feels like one authored system.
- `precision`: numbers, sources, and omissions are explicit.

## Blocking Anti-Patterns

Fix these in formal decks before delivery:

- Claim title is only a topic label.
- Proof object is too thin to support the claim.
- Product/platform slide is just feature cards without workflow, adoption,
  efficiency, or monetization logic.
- Chart has a legend when direct labels would be clearer.
- Connector or arrow floats, crosses unrelated content, or is decorative.
- Equal-role boxes differ in padding, height, or hierarchy without meaning.
- A repeated KPI rail omits value, label, or context on any item.
- Contact sheet reads like a template pack after replacing the product name.
- Body copy exists mainly to fill whitespace.
- Third-party logos, screenshots, app icons, or brand marks lack provenance.

## Express Checklist

For quick drafts, keep this tiny:

- Titles should make claims where possible.
- Avoid 3 repeated layouts in a row.
- Do not invent facts.
- Contact sheet must not show obvious clutter, weak contrast, or generic card
  grids dominating the deck.
