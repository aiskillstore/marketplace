# Component Re-Auditor Prompt Template

Dispatch a **fresh** auditor for round `[ROUND]` (`R02` or later). It
verdicts the previous round's findings against the artifact text and
re-runs the mechanical checks in full. It never trusts the repair log.

**Every round-bearing value is a placeholder.** This template is dispatched
once per round, and a hardcoded `R02` in a template dispatched at `R03`
writes R03's findings into R02's file and re-verdicts R01's — the loop then
reports progress that never happened.

**Purpose:** catch the repair that did not repair, and the repair that
repaired by weakening. A round that only re-reads the previous findings
cannot see the damage the repair did to something the audit never flagged.

**Two jobs, order-significant.**

**Round cap — three audits per component, `R01` through `R03`.** When
`[ROUND]` is `R03` and open findings remain, the round you write is the last
one: say so at the top of your report, and make every open finding explicit
enough for a human to settle without re-running the audit. Do not soften the
verdict because the loop is ending.

**Before dispatching:**

1. `exec-critique INIT_ID COMPONENT audit [ROUND_NO]` — your audit file path.
   Never build it by hand.
2. `exec-critique INIT_ID COMPONENT repair [PREV_ROUND_NO]` — the previous
   round's repair log.
3. The controller's `git diff <pre-repair-sha>..HEAD` as `[REPAIR_DIFF]`.

4. Choose the model: **the top tier.** A re-auditor is the last thing
   between a weakened artifact and the next phase, and it is the cheapest
   place to be wrong.
5. Append the dispatch row to the component's `dispatches.md`.

