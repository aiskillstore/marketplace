# Contract-driven DeckKits

Read this reference when a selected catalog entry has `designContract`. Other DeckKits keep their
existing workflow. Registered designs include `biennale-yellow`, `cartesian`, `broadside`, `long-table`,
`black-gold`, `green-slate`, `clear-value`, `swiss-grid`, `mckinsey-blue`, `clear-impact`, `warm-clay` and `amber-ledger`; this is a pptx-nova
extension, not a new xdoc format.

## Agent workflow

Discover only the selected design and its layout capacities:

```bash
node <skill-root>/scripts/cli/deckkits/design.mjs --deckkit biennale-yellow
```

Read `assets/deckkits/biennale-yellow/intent.md` for design judgment and the evidence page schema under
`assets/deckkits/biennale-yellow/schemas/` for content fields. Biennale 2.0 retains the nine slide type names and routes every page through registered layouts.
For `biennaleDataSlide`, supply numeric `bars[].value`, `unit` and `source`; retired `pct` and display
strings require an explicit source-data migration. See `intent.md` for the field mapping. Use `biennaleEvidenceSlide` for a native numeric chart:

```json
{
  "type": "biennaleEvidenceSlide",
  "layoutId": "auto",
  "data": {
    "title": "Participation keeps growing",
    "label": "ANNUAL REGISTER",
    "source": "Source: annual participation register",
    "seriesName": "Participants",
    "unit": "people",
    "kind": "bar",
    "points": [
      { "label": "2024", "value": 120 },
      { "label": "2025", "value": 180 },
      { "label": "2026", "value": 240, "emphasis": true }
    ],
    "stats": [
      {
        "value": "240",
        "suffix": "",
        "label": "PARTICIPANTS",
        "description": "A wider public takes part."
      },
      {
        "value": "2",
        "suffix": "×",
        "label": "GROWTH",
        "description": "Participation doubled over two years."
      }
    ]
  }
}
```

Resolve before rendering when content fit or repetition is uncertain:

```bash
node <skill-root>/scripts/cli/deckkits/design.mjs \
  --deckkit biennale-yellow --content content.json --output design-preview.json
```

The report records eligible layouts, the selected layout, actual frames, title adaptation, requested
number format, geometry fingerprint and reasons. `auto` chooses deterministically from fitting layouts
and avoids repeated resolved compositions when alternatives fit. An explicit `layoutId` can be
`chart-left`, `chart-wide` or `chart-top`; explicit choices do not bypass capacity checks.
If only one layout fits, repetition is disclosed. Do not delete data or invent another proof object
just to meet a variety target.

For decks made entirely of evidence slides, diversity is assessed from resolved compositions rather
than the legacy page-type groups. `auto` favors less-used fitting compositions and avoids consecutive
repetition when alternatives fit. Explicit repeated layouts produce a review warning. Legacy and
mixed page-type decks retain their existing group checks.

Keep using `validate-content.mjs`, `cli/create/build.mjs` and `cli/create/run.mjs`. Builds with an
output patch also save `design-contract.json`, `design-plan.json` and `design-check.json` beside it.
The standard create runner automatically inspects the candidate, exports its native chart data and
writes `design-readback.json`. Those artifacts are retained and bound to finalization. A changed
contract requires a new candidate. Choreography composition rechecks the design and updates the
final patch binding before apply.

For manual pipelines, after dry-run/apply save `xdoc pptx inspect ... --json` and
`xdoc convert ... --to json --output model.json`, then run:

```bash
node <skill-root>/scripts/cli/deckkits/design.mjs \
  --deckkit biennale-yellow --plan design-plan.json --patch patch.json \
  --inspect inspect.json --model model.json --output design-readback.json
```

Readback checks object identity, geometry, native chart presence, category labels, series names and
numeric values. It does not prove full chart XML/workbook equality, effective theme inheritance or
PowerPoint parity. Actual PNG/PDF review and the existing canonical visual gate remain mandatory.
Visible numeric formatting is separate from raw source values. Unsupported number formats may use
the renderer's full-value fallback; inspect the visible output rather than claiming the requested
format was applied.

### Violet operational family

`violet-momentum` uses `violet-operations/v1`: white evidence, near-black verdict cover,
Electric Violet, open native tables, single-series native columns, convergence totals,
outlined progress, milestone actions and ten-position ratings. Discover its ten roles and
eighteen compositions through the same design/slots/build/Create commands. Read
`assets/deckkits/violet-momentum/intent.md` for capacities and editing boundaries.

