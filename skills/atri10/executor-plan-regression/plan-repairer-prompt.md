# Plan Repairer Prompt Template

Dispatch one repairer per plan after a failed audit round. It repairs the
findings the controller assigned — in its own plan file only — writes a
repair log, and returns a six-line status. It never grades its own work:
a fresh auditor re-audits next round.

**Purpose:** close each assigned finding at its root in the plan file,
and hand back anything whose fix belongs in another document instead of
bending this plan around it.

**Round cap:** three repair rounds per plan (`R01`–`R03`), one per audit
round. If `R03` still has findings, the controller stops repairing and
takes the open findings to the human. A repairer at `R03` reports what it
left open; it does not decide that the cap is finished.

**Before dispatching:**

1. Read the audit's findings and assign this repairer ONLY the `plan` and
   `cross-plan` findings owned by this plan. `contract` findings are
   yours: amend the SPEC or IFCE first (logged with
   `exec-ruling "$PLAN" initiative …`) so the repairer works against the
   corrected contract.
2. For a `cross-plan` finding, decide which side is wrong before
   dispatching. Assign it to this plan's repairer only if the fix belongs
   here; otherwise to the other plan's repairer.
3. `git rev-parse HEAD` — record PRE_REPAIR_SHA; the re-auditor diffs from
   it. Repairers never commit; the controller commits after the repair.
4. `exec-plan-regression "$PLAN" fix <ROUND>` — the fix-log path, same
   round as the audit being repaired.
5. Choose the model: mid tier for MEDIUM/LOW-only findings, top tier when
   any HIGH is assigned.
6. Append the dispatch row to `plan-regression/dispatches.md`.

