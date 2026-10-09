# Frontmatter Contract

Every Executor document opens with YAML frontmatter. Fields carry the ID
graph; without them a document is unreachable by any index or script.

Values come from repository state, executed commands, or the human's
explicit statement. **Never invent a timestamp, an ID, a status, or a
provenance claim.** If a check did not run, the field says so.

## Common fields (every document)

```yaml
---
id: INIT-0004-ADR-02              # this document's ID; unique within the initiative
initiative: INIT-0004             # owning initiative; always present
kind: adr                         # charter|research|options|architecture|adr|interface|design|spec|risk|verification|plan|brainstorm
title: Tenant isolation boundary  # one line, human-readable
status: active                    # draft|active|superseded|withdrawn
created_at: 2026-09-01T14:55:52Z  # actual UTC from an executed command
updated_at: 2026-09-01T14:55:52Z
supersedes: null                  # ID within this initiative, or null
superseded_by: null               # filled in when replaced
---
```

**`status` transitions:** `draft` while being written, `active` once the
phase gate passes, `superseded` when a newer document replaces it,
`withdrawn` when the work is abandoned. A superseded document is never
edited to hide its old content — it keeps its body and gains
`superseded_by`.

## Per-kind additional fields

### Brainstorm (`kind: brainstorm`)

```yaml
id: INIT-0004-BRN-01              # exec-id INIT-0004 BRN; null before an initiative exists
initiative: INIT-0004             # null for a pre-initiative session
mode: design                      # design = a whole feature or use case; decision = one open question
question: How should tenants onboard themselves without an operator?
feeds: [specification, planning]  # the phases this session's outcome informs
status: draft                     # draft while open; active once the human picks; withdrawn if abandoned
decided: null                     # the chosen concept or option name once the human picks
```

`feeds` is what the phase gates read: `specification entered` requires an
`active` session whose `feeds` includes `specification`, and `planning
entered` requires one whose `feeds` includes `planning` (normally a
`decision` session on how the spec decomposes into plans and tasks).

Required body sections, checked by `exec-store-check` B2:

| Mode | While `draft` | Once `active` |
|---|---|---|
| `design` | `## Brief` | `## Brief`, `## Map`, `## Concepts` with ≥3 `###` concepts, `## Stress test`, `## Decision log`, `## Design`, `## Risks and open questions`, `## Handoff`, and `decided:` set |
| `decision` | `## Options` | `## Options` with ≥3 `###` options, `## Adversarial pass`, `## Outcome`, and `decided:` set |

### Charter (`kind: charter`)

```yaml
phase: specification              # current phase of the whole initiative
skipped_phases: [discovery]       # phases deliberately skipped, with reasons in the body
depends_on: []                    # other initiative IDs — see the exception in "Validation before writing"
supersedes_initiative: null       # initiative this one replaces wholesale
superseded_by_initiative: null    # set on the replaced initiative's charter
related: []
owner: <human or team>
```

### Research (`kind: research`) / Options (`kind: options`)

```yaml
question: What does cell placement cost at 10k tenants?
sources: [<url>, <path>, <command>]     # provenance, distinguishing measured from cited
confidence: measured                    # measured|cited|inferred|unverified
recommends: INIT-0004-OPTS-01           # options docs only; the chosen approach's own ID or null
```

### Architecture (`kind: architecture`)

```yaml
supersedes: null
components: [router, placement-service, admission-control]
interfaces: [INIT-0004-IFCE-01]
decisions: [INIT-0004-ADR-01, INIT-0004-ADR-02]
```

### Decision record (`kind: adr`)

```yaml
decision: Use per-cell SQLite over a shared cluster
alternatives_considered: 3
consequences_accepted: <one line>
reversibility: one-way             # one-way|two-way — drives how much scrutiny it earned
informs: [INIT-0004-SPEC-01]
```

An ADR body carries: context, the options weighed, the decision, the
consequences accepted, and what would make this decision wrong. An ADR
without a stated falsifier is an opinion with a template.

### Interface (`kind: interface`)

```yaml
provides: [placeCell, evictCell]
consumers: [INIT-0004-P01, INIT-0004-P02]
stability: stable                  # draft|stable|frozen
```

Interface documents carry exact signatures, exact types, exact error cases.
This is the document tasks read to learn what their neighbors expose — vague
interfaces are how two tasks build incompatible halves of one seam.

### Design (`kind: design`)

```yaml
component: router
implements: [INIT-0004-ARCH-01]
interfaces: [INIT-0004-IFCE-01]
```

### Spec (`kind: spec`)

```yaml
implements: [INIT-0004-ARCH-01, INIT-0004-DSGN-01]
decisions: [INIT-0004-ADR-01]
verification: INIT-0004-VRFY-01
plans: [INIT-0004-P01]             # filled in as plans are written
global_constraints: 7              # count; the body lists them verbatim
```

### Risk (`kind: risk`)

```yaml
method: pre-mortem                 # pre-mortem|red-team|failure-mode-analysis
risks_identified: 9
mitigations_planned: 6
accepted_without_mitigation: 3     # named in the body with why
```

### Verification (`kind: verification`)

```yaml
spec: INIT-0004-SPEC-01
criteria_count: 12
evidence_types: [unit, integration, manual, smoke]
```

### Plan (`kind: plan`)

```yaml
id: INIT-0004-P01
spec: INIT-0004-SPEC-01            # the spec this plan argues from
interfaces: [INIT-0004-IFCE-01]
tasks: 7
execution_mode: subagent           # subagent|inline — set when the human picks
sequential: false                  # true = tasks commit direct to the plan branch
workspace: .executor/INIT-0004/P01
```

