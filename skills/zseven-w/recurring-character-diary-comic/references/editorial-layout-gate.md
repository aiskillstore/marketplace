# Editorial layout gate

Use this gate after the final lettered page has passed contract-fidelity QA and
before selecting it as a README example, tutorial image, hero asset, portfolio
piece, or other public-facing showcase. It judges editorial composition, not
story truth. A technically accepted page can still fail this gate.

## Keep the two axes separate

Record both outcomes on the exact reviewed final-page hash:

- `contract_fidelity`: whether the final pixels pass the locked S0/S1 story,
  identity, anatomy, continuity, relation, and lettering checks;
- `editorial_layout`: whether the page has intentional panel rhythm, hierarchy,
  inset treatment, negative space, and final-beat emphasis at normal reading
  size.

Use `showcase-ready` only when both axes pass. Otherwise use `internal-only`.
`internal-only` does not erase a valid technical acceptance: the page may remain
useful as a regression fixture for contract fidelity. Conversely, attractive
layout never cures a technical failure.

These labels do not grant publication authority. Keep `user-approved` and any
permission to publish as separate user decisions.

## Required checks

Review the original-resolution final page and also inspect the same artifact at
exactly 25%. Record `pass`, `fail`, or
`not-verified` plus a concrete visual locator for every check.

| Check ID | Pass condition |
| --- | --- |
| `reading_path` | The eye reaches every panel and bubble in the intended order without backtracking or guessing. |
| `beat_hierarchy` | Setup, anchor, reaction, turn, and final beat receive visibly different weight that agrees with their narrative jobs. |
| `panel_shape_rhythm` | Panel proportions and placement preserve the selected story-directed skeleton and create deliberate pacing rather than a resized set of interchangeable cards. |
| `border_language` | Borders, corners, gutters, overlaps, or open edges form an intentional page language; one repeated container treatment does not flatten every beat. |
| `inset_integrity` | Small or floating panels read as deliberate reactions or details; they do not look detached, accidentally cropped, or anatomically severed. |
| `negative_space_intent` | Large empty regions frame a beat, hold lettering, or create a deliberate pause; they do not look like leftover packing space. |
| `final_beat_emphasis` | The punchline or final viewpoint has enough scale, clarity, contrast, or stillness to land after the preceding panels. |
| `thumbnail_silhouette` | At exactly 25%, the composition still reads as one paced comic page rather than a dashboard or card grid. |

Do not require diagonal borders, rotation, overlap, or border breaks merely for
decoration. A quiet rectilinear page can pass when its hierarchy and rhythm are
clearly intentional. The gate judges the resulting page, not the number of
effects used.

For a page-native final, also verify one coherent line language, paper texture,
palette, environmental space, and character scale system across the complete
page. For a reconstructed fallback, disclose that route and do not infer
coherence from individually accepted panels.

## Accidental card-grid test

Record these six boolean signals. Three or more positive signals classify the
page as an `accidental-card-grid` and block `showcase-ready`:

1. `uniform_panel_containers` — nearly every panel uses the same border weight,
   corner radius, fill, and card treatment;
2. `axis_aligned_row_stack` — the page is primarily a sequence of horizontal
   rows and columns with no other grouping or transition language;
3. `repeated_rectangular_aspect_family` — setup, reaction, anchor, and ending
   repeatedly use interchangeable rectangular proportions;
4. `detached_or_accidentally_cropped_inset` — a small panel floats like a
   leftover fragment or cuts a face/body at an unmotivated point;
5. `non_narrative_dead_space` — conspicuous empty areas have no clear pause,
   lettering, subject isolation, or reading-path purpose;
6. `weak_anchor_or_final_emphasis` — the anchor or final beat has less visual
   force than ordinary setup panels.

When the threshold is reached, record the exact visual evidence instead of only
writing “too grid-like.” Fix the layout in a successor composition; do not
rewrite the accepted story or pretend a contract-fidelity pass failed.

## Structured record

Use [the example gate record](../templates/editorial-layout-gate.example.yaml)
as the shape. Copy it into the run directory and replace its all-zero hash,
path, dimensions, checks, signals, and evidence with observed values; the
template itself is never a passing review. Every record must bind the reviewed
final hash and dimensions, contain all eight checks and all six card-grid
signals, list blocking defects, and state both axes plus `showcase-ready` or
`internal-only` exposure.

The decision rules are executable:

- `editorial_layout: pass` requires all eight checks to pass, no blocking
  defect, and fewer than three card-grid signals;
- `editorial_layout: fail` requires at least one failed check and one blocking
  defect;
- `showcase-ready` requires both `contract_fidelity: pass` and
  `editorial_layout: pass`;
- every other resolved combination is `internal-only`;
- missing original-resolution or normal-size evidence is `not-verified` and
  therefore `internal-only`.

Only a later, separately reviewed final-page hash can replace a failed layout
record. Do not promote a plan, compositor capability, or intended irregular
geometry as evidence that the page passed.
