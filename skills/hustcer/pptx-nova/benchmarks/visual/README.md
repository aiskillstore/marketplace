# pptx-nova Visual Benchmarks

This directory holds DeckKit-first visual regression cases. It does not store
generated PPTX files, full patches, full vision reports, or per-slide PNG images.
It does store reviewed low-severity vision baselines so every DeckKit can
separate expected style noise from newly introduced visual issues.

Case `review.md` files record the dated acceptance run and its original scope.
Their recorded runtime, counts and candidate/default status are historical evidence;
current selection eligibility comes from the [DeckKit catalog](../../assets/deckkits/catalog.json) and readiness,
and a new delivery still requires evidence bound to its own candidate.

## Layout

```text
benchmarks/visual/
├── index.json
├── cases/
│   ├── <deckkit>/               # one directory per DeckKit id in index.json
│   └── consulting-dark/
│       ├── golden-roadshow/
│       │   ├── expected.json
│       │   └── review.md
│       ├── stress-density/
│       │   ├── content.json
│       │   ├── expected.json
│       │   └── review.md
│       └── mixed-language/
│           ├── content.json
│           ├── expected.json
│           └── review.md
└── baselines/
    └── <deckkit>.<case>.vision-baseline.json
```

Golden cases reference existing DeckKit example content through `contentPath`
(`../../assets/deckkits/<id>/examples/content.json`) to avoid duplicating
large JSON fixtures; stress and mixed-language cases ship their own immutable
`content.json` beside `expected.json`.

## Minimum Gate

For each case:

1. Run shared `validateContent` schema and page-type fit diagnostics against `contentPath`.
2. Build patch with the DeckKit example build entry.
3. Apply the patch, run `vision-check`, classify low issues against the DeckKit
   visual policy and reviewed baseline, and render PNG preview artifacts.
4. Only promote a DeckKit after the repo-indexed benchmark cases pass. Golden is
   the minimum committed case for new DeckKits; stress and mixed-language inputs
   must still be reviewed, but may live in `.tmp` unless they are useful as
   long-term visual regression fixtures.

## Low-Severity Baseline Lifecycle

`vision-check` low findings are normalized into canonical Nova issues before
they are summarized. The canonical identity uses stable fields such as severity,
family, slide index, shape role/name, message key, and normalized metrics. It
does not rely on transient object ids or raw floating-point geometry.

Each low issue is assigned to one of these buckets:

- `styleAllowed`: allowed by the DeckKit catalog `qualityProfile`, such as
  intentional compact typography.
- `baselineKnown`: present in the reviewed case baseline.
- `new`: not allowed by style policy and not present in the baseline.
- `changed`: same stable issue identity as the baseline but with changed
  normalized metrics.
- `resolved`: present in the baseline but absent from the current run.

High and medium findings remain hard gates. Low findings are review gates:
`new` and `changed` low findings do not fail the benchmark by default, but they
block delivery/default readiness and production/default promotion until reviewed.

Accept the current low findings as the reviewed baseline with:

```bash
node <skill-root>/scripts/cli/deckkits/benchmark.mjs \
  --deckkit consulting-dark \
  --all \
  --update-baseline \
  --clean
```

The command writes `benchmarks/visual/baselines/*.vision-baseline.json` and the
same run summary is recomputed against the accepted baseline. Future benchmark
runs then surface only `new` or `changed` low findings for human review.

## Current CLI

```bash
node <skill-root>/scripts/cli/deckkits/benchmark.mjs \
  --deckkit consulting-dark \
  --case golden-roadshow \
  --repeat 3 \
  --clean
```

The current CLI runs validate/build, xdoc dry-run, real apply, `vision-check`,
canonical low bucketing, PNG preview, and contact-sheet gates. It writes
`patch.json`, `deck.pptx`, `dry-run.json`, `apply.json`, `vision.json`,
`convert-report.json`, `previews/`, `contact-sheet.png`, `timing.json`, and
`summary.json` to `.tmp/pptx-nova-visual/<deckkit>/<case>/`.

After benchmark output exists, run the readiness audit:

```bash
node <skill-root>/scripts/cli/deckkits/readiness.mjs \
  --deckkit consulting-dark \
  --target candidate \
  --benchmark-mode required-live
```

In `required-live` mode the audit reads `catalog.json`, `index.json`, and the
generated `summary.json` files. Golden is required. Any additional case registered for the DeckKit in
`index.json` is also gated, so existing stress and mixed-language fixtures keep
their coverage while new DeckKits can commit only golden. It reports whether the
DeckKit is ready for candidate, delivery, and default use. Delivery/default
should remain blocked when PNG preview or contact-sheet artifacts are skipped,
missing, empty, or out of sync with the slide count, or when
`vision.lowBuckets.new` / `vision.lowBuckets.changed` is non-zero.

To write machine-verifiable benchmark metadata back to `catalog.json`, run:

```bash
node <skill-root>/scripts/cli/deckkits/catalog-update.mjs \
  --deckkit consulting-dark \
  --write
```

This updates `quality.lastBenchmark`, aggregate `quality.vision`, and
`quality.benchmark` from `.tmp/pptx-nova-visual/<deckkit>/<case>/summary.json`.
Aggregate vision metadata includes low buckets across all repo-indexed gated
cases. It does not change readiness by default and does not invent manual PNG
review data.

Manual PNG review remains a separate human step:

1. Open each case `contact-sheet.png` and inspect the per-slide PNGs under
   `.tmp/pptx-nova-visual/consulting-dark/<case>/previews/`.
2. Fill the corresponding `review.md` with last reviewed date, reviewer, result,
   checked manual items, and notes.
3. Count hard visual defects. Only after this review is complete, write the
   manual count:

```bash
node <skill-root>/scripts/cli/deckkits/catalog-update.mjs \
  --deckkit consulting-dark \
  --manual-hard-defects 0 \
  --write
```

Promotion requires an explicit manual review confirmation:

```bash
node <skill-root>/scripts/cli/deckkits/catalog-update.mjs \
  --deckkit consulting-dark \
  --manual-hard-defects 0 \
  --readiness production \
  --confirm-manual-png-review \
  --write
```

Do not run the promotion command until all repo-indexed PNG reviews are complete
and any non-committed stress/mixed-language reviews required by the DeckKit
creation workflow have been recorded in `.tmp`.

Current consulting-dark cases:

- `golden-roadshow` covers all ten 2.0 roles with English synthetic content.
- `stress-density` exercises maximum item counts, a nine-by-five native table,
  and native chart negative, zero and tiny values without blocking fit warnings.
- `mixed-language` verifies Chinese/English regular and bold text in a synthetic
  community-library scenario. The migration report records the separate complete
  Chinese, alternate-layout and sparse probes. Those acceptance records used
  candidate readiness; the current catalog registers consulting-dark as production.
