# Refurbish Runner

Use this compact route to restyle an existing PPTX while preserving its content. The standard runner is
the execution boundary: it chooses a route, validates fidelity, binds publication, and leaves visual judgment explicit.

## Non-skippable contract

- Treat the source PPTX as read-only content truth.
- Preserve slide ownership, visible content, notes, links, and editable semantics unless explicitly approved.
- Apply the requested DeckKit visibly. A light chrome-only change is not a completed refurbishment.
- Never preserve content by inserting source-slide screenshots or opaque page overlays.
- Let the compare gate publish the final PPTX. Do not copy or overwrite it afterward.

## Standard command

Check that the requested final path does not already exist, then run:

```bash
node <skill-root>/scripts/cli/refurbish/run.mjs \
  --deckkit <id> \
  --source source.pptx \
  --output out.pptx \
  --prompt-text "<original user request>" \
  --json
```

Add `--explicit` only for a user-selected non-production/non-default DeckKit, and `--review-policy` only
for an exact source-hash-bound finding. `--prompt-text` (or `--prompt-file`) archives the request for the
feedback gate. Compare parts render concurrently (`--compare-concurrency`, default 3). `--route fallback`
makes the saved plan, commands, gates, and references consistently describe fallback execution. `auto`
normally tries declared native support first; `native` never recovers through fallback.

Do not add `--contact-diff` for ordinary full-deck review. The mandatory compare is complete; the
compatibility alias is materialized from the same final evidence without another render.

## Agent-facing output

`--json` prints a compact `pptx-nova-refurbish-result/v1` document containing only the decision surface:

- status, run directory, output path, and human-review requirement;
- `agentSummary` with gate results and artifact pointers;
- `agentSummary.routeDecision`, `operationAudit`, and executable review/feedback/recovery commands;
- shadow Finding Analysis with `effectiveStatus=not-applied`;
- `artifactBytesByRole` and `agentContextRisk` for JSON files at least 128 KiB; tokens are not estimated;
- `performance` with total time, render share, top phases, budget, and Finding Analysis overhead;
- the terminal error when the run fails.

Compact Agent artifact paths are relative to `runDir`; published files outside it remain absolute. The
full report and `--json-full` retain compatibility fields and absolute paths.

After path preflight, the full report is saved as `<run-dir>/refurbish-run-summary.json`; an earlier error
cannot create it. Read it only for warnings, failures, unsupported regions, or diagnosis. Use
`--json-full` only when a consumer explicitly needs complete phase history.

Progress is archived to `<run-dir>/progress.jsonl` by default; `--progress-file` overrides it and
`none` disables it. Stderr carries only phase summaries. Read JSONL on failure or for performance.

## Progressive failure routing

Read `refurbish-plan.json.requiredReferences[]` after route selection. Those references are the only
additional workflow documents required for the current route:

- Native route with production/default readiness normally requires no deeper reference.
- Fallback loads the named Refurbish section from `../create/reference-create.md`.
- A readiness exception or missing DeckKit loads the named selection section from `../create/deckkit-mode.md`.
- Load `inspect-and-edit.md` only for a page-local repair with ambiguous selectors.
- Load `../review/export-and-check.md` only for a nonstandard export or compatibility investigation.

Do not preload broad references for a standard run; the runner already enforces isolation, collision
safety, capability probing, audit gates, comparison coverage, and publication binding.

`auto` retains the failed native report and recovers only for `UnsupportedComplexity`, or a valid failed
native report with passed audit/remap, no new high or worsened blocker, and only consistently counted new
`low-contrast-text` medium issues. Other failures stop; inspect `agentSummary.recovery.checks`.

## Canonical evidence flow

```text
plan and readiness -> capability probe and source inspect
  -> native skin or generated fallback patch -> vision-diff and refurbish-audit
  -> layout snapshots -> semantic diff -> one review-policy evaluation
  -> Finding Analysis shadow -> fidelity gate -> candidate preview
  -> one cached high-DPI comparison plus low-DPI Agent review -> publication gate
```

