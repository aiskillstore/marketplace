---
name: executor-planning
description: Use when a spec has passed its phase gate and must become implementable tasks before any code is written, or when an existing plan must be split, extended, or repaired so it can be dispatched.
---

# Planning

Turn `INIT-NNNN-SPEC-nn` into `INIT-NNNN-Pnn`: a document whose every task
carries an ID, exact file paths, exact signatures, verbatim test
expectations, and a dependency map. Planning ends when the human picks an
execution mode.

**Write for an engineer with zero context for this codebase.** Assume a
skilled developer who knows almost nothing about our toolset or problem
domain. Document which files they touch, what each change must do, what
tests prove it, and how to run those tests — the WHAT and the WHERE are
yours to pin down. The HOW inside those files — local names, internal
structure, error-handling style — is the implementer's own decision inside
that contract. DRY. YAGNI. TDD. Frequent commits.

That framing is not politeness. Under `executor-execution` each task is
dispatched to a **fresh subagent that reads only its own brief** — the task's
verbatim text plus an identity header. Anything you leave implicit is
unavailable to the person implementing it — and any implementation you
write out in full is a design decision they no longer make, bugs included.

## Before You Write Anything

| Read | Why |
|---|---|
| `../executor/SKILL.md` | ID grammar, citation rule, phase gates, rulings policy |
| `../executor/references/frontmatter.md` | plan frontmatter is contract, not style |
| `../executor/references/layout.md` | plans live in `plans/`, nothing else |
| `../executor/references/indexes.md` | the two index updates planning owns |
| The spec `INIT-NNNN-SPEC-nn` | the plan argues from it; you copy from it |
| Its `INIT-NNNN-IFCE-nn` | every signature you write comes from here |
| The ADRs the spec lists in `decisions:` | a plan that reopens a decided question is a defect |

**Prerequisites.** The spec's phase gate passed (`status: active`, phase log
row for `specification` has a gate date). No approved spec → stop; route to
`executor-spec`. No interface document and the work spans components → stop;
route to `executor-architecture`. Planning does not invent structure.

**Brainstorm the decomposition first — required.** `exec-initiative phase
<INIT> planning entered` refuses until a decided brainstorm session feeds
planning: an `executor-brainstorm` decision session (`feeds: [planning]`,
`status: active`) that compared at least three ways to split the spec into
plans and tasks — by component, by user-visible slice, by risk-first
spike — and recorded the human's pick. The design session's `## Handoff`
(MVP slice and increments) is its main input. The plan set follows the
decided split; a plan that splits differently cites a new session.

**The citation rule is absolute.** Every ID in a plan begins with this
plan's own initiative. A task needing something from `INIT-0002` states the
requirement in its own words; the dependency lives only in the charter /
initiative INDEX `depends_on`.

### Citing spec requirements and constraints

A spec's individual requirements and global constraints are addressable IDs.
Use them; never write prose like "requirement 7".

| Token | Means |
|---|---|
| `INIT-0004-SPEC-01-R07` | requirement 7 of that spec |
| `INIT-0004-SPEC-01-C03` | global constraint 3 of that spec |

These never collide with review rounds: a round ID always carries a `-T<nn>-`
segment before its `-R<nn>` (`INIT-0004-P01-T03-R02`), while a requirement
hangs off `-SPEC-<nn>-`. Requirement IDs are what make the spec-coverage
check mechanical instead of impressionistic.

## Step 1 — Allocate the plan ID

Plans are numbered per-initiative from `01`: `INIT-0004-P01`,
`INIT-0004-P02`. Allocate by **listing `plans/` immediately before writing**
and taking the next free number — or let `exec-id` do both:

```bash
../executor/scripts/exec-initiative resolve INIT-0004        # → the initiative folder
ls "$(../executor/scripts/exec-initiative resolve INIT-0004)/plans/"
../executor/scripts/exec-id INIT-0004 P                      # → INIT-0004-P01
```

