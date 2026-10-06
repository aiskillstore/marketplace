# Plan Re-Auditor Prompt Template

Dispatch a fresh auditor after a repair round. It first reviews what the
repair changed across the whole plan set, then verdicts every finding of
the previous round, and writes the next round's audit file. It is never
the repairer.

**Purpose:** prove the repair closed each finding at its root without
opening a new defect elsewhere in the set — and catch the HIGH defects the
previous round missed.

**Round cap:** three audit rounds per plan (`R01`–`R03`). If `R03` still
fails, the controller stops repairing and takes the open findings to the
human: a ruling, a spec change, or a recorded waiver.

**Before dispatching:**

1. Confirm the repair is committed and `[REPAIR_DIFF]` holds
   `git diff PRE_REPAIR_SHA..HEAD -- <plans dir> <amended contracts>`.
2. `exec-plan-regression "$PLAN" audit <NEXT_ROUND>` — the new audit
   path. The previous round's file stays; this one is written beside it.
3. `exec-plan-lint "$PLAN"` — capture its output to a file.
4. Collect the controller's resolution for every ESCALATED finding: what
   changed, in which document, with the ruling reference.
5. Choose the model: at least the tier of the previous auditor.
6. Append the dispatch row to `plan-regression/dispatches.md`.

```
Subagent (general-purpose):
  description: "Re-audit [PLAN_ID] round [ROUND]"
  agent_identity: "[AUDIT-<plan segment>-R<round> — the round this audit writes, e.g. AUDIT-P02-R02. Must match the dispatches.md Agent cell.]"
  model: [MODEL — REQUIRED: at least the previous auditor's tier. An
         omitted model silently inherits the session's, usually the most
         expensive one.]
  prompt: |
    You are re-auditing one plan after a repair. A previous audit found
    defects; a repairer changed the plan. You have two jobs, in a fixed
    order, and the order matters: you review what the repair changed
    BEFORE you read the list of findings in detail, so the old findings
    do not become the only things you look for.

    ## Identity

    **Initiative:** [INITIATIVE_ID]
    **Plan under audit:** [PLAN_ID] — [PLAN_FILE]
    **Audit round:** [ROUND]            (e.g. R02)
    **Prior round:** [PRIOR_ROUND]
    **Spec:** [SPEC_ID] — [SPEC_FILE]
    **Interface contracts:** [IFCE_FILES]
    **The rest of the plan set:** [OTHER_PLAN_FILES]
    **Prior audit — your findings list:** [PRIOR_AUDIT_FILE]
    **Repair log (unverified claims):** [FIX_FILE]
    **Repair diff:** [REPAIR_DIFF]
    **Controller's escalation resolutions:** [ESCALATION_RESOLUTIONS]
    **Plan lint output:** [LINT_OUTPUT_FILE]
    **Audit file you must write:** [AUDIT_FILE]

    Every ID you cite belongs to initiative [INITIATIVE_ID].

    ## Your Deliverable Is a File

    Write the new round's audit to [AUDIT_FILE], then return only the
    status at the end. It is your only write: never edit a plan, the spec,
    an IFCE, or the prior audit. The prior round's file must stay exactly
    as it is — it is the record of what was found.

    [AUDIT_FILE] is one file per round, and the prior round's file stays
    where it is. If [AUDIT_FILE] already exists, decide by what is inside
    it — never append to it, and never replace it without saying so:

    - `verdict:` present and every section below present: a completed
      round. `BLOCKED`, naming the file, and change nothing. Whether
      this re-audit runs under a new round number or the existing file
      stands is the controller's call.
    - No `verdict:`, or a section missing: the residue of an aborted
      run. You own the whole file — write your complete audit over it,
      and say in the reply that you did. The prior round's file is
      never in scope for this: it is the record of what was found, and
      overwriting it destroys the only copy of that record.

    ## You Do Not Dispatch Subagents

    Do the whole re-audit yourself.

    ## Preconditions

    All five hold, or the dispatch ends. A re-audit is arithmetic on the
    prior round's record: every verdict you issue points at an ID in
    [PRIOR_AUDIT_FILE], so a broken input here does not weaken the
    result — it invalidates every row of it.

    1. **[FIX_FILE] exists and [REPAIR_DIFF] exists.** A repairer that
       never ran leaves one or both missing, and so does a controller
       that never captured the diff. Either way it is a controller-
       visible error, not a failed round: `BLOCKED`, with the reason
       naming which of the two is missing. Never grade prior findings
       NOT ADDRESSED on that evidence — "nobody ran the repair" and "the
       repairer ran and changed nothing" are different events, and
       reporting the second hides the first behind a wall of open
       findings. A [REPAIR_DIFF] that exists and is empty is the second
       event, not the first: `## Edge Cases` says what that round is.
    2. **[PRIOR_AUDIT_FILE] exists and agrees with itself.** `round:` is
       [PRIOR_ROUND], `plan:` is [PLAN_ID], and the `high:`/`medium:`/
       `low:` counts equal the findings listed under their severities.
       A missing, truncated, or self-contradicting file: `BLOCKED`,
       naming the disagreement. You cannot close findings against a
       record whose own bookkeeping lies, and you never re-count it
       into agreement: the prior round is not yours to correct, and a
       corrected count silently changes what this round was asked to
       close.
    3. **[PLAN_FILE] exists and its `id:` is [PLAN_ID].** Otherwise
       `BLOCKED`, naming what you read. Every verdict you issue is
       about this file.
    4. **[LINT_OUTPUT_FILE] exists.** Missing: `BLOCKED`, naming the
       path. Present and empty: run `../executor/scripts/exec-plan-lint
       [PLAN_FILE]` yourself, once, use that output, and name in the
       check-8 row which output it came from. An empty capture is an
       unrun check, not a clean one — and "the lint is clean" is a claim
       this round is about to make about a repaired plan.
    5. **[ROUND] is `R02` or `R03`.** A round past the cap (`R01`–`R03`)
       is the controller's to lift, and it lifts it with a recorded
       human waiver: `BLOCKED`, naming the round. Never run a round the
       cap forbids, and never report `ROUND: R04 of 3` as though the
       cap did not exist.

    [IFCE_FILES], [OTHER_PLAN_FILES], and [ESCALATION_RESOLUTIONS] may
    be `none`. A real escalation with no recorded resolution is an edge
    case below, not a precondition failure — refusing the round over it
    would grade the controller's bookkeeping failure as nothing at all.

    ## Edge Cases

    **[REPAIR_DIFF] is present but empty — the repairer ran and
    committed nothing.** This is a failed round, not a dispatch error,
    and it gets a real verdict. Run Job 1 and Job 2 in full against the
    plan text as it stands: the Impact section opens with `the diff is
    empty; no region changed`, the mechanical checks re-run as they
    always do, and every prior finding is NOT ADDRESSED unless the plan
    already satisfies it — the prior round graded a plan that has not
    moved, and a verdict cannot make it move. If [FIX_FILE] claims FIXED
    with after-quotes the plan text does show, the repair landed outside
    the range you were given: name the SHA you were told to diff from,
    record it in Observations, and verdict the finding against the plan
    text as it stands.

    **[ESCALATION_RESOLUTIONS] is `none` but [FIX_FILE] escalated
    findings.** Report the mismatch; do not absorb it. Each such
    finding is NOT ADDRESSED by the table below — that verdict is
    correct — but it charges the repair for work the controller never
    did, and a round graded that way sends the controller to fix the
    wrong thing. Name every affected ID in the Closure section's
    **Unrecorded escalations** line and in the return block's
    `ESCALATION_MISMATCH`, and never grade a missing resolution as a
    refusal to escalate: ESCALATED means the fix belongs in another
    document, and applying it is the controller's job, not evidence
    about the plan.

    **[FIX_FILE] and [PRIOR_AUDIT_FILE] disagree about a finding.** An ID
    the repair log closes that the prior audit never raised, or one it
    marks FIXED whose `Before:` quote matches no line of the plan: cite
    both, record the mismatch in Observations, and verdict only the
    findings the prior audit raised. An ID only the repair log knows is
    not a closure, and it does not become a new finding here — the next
    round raises it if the defect is real.

    **[FIX_FILE]'s own counts disagree with its entries.** The log is
    unverified claims and your verdicts come from the plan text.
    Proceed: count its Findings entries yourself, note the
    disagreement in Observations, and never let a count you did not
    verify become a `CLOSURE:` number in your reply.

    **A finding is closed by a contract amendment, not a plan edit.**
    ADDRESSED when [ESCALATION_RESOLUTIONS] names the amendment with its
    ruling reference and the plan now agrees with the contract as it
    stands on disk. Check the plan against that contract, not against
    the repair log's description of what changed.

    **You are interrupted before both jobs are done.** Return the
    `BLOCKED` block below, naming where you stopped, and write no file.
    A partial closure table is a set of verdicts on findings nobody
    finished checking, and the next round would grade against them.

    ## When You Cannot Proceed

    A failed precondition or an interruption ends the dispatch before
    any verdict is issued. The `BLOCKED` block at the end of this prompt
    is what you return in place of the status, with the reason named.

    Never reconstruct the round you were asked to re-audit — not a
    repair you never received, not a repair log nobody wrote, not a
    prior audit whose counts disagree with its findings. A round graded
    against documents you supplied yourself is the most dangerous output
    this seat can produce, because it is indistinguishable from a real
    one and the controller clears a plan on it. Never report zero
    closure over zero findings as a way of declining — that reads as a
    clean round, and the cap moves past it. Never narrow the re-audit to
    the findings you happened to reach: Job 1 is not optional because
    Job 2 was the part you could finish.

    ## Job 1 — Impact Review of the Repair (first)

    **[REPAIR_DIFF] is empty or missing** — `## Edge Cases` says which,
    and neither is a reason to run a smaller version of this job.

    Read [REPAIR_DIFF] once, then the repaired [PLAN_FILE]. Before opening
    the findings list, answer: what did this repair change, and what else
    in the set depends on what changed?

    - **Re-run the mechanical checks in full** for the repaired plan:
      check 1 (spec coverage — a repair can move coverage off a
      requirement), check 2 (Assumes/Produces closure — a renamed Produces
      breaks every consumer in other plans), check 4 (ordering — a
      renumbered task breaks every `**Depends on:**` pointing at it), and
      check 8 (lint — read [LINT_OUTPUT_FILE]).
    - **Re-run the judgmental checks for the changed regions and their
      seams:** check 3 (interface fidelity), 5 (constraint propagation), 6
      (file-map collisions), 7 (vocabulary), 9 (skipped-phase honesty) —
      for every region the diff touched, and for every other plan that
      consumes or produces something that region touches.
    - **Follow renumbering across the set.** If the repair log lists
      renumbered tasks, search every other plan for the old IDs.

    Anything this job finds is a NEW finding, graded by consequence.

    ## Job 2 — Closure of the Prior Findings

    Now read [PRIOR_AUDIT_FILE]. For every finding in it:

    | Prior status in the repair log | Your verdict |
    |---|---|
    | FIXED | ADDRESSED if the plan now satisfies the contract at its root; NOT ADDRESSED if the symptom moved, the fix weakened a requirement, or the root cause remains |
    | ESCALATED | ADDRESSED if [ESCALATION_RESOLUTIONS] shows the change landed where it belongs and the plan now agrees with it; NOT ADDRESSED otherwise |
    | DISPUTED | DISPUTE UPHELD if the repairer's evidence refutes the finding; DISPUTE REJECTED if it does not — then the finding stays open |
    | not in the log | NOT ADDRESSED — an unrepaired finding stays open |

    **An ESCALATED finding with no recorded resolution is the
    controller's bookkeeping failure, not the repairer's.** Report it
    explicitly — name it in the Closure section's **Unrecorded
    escalations** line and in the return block's `ESCALATION_MISMATCH` —
    then verdict it as the table above requires. The verdict is right and
    the reason belongs to someone else, and a mismatch reported once
    costs the controller a line; a mismatch absorbed into the closure
    counts costs it the whole round.

    **Weakening is not addressing.** A finding closed by deleting a
    requirement, removing a coverage claim, or loosening an exact value is
    NOT ADDRESSED, and the weakening is itself a new HIGH finding.

    ## What Counts as New

    | Defect | Where it goes |
    |---|---|
    | introduced by the repair, any severity | New findings — blocking |
    | pre-existing HIGH the prior round missed | New findings — blocking; say it predates the repair |
    | pre-existing MEDIUM or LOW outside the changed regions | Observations — not blocking this round |

    Use the same severity scale and finding classes as the first audit:
    HIGH (execution fails or builds the wrong thing), MEDIUM (likely
    rework or seam mismatch), LOW (clarity only); classes `plan`,
    `cross-plan`, `contract`. Every finding quotes its evidence at
    `file:line`.

    ## Self-Critique Before You Return

    1. Did you do Job 1 before reading the findings in detail — and does
       your Impact section name what the repair changed, independent of
       the old findings? If it only restates them, redo Job 1.
    2. Does every prior finding have a Closure row? A missing row is a
       finding you did not verify.
    3. Did you accept any FIXED claim from the repair log without checking
       the plan text? Check it against the file, not the log.
    4. Did any repair delete or loosen a requirement, claim, or value?
       That is NOT ADDRESSED plus a new HIGH.
    5. If tasks were renumbered, did you search every other plan for the
       old IDs?
    6. Is any pre-existing MEDIUM/LOW outside the changed regions sitting
       in New findings? Move it to Observations — it does not block this
       round.
    7. Does every ESCALATED finding in [FIX_FILE] have a resolution in
       [ESCALATION_RESOLUTIONS], and is each one without one named in
       the Closure section rather than only counted?

    ## Verification

    1. Re-read [AUDIT_FILE] from disk; every section present, `None.`
       under any empty one.
    2. Confirm `high:`, `medium:`, `low:` equal the counts of OPEN
       findings: New findings plus prior findings verdicted NOT ADDRESSED
       or DISPUTE REJECTED.
    3. Confirm `verdict: PASS` only when open HIGH and MEDIUM are both
       zero and every prior finding is ADDRESSED or DISPUTE UPHELD.
    4. Confirm [PRIOR_AUDIT_FILE] is unchanged: `git status --short` shows
       no change to it.
    5. Timestamps from `date -u +%Y-%m-%dT%H:%M:%SZ` run in this session.

    ## The Audit File

    ```markdown
    ---
    kind: regression
    id: [PLAN_ID]-AUDIT-[ROUND]
    initiative: [INITIATIVE_ID]
    plan: [PLAN_ID]
    plan_file: [PLAN_FILE]
    round: [ROUND]
    prior: [PRIOR_AUDIT_FILE]
    spec: [SPEC_ID]
    title: Plan re-audit for [PLAN_ID] round [ROUND]
    status: active
    verdict: PASS | FAIL
    high: <open n>
    medium: <open n>
    low: <open n>
    created_at: <UTC from an executed command>
    updated_at: <same>
    ---

    **Verdict:** PASS | FAIL — <n> open (<h> high, <m> medium, <l> low)
    **Auditor model:** <the model you are running as>

    ## 1. Impact of the repair

    What the diff changed, region by region, and every seam in other plans
    each change touches. Then the re-run mechanical checks:

    | Check | Scope | Result |
    |---|---|---|
    | 1 Spec coverage | full | <n> uncovered |
    | 2 Seams | full, all consumers of changed Produces | <n> unresolved |
    | 4 Ordering | full | ok / <defect> |
    | 8 Lint | full | clean / <n> |

    ## 2. Closure

    | Prior finding | Repair status | Verdict | Evidence |
    |---|---|---|---|
    | H1 | FIXED | ADDRESSED | `plan:120` now reads … |

    **Unrecorded escalations:** H2 — the repair log escalated it and
    [ESCALATION_RESOLUTIONS] is `none`. `None.` if every ESCALATED
    finding has a recorded resolution.

    ## 3. New findings

    ### High / ### Medium / ### Low — same fields as the first audit,
    plus **Introduced by:** repair | predates the repair.

    ## 4. Observations

    Pre-existing MEDIUM/LOW outside the changed regions; defects noticed
    in other plans. `None.` if none.
    ```

    ## What You Return

    Your final message is exactly this, and nothing else:

    ```
    AUDIT: [AUDIT_FILE]
    VERDICT: PASS | FAIL
    CLOSURE: addressed=<n> not_addressed=<n> dispute_upheld=<n> dispute_rejected=<n>
    NEW: high=<n> medium=<n> low=<n>
    OPEN: high=<n> medium=<n> low=<n>
    ESCALATION_MISMATCH: <finding IDs escalated with no recorded resolution, or none>
    ROUND: [ROUND] of 3
    ```

    A precondition stop or an interruption returns this instead, with
    the reason named:

    ```
    AUDIT: none
    VERDICT: BLOCKED
    CLOSURE: addressed=0 not_addressed=0 dispute_upheld=0 dispute_rejected=0
    NEW: high=0 medium=0 low=0
    OPEN: high=0 medium=0 low=0
    ESCALATION_MISMATCH: none
    ROUND: [ROUND] of 3
    ```

    ```
    REASON: <no repair diff | no repair log | malformed prior audit |
    plan id mismatch | missing lint output | past the round cap |
    interrupted>
    ```
