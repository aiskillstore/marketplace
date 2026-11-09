# Create Runner

Use this reference for the standard DeckKit-based new-deck workflow. It contains the shortest safe
path from prepared content to a machine-validated candidate. Load deeper creation references only for
the conditions listed below.

## Inputs

The standard runner requires:

- `content.json` matching the selected DeckKit content contract;
- `deck_lock.json` binding the output path, run directory, slide plan, assumptions, and a valid
  `artDirection.mode` (`persuade`, `read`, `operate`, or `experience`);
- an output `.pptx` path that does not already exist unless replacement was explicitly requested;
- an optional `assets_manifest.json` when the content uses registered external assets.
- an optional `choreography.json` for native animation/Morph operations; see [animations](../content/animations.md#standard-create-choreography).

If these inputs are not prepared yet:

- read `references/create/design-quality.md` for every new deck: audience, art direction,
  rendered example selection and the design floor, including one-sentence Express;
- read `references/create/create-express.md` for a simple/default deck;
- read `references/create/deckkit-mode.md` only when DeckKit selection or content slots are unresolved;
- read `references/create/create-studio.md` plus `references/create/design-lock-and-assets.md` for an explicitly
  high-control Studio task;
- read `references/create/narrative-quality.md` for persuasive decks with six or more slides.

Do not load all creation references by default.

## Standard command

```bash
node <skill-root>/scripts/cli/create/run.mjs \
  --deckkit <id> \
  --content <run-dir>/content.json \
  --lock <run-dir>/deck_lock.json \
  --output output.pptx \
  --run-dir <run-dir> \
  --json
```

Add `--assets <run-dir>/assets_manifest.json` only when the deck uses registered assets. Add
`--overwrite` only when replacing the final path was explicitly intended.

The runner owns this sequence:

```text
capability probe
-> validate content
-> build patch
-> compose optional choreography (retain deckkit.patch.json)
-> check lock
-> dry-run
-> apply candidate
-> full-package visual + semantic vision check
-> one canonical Create PDF/PNG render
-> actual Agent/human visual review of the exact candidate
-> recorded slide-specific design judgment (design_review.json)
-> finalize with identity checks and atomic publish
```

The initial run never marks visual review complete and does not write the final output.

The runner fails closed on semantic evidence: dry-run and apply must each
return an explicit empty `semanticIssues[]`; vision must return a consistent
`semanticSummary`/`semanticIssues[]` pair with `passed=true`, zero issues, and
at least 82 source rules / 81 normalized rules. Missing fields indicate an
incompatible xdoc build and stop publication rather than silently degrading the gate.

## Agent-facing output

`--json` prints a compact `pptx-nova-create-result/v1` document containing:

- status, run directory, output path, and review requirement;
- compact gate and artifact pointers in `agentSummary`;
- explicit dry-run/apply semantic issue counts plus vision semantic evidence,
  consistency, pass state, and SDK rule inventory in `agentSummary.gates`;
- phase and preview performance in `performance`;
- exact conditional documentation routes in `requiredReferences[]`;
- the terminal error when execution stops.

The complete `pptx-nova-create-run/v1` report is saved as
`<run-dir>/create-run-summary.json` after path preflight succeeds. Read it only when the compact result
reports a failure, warning, budget exception, or a fact needed for diagnosis. Use `--json-full` only
for debugging or compatibility with a caller that explicitly needs the complete report on stdout.

Progress is emitted separately. JSONL progress contains phase names, executable names, argument
counts, elapsed time, and compact status fields; complete commands remain in the full report.

## Performance contract

The standard Create route renders the final candidate once through `preview-render`. Its performance
summary records:

- total and measured phase time;
- render time and share;
- preview render invocation and slide counts;
- estimated rendered pixels;
- the five slowest phases;
- baseline invocation and pixel-budget results.

Do not add a source/candidate compare merely to make Create resemble Translation or Refurbish. During
repair loops, render changed slides only when a separate scoped review is needed; keep one final
full-deck preview as the delivery evidence.

## Failure routing

Follow `requiredReferences[]` from the compact result or full summary. The runner requests animation
case review for `animation-corpus`, and narrative review for ordinary decks with at least six slides.
Other preparation-time routes remain explicit:

- invalid DeckKit content or unresolved slots: `references/create/deckkit-mode.md`;
- unclear express content construction: `references/create/create-express.md`;
- high-control asset/layout decisions: `references/create/create-studio.md` and
  `references/create/design-lock-and-assets.md`;
- specialized charts, tables, formulas, animations, or data binding: load only the matching reference.

Do not retry past a failed gate with stale `candidate.pptx`. Repair the authoritative input, create a
new candidate, and rerun the runner in a new or safely reusable current run directory.

## Delivery boundary

With a runtime that discloses `visualModes.values` including `create`, machine success produces
`status=needs-visual-review`. Open `visual-evidence/review.html` (an index of the exact canonical PNGs)
or inspect all PNGs directly. Review narrative and brand quality as applicable. Record the actual
design judgment following [Design quality](design-quality.md), then record the actual
review using `node <skill-root>/scripts/cli/review/visual-review.mjs --mode create --candidate <run-dir>/candidate.pptx
--manifest <run-dir>/visual-evidence/manifest.json --previews <run-dir>/visual-evidence
--design-review <run-dir>/design_review.json --slides-reviewed <count>` and the required `--check` values from that helper's help. Record only
checks actually performed; the helper validates the record, it does not understand images.

Then rerun the original Create command with `--finalize --visual-review <run-dir>/visual_review.json`.
Finalization checks the review mode against the bound `deck_lock.artDirection.mode`; the locked
mode controls the signature-moment requirement. A missing or invalid locked mode requires a fresh
candidate run, as described in [Design quality](design-quality.md).
This validates frozen inputs, candidate bytes, canonical PDF/PNG bytes, full coverage and the review
binding, then publishes without rebuilding or rendering. Successful finalization reports
`status=delivered`, `deliveryReady=true`. Missing, failed or stale review evidence blocks publication.
Changed content, lock, assets manifest, choreography, original DeckKit patch, composed patch or machine
evidence requires a fresh run and review. Repeat `--choreography` when finalizing an animated candidate.

Older runtimes retain diagnostic preview and `needs-human-review`; they cannot automatically finalize
through this interface. Upgrade xdoc, or follow the legacy canonical gate and its actual human
confirmation route. Never reinterpret a candidate-only confirmation result as Create success.

Preserve the summary, candidate, content/lock, patch/sidecars, machine reports, `create-binding.json`,
canonical manifest/PDF/PNGs, `design_review.json` and `visual_review.json`. Do not compare a candidate to itself to obtain
a regression verdict. Native-object corpus tasks should follow the one-page smoke and preservation
guidance in `../edit/inspect-and-edit.md` before expanding the deck.