`exec-id` handles the plan kind correctly: `P` is the one kind whose grammar
has no separator, so it prints `INIT-0004-P01`, never `INIT-0004-P-01`. Its
scan covers file contents as well as basenames, so an existing
`INIT-0004-P01` reserves its number even when the file sits in the wrong
directory.

On a collision — another agent took your number while you were writing —
take the next one, write your file, and note the race in the initiative's
`INDEX.md`. Never overwrite.

File path: `<initiative>/plans/INIT-0004-P01-<topic-slug>.md`. The slug is
cosmetic; every script resolves through the `id:` frontmatter field, so
renaming the file never orphans its workspace.

## Step 2 — One plan or several

Split into `P01`, `P02`, … when the spec covers subsystems that can ship
independently. **Each plan must produce working, testable software on its
own** — a plan that leaves the tree broken until its successor lands is not
a plan, it is half of one.

| Split when | Keep as one plan when |
|---|---|
| Two subsystems with a stable seam between them | Tasks share a file and interleave |
| The second half depends on operational feedback from the first | The split is only "the plan feels long" |
| Different reviewers own the halves | Neither half is independently testable |

When you split, the **first** plan carries an explicit ordering statement,
and every later plan carries an `## Assumes` section naming exactly what it
takes from its predecessors, **with exact signatures**:

```markdown
## Assumes

`INIT-0004-P01` has landed and provides:

- `placeCell(tenantId: str, weight: int) -> CellId` in `src/cells/placement.py`
- `class CellId(NamedTuple): region: str; index: int` in `src/cells/types.py`

If either signature differs from the above when this plan starts, stop and
repair the plan — do not adapt around it.
```

Ordering statement in `P01`: `Execution order: P01 → P02 → P03. P02 does not
start until P01's final review is clean.`

Also split the spec's requirements across plans explicitly — each plan names
the requirement IDs it covers (`Covers: R01-R06, R11`), so no requirement
falls into the gap between two plans.

Cross-plan references are IDs inside the same initiative, so they are legal.
References to another *initiative's* plan are not.

## Step 3 — Map the files before defining tasks

This is where decomposition gets locked in. Write the file map first; tasks
fall out of it.

- Design units with clear boundaries and well-defined interfaces. **One
  clear responsibility per file.**
- You reason best about code you can hold in context at once, and edits are
  more reliable in focused files. **Prefer smaller, focused files** over
  large ones that do too much.
- **Files that change together live together.** Split by responsibility, not
  by technical layer.
- **In existing codebases, follow established patterns.** If the codebase
  uses large files, do not unilaterally restructure — but if a file you are
  modifying has grown unwieldy, including a split in the plan is reasonable.

Each task then produces self-contained changes that make sense
independently.

## Step 4 — Right-size the tasks

**A task is the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate.**

| Rule | Consequence |
|---|---|
| Fold setup, configuration, scaffolding, and documentation into the task whose deliverable needs them | a "set up the config" task has nothing a reviewer can reject |
| Split only where a reviewer could meaningfully reject one task while approving its neighbour | otherwise the split adds two dispatches and no signal |
| Every task ends with an independently testable deliverable | the review gate has something to test |
| Number contiguously from 1 within the plan | `exec-brief PLAN N` finds a task by its heading ordinal |

Tasks are `T01`…`Tnn` **per plan**. `P02` starts again at `T01`; the plan
segment keeps the IDs distinct.

## Step 5 — Write the plan

### Document order is load-bearing

`exec-brief` extracts a task by scanning from its `Task N` heading to the
**next `Task` heading or end of file**. Verified: a `## Dependency Map`
section placed after the last task is copied verbatim into that task's
brief, and the implementer reads it as their requirements.

**Every plan-level section comes before the first task heading. After the
first task heading there are only tasks.**

Section order, top to bottom:

1. frontmatter
2. header (goal, architecture, tech stack, spec, covers)
3. Global Constraints
4. Interfaces
5. Assumes — `P02` and later only
6. File Map
7. Dependency Map
8. `## Tasks`, then `### Task 1` … `### Task N` and nothing else

### Frontmatter