The high-DPI comparison is visual truth. Lower-DPI `refurbish-agent-review*.png` files reuse its page
cache without another conversion/render; do not rerender for aliases.

`finding-analysis.json` is calibration evidence. Never treat `effectiveStatus=not-applied` as a pass or
use it to weaken fidelity, comparison, publication, or human-review requirements.

## Review and delivery

A successful machine run returns `needs-human-review`. Scale the visual review to the deck size
instead of always opening every published byte:

- Always open the candidate contact sheet end to end; it is the candidate-only full-coverage overview.
- Open every Agent review part for the full overview; published high-DPI parts remain delivery evidence.
- Open actionable full-size previews and suspicious pages. `deltaStatus` distinguishes inherited
  (`unchanged`) from introduced/mixed findings; inherited findings need review but are not regressions.
- Open full high-DPI parts for actionable/suspicious slides, then spot-check the first and last parts.
  Do not load every high-DPI part after all Agent review parts have been inspected.
- When thumbnails are too small, render a focused high-resolution excerpt:

  ```bash
  node <skill-root>/scripts/cli/review/compare.mjs \
    --source source.pptx --candidate candidate.pptx \
    --run-dir . --kind refurbish --slides <n>[,<n>...] \
    --output focused-review.png --report focused-review.json --overwrite --json
  ```

  Run it from the run directory or use `focusedReviewCommand`; it reuses cached pages and does not
  replace published comparison evidence.

Confirm:

- the target DeckKit is visually apparent across the deck;
- the requested display/body font roles are actually applied: inspect the visible title and subtitle
  `fontFacts`, not only the theme fonts. For Cartesian, verify regular Playfair Display headlines and
  Inter supporting text. A successful skin report does not establish this visual identity;
- native chart recoloring preserves distinctions between series, categories and value bands; a pie
  or surface that collapses into one uniform fill needs a scoped palette repair and renewed evidence;
- titles, body text, tables, charts, diagrams, and assets remain legible;
- no source content disappeared or became a screenshot substitute;
- no new overlap, clipping, weak contrast, placeholder residue, or broken page chrome is visible.

Run `visualReviewCommand`; it supplies all 11 checks including `targetDeckkitApplied`. A captured prompt
also exposes `feedbackGateCommand`; write `skill-feedback.md` first. On failure use `recoveryCommand`,
which points at `<new-empty-run-dir>`; never retry in a failed/historical run.

If the final candidate contains ChartEx parts, xdoc preview/compare is not PowerPoint-native proof. Generate a candidate-bound `<skill-root>/scripts/cli/office/powerpoint-snapshot.nu --method pdf-render` report covering every ChartEx slide and pass it to
`<skill-root>/scripts/cli/review/finalize-evidence.mjs --mode refurbish --candidate <candidate> --powerpoint-native-render <report>` when the optional macOS + scriptable PowerPoint + Nushell + xdoc PDFium evidence route is available. With that route available, missing, stale, or incomplete coverage is a blocker. If any optional prerequisite is unavailable, the finalizer returns an explicit unverified warning without breaking the baseline workflow; do not claim PowerPoint-native verification, and stop if the user or delivery policy explicitly requires it.
Window capture is retained only after pdf-render failure and does not satisfy the ChartEx gate.

If extra repair passes ran after the standard runner, the canonical evidence still describes the earlier
candidate. Before delivery, regenerate `final-inspect.json`, re-run `<skill-root>/scripts/cli/review/finalize-evidence.mjs --mode refurbish --candidate <published-pptx>` with bound PowerPoint-native evidence when ChartEx exists, and verify SHA-256.
Refresh stale `visual_review.json`/content-audit paths; never hand-edit evidence JSON to swap paths.

Deliver only after compare and binding pass; list only key outputs, gates, evidence, and risks.
