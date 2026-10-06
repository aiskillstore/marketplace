---
name: executor-critique
description: Audit an initiative's authored artifacts against each other, repair what fails, and clear — or refuse to clear — the phase that produced them. Use when a phase's documents are drafted and need an independent audit before the next phase builds on them, or when a component's critique is not clear. One contract, one script, every component.
---

# Critique — the gate every authoring phase passes through

## Why this exists

Before this skill, two of eleven phases could reject a bad deliverable.
`plan-regression` and `review` dispatched independent auditors; the other
nine refused on file existence, on a count, or on a human nod. Architecture
and specification ran genuinely adversarial self-critiques — and their own
skills refused the word critic, because one agent grading its own work is
not review.

That gap had a concrete cost. **Upstream drift was structurally
undetectable.** No reviewer prompt in `executor-review` ever opened the
architecture store; its inputs were SPEC, PLAN, DEPENDENCY_MAP, LEDGER,
briefs, reports, verdicts and the diff. So an implementation that satisfied
every `R-nn` and every `C-nn` while violating the ARCH — adapters
importing each other, an ORM row crossing into policy, a seam renamed from
the IFCE — passed every gate in the system. There was no seat at which it
could be caught after planning.

This skill is that seat. It does not add judgment; it moves judgment off
the controller and into a dispatched agent whose report a script can read.

## The shape

Three roles, each a separate dispatch, **never one agent grading its own
work**:

```
AUDIT-<component>-R01  →  REPAIR-<component>-R01  →  AUDIT-<component>-R02
```

One auditor per component, fed the **whole set** — the defects this stage
exists for live *between* documents, so an auditor that reads one file
cannot see them. Repairs run per artifact. The re-auditor is always fresh.

**Three audits per component, then the human.** `R01`–`R03`. When `R03`
still fails, stop repairing and take the open findings to the human.

## The contract

1. **One audit per component, judged against the whole set.** The set is
   what makes seams visible.
2. **The checklist is fixed, numbered, and ordered cheap → expensive**, so
   contract-breaking defects surface before polish. Every check emits a row
   even when it finds nothing — a check with no row did not run.
3. **Severity is a consequence scale, never a fix-difficulty scale.** A
   one-word fix to a drifted name is still HIGH.
   - `HIGH` — the next phase fails, or builds the wrong thing
   - `MEDIUM` — likely rework, or a seam mismatch caught late
   - `LOW` — clarity only
   `PASS` means **zero HIGH and zero MEDIUM**. The gate checks the verdict
   against the auditor's own counts, so `verdict: PASS` beside `high: 2` is
   refused rather than believed.
4. **Findings carry stable IDs across rounds and default to NOT ADDRESSED**
   when absent from the repair log. An omission fails closed.
5. **Contracts are a finding class the repairer may not touch.** A defect in
   an upstream document is amended at its source with an
   `exec-ruling … initiative`, never papered over downstream.
6. **A waiver is the human's alone.** You may recommend one; you may never
   grant one. It is recorded twice — `waived` in the summary **and** an
   initiative ruling naming what was waived — and the gate refuses a waiver
   with an empty note or with no ruling behind it.
7. **Weakening is not addressing.** A finding closed by deleting a
   requirement, dropping a coverage claim, or loosening an exact value is
   NOT ADDRESSED, and the weakening is itself a new HIGH finding.

## Running a stage

Everything below is mechanical. Never hand-build an artifact path.

```bash
../scripts/exec-critique INIT_ID COMPONENT dir              # this component's dir
../scripts/exec-critique INIT_ID COMPONENT catalog          # which check catalog applies
../scripts/exec-critique INIT_ID COMPONENT init             # seed summary + dispatch log + rulings
../scripts/exec-critique INIT_ID COMPONENT audit 01         # the audit path to dispatch against
../scripts/exec-critique INIT_ID COMPONENT repair 01        # the repair-log path
../scripts/exec-critique INIT_ID COMPONENT latest           # newest audit, or exit 1
../scripts/exec-critique INIT_ID COMPONENT check            # cleared to gate? exit 1 on any gap
```

`check` is the gate. It refuses: no summary; no audit; an audit whose
`kind:` is not `critique`; a row that is neither `clean` nor `waived`; a
`clean` row whose newest audit is not `PASS`; a `PASS` that contradicts the
audit's own counts; a waiver with no note; a waiver with no ruling; a set
member with no row; a row whose artifact is gone; and a component with
nothing to clear.

**Round cap is enforced by the script.** `audit 04` is refused with a
message, not a shrug. A cap nobody counts is a suggestion, and a suggestion
is how a seventh round appears with nobody able to say when the loop started.

## The components

Every authoring phase has one. The mapping is data in `exec_phases`'
sibling registry (`_exec-lib.sh`, `exec_critique_components`), so adding a
component is a row, not a fork.

| Component | Gates | Catalog |
|---|---|---|
| `charter` | intake | charter |
| `discovery` | discovery | discovery |
| `architecture` | architecture | architecture |
| `design` | design | design |
| `specification` | specification | specification |
| `plans` | planning | plans (the plan-set regression contract, unchanged) |
| `code` | execution | code |
| `verification` | verification | verification |
| `handoff` | handoff | handoff |

`code` and `handoff` audit the **run axis** rather than a directory: their
set is the run itself, so their clearance carries one row per plan and the
gate requires the table to be non-empty.

`plans` resolves to the pre-existing `plan-regression/` home and reads the
same `summary.md` that `executor-plan-regression` writes. One gate, two
front doors — not two gates that can disagree.