Common fields plus the plan block, per the frontmatter contract. Timestamps
are real UTC from an executed command, never invented.

```yaml
---
id: INIT-0004-P01
initiative: INIT-0004
kind: plan
title: Cell router
status: draft
created_at: 2026-09-01T14:55:52Z
updated_at: 2026-09-01T14:55:52Z
supersedes: null
superseded_by: null
spec: INIT-0004-SPEC-01
interfaces: [INIT-0004-IFCE-01]
tasks: 7
execution_mode: null
sequential: false
workspace: .executor/INIT-0004/P01
---
```

| Field | Rule |
|---|---|
| `id` | matches the filename's ID segment; scripts resolve the workspace from it |
| `spec` | the one spec this plan argues from; copied into every brief header |
| `interfaces` | every IFCE document a task's signatures came from |
| `tasks` | the actual count of `### Task` headings — fix it when you add one |
| `execution_mode` | `null` until the human picks; then `subagent` or `inline` |
| `workspace` | `.executor/<INIT>/<Pnn>` — must equal what `exec-workspace` computes from `id`, or the field is a lie |
| `status` | `draft` while writing, `active` when the human picks a mode |

### Header

```markdown
# Cell router — implementation plan

> **For agentic workers:** dispatch this plan with `executor-execution`.
> Steps use checkbox (`- [ ]`) syntax for tracking. Do not begin Task 1
> before the preflight scan is written.

**Goal:** [one sentence describing what this builds]

**Architecture:** [2-3 sentences about the approach, pointing at
`INIT-0004-ARCH-01`]

**Tech Stack:** [key technologies and libraries, with version floors]

**Spec:** `INIT-0004-SPEC-01` — `specs/INIT-0004-SPEC-01-cell-placement.md`

**Covers:** `R01`-`R06`, `R11` of `INIT-0004-SPEC-01`
```

The spec travels with the plan because the plan argues from it; a reviewer
reads both.

### Global Constraints

Project-wide requirements — version floors, dependency limits, naming and
copy rules, platform requirements — one line each, **exact values copied
verbatim from the spec**, each tagged with its constraint ID. Never
paraphrased, never summarised.

```markdown
## Global Constraints

Every task's requirements implicitly include this block.

- `C01` — Python >= 3.11; no new runtime dependencies beyond `pydantic>=2.6`.
- `C02` — All public functions carry type annotations; `mypy --strict` passes.
- `C03` — User-visible strings use the exact copy in `INIT-0004-SPEC-01 §4`.
- `C04` — No network calls in unit tests.
```

IDs are the spec's own (`INIT-0004-SPEC-01-C03`, shortened to `C03` inside
this block since the plan names its spec once, at the top). A reviewer
rejecting on a constraint cites the ID, not a quotation.

**The leak you must close:** a brief carries only the task's own text, so
this block does not travel with it. Any constraint a task can violate inside
its own code — a version it pins, a string it writes, a dependency it adds —
is **also stated verbatim inside that task's steps**, with its ID. The block
stays for the reviewer and the human; the duplicate is for the implementer
who sees nothing else.

### Interfaces

Name the IFCE document, then reproduce the signatures this plan touches.

```markdown
## Interfaces

Source of truth: `INIT-0004-IFCE-01` —
`architecture/INIT-0004-IFCE-01-service-contracts.md`. Signatures below are
copied verbatim. If the code diverges from them, the code is wrong.

- `placeCell(tenantId: str, weight: int) -> CellId`
- `evictCell(cell: CellId, reason: EvictReason) -> None`
- `class EvictReason(StrEnum): DRAIN; OVERLOAD; MANUAL`
```

**A signature that does not exist yet is an architecture gap.** Stop, go back
to `executor-architecture`, get the interface defined, then resume. Do not
invent a signature in a plan — an invented signature is a decision made
without an ADR, discovered at review time by two tasks that built
incompatible halves of one seam.

### Dependency Map

One row per pair of tasks sharing a file or an interface. This is the input
to `executor-execution`'s preflight scan; produce it here rather than making
the controller derive it from prose.

