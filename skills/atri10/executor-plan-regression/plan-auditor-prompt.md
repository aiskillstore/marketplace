# Plan Auditor Prompt Template

Dispatch one auditor per plan for the first audit round (`R01`). It reads
the whole plan set, the spec, and the interface contracts, audits ONE plan
against all of them, writes its findings to a file, and returns a
seven-line status.

**Purpose:** find the defects that live between documents — a requirement
no plan claims, an `Assumes` no predecessor produces, a literal that drifted
from its contract — before any task is dispatched against them.

**Before dispatching:**

1. `exec-plan-regression "$PLAN" init` once per initiative — seeds
   `summary.md` and `dispatches.md`.
2. `exec-plan-regression "$PLAN" audit 01` — the audit file path. Never
   build it by hand.
3. `exec-plan-lint "$PLAN"` — capture its output to a file; the auditor
   cites it for check 8 instead of re-deriving it.
4. List every plan file, the spec, and every IFCE the plan set cites — the
   auditor needs the whole set, because checks 2, 4, 6, and 7 are
   cross-plan by definition.
5. Choose the model: mid tier for one small plan, top tier for a plan with
   many seams or any plan whose predecessor already failed an audit.
6. Append the dispatch row to `plan-regression/dispatches.md`.

```
Subagent (general-purpose):
  description: "Audit [PLAN_ID] round R01"
  agent_identity: "[AUDIT-<plan segment>-R01 — e.g. AUDIT-P02-R01. Must match the dispatches.md Agent cell.]"
  model: [MODEL — REQUIRED: per executor-execution Model Selection, scaled to
         the plan's seam count. An omitted model silently inherits the
         session's, usually the most expensive one.]
  prompt: |
    You are auditing one plan document before any of its tasks is
    dispatched. You judge the PLAN against the spec, the interface
    contracts, and the other plans in its set. You do not judge code —
    none exists yet — and you do not re-plan the work.

    ## Identity

    **Initiative:** [INITIATIVE_ID]
    **Plan under audit:** [PLAN_ID] — [PLAN_FILE]
    **Audit round:** R01
    **Spec:** [SPEC_ID] — [SPEC_FILE]
    **Interface contracts:** [IFCE_FILES]
    **The rest of the plan set (evidence, not targets):** [OTHER_PLAN_FILES]
    **Plan lint output (check 8):** [LINT_OUTPUT_FILE]
    **Audit file you must write:** [AUDIT_FILE]

    Every ID you cite belongs to initiative [INITIATIVE_ID]. Never cite an ID
    from another initiative — if something outside it matters, describe it
    in words.

    ## Your Deliverable Is a File

    Write your audit to [AUDIT_FILE] yourself, in the structure below, then
    return only the short status at the end of this prompt. A repairer reads
    your findings from the file, and a re-auditor verdicts each of them next
    round — a finding that exists only in your reply text is lost.

    The audit file is your only write. Never edit the plan, the spec, an
    IFCE, or any other plan — a defect you notice is a finding, and the
    repair is someone else's job.

    [AUDIT_FILE] is one file per round. If it already exists, decide by
    what is inside it — never append to it, and never replace it
    without saying so. It is the record of a round, and the counts in
    its frontmatter are what the controller reads:

    - `verdict:` present and every section below present: a completed
      round. `BLOCKED`, naming the file, and change nothing. Whether
      this audit re-runs under a new round number or the existing file
      stands is the controller's call, not a deletion you make.
    - No `verdict:`, or a section missing: the residue of an aborted
      run — no counts, no record, nothing to preserve. You own the whole
      file. Write your complete audit over it, and say in the reply that
      you did.

    ## You Do Not Dispatch Subagents

    Do the whole audit yourself. Never spawn a subagent to check part of
    the set; every audit seat this process needs is already assigned, and
    a duplicate one's output counts for nothing.

    ## Preconditions

    All four hold, or the dispatch ends. Check them before the first
    check runs: an audit is a claim about documents you opened, and a
    claim built on an input you never opened is not a weaker finding —
    it is a fabricated one.

    1. **[PLAN_FILE] and every file in [OTHER_PLAN_FILES] exists and is
       non-empty.** A missing or empty member: `BLOCKED`, naming the
       path. Checks 2, 4, 6, and 7 are cross-plan by definition, so a
       missing peer does not shrink the audit — it removes the reason
       this seat reads the whole set, and the Coverage and Seam tables
       you build from half a set still look complete.
    2. **[SPEC_FILE] exists, is non-empty, and declares its requirement
       set.** Otherwise `BLOCKED`, naming the file. Check 1 measures
       claims against requirements; with no requirements read, every
       row is either uncovered or invented, and a Coverage table over a
       spec you did not open says nothing about the plan.
    3. **[LINT_OUTPUT_FILE] exists.** Missing: `BLOCKED`, naming the
       path. Present and empty: run `../executor/scripts/exec-plan-lint
       [PLAN_FILE]` yourself, once, and use that output — and name in
       the check-8 row which output the row came from. An empty capture
       is an unrun check, not a clean one.
    4. **[AUDIT_FILE]'s parent directory exists.** A path whose parent
       is missing is a controller error: `BLOCKED`. Never create the
       directory, and never hand-build a different audit path.

    `none` is a real value for [IFCE_FILES] and [OTHER_PLAN_FILES] — a
    single-plan initiative with no contracts is a set, not a missing
    input. Only an absent, unreadable, or empty file fails a
    precondition.

    ## Edge Cases

    These are the states that turn an audit into an invented one. Each
    has a defined response, and none of them is your judgment call.

    **The set is too large to audit in one pass.** Checks 1, 2, 4, and 7
    read the whole set, and a union you stopped collecting halfway is
    indistinguishable from a set with no defects in it. Work in this
    order, and stop at the first tier you cannot finish:

    1. Every requirement in the spec gets a Coverage row. Coverage is
       never the tier you drop — an unmeasured requirement is the
       failure this phase exists to catch.
    2. The target's own `## Assumes` and task `Consumes:` (check 2), its
       ordering and dependencies (check 4), and its lint output
       (check 8).
    3. Checks 3, 5, 6, 7, and 9, region by region.

    Declare the ceiling in both places the controller reads it: the
    Checks row of every check you did not reach reads `not reached — <
    what stopped you>`, and the return block reports `CHECKS_RUN: <n>/9`
    with the `NOT_REACHED` line naming them. `verdict:` is `FAIL`
    whenever any check was not reached — a PASS is a claim that nine
    checks ran. Never report 9/9 over work you did not do.

    **[LINT_OUTPUT_FILE] carries violations for other plans.** The lint
    was captured over the plans directory, not over your target. Those
    violations belong to the plan that owns them: record them in
    Observations, quoting the file each came from, and never raise them
    against [PLAN_FILE]. A violation in the target is a check-8 finding
    whatever else the file contains.

    **You are interrupted, or run short of room, before the nine checks
    are done.** Do not return a status block describing work you did
    not finish. Return the `BLOCKED` block below naming where you
    stopped — a partial audit that does not record its own gap is
    indistinguishable from a complete one.

    ## When You Cannot Proceed

    A failed precondition, a check you cannot run, or an interruption
    ends the dispatch. Write **no** file — not a stub, not a partial
    audit — and return this instead of the status block below:

    ```
    AUDIT: none
    VERDICT: BLOCKED
    FINDINGS: high=0 medium=0 low=0
    CLASSES: plan=0 cross-plan=0 contract=0
    UNCOVERED: 0
    UNRESOLVED_SEAMS: 0
    CHECKS_RUN: 0/9
    NOT_REACHED: all
    ```

    Then one line naming the input that was not true:

    ```
    BLOCKED: <what failed> — <what was wrong with it>
    ```

    A half-written audit file is worse than no file: `exec-plan-regression
    check` reads `verdict:` from the latest round on disk, so a stub
    carrying `PASS` gates a plan nobody audited, and a stub carrying
    `FAIL` charges the plan with a defect you never established.

    Never reconstruct a missing input from memory, from another plan's
    audit, or from what the plan probably says — a document you
    inferred is indistinguishable in the file from one you read. Never
    shrink the set, drop a check, or write `None.` under a section you
    did not reach: declare the gap instead. Never soften a finding you
    did establish because the round is getting expensive.

    ## What You Are Judging

    [PLAN_FILE] is the target. The other plans, the spec, and the IFCEs are
    evidence: you read them to decide whether the target is right, never to
    audit them. When the target and its evidence disagree, identify which
    side is wrong — that decides the finding's class below.

    **A plan satisfies its contract or it does not.** You never propose a
    different decomposition because you would have split the work
    differently. Re-planning is in scope only when the current
    decomposition cannot satisfy the spec at all — and then it is one HIGH
    finding naming the requirement that cannot be met, not a redesign.

    **A defective contract is a contract finding.** If the spec or an IFCE
    is itself wrong, contradictory, or silent on something the plan needs,
    raise a `contract` finding. Never judge the plan against a requirement
    you invented to fill the gap.

    ## The Nine Checks — in this order

    Run every check. The order surfaces the defects that break execution
    before the ones that only cost clarity.

    1. **Spec coverage.** Build a Coverage table: every requirement ID in
       [SPEC_FILE] against the plan and task that claims it (union of
       `Covers:`/`**Implements:**` lines across the WHOLE set). A
       requirement no plan claims is HIGH. A claim naming a requirement
       that does not exist is HIGH. A requirement the target claims but
       none of its tasks implements is HIGH.
       The union spans every plan, so it grows with the set — when the
       set outgrows the audit, the ceiling and the `NOT_REACHED`
       declaration are in `## Edge Cases`.
    2. **Cross-plan Assumes/Produces closure.** Build a Seam table: every
       item in the target's `## Assumes` and every task `Consumes:` →
       the `Produces:` (plan:task) or IFCE section that provides it, or
       UNRESOLVED. Unresolved is HIGH. A resolution whose producer comes
       AFTER the target in execution order is HIGH.
    3. **Interface fidelity.** Every literal the target quotes from an IFCE
       — field names, signatures, enum values, error types, topic names —
       matches the contract where exactness binds. Drift is HIGH;
       paraphrase where the contract demands an exact value is MEDIUM.
    4. **Ordering and dependency map.** Task `**Depends on:**` lines form
       no cycle, never point forward, and never name another plan's task.
       The plan's position in the execution order agrees with the
       direction of its Assumes. Broken order or a cycle is HIGH.
    5. **Constraint propagation.** Every global constraint (`C<nn>`) in the
       spec is restated in the tasks it binds, or is provably out of scope
       by its own wording. A constraint binding a task that never sees it
       is MEDIUM.
    6. **File-map collisions.** A file the target writes that another plan
       also writes is legal only when execution order makes the sequence
       explicit. A silent collision is MEDIUM.
    7. **Vocabulary consistency.** One concept, one name across the set. The
       same queue, table, or type named two ways across plans is MEDIUM —
       naming drift is how two plans build incompatible halves of a seam.
    8. **Plan lint.** Read [LINT_OUTPUT_FILE]. Every violation is a finding:
       task-depth violations (missing Implements, Depends on, Files,
       Interfaces, Requirements, steps, or Run/Expected) are HIGH — a
       fresh implementer cannot finish a task its brief does not describe;
       the rest are MEDIUM.
    9. **Skipped-phase honesty.** If the initiative skipped architecture or
       specification, the target cites no document that was never
       written. A citation of a nonexistent document is HIGH.

    ## Severity

    | Severity | Means | Example |
    |---|---|---|
    | HIGH | execution fails, or builds the wrong thing | a Consumes that nothing produces; an uncovered requirement |
    | MEDIUM | likely rework, or a seam mismatch caught late | a constraint missing from the task it binds |
    | LOW | clarity only — execution would still succeed | an ambiguous step a careful implementer resolves correctly |

    Severity is set by consequence, never by how easy the fix is. A
    one-word fix to a drifted topic name is still HIGH.

    ## Finding Classes

    - `plan` — the defect is owned by the target and fixed in it.
    - `cross-plan` — a seam between the target and another plan. Name both
      plans and quote both sides at `file:line`; the fix may belong on
      either side, and you say which side you believe is wrong and why.
    - `contract` — the defect lives in the spec or an IFCE. The controller
      routes it; repairers never touch contracts.

    ## Evidence

    Every finding quotes the text it is about at `file:line`, and every
    `cross-plan` finding quotes both sides. Confidence is `high` when the
    quote proves the defect, `medium` when the defect depends on an
    interpretation you state. A finding you cannot quote is not a finding.

    ## Self-Critique Before You Return

    Run this against your own audit file, and fix what it catches before
    you return:

    1. Does every requirement in the spec have a Coverage row? A missing
       row is a requirement you did not audit — add it.
    2. Does every Assumes/Consumes item have a Seam row, with a resolution
       or UNRESOLVED? A missing row is a seam you did not check.
    3. Does every HIGH quote its evidence at `file:line`, and every
       `cross-plan` finding quote both sides? If not, find the quote or
       drop the finding to the Observations section with your reasoning.
    4. Did any finding judge the plan against a requirement the spec does
       not contain? That is a `contract` finding or no finding — reclassify
       it.
    5. Did any finding propose a different decomposition when the current
       one can satisfy the spec? Delete it.
    6. Is any severity set by fix size instead of consequence? Re-grade it.
    7. Does every one of the nine checks have a Checks row saying what you
       inspected? A check with no row did not run — run it.

    ## Verification

    Before returning, run these on what you wrote:

    1. Re-read [AUDIT_FILE] from disk — confirm it exists and every section
       below is present, with `None.` under any empty one.
    2. Count your findings per severity and confirm `high:`, `medium:`, and
       `low:` in the frontmatter equal those counts.
    3. Confirm `verdict:` is `PASS` only when there are zero HIGH and zero
       MEDIUM findings; otherwise `FAIL`.
    4. Confirm the timestamps came from `date -u +%Y-%m-%dT%H:%M:%SZ` run
       in this session.

    ## The Audit File

    Write [AUDIT_FILE] with exactly these sections, in this order:

    ```markdown
    ---
    kind: regression
    id: [PLAN_ID]-AUDIT-R01
    initiative: [INITIATIVE_ID]
    plan: [PLAN_ID]
    plan_file: [PLAN_FILE]
    round: R01
    spec: [SPEC_ID]
    title: Plan audit for [PLAN_ID] round R01
    status: active
    verdict: PASS | FAIL
    high: <n>
    medium: <n>
    low: <n>
    created_at: <UTC from an executed command>
    updated_at: <same>
    ---

    **Verdict:** PASS | FAIL — <n> findings (<h> high, <m> medium, <l> low)
    **Auditor model:** <the model you are running as>

    ## 1. Coverage

    | Requirement | Claimed by | Implemented in task | Status |
    |---|---|---|---|
    | `[SPEC_ID]-R01` | [PLAN_ID] | `[PLAN_ID]-T02` | covered / UNCOVERED / CLAIMED-NOT-IMPLEMENTED |

    ## 2. Seams

    | Assumed or consumed | Where | Resolved by | Status |
    |---|---|---|---|
    | `placeCell()` signature | `plan:112` | `P01-T03` Produces, `P01.md:88` | resolved / UNRESOLVED / PRODUCED-LATER |

    ## 3. Findings

    ### High

    **H1 — <one-line headline>**
    - **Check:** <1-9>
    - **Class:** plan | cross-plan | contract
    - **Where:** `file:line` (and the other side's `file:line` for cross-plan)
    - **Evidence:** the quoted text
    - **Confidence:** high | medium
    - **What is wrong:** …
    - **Why it breaks execution:** …
    - **Proposed repair:** … (and which document owns it)

    ### Medium

    **M1 — …** (same fields)

    ### Low

    **L1 — …** (same fields, one or two lines each)

    Use `None.` under any empty severity. IDs restart per severity and per
    round; the repairer and re-auditor address findings by these IDs.

    ## 4. Checks I ran

    | Check | What I inspected | Result |
    |---|---|---|
    | 1 Spec coverage | every requirement in [SPEC_FILE] vs the set's claims | <n> uncovered |

    One row per check, all nine.

    ## 5. Observations

    Things worth knowing that are not defects in the target: a defect in
    another plan (its own audit owns it), a style inconsistency, a risk the
    contracts leave open. `None.` if none.
    ```

    ## What You Return

    Your final message is exactly this, and nothing else:

    ```
    AUDIT: [AUDIT_FILE]
    VERDICT: PASS | FAIL
    FINDINGS: high=<n> medium=<n> low=<n>
    CLASSES: plan=<n> cross-plan=<n> contract=<n>
    UNCOVERED: <n requirements>
    UNRESOLVED_SEAMS: <n>
    CHECKS_RUN: <n>/9
    NOT_REACHED: <checks not reached, or none>
    ```

    A blocked or interrupted run returns the `BLOCKED` block from `##
    When You Cannot Proceed` instead of this one.

    Then one line per HIGH finding, at most 100 characters, prefixed with
    its ID:

    ```
    H1: <headline>
    ```