All data, units, status wording, owners, dates and decisions come from content. Signed/zero
numeric evidence stays unchanged; tiny observations can be subpixel. Independent annotations,
derived gaps, tracks and bubbles require regeneration after manual data edits. The uniform
violet series avoids redundant per-point style overrides. No image ingestion, forecast,
animation or arbitrary existing-deck refurbishment is registered. Candidate status requires
explicit selection and does not imply production/default eligibility.

## Maintainer boundary

### Poster family: Broadside

`broadside` 2.0 uses `broadside-poster/v1`. Its sixteen retained slide types resolve into twenty-eight
registered compositions through the same design, slots, validation, build and Create commands.
Read `assets/deckkits/broadside/intent.md` and start from its content example. Dark/orange registers,
heavy upright display, monospace chrome, slash lists and the closed cycle are design identity.
Ordinary English headings default to sentence case, preserving proper names and acronyms. Covers,
chapter openers and short declarations may deliberately use lowercase. User or brand casing takes
precedence; the renderer preserves input, and line breaks do not restart capitalization.
Explicit `layoutId` still requires capacity; full decks open with cover and end with closing.
Use `meta.designScope: "excerpt"` for extracts.

Native column/bar and doughnut pages require numeric values, unit, source and series name. Legacy
display strings and arbitrary segment colors fail validation. Zero values have no artificial
minimum height. The native chart retains raw data while its independent doughnut legend is editable
text; manual chart edits do not synchronize that legend. Statistics are display strings and the
stepped hierarchy is categorical. `image.split` remains a native placeholder shell without asset
ingestion. Arial Black / Arial / Menlo and Noto Sans SC replace unavailable reference fonts; fonts
are not bundled. Canonical review and applicable native-host checks remain necessary.

### Single-ink editorial family: Long Table

`long-table` 2.0 uses `long-table-editorial/v1`. Read `assets/deckkits/long-table/intent.md` and discover
its eight retained slide types and fifteen registered compositions with the same CLI. All roles except
the five-column calendar have two genuinely different geometries. Explicit `layoutId` still needs to
fit; `auto` checks capacity and recent layout rhythm. Complete decks open with cover and end with
closing; use `meta.designScope: "excerpt"` for extracts. The optional large edition, label and metadata
fields on the cover remain independent. Input casing and explicit line breaks are preserved.

Cream paper, rust single ink, heavy display, serif English, fine rules, owned edition badges and
native freeform capsules define the identity. Arial Black / Georgia and upright Arial Unicode MS
replace unavailable reference fonts; fonts are not bundled. The flat paper fill deliberately omits
the source grain because the tested native pattern differed between PowerPoint and canonical rendering.
The native calendar preserves every header and cell. Its separate status outlines do not follow
manual row-height or column-width edits; regenerate from content to synchronize them. No chart or
image ingestion is provided. Candidate readiness does not prove arbitrary existing-deck refurbishment.

### Warm editorial family: Cartesian

`cartesian` 2.0 uses `cartesian-editorial/v1`. Read `assets/deckkits/cartesian/intent.md` and discover
its ten retained slide types and eighteen registered compositions with the same CLI. Cover,
agenda, statement, column chart, image/stats, cards, line chart and timeline each have two real
geometries; team and closing have one. `auto` resolves capacity and recent layout rhythm;
explicit IDs still need to fit. A complete deck opens with cover and ends with closing;
use `meta.designScope: "excerpt"` for extracts.

Both chart types require `data.unit` and `data.source`, two named numeric series and matching
categories. Authored axis domains cannot clip data. Formatting changes visible ticks while raw
values stay unchanged. Native lines use straight segments. Tiny observations on a shared linear
axis may be subpixel; raw values are independently checked by readback.

`image.editorial` accepts an assets manifest; contain and cover are verified. An unbound image
uses the intentionally editable crossed frame. Native paragraph agenda keeps its existing target
and levels; row mode rejects levels rather than dropping them. Circles own their centered text.
Picture readback checks presence, geometry and crop in addition to text/shape/chart checks.
Final canonical review and applicable native-host checks remain necessary. Candidate readiness
does not prove arbitrary existing-deck refurbishment or preservation; fonts are not bundled.

### Editorial family: Black Gold

`black-gold` uses the `editorial-ledger/v1` family with six content types: `ledgerCoverSlide`,
`ledgerSummarySlide`, `ledgerTrendSlide`, `ledgerMatrixSlide`, `ledgerRankingSlide`,
`ledgerDecisionSlide`. Discover its own contract and content schemas; do not reuse Biennale fields.
Its example is `assets/deckkits/black-gold/examples/content.json`.

