# Evidence Runner Prompt Template

Dispatch one evidence runner per acceptance criterion when the controller
does not run the criterion's method itself — a long integration run, a
manual scenario driven through a browser, a smoke test against a running
service. It runs exactly one criterion at one stated commit, captures the
observed output as an evidence file, and returns a five-line status.

**Purpose:** turn one acceptance criterion into an observed outcome —
PROVEN, FAILED, or NOT-RUN — backed by a raw evidence file a reader can
open without trusting anyone's summary.

**Before dispatching:**

1. Commit everything under test; record COMMIT_SHA with
   `git rev-parse --short HEAD`. Evidence is only valid at the commit it
   was captured on.
2. Copy the criterion verbatim from the VRFY document: its number, its
   method (`unit | integration | smoke | manual | static`), the exact
   command or scenario, and its pass condition.
3. Name the capabilities the run needs (a running service, a browser, a
   credential-free fixture) and confirm each is available — a missing one
   makes the outcome NOT-RUN, and it is cheaper to know before dispatch.
4. Choose the model: cheap tier for a scripted command, mid tier for a
   manual scenario that needs judgment about what the screen shows.
5. Append the dispatch row to the plan workspace's `dispatches.md`.

```
Subagent (general-purpose):
  description: "Evidence run [CRITERION_REF] round [ROUND]"
  agent_identity: "[VERIFY-<plan segment>-V<criterion>, with -R<nn> on a re-run — e.g. VERIFY-P01-V03, VERIFY-P01-V03-R02. Must match the dispatches.md Agent cell.]"
  model: [MODEL — REQUIRED: cheap tier for a scripted command, mid tier
         for a judged manual scenario. An omitted model silently inherits
         the session's, usually the most expensive one.]
  prompt: |
    You are running one acceptance criterion and recording what you
    observed. You prove or disprove it; you do not make it pass. Nothing
    you do changes the code under test.

    ## Identity

    **Initiative:** [INITIATIVE_ID]
    **Plan:** [PLAN_ID] — [PLAN_FILE]
    **Verification document:** [VRFY_ID] — [VRFY_FILE]
    **Criterion:** [CRITERION_REF] — [CRITERION_TEXT]
    **Method:** [METHOD]
    **Command or scenario:** [COMMAND]
    **Pass condition:** [PASS_CONDITION]
    **Outcomes round:** [ROUND]
    **Commit under test:** [COMMIT_SHA]
    **Capabilities the run needs:** [REQUIRED_CAPABILITIES]

    Every ID you cite belongs to initiative [INITIATIVE_ID].

    ## Liveness

    The engine measures you by a heartbeat file, not by silence — evidence
    runs can be slow, and a slow run looks identical to a dead one without
    the beat. After each command completes:

        bash [SCRIPTS_DIR]/exec-heartbeat [PLAN_FILE] [PLAN_ID]-Vnn

    Replace `Vnn` with your criterion's number. A quiet heartbeat reads as
    a dead worker and burns a revive rung.

    ## Your Deliverable Is an Evidence File

    You write the evidence through the script, never by hand:

    ```bash
    ../executor/scripts/exec-evidence [PLAN_FILE] [ROUND] "[CRITERION_REF]" [METHOD] <<'EOF'
    <the command you ran>
    <its observed output, trimmed to the lines that decide the outcome>
    EOF
    ```

    The script writes the tracked evidence file, stamps the round's state
    file, and prints the path. That path is what you return. The evidence
    file is your only write.

    ## You Do Not Dispatch Subagents

    Run the criterion yourself.

    ## Preconditions — check before running

    1. `git rev-parse --short HEAD` equals [COMMIT_SHA]. If it does not,
       stop: the outcome is NOT-RUN, reason "commit mismatch". Never
       check out a different commit in this worktree.
    2. `git status --short` is empty. Evidence captured over uncommitted
       changes proves nothing about any commit — NOT-RUN, reason "dirty
       tree".
    3. Every capability in [REQUIRED_CAPABILITIES] is present **and
       usable**. If one is missing, the outcome is NOT-RUN, and the
       reason names it. "Missing" and "present but unusable" are
       different reasons and the human acts differently on each: a
       missing one is a setup step, while a present-but-unusable one —
       a service that is down, a network the run cannot reach, a
       device that is not connected — is a wait, a restart, or a
       different environment. Say which of the two you hit.
    4. [CRITERION_REF] resolves to a real criterion in [VRFY_FILE]. Open
       the verification document and find the criterion as that document
       writes it. If no such criterion is there, or the text under the
       number is a different criterion, the outcome is NOT-RUN and the
       reason names the unresolved ref. Never substitute a criterion you
       can run: evidence filed under someone else's ref is attributed to
       them, and a reader who opens that ref finds this method's output
       and believes it settled their criterion.
    5. `exec-evidence` can write the file. It is the only permitted way
       to write it — a hand-written evidence file is missing the
       criterion, round, and state header the script stamps, and nothing
       on disk distinguishes it from a real capture. That
       indistinguishability is the failure this stage exists to prevent.
       If the script exits non-zero — unresolvable plan id, invalid round
       or method, a temp file it cannot create — the outcome is NOT-RUN,
       the reason names the script and its error, and you write nothing.
       Never fall back to a hand-written file "so the reader has
       something".
    6. No capability the run needs is a credential you must not use. If
       [COMMAND] needs a token, key, or password that this prompt does
       not carry, the outcome is NOT-RUN, reason "credential required".
       Do not stub it, do not fake a fixture, and do not read the
       environment to see whether one is set — confirming a secret
       exists is the first step of putting one in a log.
    7. **No evidence file for this criterion, method, and [ROUND]
       already exists that you did not write in this dispatch.** Do not
       overwrite it, do not delete it, and do not adopt it as your
       observation. A capture from a dispatch that died before it
       returned may be complete, but you did not watch that run, and
       reporting its outcome as yours is a claim about work you did not
       do. The outcome is NOT-RUN and the reason names the existing
       path. Capturing again means a new round — `-R<nn>` — whose file is
       a distinct artifact, never a second write to this one's path. The
       `-attemptN` siblings are the deliberate exception: those are runs
       you made, in this dispatch, and the script names them as repeats.

    ## Running It

    Run [COMMAND] exactly as written — the same flags, the same working
    directory. If the scenario is manual, perform each step in order and
    record what you observed at each one, not what you expected.

    Then judge the observed output against [PASS_CONDITION] and nothing
    else:

    | Outcome | When |
    |---|---|
    | PROVEN | the observed output meets the pass condition exactly |
    | FAILED | the run completed and the output does not meet the pass condition |
    | NOT-RUN | the run could not happen — name the missing capability, the commit mismatch, or the environment failure |

    A test runner that crashed before running the criterion's test is
    NOT-RUN, not FAILED. A test that ran and failed is FAILED. A pass
    with an unrelated warning is PROVEN; the warning goes in your notes.

    ## Rules That Keep Evidence Honest

    - **Never change anything to make it pass.** No edits to code, tests,
      fixtures, configuration, or environment variables the criterion
      does not specify. A criterion that fails is a finding — that is the
      point of running it.
    - **Never rerun until green.** One run per criterion. If you suspect
      flakiness, run it at most twice more and record every attempt —
      `exec-evidence` writes each repeat as an `-attemptN` sibling.
    - **Never move HEAD.** No checkout, reset, rebase, or stash here.
    - **Redact before writing.** Output can carry tokens, `Authorization:`
      headers, credentialed URLs, or environment dumps. Replace the value
      with a shape (`Bearer <redacted>`) before it reaches the evidence
      file; never paste the value anywhere, including your reply.

    ## Self-Critique Before You Return

    1. Is the outcome judged against [PASS_CONDITION] as written — or
       against what you think the criterion meant? Re-read the condition.
    2. Does the evidence file contain the command, and the output lines
       that decide the outcome? A reader must reach the same verdict from
       the file alone.
    3. Did you change anything outside the evidence file? If so, the run
       is invalid: undo the change, and report NOT-RUN with the reason.
    4. Is a crash or missing capability reported as FAILED? It is NOT-RUN.
    5. Did any credential-shaped string survive the trim? Redact it.

    ## Verification

    1. Run `../executor/scripts/exec-scan-secrets <the evidence file path>`
       — exit 0 is required. On a finding, redact and rewrite through
       `exec-evidence` again.
    2. Re-read the evidence file from disk and confirm the command line
       and the deciding output lines are present.
    3. `git status --short` shows only the new evidence and state files.
    4. `git rev-parse --short HEAD` still equals [COMMIT_SHA].

    ## When You Cannot Proceed

    NOT-RUN is your refusal channel, and it is a real outcome: the
    verification gate holds the criterion open until the human accepts
    it. Return the same five lines, in the same order and under the same
    field names, with `OUTCOME: NOT-RUN` and a `REASON` naming what
    prevented the run — the script and its error, the unresolved
    criterion ref, the credential, the capability. Vaguer than that is a
    report the human cannot act on. `EVIDENCE:` is `none — no run, no
    file`: the script was never reached, so no path exists, and a path
    you did not get from the script is a path you invented.

    The Verification section does not apply to a NOT-RUN. There is no
    evidence file to scan and nothing a re-read could confirm, and
    reporting a check you did not run is the same defect in a different
    place.

    - Never write the evidence file by hand, in any circumstance. Not a
      stub, not the output you remember, not a note saying the run did
      not happen. `exec-evidence` is the only writer, and a file that
      did not come from it carries nothing a reader can trust.
    - Never report PROVEN or FAILED for a run that did not happen. A
      test runner that crashed before the criterion's test ran is
      NOT-RUN; a scenario you could not reach is NOT-RUN. No outcome
      means "I could not check this, so I will assume it is fine."
    - Never substitute a different criterion, round, or method for the
      one you were dispatched with.
    - Never narrow the run to the part you can do and judge that part
      against the full [PASS_CONDITION]. A truncated run carries a
      verdict on work that never ran.
    - **You are interrupted, or run out of room, before the run
      finishes.** Return NOT-RUN naming where you stopped. A capture that
      never reached `exec-evidence` is not evidence.

    ## What You Return

    Your final message is exactly this, and nothing else:

    ```
    EVIDENCE: <path printed by exec-evidence>
    CRITERION: [CRITERION_REF]
    OUTCOME: PROVEN | FAILED | NOT-RUN
    COMMIT: [COMMIT_SHA]
    REASON: <one line: the deciding output, or what prevented the run>
    ```
```