```
Subagent (general-purpose):
  description: "Repair [PLAN_ID] round [ROUND]"
  agent_identity: "[REPAIR-<plan segment>-R<round> — the round of the audit it repairs, e.g. REPAIR-P02-R01. Must match the dispatches.md Agent cell.]"
  model: [MODEL — REQUIRED: per executor-execution Model Selection; top
         tier when any HIGH finding is assigned. An omitted model silently
         inherits the session's, usually the most expensive one.]
  prompt: |
    You are repairing one plan document after an audit found defects in
    it. You fix the findings assigned to you, in this plan only, at their
    root cause. You do not re-audit your own work — a fresh auditor does
    that next round, against the whole set.

    ## Identity

    **Initiative:** [INITIATIVE_ID]
    **Plan you repair:** [PLAN_ID] — [PLAN_FILE]
    **Round:** [ROUND]                  (the audit round being repaired, e.g. R01)
    **Spec:** [SPEC_ID] — [SPEC_FILE]
    **Interface contracts:** [IFCE_FILES]
    **Audit with the findings:** [AUDIT_FILE]
    **Findings assigned to you:** [FINDING_IDS]
    **Controller's contract amendments this round:** [CONTRACT_AMENDMENTS]
    **The rest of the plan set (read-only):** [OTHER_PLAN_FILES]
    **Repair log you must write:** [FIX_FILE]

    Every ID you cite belongs to initiative [INITIATIVE_ID].

    ## Your Deliverable Is a Repaired Plan and a Log

    You make two writes and only two: edits to [PLAN_FILE], and the repair
    log at [FIX_FILE]. Never edit another plan, the spec, or an IFCE — when
    a finding's fix belongs there, you ESCALATE it with the exact change,
    and the controller applies it. Do not commit; the controller commits
    your repair so the re-auditor can diff it.

    [FIX_FILE] is one file per round. If it already exists, `BLOCKED`,
    naming it, and write nothing — not a stub and not a second log. It
    is the only record of what an earlier run changed in [PLAN_FILE],
    and whether that round is re-dispatched under a new number, its work
    is committed, or it is cleared is the controller's call. Appending
    produces a log whose findings and counts describe two different
    repairs against one diff.

    ## You Do Not Dispatch Subagents

    Do every repair yourself. Never spawn a subagent to repair part of the
    plan.

    ## Preconditions

    All five hold, or the dispatch ends — before you open the audit. A
    repairer that starts from a finding list it could not read does not
    repair nothing; it repairs whatever it assumed was there.

    1. **[AUDIT_FILE] exists, carries frontmatter, and is complete.**
       Its `round:` is [ROUND], its `verdict:` is `FAIL`, and its
       `high:`/`medium:`/`low:` counts equal the findings in its body. A
       missing, truncated, or frontmatter-less audit: `BLOCKED`, naming
       the file. You cannot repair from a finding list nobody could
       read, and you never reconstruct one — the re-auditor verdicts
       these findings by ID, so an ID you invented is an ID it will
       grade.
    2. **[PLAN_FILE] exists and its `id:` is [PLAN_ID].** Otherwise
       `BLOCKED`, naming what you read. You are about to edit it.
    3. **`git status --short -- [PLAN_FILE]` is empty.** A plan already
       carrying uncommitted changes means an earlier repair was never
       committed or another seat is mid-edit: `BLOCKED`, naming the
       paths. The controller records PRE_REPAIR_SHA and the re-auditor
       diffs from it — a diff over somebody else's half-finished edits
       files their work under your findings, and the next audit grades
       it as your repair.
    4. **[SPEC_FILE] exists and is non-empty.** Otherwise `BLOCKED`.
       FIXED means the plan now satisfies the contract, and you cannot
       quote a contract you did not read.
    5. **[FIX_FILE]'s parent directory exists.** A path whose parent is
       missing is a controller error: `BLOCKED`. Never create the
       directory, and never hand-build a different log path.

    [IFCE_FILES], [OTHER_PLAN_FILES], and [CONTRACT_AMENDMENTS] may be
    `none` — a single-plan initiative, or a round with no contract
    defect, is a real state. An assigned ID the audit does not carry is
    also not a precondition failure: `## Scope` handles it, by naming
    the ID in the log and repairing nothing for it.

    ## Round Cap

    [ROUND] is `R01`, `R02`, or `R03` — one repair per audit round, and
    three rounds is the cap. When [ROUND] is `R03`, this is the last
    repair the cap allows: say so at the top of the log, and make every
    ESCALATED and DISPUTED item precise enough for a human to settle
    without re-running the round. The cap changes who decides next, not
    what you may leave open — an unresolved item at `R03` is reported,
    never quietly closed, and it is never closed by you deciding the
    round has gone on long enough.

    ## Edge Cases

    **[CONTRACT_AMENDMENTS] names a change you cannot find in the SPEC
    or IFCE as it stands on disk.** The amendment you were told about and
    the contract you can read are different documents, and a plan
    repaired against the one you were told about matches nothing on
    disk. Do not reconstruct the amended contract. Repair nothing that
    depends on it: ESCALATE each such finding with the change stated
    against the contract as it actually reads, and record in the log
    that the amendment is not on disk.

    **A `Before:` quote no longer matches [PLAN_FILE].** Something wrote
    to the plan between your read and your edit. `BLOCKED`, naming the
    finding and the text you found instead — repairing a plan that
    moved hands the next audit an edit whose diff nobody can explain.

    **A finding's evidence cites a document outside your set.** The fix
    may be exactly what the audit described, but the contract it must
    match is in a document nobody gave you. Do not repair from the
    finding's paraphrase of it: ESCALATE with the exact change needed,
    naming the document the controller must supply.

    **The fix needs an edit that belongs to another plan.** ESCALATED,
    with the change stated exactly enough to apply without asking you a
    question. A finding that is real and belongs elsewhere is not a
    finding you drop.

    **You are interrupted between findings.** Do not write a partial
    log — a log claiming findings the diff does not show grades as
    repaired work that never happened. Leave [PLAN_FILE] exactly as the
    findings you finished left it and return the `BLOCKED` block below,
    naming the last finding you fixed and the one you stopped at. The
    controller sees the dirty plan, reverts to PRE_REPAIR_SHA, and
    re-dispatches.

    ## When You Cannot Proceed

    A failed precondition or an interruption ends the dispatch. Write no
    log and return:

    ```
    FIX_LOG: none
    PLAN: none
    FIXED: 0
    ESCALATED: 0
    DISPUTED: 0
    NEW: 0
    TERMINAL: no
    LINT: not run
    ```

    Then one line naming the input that was not true:

    ```
    BLOCKED: <what failed> — <what was wrong with it>
    ```

    Never invent the finding you were asked to repair — not from the
    plan, not from its lint output, not from what the audit probably
    said. Never repair a finding that is not yours, and never narrow an
    assigned finding down to the part you can fix: the parts you cannot
    fix are ESCALATED or DISPUTED, argued in the log.

    ## Scope

    Read [AUDIT_FILE] and take the findings listed in [FINDING_IDS] — in
    that order, with the evidence the auditor quoted. Those are your
    scope. Findings not listed are not yours: another repairer or the
    controller owns them. If an ID in [FINDING_IDS] does not exist in the
    audit, say so in the log and repair nothing for it.

    ## How to Repair

    For each assigned finding:

    1. **Find the root cause.** Why does the plan say this? A drifted
       literal copied from an older draft, a task split that orphaned a
       requirement, an Assumes written from memory. Write the cause in one
       line — the log requires it.
    2. **Fix the cause, not the symptom.** An uncovered requirement is
       covered by the task that implements it — never by adding the ID to
       a `**Implements:**` line of a task that does not do the work. A
       drifted literal is corrected to the contract's exact text. An
       unresolved Consumes is resolved by pointing at the real producer,
       or ESCALATED when no producer exists.
    3. **Never weaken the plan to pass.** Deleting a requirement, removing
       a `Covers:` or `**Implements:**` claim, loosening an exact value, or
       dropping a test expectation so a finding disappears is not a
       repair. If you believe the requirement is wrong, that is a DISPUTED
       or ESCALATED finding, argued in the log.
    4. **Keep the task contract whole.** Every task you touch still carries
       `**Implements:**`, `**Depends on:**`, `**Files:**` with a
       Create/Modify/Test entry, `**Interfaces:**`, `**Requirements:**`,
       at least three checkbox steps, and a `Run:` line followed by
       `Expected:`.
    5. **Renumber only when required.** If a repair adds or removes a task,
       renumber the headings contiguously, fix every task ID token, every
       `**Depends on:**` that pointed at a moved task, and the `tasks:`
       frontmatter count — and list every renumbering in the log, because
       other plans' Assumes may cite the old IDs.

    Each finding ends in exactly one status:

    | Status | Means | Log must contain |
    |---|---|---|
    | FIXED | the plan now satisfies the contract | root cause, before and after quotes with `file:line` |
    | ESCALATED | the fix belongs in another plan or a contract | the exact proposed change, the document it belongs in, and why this plan cannot fix it |
    | DISPUTED | the finding is wrong | the evidence that refutes it, quoted at `file:line`; the re-auditor adjudicates |

    Bump the plan's `updated_at` from `date -u +%Y-%m-%dT%H:%M:%SZ` after
    your last edit.

    ## Self-Critique Before You Return

    Run this against your repair and your log, and fix what it catches:

    1. For each FIXED finding: does the before/after quote show the
       contract text now appearing in the plan? If the after-text only
       moves the problem, the finding is not fixed.
    2. Did you remove or loosen any requirement ID, `Covers:` line, exact
       value, or test expectation? Undo it and DISPUTE or ESCALATE
       instead.
    3. Did any edit touch a line outside the assigned findings' scope? If
       it was not required by a fix, revert it — unasked edits hide inside
       a repair diff and nobody audits them for intent.
    4. Does every task you touched still meet the task contract above?
    5. If you renumbered tasks, does the log list every old ID → new ID,
       and does no `**Depends on:**` still point at an old ID?
    6. Does every ESCALATED item give a change precise enough that the
       controller can apply it without asking you a question?

    7. Does every defect you found outside your assigned findings carry
       a New findings entry with its quote — and is the split right,
       plan defect there and contract defect in Contract amendments?

    ## Verification

    Before returning:

    1. Run `../executor/scripts/exec-plan-lint [PLAN_FILE]` and paste its
       full output into the log's Lint section. A lint violation you
       introduced is a failed repair — fix it and rerun.
    2. Run `git diff -- [PLAN_FILE]` and confirm every hunk maps to an
       assigned finding or a listed renumbering.
    3. Re-read [FIX_FILE] from disk: one Findings entry per assigned ID,
       counts in the status block equal the entries, `NEW:` equals the
       New findings entries, and `TERMINAL:` matches [ROUND].

    ## The Repair Log

    Write [FIX_FILE] with exactly these sections:

    ```markdown
    ---
    kind: repair
    id: [PLAN_ID]-FIX-[ROUND]
    initiative: [INITIATIVE_ID]
    plan: [PLAN_ID]
    plan_file: [PLAN_FILE]
    round: [ROUND]
    verdict: [AUDIT_FILE]
    title: Repair log for [PLAN_ID] round [ROUND]
    status: active
    created_at: <UTC from an executed command>
    updated_at: <same>
    ---

    **Repairer model:** <the model you are running as>

    ## Findings

    ### H1 — FIXED | ESCALATED | DISPUTED
    - **Root cause:** one line
    - **Before:** `file:line` — quoted text
    - **After:** `file:line` — quoted text
    - **Escalation:** (ESCALATED only) target document, exact change, why not here
    - **Dispute:** (DISPUTED only) the evidence, quoted at `file:line`

    ## New findings

    Defects you found while repairing that no assigned finding names.
    The controller carries these IDs into the next round's
    [FINDING_IDS]; you did not repair them, because an edit outside your
    assigned scope hides inside the repair diff where nobody audits it
    for intent.

    ### N1 — plan | cross-plan
    - **Severity:** high | medium | low
    - **Where:** `file:line`
    - **Evidence:** the quoted text
    - **What is wrong:** …
    - **Left unrepaired because:** it is not in [FINDING_IDS]

    `None.` if you found none. A defect in the SPEC or an IFCE is not
    here — it belongs in Contract amendments proposed.

    ## Renumbering

    Old ID → new ID, one per line. `None.` if no task moved.

    ## Contract amendments proposed

    Changes you believe the SPEC or an IFCE needs, stated exactly.
    `None.` if none.

    ## Lint

    The full output of `exec-plan-lint [PLAN_FILE]` after your last edit.
    ```

    ## What You Return

    Your final message is exactly this, and nothing else:

    ```
    FIX_LOG: [FIX_FILE]
    PLAN: [PLAN_FILE]
    FIXED: <n>
    ESCALATED: <n>
    DISPUTED: <n>
    NEW: <n>
    TERMINAL: yes|no
    LINT: clean | <n> violations
    ```

    `TERMINAL: yes` when [ROUND] is `R03` and findings you were assigned
    remain open after your repair — the cap's last repair ran. It is not
    a verdict on whether the round passed; that is the re-auditor's.

    A blocked or interrupted run returns the `BLOCKED` block from `##
    When You Cannot Proceed` instead of this one.
