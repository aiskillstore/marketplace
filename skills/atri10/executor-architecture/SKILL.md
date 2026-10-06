---
name: executor-architecture
description: Use when an approach has been chosen and structure must be decided before a spec exists, when superseding a decision, when a task is blocked on a missing interface, or when declaring that an initiative needs no ADRs or designs.
---

# Architecture & Design

Two phases, one skill. **Architecture** settles what the parts are, what may
depend on what, and what every shared seam looks like exactly. **Design**
settles how one component works inside its boundary.

This is the layer that decides whether the spec has anything to argue from.
A plan built on prose architecture produces tasks whose halves do not meet.

Read [`../executor/SKILL.md`](../executor/SKILL.md) and its four references
before writing into either store. Paths, ID grammar, frontmatter fields, and
index formats come from there and are binding.

Scripts live in [`../executor/scripts/`](../executor/scripts/) and are
written below with that prefix; they must run inside the git repository,
since every store path resolves from the repo root.

## Outputs

| Kind | ID | File location | Template | Produced when |
|---|---|---|---|---|
| Architecture | `INIT-NNNN-ARCH-nn` | `architecture/` | [arch-template.md](references/arch-template.md) | Every initiative reaching this phase gets exactly one. It may be a single page. |
| Decision | `INIT-NNNN-ADR-nn` | `architecture/` | [adr-template.md](references/adr-template.md) | One per decision that had a live alternative and that a future reader could reasonably reverse. |
| Interface | `INIT-NNNN-IFCE-nn` | `architecture/` | [interface-template.md](references/interface-template.md) | One per seam crossed by more than one task or plan. |
| Design | `INIT-NNNN-DSGN-nn` | `design/` | [design-template.md](references/design-template.md) | One per component whose internals are not obvious from ARCH plus IFCE. |

**No code is written in this phase.** The only code-shaped text produced is
signatures and type declarations inside an IFCE — those are contract text,
not implementation. Writing implementation here means the gate has nothing
left to reject.

## Preconditions

| Check | If it fails |
|---|---|
| The initiative folder exists and the charter states goals, non-goals, and success criteria | Route to `executor-initiative`. Architecture with no success criteria optimises for nothing. |
| Discovery produced an `OPTS` document with a recommendation the human accepted, **or** the charter lists `discovery` in `skipped_phases` | Stop. Architecture without a chosen approach silently invents the approach, and the human never got to reject it. |
| The intake and discovery phase-log rows show `Gate passed` (or `skipped`) | Do not proceed on an unpassed gate. Restructuring after a spec exists invalidates the spec. |

## Procedure

### 1. Ground yourself, then open the phase

```bash
../executor/scripts/exec-initiative resolve INIT-0004
../executor/scripts/exec-initiative phase INIT-0004 architecture entered
```

Read, in this order: `charter.md` (problem, success criteria, constraints,
scope boundaries), the accepted `OPTS` document, then any `RSCH` note whose
measurements bear on structure. Everything you write must be traceable to a
constraint or criterion in one of those. A component nobody asked for is the
cheapest thing to delete now and the most expensive later.

### 2. Triage what this initiative warrants