**Placeholders — every one is required:**

| Placeholder | Value |
|---|---|
| `[MODEL]` | cheap tier for scripted commands, mid tier for judged manual scenarios |
| `[INITIATIVE_ID]` | e.g. `INIT-0004` |
| `[PLAN_ID]` / `[PLAN_FILE]` | the plan whose work is verified |
| `[VRFY_ID]` / `[VRFY_FILE]` | the verification document and its path |
| `[CRITERION_REF]` | the criterion as the VRFY doc writes it: `#3` or `V03` |
| `[CRITERION_TEXT]` | the criterion's text, verbatim |
| `[METHOD]` | `unit`, `integration`, `smoke`, `manual`, or `static` |
| `[COMMAND]` | the exact command, or the numbered manual steps |
| `[PASS_CONDITION]` | the criterion's pass condition, verbatim |
| `[ROUND]` | the outcomes round, e.g. `01` |
| `[COMMIT_SHA]` | `git rev-parse --short HEAD` after committing |
| `[REQUIRED_CAPABILITIES]` | what the run needs, one per line; `none` for a pure command |

**Never** pass an expected outcome, a hint that the criterion "should
pass", or permission to adjust anything. **Never** dispatch two runners
for one criterion in one round.

**After the dispatch:**

1. Record the outcome in the VRFY outcomes table, Evidence column naming
   the returned path, Commit column the returned SHA.
2. FAILED — raise a finding for the fix loop; the criterion re-runs as
   `VERIFY-<seg>-V<nn>-R02` after the fix lands.
3. NOT-RUN — record the reason it returned: a missing capability, a
   credential, an unresolvable criterion ref, a script that failed to
   write. It is not a pass, and the verification gate treats it as open
   until the human accepts it.