`sequential: true` opts the plan out of per-task branches
(`references/branches.md`): tasks commit directly to the plan branch. It is
only honest for a single chain, so `exec-plan-lint` requires every task
after the first to declare `**Depends on:**` the preceding task's ID.

## Execution artifacts (the `.executor/` store)

Every file the execution phase generates carries the same identity block as
a thinking document, so a brief found on disk is traceable without opening
the plan. These artifacts are **generated** — scripts write them, agents
append to them; nobody hand-writes frontmatter for one. `exec-brief`,
`exec-context`, and `exec-workspace` emit this block automatically.

Common shape (all execution artifacts):

```yaml
---
kind: brief                        # brief|context|ledger|rulings|preflight|dispatches|report|verdict|fix-package|evidence|regression|repair|gate
id: INIT-0004-P01-T03              # the task ID; ledger/rulings/preflight/dispatches use the plan ID instead
initiative: INIT-0004
plan: INIT-0004-P01
plan_file: docs/executor/INIT-0004-<slug>/plans/INIT-0004-P01-<topic>.md
spec: INIT-0004-SPEC-01            # omitted where meaningless (rulings, dispatches)
title: Brief for INIT-0004-P01-T03
status: active
created_at: <UTC from an executed command>
updated_at: <UTC from an executed command>
---
```

Per-kind fields:

| Kind | Written by | Extra fields | Notes |
|---|---|---|---|
| `brief` | `exec-brief` | — | regenerated per dispatch; `updated_at` moves only on regeneration |
| `context` | `exec-context` | — | same lifecycle as the brief |
| `ledger` | `exec-workspace` | — | `progress.md`; appended by the controller through the run |
| `rulings` | `exec-workspace` | — | `rulings.md`; `exec-ruling` appends entries |
| `preflight` | `exec-workspace` | — | `preflight-scan.md` |
| `dispatches` | `exec-workspace` | — | `dispatches.md` |
| `report` | the implementer | `task: INIT-0004-P01-T03`, `rounds: 2` | one file per task, appended per fix round |
| `verdict` | the reviewer | `task`, `round: INIT-0004-P01-T03-R02`, `spec_verdict: PASS`, `quality: APPROVED` | one file per review round |
| `fix-package` | `exec-fix-package` | `task`, `round: INIT-0004-P01-T03-R02`, `verdict:` provenance path | verdict findings + report + brief + context assembled for the fix dispatch |
| `evidence` | `exec-evidence` | `criterion: INIT-0004-VRFY-01 #3`, `method: unit`, `state: a91e502` | one file per criterion; written to the initiative's tracked `verification/evidence/PNN/` |
| `regression` | the plan auditor (`AUDIT` dispatch) | `id: INIT-0004-P02-AUDIT-R01`, `plan`, `round: R01`, `verdict: PASS \| FAIL`, `high`, `medium`, `low` | one file per plan per round, never overwritten: `.executor/<INIT>/plan-regression/regression-P<nn>-R<nn>.md`; `exec-plan-regression check` requires the latest round's `verdict: PASS` for a `clean` summary row |
| `repair` | the plan repairer (`REPAIR` dispatch) | `id: INIT-0004-P02-FIX-R01`, `plan`, `round: R01`, `verdict:` the audit path it repairs | one repair log per plan per round: `.executor/<INIT>/plan-regression/fix-P<nn>-R<nn>.md` |
| `gate` | `exec-plan-regression init` | — | the plan-set clearance summary, `.executor/<INIT>/plan-regression/summary.md`; rows: clean\|waived |
| `dispatches` (plan regression) | `exec-plan-regression init` | `initiative` | `.executor/<INIT>/plan-regression/dispatches.md`; one row per `AUDIT` and `REPAIR` dispatch |

`report` and `verdict` files are written by subagents, not scripts — the
subagent copies the identity block from its brief (or verdict path) and
fills the fields it owns. `updated_at` is bumped by whoever appends last.

The `status` vocabulary is unchanged: `active` while the run lives. Nothing
in `.executor/` is ever superseded or deleted — a finished run's artifacts
keep `status: active` and the run's row in `.executor/INDEX.md` says
`complete`.

Branch provenance is not frontmatter but follows the same never-invent
rule: `exec-initiative branch` writes the initiative's `**Branch:**` line
(branch name, base branch, fork-point short SHA) to the initiative's
`INDEX.md` at fork time — never afterwards from memory.

## Task identity

Tasks are headings inside a plan, not separate files. They are addressed by
ID everywhere else:

```markdown
### Task 3: Cell placement scoring — `INIT-0004-P01-T03`
```

The ID in the heading is what `exec-brief` extracts and what every brief,
report, diff, verdict, ledger line, and ruling references. A plan whose task
headings carry no IDs cannot be executed by `executor-execution`.

## Validation before writing

1. Does `id` match the filename's ID segment?
2. Does `initiative` match the containing folder's ID?
3. Does every ID referenced in any field begin with this same initiative ID?
   If not — **stop**: that is a cross-initiative citation, which is
   forbidden. State the requirement in your own words and move the
   dependency to the charter.

   **The one exception, and it is the whole exception:** the charter's four
   relationship fields — `depends_on`, `supersedes_initiative`,
   `superseded_by_initiative`, `related` — hold other initiatives' IDs by
   design. They are the canonical, machine-readable home for every
   cross-initiative link. No other field in any document, charter included,
   may carry one.
4. Are `created_at` / `updated_at` real timestamps from an executed command?
5. If this supersedes something, does the old document's `superseded_by`
   point back at this one?

A document failing any check is not written until it passes.