## The catalogs

Each catalog is a fixed, numbered list. `../scripts/exec-critique INIT_ID
COMPONENT catalog` prints the key; the auditor reads the section below.

### `charter`

1. Goals are stated as outcomes, not as tasks.
2. Non-goals are explicit and are actually non-goals.
3. Every success criterion is checkable without reading the implementation.
4. Scope boundary holds: nothing in the initiative is outside it.
5. The problem statement would let a stranger recognize it.

### `discovery`

1. **Does the options document honestly represent the research?** Every
   option traceable to a cited finding; a finding that supports no option
   is a finding the document is hiding.
2. **Are the axes fair to every option?** An axis answered only for the
   recommended option is rigging, and rigging is HIGH.
3. Are the non-recommended options straw men? Name the strongest version of
   each.
4. Does the recommendation state what would falsify it?
5. Does anything cite prior art that the research never looked at?

### `architecture`

1. **Are the boundaries enforceable?** A boundary you cannot enforce is a
   diagram. Name the mechanism that holds it.
2. Does every IFCE cited by a plan exist, and does every quoted literal
   match byte-for-byte?
3. Does each ADR carry a falsifier specific enough to be wrong? "This is
   wrong if requirements change" is not a falsifier.
4. Is each decision labelled with its reversibility cost?
5. Do the components compose — hand two readers who will never read each
   other's work the halves, and ask whether they could each build theirs?

### `design`

1. Does the design state its state machine, or declare that it has none?
2. Are ordering and concurrency decisions explicit, including the ones that
   look safe because they are single-threaded today?
3. Are edge cases enumerated, or is there a stated reason none exist?
4. Are the testing seams named — the places a test can reach in?
5. Does the file decomposition avoid two components writing one file?

### `specification`

1. **Is every requirement verifiable?** A requirement no VRFY criterion can
   prove is a wish.
2. Does every requirement trace to a goal in the charter, and every goal to
   at least one requirement?
3. **Does any requirement contradict an active ADR?** A contradiction is a
   defect in one of them, and it is the one defect that survives every
   downstream gate unless it is caught here.
4. Is there placeholder prose — "handle edge cases", "add appropriate
   error handling"? Declared blocking, and blocking nothing mechanically
   until an auditor says so.
5. Does every risk have a mitigation that is a plan, not an intention?
6. Does the VRFY criteria count match the criteria rows?

### `plans`

The plan-set contract, unchanged: spec coverage, cross-plan
`Assumes`/`Produces` closure, interface fidelity, ordering, constraint
propagation, file-map collisions, vocabulary consistency, plan lint,
skipped-phase honesty. See `executor-plan-regression/SKILL.md`.

### `code`

This is the **upstream-drift seat** — the checks that had nowhere to live.

1. **Does the branch obey the ARCH's boundaries?** The architecture store is
   a required input here, not an optional one. Adapters importing each
   other, a domain type crossing into a transport type, a dependency
   pointing the wrong way: each is HIGH.
2. **Do the IFCE signatures match the implementation byte-for-byte?** A
   renamed seam is a HIGH; a seam that drifted in meaning is worse.
3. Is the DSGN still true of the code, or did implementation quietly
   replace a design decision?
4. Do the ADRs still describe what was built?
5. Plus the whole-branch coherence checks `executor-review` already runs.

### `verification`

1. Does every VRFY criterion carry evidence that was **observed**, not
   expected?
2. Did any evidence run change code, tests, or config to get green? Then the
   criterion was not proven — it was edited.
3. Is every `NOT-RUN` explained rather than upgraded by inference?
4. Does any evidence predate the commit it claims to describe?

### `handoff`

1. Every executed plan has a run row and a workspace — a plan that merged
   commits with no row is CRITICAL.
2. The run registry matches reality: no row says `running` for a plan that
   finished.
3. No "To be filled" placeholder survived into the VRFY outcomes.
4. Every superseded ADR is linked from its successor.
5. The secret scan is clean and the suite is green **on the current tree**.

## What this skill never does

- **Never lets the controller audit its own work.** If you are the
  controller and the component is not clear, the move is to dispatch the
  audit or present the artifact to the human — never to clear the phase by
  another route.
- **Never marks a component clean from a repair log alone.** The gate
  requires the latest audit round to say `PASS`.
- **Never writes an audit under `docs/executor/`** or inside a `Pnn/`
  workspace. The component's own `critique/` dir is the only legal home.

## Self-Critique

Before you report the stage clear, check each of these yourself:

1. **Did every check in the catalog emit a row?** A check with no row did
   not run.
2. **Did I re-audit, or did I read the repair log and believe it?** Verify a
   `FIXED` claim against the artifact text, not against the log.
3. **Did any repair weaken the artifact to pass?** Grep the diff for deleted
   requirements, dropped claims, loosened values. Each is a new HIGH.
4. **Is every finding in this round traceable to a quote?** A finding you
   cannot quote is not a finding.
5. **Did I recommend a waiver I was not granted?** That is not a waiver.
6. **Is the summary row describing the set that is actually on disk?**

## Verification

```bash
bash ../scripts/exec-critique INIT_ID COMPONENT check
```

Exit 0 means every artifact is `clean` or human-`waived` with a report
behind it. Exit 1 prints one `CRITIQUE:` line per gap. Exit 2 is a
derivation error — a bad argument or an unknown component.

Before reporting the stage clear, run it. A stage you did not check is a
stage you did not clear.