Trend pages choose full-width, explanation rail or a supporting native chart. Rankings choose a
KPI rail or a lower KPI band. Matrices support bounded row densities. Content capacity and the
geometry fingerprint, rather than random positions, determine valid changes. Repetition warnings
remain review inputs. Full decks use light evidence and dark summary/action stages; an explicit
`meta.designScope: "excerpt"` allows long evidence excerpts without inventing narrative stages.

Each body page requires assertion, basis, source, as-of, unit and verdict. Cover fields differ and
do not contain unused body slots. Dual-unit trends use `chart.categories` once; `secondary` supplies
only kind/name/unit/values and inherits those categories. Current tested JSON projection omits a
combo group, so the adapter uses two independently verifiable native plots.

Matrix input has five headers and 3–5 rows (`name`, numeric `amount`, numeric `share` from 0–100,
`representative`, `thesis`), plus `totalLabel`. The native table retains every cell's text. Share bars
are editable shapes computed from the same source numbers; editing cells manually in PowerPoint
does not automatically update the bars. Regenerate from content to keep them synchronized.
Cells use one authored paragraph with automatic wrapping. Native cell style/OOXML equality is not
proved by cell-text readback.

Gold focus is counted from actual styled objects/points, with the cover rule exempt as structure.
Bar/column focus uses an outline to avoid large accent fills; line endpoints use a small gold marker.
The palette, typography, flat effects, chart kinds, axis/grid and table-rule restrictions are checked
in patch operations. Gold pixel area, assertion quality and overall aesthetics require visual review.
Native-table creation also runs the semantic audit and binds its report to finalization.

The optional [finance research policy](../policies/finance-research.md) applies when requested content
requires it; skin selection does not activate financial assumptions or conclusions. The catalog
records the kit's production selection eligibility; arbitrary existing-deck refurbishment remains unverified.

### Strategy family: Green Slate

`green-slate` uses `strategy-report/v1`: a charcoal/forest/mint report with ten content types for
cover, summary, intervals, matrix, roadmap, value, flow, section, notice and closing. Read
`assets/deckkits/green-slate/intent.md`, discover its design and slots, and start from
`assets/deckkits/green-slate/examples/content.json`. Do not reuse another family's field names.

Rail/wide intervals and vertical/horizontal flows change geometry for the same content. Matrix
full/compact variants change density. Selection is deterministic from fit and recent layout history;
explicit `layoutId` must also fit. Matrices accept 3–6 columns and rows with column weights/alignment.
Intervals accept 2–6 categories with finite `0 <= low <= high`. Line series accept 2–8 categories;
flows accept 3–5 steps (vertical at most three); roadmaps accept 3–4 positive-duration phases with one
activity per track/phase. Exact capacities and visible fields are in the selected schema and contract.

Interval plots stack the lower bound and remaining span; exact bounds remain directly labeled.
Tiny and negative native line observations are retained without promising individual pixel visibility
on a shared linear scale. Native tables retain literal cell strings. Owned circle text is centered in
both axes, label text shares its background frame, and roadmap captions reserve space below rules.
Style checks reject unsupported chart kinds, effects, pictures and unstyled table cells; applied
readback includes shape-owned text and explicitly set frame anchors. These checks cannot establish
optical centering or replace per-page visual review.

Every body page includes title, basis, source, as-of and verdict. Full-deck/excerpt semantics follow
the declared `meta.designScope`. The skin carries no business assumptions: claims, labels, units,
dates, durations and data remain content. CJK rendering was checked with Arial Unicode MS; font
availability and regular/bold output require rechecking on another machine. Fonts are not bundled.

### Annual research family: Clear Value

`clear-value` uses `annual-research/v1`: white pages, serif headings, black rules, restrained teal
current evidence, gray history and conclusion-only terracotta. Discover its eight `value*Slide`
schemas and read `assets/deckkits/clear-value/intent.md`. The example covers cover, summary, evidence,
matrix, chart/table composite, timeline, decision and argument. The skin carries no business policy.

Evidence accepts 1–4 figures: rail/wide for one, paired for two, lead for three, quad for four.
Argument column/split and matrix full/compact change geometry or density. Capacity checks use the
actual figure count, composed series head, weighted columns, row count and positive phase duration.
Generic repeated-field budgets are discovery hints; resolved checks govern these inputs. Overflow
fails before operations rather than shrinking fonts. All pages require title, basis, source, as-of
and verdict. `meta.designScope: "excerpt"` supports standalone evidence.