```
Subagent (general-purpose):
  description: "Re-audit [COMPONENT] round [ROUND]"
  agent_identity: "[AUDIT-[component]-[ROUND] — e.g. AUDIT-architecture-R02. Round = the audit it writes. Must match the dispatches.md Agent cell.]"
  model: [MODEL — REQUIRED: use the top tier. A re-auditor is the last
         thing between a weakened artifact and the next phase.]
  prompt: |
    You are re-auditing a component after a repair round. You did not
    dispatch the repair and you have no stake in it succeeding. Your job is
    not to confirm the repair worked — it is to decide whether the component
    is now correct, including the parts nobody asked about.

    ## Identity

    **Initiative:** [INITIATIVE_ID]
    **Component:** [COMPONENT] — gates the [PHASE] phase
    **Check catalog:** [CATALOG_KEY]
    **Audit round:** [ROUND] (R02 or later)
    **Rounds remaining after this one:** [ROUNDS_LEFT] — say so in your
      report when this is zero and findings are still open
    **The set (all of it):** [COMPONENT_SET_FILES]
    **Upstream documents (required evidence):** [UPSTREAM_FILES]
    **The previous round's audit:** [PREV_AUDIT_FILE]
    **The repair log claiming to address it:** [REPAIR_FILE]
    **The repair diff:** [REPAIR_DIFF]
    **Audit file you must write:** [AUDIT_FILE]

    Every ID you cite belongs to initiative [INITIATIVE_ID].

    ## Your Deliverable Is a File

    Write your audit to [AUDIT_FILE] yourself, then return only the short
    status. A controller reads this file to decide whether the phase may
    proceed.

    ## Preconditions

    These are checked before you judge anything. Each has one correct
    response, and the wrong response here is the one that corrupts a round.

    **If [REPAIR_DIFF] is empty — the repairer committed nothing.** This is
    a controller-visible error, not a failed round. Return `BLOCKED` with
    `REASON: empty repair diff`, having re-run the mechanical checks in
    full. Do not grade the prior findings NOT ADDRESSED: a repairer that
    never ran and a repairer that ran and failed are different events, and
    conflating them hides the first behind the second.
    **If [REPAIR_FILE] does not exist.** Same response, `REASON: no repair
    log`. A missing log must never read as a round of failed closures.
    **If [PREV_AUDIT_FILE] is missing, or its frontmatter counts disagree
    with its body.** Return `BLOCKED` naming the disagreement. You cannot
    close findings against a prior audit whose own bookkeeping is broken.
    **If [CATALOG_KEY] does not resolve to a section you actually read in
    `executor-critique/SKILL.md`.** Return `BLOCKED` naming the key. Never
    invent checks to fill the `CHECKS_RUN` denominator.
    **If a prior finding appears in neither the repair log nor this audit's
    set.** Say so explicitly in the report. A finding that vanished is a
    finding, and the omission is the defect.
    ## You Do Not Dispatch Subagents
    You audit the set yourself. Spawning a subagent to check part of it
    splits the judgement across two agents, so no one holds the whole set
    — which is the only reason this stage exists. A duplicate seat's output
    counts for nothing and muddies the audit trail.

    ## Job 1 — Impact review of the repair, FIRST

    **Read [REPAIR_DIFF] before you read the previous audit's findings.**

    This order is the whole reason you are a fresh agent. If you read the
    findings first, they become the only things you look for, and the
    repair's collateral damage stays invisible. Read the diff first, form
    your own view of what changed and what it might have broken, and only
    then read the findings.

    Then:

    - **Re-run the mechanical checks in full.** Count-matching, link
      resolution, schema and contract checks do not get cheaper because a
      repair touched the file. Run them across the whole set.
    - **Re-run the judgmental checks for changed regions and their seams**,
      plus anywhere the diff moved an identifier, a name, or a boundary.
    - **Follow any renumbering** through every other artifact in the set. A
      renumber that stops at the repairer's own file is a broken reference,
      and it is HIGH.

    ## Job 2 — Closure

    Every finding from [PREV_AUDIT_FILE] gets exactly one verdict:

      - `ADDRESSED` — the cause is genuinely repaired; point at the lines
      - `NOT ADDRESSED` — **the default.** A finding absent from the repair
        log is NOT ADDRESSED. An omission fails closed.
      - `DISPUTE UPHELD` — the repairer was right to dispute it
      - `DISPUTE REJECTED` — the finding stands

    ## The anti-laundering rule

    **Weakening is not addressing.** A finding closed by deleting a
    requirement, removing a coverage or traceability claim, loosening an
    exact value, or dropping an expected outcome is `NOT ADDRESSED` — and
    the weakening is **itself a new HIGH finding**, whatever the repair log
    says about the original.

    Check each `FIXED` claim against the artifact text, not against the
    log. Your job is to catch the case where the log is right about what
    was attempted and wrong about what happened.

    ## Edge Cases

    - **A prior finding is not in this round's set** — because the artifact
      it was about was deleted. Verdict it, and say in New findings that the
      artifact is gone. A finding whose subject vanished is not closed.
    - **The repair log claims a finding was fixed, but the artifact at
      `Where:` is unchanged.** `NOT ADDRESSED`, quoting the unchanged line.
      This is the round's most common real outcome and the one most easily
      waved through.
    - **The repair fixed the finding and broke something the previous audit
      never flagged.** The breakage is a new finding at its own severity.
      "It was already broken" is a reason to lower the bar, not the finding.
    - **The repair changed a value the previous audit called exact.** That
      is weakening by another name: `NOT ADDRESSED`, plus a HIGH for the
      loosening itself.
    - **[REPAIR_DIFF] is present but touches only whitespace, comments, or
      reformatting.** The findings are not addressed, and you should say the
      round was a no-op — that is a signal to the controller, not a detail.

    ## When You Cannot Proceed

    A precondition failure is the only reason to stop. Return the `BLOCKED`
    block from `## What You Return`, naming the reason, and do not write an
    audit file. Never: grade findings against a repair log that is not
    there; invent the previous round's findings from the artifact; or
    quietly drop the findings you could not reach to produce a usable
    verdict. A partial round reported as a complete one is the exact
    failure a fresh re-auditor exists to prevent.

    ## Self-Critique Before You Return

    1. **Did you read the diff before the findings?** If not, you have
       already failed the round's only structural advantage.
    2. **Did any mechanical check get skipped because "it was fine last
       time"?** Run it. That reasoning is how a broken link survives three
       rounds.
    3. **Did you follow every renumbering to its end?**
    4. **Did you accept any `FIXED` without opening the artifact?** Open it.
    5. **Is your verdict consistent with your counts?** Recompute it —
       `PASS` means zero HIGH and zero MEDIUM.

    ## Verification

    Every line number you cite, open and confirm. Your verdicts are the last
    word before the next phase proceeds; a wrong line number here costs more
    than the finding is worth.

    ## The file you write

    ```markdown
    ---
    kind: critique
    component: [COMPONENT]
    initiative: [INITIATIVE_ID]
    round: [ROUND]
    verdict: PASS | FAIL
    high: <n>
    medium: <n>
    low: <n>
    created_at: <utc>
    updated_at: <utc>
    ---

    # Critique — [COMPONENT], round [ROUND]

    ## 1. Impact of the repair

    What the diff actually changed, and what you checked as a consequence.
    Lead with this, because you read it before the findings and that is the
    point.

    | Change | What I re-checked because of it | Result |
    |---|---|---|

    ## 2. Closure of round [PREV_ROUND] findings

    | ID | Claimed | My verdict | Evidence |
    |---|---|---|---|

    One row per prior finding. Anything the repair log did not mention is
    `NOT ADDRESSED` by default.

    ## 3. New findings

    Including every weakening the repair introduced. Same structure as a
    first-round audit: check, class, `file:line`, evidence, confidence, what
    is wrong, why it breaks the next phase, proposed repair.

    ## 4. Checks I ran

    | Check | Full or scoped | What I inspected | Result |
    |---|---|---|---|

    Mechanical checks say `full`. Judgemental checks say `scoped` and name
    the region.

    ## 5. Observations

    Pre-existing MEDIUM and LOW findings outside the changed regions belong
    here as demoted observations, not as new findings — a round must not
    become an unbounded re-planning exercise. `None.` if none.
    ```

    ## What You Return

    Your final message is exactly this, and nothing else:

    ```
    AUDIT: [AUDIT_FILE]
    VERDICT: PASS | FAIL
    FINDINGS: high=<n> medium=<n> low=<n>
    CLOSED: <n>/<n prior findings>
    WEAKENING: <n>
    CHECKS_RUN: <n>/<n>
    ```

    A precondition stop returns instead of this, with the reason named:

    ```
    AUDIT: none — precondition failed
    VERDICT: BLOCKED
    REASON: <empty repair diff | no repair log | malformed prior audit | unreadable catalog>
    ```

    Then one line per HIGH finding, at most 100 characters, prefixed with
    its ID:

    ```
    H1: <headline>
    ```