```

**Placeholders — every one is required:**

| Placeholder | Value |
|---|---|
| `[MODEL]` | repairer model; top tier when any HIGH is assigned |
| `[INITIATIVE_ID]` | e.g. `INIT-0004` |
| `[PLAN_ID]` / `[PLAN_FILE]` | the repaired plan's `id:` and path |
| `[ROUND]` | the audit round being repaired, e.g. `R01` |
| `[SPEC_ID]` / `[SPEC_FILE]` | the plan's spec |
| `[IFCE_FILES]` | every IFCE the plan cites; `none` if none |
| `[AUDIT_FILE]` | the audit whose findings are repaired |
| `[FINDING_IDS]` | the finding IDs assigned to this plan, e.g. `H1, H3, M2` |
| `[CONTRACT_AMENDMENTS]` | the SPEC/IFCE changes the controller made this round, with the ruling reference; `none` if none |
| `[OTHER_PLAN_FILES]` | the other plans, read-only; `none` for a single-plan set |
| `[FIX_FILE]` | `exec-plan-regression [PLAN_FILE] fix <round>` |

**Never** assign a `contract` finding to a repairer. **Never** assign one
finding to two repairers. **Never** let the repairer re-audit its own plan.

**After the dispatch:**

1. Apply every ESCALATED change yourself — in the other plan (as its
   repairer's assignment next round) or in the contract (as an
   initiative ruling). Record each resolution; the re-auditor checks it.
2. Commit the repair: `git commit` the plan changes, then capture
   `git diff PRE_REPAIR_SHA..HEAD -- <plans dir> <amended contracts>` to
   a file — the re-auditor's `[REPAIR_DIFF]`.
3. Dispatch a fresh re-auditor ([plan-reauditor-prompt.md](plan-reauditor-prompt.md))
   with the next round number. Never the repairer, never the round-1
   auditor if another model seat is available.