```markdown
## Dependency Map

| Producer | Consumer | Shared surface | What flows across it |
|---|---|---|---|
| T02 | T04 | `src/cells/types.py` | `CellId` NamedTuple definition |
| T02 | T05 | `src/cells/types.py` | `CellId` NamedTuple definition |
| T03 | T05 | `placeCell()` | signature and `CellError` raise contract |
| T04 | T06 | `src/cells/router.py` | `Router.dispatch()` added, T06 extends it |

No pair outside this table shares a file or a symbol.
```

| Rule | Why |
|---|---|
| **Producer is ordered before consumer** — always | a consumer dispatched first has nothing to import |
| One row per *pair*, not per file | the controller needs the direction, not an inventory |
| Two tasks writing the same file appear here even with no symbol shared | that is a merge conflict, and the controller must serialise them |
| The closing "no pair outside this table" line is required | it turns an omission into a falsifiable claim |

If the table shows a cycle — T04 needs T06 and T06 needs T04 — the task
boundary is wrong. Merge them or move the shared symbol into an earlier
task. Do not ship a cyclic plan and let the controller discover it.

### Task structure

Heading format, exactly:

```markdown
### Task 3: Cell placement scoring — `INIT-0004-P01-T03`
```

| Constraint | Failure if broken |
|---|---|
| Heading starts `### Task <N>:` with the literal word `Task` and the ordinal | `exec-brief PLAN N` cannot find the task |
| The ID matches `INIT-NNNN-Pnn-Tnn` and sits on the heading line | `exec-brief` **errors out**; the plan cannot be executed |
| The `Tnn` digits equal the heading ordinal, zero-padded | brief, report, diff, and verdict filenames name a different task than the one dispatched |
| Task IDs are unique within the plan | two tasks overwrite one brief |

Full task shape:

````markdown
### Task 3: Cell placement scoring — `INIT-0004-P01-T03`

**Implements:** `INIT-0004-SPEC-01-R04`, `INIT-0004-SPEC-01-R05`
**Constraints restated here:** `C01` (Python >= 3.11), `C02` (`mypy --strict`)
**Depends on:** `INIT-0004-P01-T02` — or `none` for the first task

**Files:**
- Create: `src/cells/scoring.py`
- Modify: `src/cells/placement.py:88-104`
- Test: `tests/cells/test_scoring.py`

**Interfaces:**
- Consumes: `class CellId(NamedTuple): region: str; index: int` from
  `src/cells/types.py` (Task 2)
- Produces: `score(cell: CellId, load: int) -> float` — returns 0.0..1.0,
  raises `ValueError` when `load < 0`. Task 5 calls this.

**Requirements:** scores are pure functions of the arguments — no clock, no
I/O (`INIT-0004-SPEC-01-R05`).

- [ ] **Step 1: Write the failing test**

```python
def test_score_is_zero_for_unloaded_cell():
    assert score(CellId("eu-west", 3), 0) == 0.0

def test_score_rejects_negative_load():
    with pytest.raises(ValueError):
        score(CellId("eu-west", 3), -1)
```

- [ ] **Step 2: Run the test and see it fail**

Run: `pytest tests/cells/test_scoring.py -v`
Expected: FAIL — `NameError: name 'score' is not defined`

- [ ] **Step 3: Write the minimal implementation**

Sketch — the `Produces` signature, the `ValueError` contract, and purity are
what bind; the body is one workable shape, not authority:

```python
def score(cell: CellId, load: int) -> float:
    if load < 0:
        raise ValueError(f"load must be non-negative, got {load}")
    return min(load / CELL_CAPACITY, 1.0)
```

- [ ] **Step 4: Run the test and see it pass**

Run: `pytest tests/cells/test_scoring.py -v`
Expected: PASS — 2 passed

- [ ] **Step 5: Refactor (behavior unchanged, tests stay green)**

Check the implementation against the rest of `src/cells/` for duplication
or naming drift. Extract nothing unless the task needs it — this task's
implementation is already minimal. Re-run:

