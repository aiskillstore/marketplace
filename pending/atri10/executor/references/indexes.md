# Index Contract

Three indexes make the stores navigable. Each has one owner and one format.
An index that contradicts the documents it lists is a bug — fix the index in
the same change that caused the drift.

## 1. `docs/executor/INDEX.md` — the initiative registry

Every initiative, one row. This is the entry point for "what work exists."

```markdown
# Executor Initiatives

| ID | Title | Status | Phase | Folder | Updated |
|---|---|---|---|---|---|
| INIT-0004 | Cloud tenant cells | active | execution | `INIT-0004-cloud-tenant-cells/` | 2026-09-01 |
| INIT-0003 | Auth token rotation | complete | handoff | `INIT-0003-auth-token-rotation/` | 2026-08-28 |
| INIT-0002 | Legacy importer | superseded | discovery | `INIT-0002-legacy-importer/` | 2026-08-11 |
```

**Status values:** `active` (work in progress), `complete` (shipped and
closed out), `superseded` (replaced by another initiative — name it in the
charter's `supersedes_initiative`), `abandoned` (stopped deliberately;
charter body says why), `paused` (suspended, resumable).

**Phase** is the initiative's current phase from the phase table in the root
skill. It tells a reader where to pick up.

Updated by `executor-initiative` on creation and on every phase transition.

## 2. `docs/executor/INIT-<NNNN>-<slug>/INDEX.md` — the document registry

Every document inside one initiative. This is what makes an initiative
self-contained: one file lists its whole contents, and every ID in it
belongs to this initiative.

```markdown
# INIT-0004 — Cloud tenant cells

**Status:** active · **Phase:** execution · **Owner:** platform team

## Dependencies

- `depends_on: [INIT-0002]` — legacy importer must land first

## Documents

| ID | Kind | Title | Status | Path |
|---|---|---|---|---|
| INIT-0004-CHTR-01 | charter | Cloud tenant cells | active | `charter.md` |
| INIT-0004-RSCH-01 | research | Prior art: cell architectures | active | `discovery/INIT-0004-RSCH-01-prior-art.md` |
| INIT-0004-OPTS-01 | options | Placement approaches | active | `discovery/INIT-0004-OPTS-01-approach-comparison.md` |
| INIT-0004-ARCH-01 | architecture | System structure | active | `architecture/INIT-0004-ARCH-01-system-structure.md` |
| INIT-0004-ADR-01 | adr | Storage engine | active | `architecture/INIT-0004-ADR-01-storage-engine.md` |
| INIT-0004-IFCE-01 | interface | Service contracts | stable | `architecture/INIT-0004-IFCE-01-service-contracts.md` |
| INIT-0004-SPEC-01 | spec | Cell placement | active | `specs/INIT-0004-SPEC-01-cell-placement.md` |
| INIT-0004-P01 | plan | Cell router | active | `plans/INIT-0004-P01-cell-router.md` |

## Phase log

| Phase | Entered | Gate passed | Notes |
|---|---|---|---|
| intake | 2026-08-30 | 2026-08-30 | charter approved |
| discovery | 2026-08-30 | 2026-08-31 | approach B chosen |
| architecture | 2026-08-31 | 2026-09-01 | 2 ADRs |
| design | — | **skipped** | single component, folded into spec |
| specification | 2026-09-01 | 2026-09-01 | reviewed |
| planning | 2026-09-01 | 2026-09-01 | 1 plan, 7 tasks |
| plan-regression | 2026-09-01 | 2026-09-01 | 2 plans audited clean |
| execution | 2026-09-01 | — | in progress |
```

**This section mirrors the charter's frontmatter; the charter is
canonical.** The charter's `depends_on`, `supersedes_initiative`,
`superseded_by_initiative`, and `related` fields are the machine-readable
source of truth for cross-initiative links, and this section restates them
in prose so a reader sees them without opening the charter. No other
document may carry another initiative's ID, and this section must never
claim a relationship the charter does not declare.

**The phase log is the initiative's history.** A skipped phase gets a row
written by `exec-initiative phase <id> <phase> skipped "<reason>"`, which
puts `**skipped**` in the Gate-passed cell and the reason in Notes — the
difference between a considered decision and an oversight is exactly this
row.

Updated by whichever skill owns the current phase, in the same change that
produces the document.

## 3. `.executor/INDEX.md` — the execution registry

Every plan run, one row. Answers "what did we actually execute, and where
are its artifacts."

```markdown
# Executor Runs

| Plan ID | Initiative | Status | Tasks | Started | Finished | Workspace |
|---|---|---|---|---|---|---|
| INIT-0004-P01 | INIT-0004 | running | 4/7 | 2026-09-01 | — | `INIT-0004/P01/` |
| INIT-0003-P02 | INIT-0003 | complete | 5/5 | 2026-08-27 | 2026-08-28 | `INIT-0003/P02/` |
| INIT-0003-P01 | INIT-0003 | complete | 3/3 | 2026-08-26 | 2026-08-26 | `INIT-0003/P01/` |
```

**Status values:** `running`, `complete`, `blocked` (stopped on one of the
four stop conditions), `paused` (the initiative was paused mid-run; resumable
from the ledger), `abandoned`.

A `complete` row is never removed and its workspace is never deleted. The
row is how someone finds the reports and verdicts from a run that finished
months ago.

Updated by `executor-execution` at run start, at each task completion (the
`Tasks` column), and at run end.

The `.executor/<INIT>/` directory beside the `Pnn/` workspaces is the
initiative-level run area: `plan-regression/` artifacts and the
initiative-wide `rulings.md` live there (see layout.md). They do not get
INDEX rows — a row answers "what ran," and regression audits are gate
input, not runs. The row's own staleness (a `running` plan whose ledger
shows all tasks complete, a `0/?` count after dispatches) is drift that
`exec-run PLAN check` reports; update it through `exec-run`, never by hand.

## Maintenance rules

1. **Same change, always.** An index row is written in the same change as
   the document or state transition it describes. An index updated later is
   an index that drifts.
2. **Never contradict the documents.** If a row says `active` and the
   document says `superseded`, the document wins — fix the row.
3. **Append for new, edit in place for status.** New documents append a row.
   A status change edits that row's status cell. Rows are never deleted.
4. **Sort newest first** in the initiative registry and the execution
   registry; sort by ID in a document registry (it reads as a
   chronology of the initiative's own thinking).
5. **Create on first use.** A missing index is created with its header row
   by whichever skill needs it first, not treated as a blocker.