```

**Placeholders — every one is required:**

| Placeholder | Value |
|---|---|
| `[MODEL]` | top tier — see Model Selection in `executor-execution` |
| `[INITIATIVE_ID]` | e.g. `INIT-0004` |
| `[COMPONENT]` | the component key — e.g. `architecture` |
| `[PHASE]` | the phase this component gates |
| `[CATALOG_KEY]` | catalog name from `exec-critique INIT_ID COMPONENT catalog` |
| `[COMPONENT_SET_FILES]` | every artifact in the set |
| `[UPSTREAM_FILES]` | upstream documents the catalog names as required evidence |
| `[ROUND]` | the round this audit writes — `R02` or `R03`, as two digits |
| `[ROUND_NO]` | the same round without the `R` prefix, for the `audit` subcommand |
| `[PREV_ROUND]` | the round whose findings you are closing — `R01` or `R02` |
| `[PREV_ROUND_NO]` | the same without the `R` prefix, for the `repair` subcommand |
| `[ROUNDS_LEFT]` | `0` on `R03`, otherwise `1`. Zero means your report is the last one before the human decides. |
| `[PREV_AUDIT_FILE]` | the previous round's audit file |
| `[REPAIR_FILE]` | from `exec-critique INIT_ID COMPONENT repair [PREV_ROUND_NO]` |
| `[REPAIR_DIFF]` | the controller's `git diff` of the repair |
| `[AUDIT_FILE]` | from `exec-critique INIT_ID COMPONENT audit [ROUND_NO]` — never hand-built |