Run: `pytest tests/cells/test_scoring.py -v`
Expected: PASS — 2 passed

- [ ] **Step 6: Commit**
````

**Steps are bite-sized — one action, 2-5 minutes each — in TDD rhythm:**
write the failing test → run it and see it fail → minimal implementation →
run it and see it pass → refactor → commit. Every run step names the exact
command and the exact expected output.

**A task body is a contract, and its contents bind at two strengths.**

| Content | Status in the brief |
|---|---|
| `**Files:**` create/modify/test lists | contract — verbatim; the implementer writes only these |
| `Consumes:`/`Produces:` signatures and error contracts | contract — verbatim |
| Invariants, exact values, acceptance criteria | contract — verbatim |
| Test code | contract — verbatim, in full; tests are the acceptance contract |
| `**Implements:**` requirement IDs | contract — what the reviewer grades against |
| Implementation code | sketch — reference only, never authority |

**Test code stays verbatim.** Test cases are the acceptance contract; they
may be full fenced blocks, and the implementer copies them exactly.

**Implementation code is limited to seams.** Signatures, protocol and DDL
definitions, interface definitions, and short sketches of the non-obvious
branch earn their place — labeled as sketches, like Step 3 above. A fenced
implementation-language block over ~40 lines does not belong in a plan; it
belongs in an IFCE or design doc, or nowhere.

**A plan whose tasks carry complete implementations is over-specified.** It
pre-spends the implementer's design decisions, reduces the dispatch to a
transcription job, and copies the plan author's bugs into the diff
verbatim. Model selection at dispatch routes by task complexity, not by how
much code the plan already contains — a code-complete plan is not a cheaper
task, it is a defective one. If a task seems to need its whole body written
out, the design belongs upstream (IFCE, ADR, or a thicker `Consumes:`/
`Produces:` contract) — not in the task body.

**The TDD rhythm is not optional for tasks producing or changing behavior.**
The TDD Iron Law binds every implementer; the plan is where it becomes
concrete. A task with genuinely no test cycle (pure configuration, generated
code) needs its reason stated in the task's Requirements line — an unstated
exception is a plan defect the reviewer will flag.

**The RED step must name the expected failure.** Write the exact failure
the test should produce before the implementation exists — `FAIL:
NameError: name 'score' is not defined` is a correct RED; `FAIL` alone is
not. The run step then verifies the *observed* failure against it. This is
what catches fake TDD at the source: an implementer who writes test and
code together cannot state the expected failure, because they never
watched it.

**Every task that produces behavior gets a REFACTOR step** between the
green run and the commit: remove duplication, improve names, re-run the
tests. Plans that end at green teach implementers that green is the finish
line — it is not; clean is.

**Test quality is planned, not hoped for.** Tests in the plan follow the
two-principle doctrine in
[`../executor/references/test-quality.md`](../executor/references/test-quality.md):
every test names the break it catches, and every test exercises the real
thing. Concretely, when writing the test code blocks:

- Derive expected values as **literals or hand-checked fixtures** — never
  by calling the function under test (a mirror assertion passes no matter
  what the code does).
- Assert **behavior, not text**: run the script and check its output, do
  not grep its source.
- Keep **your code, not the framework's** under test — the route you
  register, not that the router dispatches.
- Mock only the slow or external dependency, **mirror its data structure
  completely**, and let the mock earn no assertions.
- Cover the **negative and boundary** paths the requirement names —
  rejection cases, off-by-one boundaries, error responses — not only the
  happy path.

**The Interfaces block is how an implementer who sees only their own task
learns what neighbours expose.** Consumes lists exact signatures of what it
uses from earlier tasks; Produces lists exact names, parameter types, return
types, and error behaviour later tasks rely on. Every Produces entry that a
later task consumes appears in the Dependency Map, and vice versa.

**The Implements line is what the reviewer grades against.** A task
implementing no requirement is scope you invented; a requirement implemented
by no task is a coverage gap. Both are caught by the ID, not by reading.

## No Placeholders