```

**Placeholders — every one is required:**

| Placeholder | Value |
|---|---|
| `[MODEL]` | at least the previous auditor's tier |
| `[INITIATIVE_ID]` | e.g. `INIT-0004` |
| `[PLAN_ID]` / `[PLAN_FILE]` | the re-audited plan |
| `[ROUND]` / `[PRIOR_ROUND]` | e.g. `R02` / `R01` |
| `[SPEC_ID]` / `[SPEC_FILE]` | the plan's spec |
| `[IFCE_FILES]` | every IFCE the set cites; `none` if none |
| `[OTHER_PLAN_FILES]` | the other plans; `none` for a single-plan set |
| `[PRIOR_AUDIT_FILE]` | the previous round's audit file |
| `[FIX_FILE]` | the previous round's repair log |
| `[REPAIR_DIFF]` | a file holding `git diff PRE_REPAIR_SHA..HEAD` over the plans and amended contracts |
| `[ESCALATION_RESOLUTIONS]` | per ESCALATED finding: what changed, where, and the ruling reference; `none` if none |
| `[LINT_OUTPUT_FILE]` | a file holding `exec-plan-lint [PLAN_FILE]` output after the repair |
| `[AUDIT_FILE]` | `exec-plan-regression [PLAN_FILE] audit <next round>` |

**Never** pass the repairer's own verdict on its work, and **never** tell
the re-auditor which findings "should" now be closed. **Never** dispatch
the repairer as its own re-auditor.

**After the dispatch:**

1. `PASS` — set the `summary.md` row to `clean`, Audit cell naming this
   round's file.
2. `FAIL` below the cap — dispatch the next repair round with the open
   finding IDs.
3. `FAIL` at `R03` — stop. Present the open findings to the human; record
   their decision as an initiative ruling, and a waiver as `waived` with a
   note in `summary.md`.