| Signal | Produce |
|---|---|
| More than one component, or one component with an externally visible boundary | ARCH — always |
| A choice was made where another option was genuinely viable | An ADR for that choice |
| Two tasks (or two plans) will touch opposite sides of one call, schema, event, or file format | An IFCE for that seam |
| A component has non-obvious internal state, a real algorithm, or contested file decomposition | A DSGN for that component |
| One component, one plan, one task, no seam | ARCH only — declare the rest skipped per [Skipping](#skipping-declared) |

Over-producing is the second failure mode of this phase; the first is prose
where a signature belongs. Neither is fixed by writing more documents — it is
fixed by writing the documents the seams demand and no others.

### 3. Write the ARCH document

Allocate the ID immediately before writing, never earlier:

```bash
../executor/scripts/exec-id INIT-0004 ARCH        # -> INIT-0004-ARCH-01
```

Write to `architecture/INIT-0004-ARCH-01-<slug>.md` following
[arch-template.md](references/arch-template.md). Sections are fixed: context
and forces, component inventory, boundaries, data flow, failure modes,
deployment shape.

The **boundaries** section is the load-bearing one. See
[Boundaries](#boundaries-the-rule-that-does-the-work). If you cannot say
which side of a boundary a component sits on, the boundary is wrong — fix it
before continuing, because every later document inherits it.

### 4. Harvest the decisions into ADRs

Re-read your own ARCH and mark every sentence of the form "we use X" or "X
owns Y" where something else was possible. Each mark is either an ADR or a
one-line note in the ARCH saying no alternative existed.

Allocate one ID per ADR, each immediately before writing that file:

```bash
../executor/scripts/exec-id INIT-0004 ADR         # -> INIT-0004-ADR-01
```

Every ADR carries a falsifier and a `reversibility`. See
[The falsifier rule](#the-falsifier-rule) and
[Reversibility discipline](#reversibility-discipline).

**A decision made in this phase is an ADR, never a ruling.** `exec-ruling`
records execution-time decisions taken without the human while a plan runs;
it requires a plan file because `rulings.md` is per-plan. In architecture the
human is in the loop and no plan exists — the artifact is a tracked ADR.

### 5. Write an IFCE for every shared seam

The test: would two implementers who never read each other's task both have
to agree on this name, this type, this error, or this ordering? Then it is an
interface document, not a paragraph.

```bash
../executor/scripts/exec-id INIT-0004 IFCE        # -> INIT-0004-IFCE-01
```

Follow [interface-template.md](references/interface-template.md). Exact
signatures, exact types, exact error cases, ordering and lifecycle,
`stability`. See [Interfaces](#interfaces-the-highest-leverage-document).

### 6. Cross-link and index in the same change

Frontmatter, per [`../executor/references/frontmatter.md`](../executor/references/frontmatter.md):

| Document | Links out via |
|---|---|
| ARCH | `components: [...]`, `interfaces: [INIT-0004-IFCE-01]`, `decisions: [INIT-0004-ADR-01, ...]` |
| ADR | `informs: [...]`, `reversibility:`, `alternatives_considered:`, `consequences_accepted:` |
| IFCE | `provides: [...]`, `consumers: [...]`, `stability:` |
| DSGN | `component:`, `implements: [INIT-0004-ARCH-01]`, `interfaces: [INIT-0004-IFCE-01]` |

Then run the contract's five validation checks (`id` matches filename,
`initiative` matches folder, every cited ID starts with this initiative,
timestamps from an executed command, supersession links both ways) and append
a row per document to the initiative's `INDEX.md` **Documents** table in the
same change. An index written later is an index that drifts.

`created_at` / `updated_at` come from a real command:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ
```

**Citation rule, absolute:** no document inside `INIT-0004` may cite an ID
from another initiative. If your architecture depends on another
initiative's output, state the requirement in your own words and declare
`depends_on` in the charter and initiative `INDEX.md`. An initiative must stay
readable and archivable on its own.

### 7. Gate on the human

Present, in this order and nothing more:

1. The component inventory and the boundary rules, in a sentence each.
2. Each decision as: what we chose, what it costs, what would make it wrong,
   `one-way` or `two-way`.
3. Each interface as: name, stability, who consumes it.
4. What you did **not** produce and why.

On approval, flip document `status: draft` → `active` and close the phase:

```bash
../executor/scripts/exec-initiative phase INIT-0004 architecture passed "2 ADRs, 1 interface"
```

**The gate ends your turn** — item 4 above is the last line of your message.
Do not start design or specification before that approval, and do not begin
either in the same message that presents the gate. The gate exists because a
spec written against unapproved structure has to be rewritten, not amended.

### 8. Design phase

```bash
../executor/scripts/exec-initiative phase INIT-0004 design entered
../executor/scripts/exec-id INIT-0004 DSGN        # -> INIT-0004-DSGN-01
```

One DSGN per component that needs one, following
[design-template.md](references/design-template.md), including the file
decomposition. Then present the designs and **end your turn** — same gate
discipline as architecture. On approval, close:

```bash
../executor/scripts/exec-initiative phase INIT-0004 design passed "router + admission control"
```

If no component needs one, skip explicitly — never silently:

```bash
../executor/scripts/exec-initiative phase INIT-0004 design skipped "single component, internals folded into ARCH-01"
```

## Boundaries: the rule that does the work

**Dependencies point inward, toward policy.** Business rules and the
interfaces they need sit at the centre. Frameworks, databases, transports,
queues, clocks, filesystems, vendor SDKs, and UI live at the edge as
replaceable details.

| Layer | May depend on | Must never depend on | Why |
|---|---|---|---|
| Policy (entities, use cases) | Other policy, ports it owns | Anything at the edge | Policy that imports a framework type cannot be tested or replaced without it |
| Ports (interfaces) | Policy types only | Concrete adapters | The inner layer owns the interface; the outer layer implements it |
| Adapters (HTTP, DB, CLI, vendor clients) | Ports, policy types | Other adapters | Adapter-to-adapter coupling turns two replaceable details into one unreplaceable pair |
| Composition root | Everything | Nothing depends on it | Concrete wiring belongs in exactly one place, at the outermost edge |

Consequences to state in the ARCH, not assume:

- **Adapters are humble.** A controller, presenter, repository, or listener
  translates formats and calls a use case. Business branching inside an
  adapter is a rule the tests cannot reach.
- **Plain models cross boundaries.** No ORM rows, framework request objects,
  or vendor response types pass into or out of policy — otherwise every
  vendor upgrade is a policy change.
- **A boundary you cannot enforce is a diagram.** Say how each one is
  enforced: package structure, visibility, import lint, build constraint, or
  a narrow API. Name it in the ARCH.
- **Name the exceptions.** If a boundary is deliberately violated for cost
  reasons, say where, why, and what it will cost to undo. An unnamed
  violation gets copied by the next component.

## The falsifier rule

**An ADR with no falsifier is an opinion with a template.** Every ADR states,
in observable terms, what would make this decision wrong.

| Weak | Strong |
|---|---|
| "This is wrong if requirements change." | "Wrong if a single tenant exceeds 40 GB — per-cell SQLite stops fitting on one node." |
| "Revisit if it doesn't scale." | "Revisit when p99 placement latency exceeds 200 ms at 10k tenants, measured by the placement benchmark." |
| "Wrong if the team dislikes it." | "Wrong if more than one adapter needs the same escape hatch — that means the port is modelling the wrong thing." |

A falsifier must be checkable by someone who was not in the room, and it must
name the **trigger** that sends a reader back to this document. That trigger
is what makes the decision revisitable instead of merely historical.

## Reversibility discipline

`reversibility: one-way|two-way` is a frontmatter field with teeth.

| | Two-way door | One-way door |
|---|---|---|
| Examples | Internal module layout, logging shape, a library that is behind a port | Public API shape, on-disk format, wire protocol, data model, anything a third party or stored data commits to |
| Scrutiny | Decide fast, one paragraph, one alternative named | At least three options, each with its cost stated, and what you would need to learn to change your mind |
| Failure mode | Deliberating for a day over a decision reversible in an hour | Deciding in an hour something reversible only by a migration |
| Revisit | Freely, when the falsifier fires | Only with a superseding ADR and a stated migration path |

Never label a one-way door two-way to skip the work — the label is what a
later reader trusts when deciding how hard to think before changing it.

## Interfaces: the highest-leverage document

**The failure it prevents:** two tasks build incompatible halves of one seam
because the plan described the interface in prose. Task 3 writes
`placeCell(tenant, region)` returning a cell id; Task 5 calls
`place_cell(tenantId)` expecting a result object. Both pass their own tests.
Integration is a rewrite, and nobody is wrong.

An IFCE is what an independent implementer reads to learn what their
neighbours expose. Requirements, all mandatory:

| Requirement | Why |
|---|---|
| Exact signature — name, parameter order, parameter names | A name invented in a brief is a name the neighbour never sees |
| Exact types, including nullability, units, ranges, and encodings | "A timestamp" is four incompatible representations |
| Exact error cases, each with what a caller must do about it | An unlisted error becomes a crash or a swallowed failure, chosen at random by whoever hits it first |
| Ordering and lifecycle — what must be initialised before what, what is idempotent, what may be concurrent, what cancellation means | Two correct implementations can still deadlock or double-apply |
| `stability: draft` \| `stable` \| `frozen` | Tells a consumer whether they may build against it now |
| Named consumers | Changing an interface with no consumer list is changing it blind |

**A task blocked by a missing signature is an architecture gap, not a
planning detail.** The fix is to write or amend the IFCE — never to let the
implementer choose a name, and never to bury the signature in one task's
description where its counterpart cannot read it.

### Stability lifecycle

| Value | Meaning | Changing it |
|---|---|---|
| `draft` | Architecture in progress | Edit freely; nothing depends on it yet |
| `stable` | Gate passed, plans may be written against it | Update every named consumer in the same change |
| `frozen` | A plan is executing against it | Do **not** edit. Write a new IFCE that supersedes it, and record the switch as a ruling in the running plan: `../executor/scripts/exec-ruling PLAN_FILE TASK_ID "<decision>" "<why>" "<cost if wrong>"` — this is execution time, so a ruling is correct here |

Freezing at execution start is what lets an implementer trust the document
they were handed. An interface that changes under a running plan invalidates
the briefs already dispatched.

## Designs

A DSGN covers exactly one component: responsibilities, what it explicitly
does not do, its state, its algorithms, its edge cases, its testing seams,
and its file decomposition. Its public surface is not restated — it points at
the IFCE.

### Testing seams

State, for the component: what is injected (clock, store, transport, random
source), what fakes exist, and what must be exercised for real. Core
behaviour must be testable without the real framework, database, network,
vendor, or hardware — that requirement is what a seam is for. Name the seams
here, because a component designed without them gets tests that mock the
plumbing and prove nothing.

### File decomposition
Carried forward from the planning contract and moved earlier on purpose:

- **One clear responsibility per file**, with a well-defined interface.
- **Files that change together live together. Split by responsibility, not
  by technical layer.** A layer-sliced tree makes one conceptual change edit
  five directories.
- **Prefer smaller, focused files over large ones that do too much.** Agents
  reason best about code they can hold in context at once, and edits are more
  reliable when files are focused.
- **In existing codebases, follow established patterns.** If the codebase
  uses large files, do not unilaterally restructure. If a file you must
  modify has grown unwieldy, propose the split here so planning can task it
  deliberately.

Decomposition decided in a design is decided once, with the whole component
in view. Decided in a plan, it is decided per task by whoever wrote that
task — which is how two tasks create two files with the same responsibility.

## Skipping, declared

| Output | May be skipped when | Never skipped when |
|---|---|---|
| ADR | No choice had a live alternative — say so in one line in the ARCH | Any option was viable and was rejected |
| DSGN | Internals are obvious from ARCH plus IFCE, or the component is a single function | State, ordering, or algorithms are non-trivial |
| IFCE | The whole initiative is one component with no seam crossed by more than one task | Two tasks or two plans touch the same call, schema, event, or format |
| ARCH | Only by explicit human waiver, with the structure then carried by the spec | Default — it can be one page, but it exists |

Mechanics, both required:

1. Add the phase to the charter's `skipped_phases`, with the reason in the
   charter body.
2. Record the phase-log row:
   `../executor/scripts/exec-initiative phase INIT-0004 design skipped "<reason>"`

Silence is the failure this prevents. A reader must be able to tell
"considered and rejected" from "nobody looked" — that distinction is exactly
the `skipped` row.

## Supersession

**Correcting a decision means a new ADR that supersedes the old one.** Never
edit an old ADR to hide the reasoning that led to the original call: the
superseded reasoning is why the new decision is defensible, and a repo where
decisions appear fully formed teaches nobody. The next person re-derives the
rejected option and re-pays its cost.

1. Allocate a new ID: `../executor/scripts/exec-id INIT-0004 ADR`.
2. Write the new ADR with `supersedes: INIT-0004-ADR-03`. Its context section
   restates the original context and names what changed: new evidence, a
   changed constraint, or the old falsifier firing.
3. Edit the old document's **frontmatter only** — `status: superseded`,
   `superseded_by: INIT-0004-ADR-07`, `updated_at:`. The body stays exactly
   as written.
4. Update both rows in the initiative's `INDEX.md`.
5. Repoint anything whose `decisions:` field names the old ADR (ARCH, SPEC),
   or, if a document deliberately still argues from the old call, say so in
   the new ADR.

The same rule governs ARCH, IFCE, and DSGN. A `frozen` interface is
especially strict: supersede it, never edit it, because its consumers were
written against the text they read.

## Self-Critique

Run this yourself before the gate — an adversarial pass, not a subagent
dispatch.

**The mismatch test.** Pick any two components on opposite sides of a seam.
Hand their sections to two readers who will never read each other's. Could
they produce halves that fail to connect — different names, different types,
different error contracts, different ordering assumptions? If yes, name what
is missing and write it into the IFCE. This is the acceptance test for the
whole phase.

- [ ] Every component has a one-line responsibility, and no component has two.
- [ ] Every dependency in the data-flow section is permitted by the boundary
      table; every deliberate exception is named with its cost.
- [ ] Every boundary states how it is enforced, not just that it exists.
- [ ] Every "we use X" has an ADR, or a one-line note that no alternative
      existed.
- [ ] Every ADR has an observable falsifier with a revisit trigger, and a
      `reversibility` that matches the scrutiny actually applied.
- [ ] Every IFCE operation has exact types, exact error cases with caller
      responses, and stated ordering or lifecycle requirements.
- [ ] Every DSGN names its testing seams and its file decomposition.
- [ ] Every ID cited in any frontmatter field starts with this initiative's ID.
- [ ] No credential, token, key, connection string, or personal data appears
      anywhere — auth and config are described as a redacted existence
      statement plus a safe pointer, per
      [`../executor/references/safety.md`](../executor/references/safety.md).
- [ ] Every index row exists for every document written, and the phase-log
      row is updated.
- [ ] Every one-way-door decision in the design session's dossier has an
      ADR, and every ADR's chosen option matches the session's decided
      concept — or supersedes it with a stated reason.
- [ ] The strongest rejected concept from the design session appears in
      the ADR's alternatives, argued honestly, not as a strawman.

## Verification

Run these in this session and cite their output at the gate:

1. `../executor/scripts/exec-store-check` — no finding for this
   initiative; D8 requires every ARCH to carry a top-level `mermaid`
   diagram.
2. `rg -n 'INIT-[0-9]{4}' architecture/` — every ID belongs to this
   initiative.
3. For each IFCE: count its `provides:` entries against the operations it
   specifies with exact types and error cases — equal.
4. `../executor/scripts/exec-scan-secrets docs/executor/<INIT>-<slug>/architecture`
   — exit 0.
5. `../executor/scripts/exec-initiative phase <INIT> architecture passed "…"`
   — accepted; the gate refuses with no ARCH or ADR on disk.

## Handoff to specification

`executor-spec` reads your output as the contract it argues from: the ARCH for
structure and boundaries, the ADRs for what is already decided (and therefore
not up for debate in the spec), the IFCEs for exact surfaces, the DSGNs for
internals. A spec requirement that contradicts an active ADR is a defect in
one of them — resolve it by superseding the ADR, not by quietly specifying
around it.

## Common rationalizations

| Excuse | Reality |
|---|---|
| "The interface is obvious from the task description" | Then write it down in one minute. Obvious-to-you is how `placeCell` meets `place_cell`. |
| "I'll add the falsifier later" | Later you no longer remember what would have changed your mind, which is the only part with future value. |
| "It's reversible, so it doesn't need an ADR" | Two-way doors get short ADRs, not no ADRs. The record is what stops the same debate reopening monthly. |
| "I'll fix the old ADR so it reads correctly" | You have deleted the reasoning that justifies the new decision. New ADR, `supersedes`, old body untouched. |
| "This initiative is small, no architecture needed" | Then it is one page. Skipping is a `skipped` row with a reason, never an absence. |
| "The implementer can pick the signature" | The implementer cannot see the neighbour who calls it. That is the definition of an architecture gap. |
| "I'll record this as a ruling" | Rulings are execution-time and need a plan file. In architecture the human is present: it is an ADR. |
| "I'll draw the boundaries and enforce them in review" | Review is not enforcement. Name the package rule, visibility, or lint that makes the violation fail. |