Every step contains the actual content the engineer needs. These are **plan
failures** — never write them:

- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" without the actual test code
- "Similar to Task N" instead of restating the contract — **the engineer may
  be reading tasks out of order**, and under `executor-execution` they are
  reading exactly one task and nothing else
- Steps that describe *what* to do with no checkable acceptance criteria —
  an unverifiable step is a defect whether or not it shows code
- Implementation code blocks that pre-spend the implementer's design
  decisions — full file bodies, complete class implementations. Keep the
  signatures, invariants, and test expectations; drop the bodies
- References to types, functions, or methods defined in no task and in no
  interface document

A placeholder is not a shortcut you pay for later. It is a question the
implementer answers at 2 a.m. with the worst plausible guess, which the
reviewer then rejects, which costs one full dispatch round.

## Self-Critique

After the plan is complete, read it against the spec with fresh eyes — an
adversarial pass you run yourself, not a subagent dispatch. Fix findings
inline. Items 8 and 10 are the mechanical ones; they run again, with cited
output, under Verification.

**1. Spec coverage.** Walk the spec's requirement IDs in order — `R01`,
`R02`, … — and name the task that implements each. Write the mapping down;
an unmapped requirement gets a task, and a task mapped to nothing gets
deleted or justified.

| Requirement | Task |
|---|---|
| `R01` | T01 |
| `R02` | T01 |
| `R03` | T02 |
| `R04` | T03 |
| `R05` | T03 |
| `R06` | T04 |
| `R11` | T07 |

**2. Placeholder scan.** Search the plan for every pattern in the section
above. Fix each hit.

**3. Type consistency.** Do the types, signatures, and property names used in
later tasks match what earlier tasks defined? `clearLayers()` in Task 3 and
`clearFullLayers()` in Task 7 is a bug — the second dispatch fails on an
import error and burns a review round.

**4. Interface fidelity.** Every signature in every Interfaces block is
character-identical to `INIT-0004-IFCE-nn`. A paraphrase is a defect.

**5. Dependency map completeness.** Every Produces entry that another task
consumes has a row. Every shared file has a row. No cycles. Producers
precede consumers in task order.

**6. Citation check.** Every ID in the document starts with this
initiative's ID. `id`, `spec`, `interfaces`, the ID in every task heading,
and every `R`/`C` token resolve inside this initiative.


**7. TDD completeness.** Every task that produces or changes behavior has
the full rhythm: failing test → run with expected failure named → minimal
implementation → run green → refactor → commit. A task skipping the RED
run, or stating `FAIL` without the expected failure, is a defect — fix the
task. Test code blocks pass the two-principle doctrine:
`../executor/references/test-quality.md` — literals not mirror assertions,
behavior not text, mocks only the external dependency, negative paths
covered where the requirement names them.

**8. ID extraction — run it.** The definitive check, using the three-argument
form, which writes to the path you give and does **not** create the
execution workspace:

```bash
for n in $(seq 1 7); do
  ../executor/scripts/exec-brief docs/executor/INIT-0004-.../plans/INIT-0004-P01-....md \
    "$n" /tmp/brief-check.md >/dev/null || echo "TASK $n FAILS"
  grep -m1 '^\*\*Task:\*\*' /tmp/brief-check.md
done
cd /tmp && rm -f brief-check.md
```

Every task prints its own `INIT-0004-P01-Tnn` and none errors. A task that
errors cannot be dispatched. A task printing the wrong `Tnn` means the
heading ordinal and the ID disagree.

**9. Trailing-content check.** The last task's brief ends with the last
task's last step. If it contains a plan-level section, move that section
above the first task heading.

**10. Mechanical lint.** `exec-plan-lint` catches what reading re-derives
every time: literal store paths written into tasks (artifact locations are
resolved by `exec-workspace`/`exec-evidence`, never named in a plan — a
guessed path breaks the moment the workspace moves and every ID-resolving
tool then disagrees with the plan), task headings missing their ID tokens,
missing frontmatter, the task-depth contract below, and the sketch-vs-code
cap (≤40-line implementation fences, ≤60% code per task body — a plan
carrying implementations is a defect, not a shortcut).