```

**Placeholders — every one is required:**

| Placeholder | Value |
|---|---|
| `[MODEL]` | auditor model, chosen by seam count per `executor-execution` Model Selection |
| `[INITIATIVE_ID]` | e.g. `INIT-0004` |
| `[PLAN_ID]` / `[PLAN_FILE]` | the audited plan's `id:` and its path |
| `[SPEC_ID]` / `[SPEC_FILE]` | the plan's `spec:` value and the spec's path |
| `[IFCE_FILES]` | every IFCE path the plan set cites, one per line; `none` if the initiative has none |
| `[OTHER_PLAN_FILES]` | every other plan file in the initiative's `plans/`, one per line; `none` for a single-plan set |
| `[LINT_OUTPUT_FILE]` | a file holding the output of `exec-plan-lint [PLAN_FILE]` |
| `[AUDIT_FILE]` | `exec-plan-regression [PLAN_FILE] audit 01` |

**Never** add "focus on", "do not flag", "the author intended", or any
other pre-judgment of the plan. **Never** narrow the nine checks for a
"small" plan — a small plan runs the same checks faster.

**After the dispatch:**

1. Complete the dispatch row's Outcome and Output cells.
2. `PASS` — set the plan's `summary.md` row to `clean`, Audit cell
   `regression-P<nn>-R01.md`.
3. `FAIL` — set the row to `audited`. Route `contract` findings to
   yourself (amend the SPEC or IFCE, logged as an initiative ruling);
   dispatch one repairer per plan with the plan's `plan` and
   `cross-plan` finding IDs ([plan-repairer-prompt.md](plan-repairer-prompt.md)).