Charts support bar, column, line and native doughnut, plus two data-derived editable circles.
Native JSON calls doughnut `ring`; readback normalizes only that verified alias and still checks
every category, series name and raw value. Lines show first/last values in the figure head because
selective classic endpoint value labels were not supported by the tested runtime. Forecasts use
single-series columns: `forecastFrom` is the last observed zero-based category index; subsequent
columns are dashed outlines. Stacked labels use light backgrounds and dark text. A common linear
axis does not make tiny observations separately visible. Circle area, rather than diameter, tracks
value; regenerate to synchronize these shapes after data changes.

Matrices have 2–7 weighted/aligned columns and bounded rows; exact per-type limits live in schemas.
Each cell/header is one authored paragraph with automatic wrapping. Native readback checks literal
cell text, not complete table XML or visual styling. Timeline widths encode positive durations,
with a separate risk table and reserved lower note. Actual Latin/CJK regular/bold rendering and
every accepted PNG still require review. Fonts are not bundled; no PowerPoint parity is inferred.

### Warm clay editorial family: Warm Clay

`warm-clay` uses `warm-clay-editorial/v1`: cream paper, upright serif assertions/numerals, terracotta
evidence, blush numbered squares, corner quarter-disks/rings and open hairline structures. Eight roles
resolve into fifteen bounded layouts; discover its `clay*Slide` schemas and read
`assets/deckkits/warm-clay/intent.md`. It is candidate and requires explicit selection.

Native single-series columns and horizontal-rule tables retain numeric data and every cell. Integer,
decimal and scientific labels use separate formats checked against PowerPoint. Metric units append
as native runs on the numeral baseline; shared readback follows appended text by paragraph.
The cover portrait is an editable placeholder shell only, without image ingestion. Fonts are not
embedded. Claims, status meanings, units, sources, dates and targets remain content; no sector policy
is added. Complete decks open with a cover and end with commitments; extracts declare excerpt scope.

### Amber ledger family: Amber Ledger

`amber-ledger/v1` provides eight annual-report roles and sixteen bounded compositions. Warm ivory,
charcoal assertions, upright serif interpretation, gray history and honey-amber emphasis remain
identity constraints. Read `assets/deckkits/amber-ledger/intent.md` for the role/layout mapping.
Business claims, sources, units, dates, targets and status meanings stay in content.

Ordinary columns, point-lines and rings are native charts; matrices and decision registers are native
tables. Tiny nonzero column/line domains below `1e-5` use editable numeric-derived shapes with literal
values, including a native freeform line. Reconciled bridges and actual/plan tracks also derive from
raw content. Independent labels, totals, interpretations and derived shapes require regeneration
after data edits. No minimum fake bar is added for zero. Fonts are not embedded. Candidate selection
is explicit; no arbitrary images, existing-deck preservation or all-host pixel parity is implied.

### Shared contract boundaries

The published runtime uses only Node built-ins and xdoc. The design schema is a bounded first-party
schema, validated by `shared/design-contract.mjs`; this is not an exported general-purpose JSON Schema
implementation. Unknown fields/checkers and invalid token references fail. Current checks cover
palette, font families, a font floor, forbidden effects/operations and creation bounds. The public
readback report names its coverage; a rule's presence alone is never visual proof.

Biennale repeating components are resolved per instance. Composed fields such as value+suffix share
one budget; programme rows and all calendar cells use actual instance geometry. Capacity estimates
are heuristics and require canonical render review. Discovery v2 reports `registeredSlideTypes` and
registered families; the retired `legacySlideTypes` and slot APIs are no longer exposed. Existing
design-less DeckKits retain their original checks. `shared/core-primitives.kit.mjs` owns common
geometry and baseline validation; suite-specific design rules stay outside it.

Edit the selected contract rather than hand-editing generated budgets or projected refurbishment
tokens. In a source checkout, the maintainer-only projection command is
`node tools/generate-pptx-design-projections.mjs biennale-yellow`, followed by the same command with
`--check`. That tool is not needed or distributed as a user workflow dependency. Keep new design
languages opt-in; shared semantics do not require every design to use the same visual components.

New visual families register assertion, resolver, style checks and projection metadata in
`shared/design-family-registry.mjs`. Projection preserves existing per-type asset metadata and independently
registered refurbishment mappings. Adding a creation family does not create refurbishment support.