**11. The fresh-implementer test.** For each task, ask: could an
implementer who reads only this brief — no plan, no conversation, no spec
— finish the task without asking a single question? Every question you
can imagine them asking is a missing line: an unstated file, an implicit
signature, an expected output nobody wrote. Add it.

**12. Decomposition fidelity.** Does the plan set follow the split the
decided planning session chose? A plan that silently re-splits the work
discards the human's decision.

### The task-depth contract

Every `### Task N:` carries all of these; `exec-plan-lint` fails a task
missing any one:

| Field | Why it is required | Lint failure |
|---|---|---|
| `**Implements:**` with a requirement ID | the reviewer grades the task against it | "no **Implements:** line naming a requirement ID" |
| `**Depends on:**` a task ID or `none` | the controller orders dispatch from it | "no **Depends on:** line" |
| `**Files:**` with a Create/Modify/Test/Delete entry | the implementer writes only listed files | "no **Files:** list" |
| `**Interfaces:**` (Consumes/Produces, or `none`) | an implicit seam is one the next task guesses | "no **Interfaces:** block" |
| `**Requirements:**` | invariants and exact values bind only when written | "no **Requirements:** block" |
| At least three `- [ ]` steps | failing test, implementation, passing test at minimum | "has N checkbox step(s)" |
| A `Run:` line followed by `Expected:` | every task proves itself with a command and its output | "no 'Run:' line followed by an 'Expected:' line" |

Fields inside a fenced code block do not count — an example is not a
contract.

## Verification

Run these in this session, and cite their output in the gate
presentation. The planning gate is claimed only after all of them pass:

1. `../executor/scripts/exec-plan-lint PLAN_FILE` for every plan — exit 0.
2. The ID extraction loop from item 8 — every task prints its own ID and
   none errors.
3. `../executor/scripts/exec-store-check` — no finding for this
   initiative, including B2/B3 for the decomposition session.
4. The Coverage table from item 1 has a row for every requirement ID in
   the spec — count them against the spec's `### R<nn>` headings.
5. `../executor/scripts/exec-scan-secrets docs/executor/<INIT>-<slug>/plans`
   — exit 0.

## Rulings Do Not Apply Here

A **ruling** is an execution-time concept: the controller decides something
without the human *while a plan is running*, and `exec-ruling` records it
into that plan's `rulings.md`. It requires a plan file, and a workspace, and
a task in flight.

A decision taken while planning — a structure choice, a library pick, a
boundary you moved — is an **ADR** (`INIT-0004-ADR-nn`), written into
`architecture/`, registered in the initiative INDEX, with the human in the
loop. Do not call `exec-ruling` before execution starts.

If planning surfaces a decision the architecture never made, that is the
signal to stop planning: write the ADR (or route to
`executor-architecture`), then resume. Planning around an unmade decision
buries it in a task where no reviewer will recognise it as a decision.

## Execution Handoff

The handoff has two gates in sequence: **plan regression first** (the plan
set survives an adversarial audit as a set), **then** the human picks an
execution mode. Never offer modes before regression clears — a mode picked
on an unaudited plan set is approval of defects nobody has read yet.

**0. Plan-set regression.** When the plan set is drafted — whether one
plan or five — route to `executor-plan-regression` before this section
continues:

```bash
../executor/scripts/exec-plan-regression "$PLAN" init   # seeds the summary
```

The regression skill audits every plan against the spec, the interface
contracts, and each other; repairs findings in place; and leaves
`.executor/<INIT>/plan-regression/summary.md` reading clean-or-waived per
plan. When `exec-plan-regression "$PLAN" check` exits 0:

```bash
../executor/scripts/exec-initiative phase INIT-0004 plan-regression entered "P01..P03 audit"
# … audits + repairs land …
../executor/scripts/exec-initiative phase INIT-0004 plan-regression passed "3 plans clean"
```

(Skippable only by the human, recorded via
`exec-initiative phase INIT-0004 plan-regression skipped "<reason>"`.)

**1. Update the initiative INDEX** (`<initiative>/INDEX.md`) — append the
documents row and update the phase log:

```markdown
| INIT-0004-P01 | plan | Cell router | active | `plans/INIT-0004-P01-cell-router.md` |
```

**2. Update the spec's `plans:` field** to include this plan's ID, and bump
its `updated_at`. The spec and the plan point at each other or the graph is
broken in one direction.

**3. Record the phase transition:**

```bash
../executor/scripts/exec-initiative phase INIT-0004 planning entered "P01 drafted, 7 tasks"
```

**4. Commit atomically** — plan, initiative INDEX, spec cross-link, one
commit:

```bash
git add docs/executor/INIT-0004-cloud-tenant-cells
git commit -m "docs(INIT-0004): add plan P01 — cell router"
```

**5. Offer the two execution modes:**

> **Plan complete: `INIT-0004-P01` — 7 tasks, saved to
> `plans/INIT-0004-P01-cell-router.md`. Two execution options:**
>
> **1. Subagent-driven (recommended)** — `executor-execution` dispatches a
> fresh subagent per task with a generated brief, packages a diff, and runs
> an independent reviewer per task. Isolated context, written verdicts.
>
> **2. Inline** — I execute the tasks in this session, committing per task.
> Faster for a short plan; no independent review and no context isolation.
>
> **Which approach?**


**The gate ends your turn.** The offer above is the last thing in your
message. Do not begin executing either mode in the same message — the human
has not picked yet, and `execution_mode` stays `null` until they do.

**If the human picks inline**, note it plainly: inline mode means you
execute the tasks yourself in this session, still committing per task, still
following every task step verbatim — but with no independent review and no
context isolation. Inline execution does **not** relax the plan's task
boundaries, the TDD rhythm, or the per-task commits; it only removes the
subagent dispatch. If the plan is long or the tasks are intertwined, say so
and recommend subagent mode again once — then execute whichever they chose.

**6. Record the choice** in the plan's `execution_mode` (`subagent` or
`inline`), flip `status` to `active`, bump `updated_at`, and pass the gate:

```bash
../executor/scripts/exec-initiative phase INIT-0004 planning passed "subagent mode"
```

Then hand to `executor-execution`. **Once execution starts it runs to
completion without check-ins** — approval happens at phase boundaries, not
inside them. That is exactly why every defect above must be caught here.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The implementer can look up the signature" | They read one brief. Copy it in, or they invent one. |
| "Task 5 is similar to Task 3" | Briefs are dispatched independently and out of order. Restate the contract — files, signatures, tests. |
| "I'll add the task IDs when execution starts" | `exec-brief` errors out; the plan is undispatchable until you do. |
| "The dependency map is obvious from the tasks" | Obvious to you, holding all seven. The controller serialises dispatch from that table. |
| "The interface isn't defined yet, I'll approximate" | That is an architecture gap and an unwritten ADR. Stop and go back. |
| "Global Constraints cover it, no need to repeat" | The block never reaches the brief. Restate anything a task can violate. |
| "Citing requirement numbers in prose is the same thing" | `R07` is greppable and reviewable; "requirement 7" drifts the moment the spec is renumbered. |
| "One giant task is simpler to review" | A reviewer cannot reject half of it, so they approve all of it. |
| "'Add error handling' is clear enough" | It is the single most rejected step in review. Specify the raise contract and write the test. |
| "Writing the code in the plan prevents implementer mistakes" | It transcribes the plan author's mistakes instead — verbatim, into the diff. The contract travels in the brief; bodies are the implementer's job. |
| "I'll fix the type mismatch during execution" | It surfaces as an import error mid-dispatch and costs a full review round. |
| "I'll start executing while the human reviews the plan" | The gate ends your turn. Work past an unpicked mode is work the approval cannot cover. |
| "Inline mode means I can skip the brief ceremony" | Inline removes the dispatch, not the task boundaries, the TDD steps, or the per-task commits. |
