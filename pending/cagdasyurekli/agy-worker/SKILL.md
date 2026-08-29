---
name: agy-worker
description: Let Codex use Google Antigravity CLI (agy) for repository exploration, feature work, and project-scale implementation. Codex owns the diff review, verification, repair loop, and transparent delivery assurance; agy is not limited to mechanical edits or predeclared files.
---

# Use agy to explore, build, and repair

`agy-worker` is for making progress on real repository work. Default to the workflow
that matches the user's request; do not decline merely because files, architecture, or
verification commands must be discovered during the work.

## Before dispatch

`agy` is an external CLI backed by Google/Gemini services. Before the first dispatch
for a repository, tell the user which repository/path scope may be read and obtain
explicit approval to send the task and readable repository content to the provider,
unless the user has already approved that exact transmission. Do not put credentials,
private keys, unrelated local files, raw worker logs, or local controller state in the
prompt.

Before every provider-launch attempt (initial start/run, resume, continue, and restart), tell the user in one or two concise user-facing sentences what task is being sent to AGY.
Include a short public-safe task label, caller-selected model information, caller-selected effort when separately selectable, and the exact resolved model slug.
For default selection where no model is selected or the default tier is used, state truthfully that the provider default model is used and that model or effort is unresolved, without inventing a resolved slug or thinking level.
For fixed/compound/literal models where effort is not separately selectable, state that accurately without inferring backend reasoning or inventing a thinking level.
The notice must precede every dispatch attempt and remain accurate afterward.
If preflight fails before provider launch, explicitly state that the task was not sent to AGY.
If provider reach is genuinely uncertain, state that it is unverified rather than claiming success.
Direct model and effort selection remain caller-owned; recommendations are advisory.

Resolve the installed skill instead of guessing a checkout path:

```bash
PIPELINE="$(bash "$SKILL_ROOT/scripts/resolve-pipeline.sh")" || exit $?
```

Optionally inspect offline readiness before spending quota:

```bash
"$PIPELINE/doctor.sh" --repo /absolute/path/to/target
```

`ready` covers only offline prerequisites. `review-required` does not prevent the
agy-owned default or an explicitly approved literal model; it prevents only reviewed
matrix resolution. `not-ready` is a real dispatch blocker. The doctor never tests
auth, provider availability, task quality, or a future job.

## Choose a workflow

| User request | Pass | agy mode | Codex must do |
|---|---|---|---|
| Explore, inspect, review, understand, or make a plan | `--workflow explore --max-cycles 2` | `plan` | Report useful findings, spot-check material claims, and state coverage limits. |
| Add a feature, refactor, write tests, or make a bounded repair | `--workflow task --max-cycles 2` | `accept-edits` by default | Inspect the diff and run relevant checks; request a bounded repair when they fail. |
| Build an app, complete a project, make a broad implementation, or audit-and-fix | `--workflow project --max-cycles 5` | `accept-edits` | Let agy work across the disposable worktree; then run build/test/lint and continue the same conversation with driver-owned results. |

`explore` and `task` accept `1..2` cycles and default to `2`; `project` accepts
`1..5` and defaults to `5`. Legacy raw mode is one attempt and cannot take
`--max-cycles`.

Personas are optional prompt specializations. Use them only when they help the task;
they never authorize dispatch, prove quality, or make a broad task inadmissible. A
plain `explore` job is valid. A broad report is informative, not proof that every
semantic path was inspected.

Do not choose `project` solely to avoid thinking through the request. Ask for product
intent when it is genuinely missing, but let the worker discover ordinary repository
structure and test entry points.

For material UX, lifecycle, trust-boundary, security, data-semantics, or other domain plans:
A coordinator and suitable domain expert must co-plan.
Freeze user journeys, acceptance tests, and authority/privacy constraints before implementation.
The final acceptor must be a different agent or fresh context; no planner or implementer may self-accept.
Purely mechanical changes are exempt.
Verification v2 and the controller bind candidate evidence, not agent identity or governance.
The final human-readable handoff must report the planner/reviewer separation.

## Prepare an isolated target

Run every edit job in a branch-backed disposable worktree. The lifecycle helper binds
the repository, immutable base, worktree, branch, and job ID in private state:

```bash
TARGET=/absolute/path/to/target-repo
BASE="$(git -C "$TARGET" rev-parse HEAD)"
STATE_DIR="$(mktemp -d -t agyworker-job-state.XXXXXX)"
WT="$(mktemp -d -t agyworker-job-worktree.XXXXXX)"
rmdir "$WT"
"$PIPELINE/job.sh" init --state "$STATE_DIR/job.json" \
  --repo "$TARGET" --worktree "$WT" --branch "agy/job-12345" \
  --base "$BASE" --job-id job-12345
```

The worker may write anywhere in that worktree for a project workflow. Do not allow
writes into `.git`, outside the worktree, through a symlink escape, into local secret
files, or into user-denied paths. Never ask the worker to run shell commands: under
agy sandboxing they run in a scratch directory, not the repository. Use absolute
paths in the prompt and pass `--workdir "$WT" --add-dir "$WT"`.

## Dispatch and measure quality

For a normal task, emit the mandatory user-facing notice, dispatch once, and keep stdout only when exit status is zero:

```bash
printf '%s\n' "$TASK" | "$PIPELINE/agy-worker.sh" \
  --workflow task --workdir "$WT" --add-dir "$WT" > "$STATE_DIR/envelope.json"
```

For an explicit workflow, emit the mandatory user-facing notice and start the local controller when its state must safely track
multiple same-conversation repair cycles:

```bash
printf '%s\n' "$TASK" | "$PIPELINE/agy-worker.sh" start \
  --workflow project --max-cycles 5 --workdir "$WT" --add-dir "$WT"
```

Use `status` or bounded `wait` for a deliberately started job. Progress renews only
the idle lease; it does not prove correctness or grant unlimited runtime. The defaults
are `10m` idle, `2h` initial hard deadline, and `12h` maximum. `extend` can make a
bounded, state-SHA-approved extension while fresh progress exists. `cancel` describes
local process closure, not proven remote-provider cancellation.

Codex owns quality measurement:

1. Inspect the actual diff and identify project-owned build, test, lint, or type-check
   commands from the repository and its CI configuration.
2. Run those commands itself. Never execute `commands_run` or `tests_run` from an agy
   envelope.
3. Convert only the bounded, driver-owned result into Verification v2 JSON bound to
   the current candidate SHA. It includes check counts, coverage, evidence/gap counts,
   and `diff_review_complete`; do not pass raw prompts, source, logs, secrets, or
   worker prose back through this channel. V1 is readable compatibility data, never
   authority for `continue` or `finalize`.
4. For any explicit `explore`, `task`, or `project` candidate, if a driver check fails
   or is missing and the cycle budget remains, emit the mandatory user-facing notice
   for the continuation attempt and continue the exact conversation; do not silently
   start a new provider attempt:

```bash
"$PIPELINE/agy-worker.sh" continue --job-id "$JOB_ID" \
  --approve-state-sha "$STATE_SHA" < "$STATE_DIR/verification.json"
```

5. When Codex has completed its checks or the budget is exhausted, finalize with the
   same strict driver-owned verification JSON and one accurate assurance label:

```bash
"$PIPELINE/agy-worker.sh" finalize --job-id "$JOB_ID" \
  --approve-state-sha "$STATE_SHA" \
  --assurance verified < "$STATE_DIR/verification.json"
```

Codex's `verified` policy is strict: `explore` requires complete coverage, zero
unresolved gaps, zero failed checks, and zero missing checks; `task`/`project` require
at least one passed check, zero failed/missing checks, and completed driver diff review.
Use `partially_verified` for a useful candidate with unresolved, failed, or unavailable
checks; use `rejected` or `blocked` only for Codex's actual decision. The controller
validates the enum and current bindings, then persists that exact Codex declaration; it
does not derive a different label from the verification counters. A bounded repair may
be requested for advisory, coverage-gap, or review-driven evidence as well as a failed
or missing check. Keep partial work for review; do not delete it simply because a
quality check failed. `restart` starts a new conversation, requires explicit user direction,
and must be preceded by the mandatory user-facing notice.

The provider-facing envelope may omit only `commands_run` and `tests_run`; the
controller restores those omissions to empty arrays, then requires the canonical
envelope with both fields present. `summary` is capped at 8,192 characters. Never
execute worker command/test claims; a non-empty array is a gate rejection, not
evidence.

For a bounded candidate that needs gate/receipt evidence, run `verify-job.sh` with the
immutable base, a suitable `--only` policy when one exists, and driver-authored
`--verify` commands. A passed gate is strong candidate evidence, not a merge, release,
or claim of general correctness.

## Hard stops

Do not dispatch or continue when the request requires any of these without the
necessary authorization or safe scope:

- provider transmission approval is absent;
- the requested path is outside the approved worktree, `.git`, a credential/secret,
  a symlink escape, or user denylist;
- the request would use dangerous permission/approval bypass flags;
- the request would commit, push, open a PR, submit feedback, publish, install tools,
  or apply an update without the separate approval required for that external action.

Do not confuse a hard stop with ordinary uncertainty. Unknown files, missing initial
test commands, broad architecture, lack of a persona, a partial worker answer, or a
failed first check should normally lead to discovery, same-conversation repair, or
transparent partial delivery instead.

## Selection, failure, and maintenance rules

Model and effort selection belong to the caller. Recommendations are advisory only:
never replace the caller's selection, invent a thinking-level flag, or escalate
permission, authentication, scope-policy, or human-required outcomes. With no
selector, leave the provider's default intact. Use `--literal-model` only when the
caller explicitly selects that unreconciled pass-through surface.

The reviewed matrix remains evidence for its accepted version. Every direct caller
selection requires both a bounded safe-target `--version` probe and strict critical
`--help` structural probe. An exact matrix-version match proceeds mechanically;
installed-version drift requires Codex's explicit `--compatibility-disposition proceed
--approve-help-sha SHA256`. Codex must locally inspect bounded raw `agy --help` and
independently verify that SHA against the sanitized review evidence; never copy a
digest blindly or infer semantic usefulness from option-local prose. Before every
reviewed direct dispatch, including an exact-version match, Codex must inspect the
current bounded raw help and stop if the exact caller-selected model or effort cannot
be honored. Structural controller acceptance is not semantic approval, and the
controller must not encode provider-prose matching. Preserve the exact resolved caller slug, record model
availability as `not_assessed`, and make no provider-model availability claim. A
final reprobe failure is a local selection-preflight failure:
do not launch, rewrite selection, retry, or recommend. No same-job `resume` or
`restart` is safe for this state; Codex must review current sanitized `agy --help`
evidence and create a new job using the same caller-selected model and effort.

No automatic fresh retry or continuation exists. A candidate-free failed state other
than `selection_preflight_failed` may allow `resume --approve-state-sha SHA` into the
exact stored conversation (preceded by the mandatory user-facing notice) or explicit
fresh `restart --approve-state-sha SHA` (also preceded by the notice). A terminal provider `ERROR` (exit `25`) with a
valid candidate requires `result`, driver Verification v2, then `continue` or
`finalize`; it is never resumed. A `CANCELED`/`CANCELLED` candidate (exit `22`) is
preserved for `result` and finalization, or explicit fresh restart; it is never resumed
or continued. Do none of these automatically. Status is controller truth, not provider
truth. Worktree reconciliation captures the baseline before provider launch, captures
the terminal candidate after provider-group reap, and recomputes the exact digest
before queued `Popen`, `continue`, or `finalize`. Its bounded no-follow double-manifest
comparison binds Git, index, root, and selected-Git target facts under
controller-managed provider quiescence; drift or unavailable evidence fails closed.
Treat it only as a physical-change signal, never as a clean candidate, completed
review, acceptance, or semantic recommendation. It is not a
filesystem snapshot, FSEvents watcher, or hostile same-user tamper defense: the local
owner, same-UID processes, and OS administrators are trusted, and mutation after an
entry's final read remains a portable residual.

V9 uses `dispatching` for an active initial, resume, or restart attempt;
`attempt-failed` for a pre-candidate failure; `awaiting-verification` for a recognized
candidate; `repairing` for an active continuation; and `repair-failed` for an actual
failed continuation attempt. Controller terminal phases are `completed` or `blocked`;
exact Codex driver decisions/dispositions are `verified`, `partially_verified`,
`rejected`, or `blocked`. Public state adds candidate
recognition/source/availability, driver disposition, failure stage, `last_activity`,
and mechanically derived `available_actions`. `next_action` and its safe current-SHA
command are deprecated mechanical aliases, not controller recommendations.
`assurance` is public only after bound driver finalization; `phase` is deprecated raw
compatibility storage and `controller_phase` is the mechanical current projection.
`last_activity` is only
`provider_initialized`, `progress_signal`, or `terminal_received`: it is nonsemantic.
`has_prior_candidate` is deprecated and does not mean a clean worktree. V1 remains
read-only. A V3/V4 current result can make its first lifecycle transition only when
`status` supplies an exact `migration_binding_sha256` and the command receives both
that digest and the current state SHA; it is recomputed under the transition lock.
`last_success_*`-only V3/V4 evidence remains read-only. Persisted V5/V6 state retains its exact legacy digest;
V7 retains its exact semantic-v1 digest; and V8 retains its explicit semantic-v1
algorithm. An approved V5/V6 transition proves its legacy state, then atomically
captures a fresh semantic-v1 V9 baseline/candidate; V7/V8 reuse an exact semantic
proof. V9 separately persists stable no-follow root/Git authority and excludes mutable
worktree, index, HEAD, ref, and object content. `status`, `wait`,
`result`, `resume`, `restart`, `continue`, and `finalize` default to JSON and accept text; text is
three sanitized driver-owned lines. Every emitted action or stale-approval rerun command uses
`"$PIPELINE/agy-worker.sh"`; export the resolved `PIPELINE` value before copying and running it.

Those lines distinguish an unreviewed current bound result, a finalized current bound
result, and V3/V4 historical result evidence. Only an unreviewed current bound result
can supply Verification v2 or an eligible `continue` or `finalize`; a result whose
`verified`, `partially_verified`, `rejected`, or `blocked` disposition is already
recorded offers only optional finalized-result JSON readback and does not invite a new
Verification v2, `continue`, or `finalize`. Historical evidence is readable only.

### Reading lifecycle JSON and supplying Verification v2

Read public JSON in this order: `status` first for `state_sha256`,
`controller_phase`, `cycle`/`max_cycles`, `failure_stage`, and
`available_actions`; use `candidate_sha256` only when `result_available` is `true`;
then retrieve `result` only when its mechanically derived action is present. Review
the bound result and build driver evidence before choosing an eligible `continue` or
`finalize`; the controller chooses neither. A `null` candidate hash is not
Verification v2 input.

Run driver checks that can create bytecode, caches, coverage files, or generated output
in an isolated verification copy. Do not try to restore the candidate by deleting or
regenerating artifacts: tracked, untracked, deleted, and ignored paths all remain part
of its strict binding. Inspect Git-dependent facts read-only against the candidate,
then build/test the copy, which deliberately has no `.git` administration:

```bash
VERIFY_PARENT="$(mktemp -d -t agyworker-verify.XXXXXX)" || exit $?
VERIFY_PARENT="$(CDPATH= cd -- "$VERIFY_PARENT" && pwd -P)" || exit $?
VERIFY_DIR="$VERIFY_PARENT/candidate"
"$PIPELINE/agy-worker.sh" verification-copy --job-id "$JOB_ID" \
  --destination "$VERIFY_DIR" --format text
( cd "$VERIFY_DIR" && /usr/bin/python3 -m pytest -q )
```

The helper rebinds the current candidate before and after a no-symlink-following copy.
It preserves regular files and executable bits, and rebases every contained symlink to
an equivalent relative target in the copy. It rejects broken/outward/Git-admin links,
excludes `.git`, and records neither acceptance
nor a driver result. The destination must be a new, canonical owner-private directory
outside the candidate; any detected source drift fails closed.

This is a bounded quiescent-owner assumption, not same-UID tamper resistance. A local
same-UID actor can still replace a regular file with an outward link only during a read
and restore it before the later checks. A copy failure never reports success and leaves
no usable verification destination. After wrapper argument parsing, unavailable,
binding, copy, and destination failures return `20`; malformed wrapper arguments return
`64`.

`available_actions` is canonical. `next_action`/`next_action_command`,
`has_prior_candidate`, and raw `phase` remain deprecated compatibility aliases; they
are not recommendations or acceptance facts, and no public field is removed.

Verification v2 has no separate public schema. Its canonical validator is
`_validate_verification` plus `_require_current_candidate_verification` in
`"$PIPELINE/scripts/agy_dispatch.py"`; it permits no unknown fields. This is the
install-relative runtime authority pointer after `resolve-pipeline.sh` succeeds.
This complete copyable example obtains the candidate digest only from public status:

```bash
: "${PIPELINE:?set PIPELINE to the resolved skill runtime}"
: "${JOB_ID:?set JOB_ID to the controller job ID}"
: "${STATE_DIR:?set STATE_DIR to an existing private state directory}"
test -d "$STATE_DIR" || { echo "STATE_DIR is not a directory" >&2; exit 64; }

STATUS_JSON="$("$PIPELINE/agy-worker.sh" status --job-id "$JOB_ID" --format json)"
STATE_AND_CANDIDATE="$(printf '%s\n' "$STATUS_JSON" | python3 -c '
import json, re, sys
status = json.load(sys.stdin)
state_sha = status.get("state_sha256")
candidate = status.get("candidate_sha256")
if not isinstance(state_sha, str) or re.fullmatch(r"[0-9a-f]{64}", state_sha) is None:
    raise SystemExit("status state SHA is unavailable")
if status.get("result_available") is not True or not isinstance(candidate, str) or re.fullmatch(r"[0-9a-f]{64}", candidate) is None:
    raise SystemExit("status has no current bound candidate")
print(state_sha, candidate)
')" || exit $?
read -r STATE_SHA CANDIDATE_SHA <<EOF
$STATE_AND_CANDIDATE
EOF

python3 - "$CANDIDATE_SHA" > "$STATE_DIR/verification-v2.json" <<'PY'
import json, sys

json.dump({
    "schema_version": 2,
    "summary": "driver reviewed the bound candidate and found one repair",
    "passed_checks": ["unit"],
    "failed_checks": ["targeted-regression"],
    "advisory_checks": 0,
    "missing_checks": 0,
    "candidate_sha256": sys.argv[1],
    "coverage": "partial",
    "verified_findings": 1,
    "unresolved_gaps": 1,
    "diff_review_complete": True,
}, sys.stdout, sort_keys=True, separators=(",", ":"))
sys.stdout.write("\n")
PY

"$PIPELINE/agy-worker.sh" continue --job-id "$JOB_ID" \
  --approve-state-sha "$STATE_SHA" < "$STATE_DIR/verification-v2.json"
```

`resume`, `restart`, `continue`, `finalize`, `cancel`, and `extend` require a current
`--approve-state-sha`; `wait` uses `--after-state-sha`; read-only `status`/`result`
need neither. Both resume and restart show their approval flag in help. Direct
reviewed selection has a separate compatibility approval:
`--compatibility-disposition proceed --approve-help-sha SHA256`; it never changes the
caller choice or grants lifecycle authority. `status`, `wait`, `result`, `resume`,
`restart`, `continue`, and `finalize` accept `--format json|text`; JSON is canonical.

An exact agy `1.1.13` terminal quota response may appear as exit `24` with a sanitized
`retry_after_seconds` countdown. Treat it as a stop/explicit-resume decision: never
sleep, retry, restart, or change the selected model automatically. The classifier is
version- and byte-shape-bound. Wrong-version or altered quota terminals without a
report are `invalid_envelope` with exit `4` and
`failure_stage=missing_structured_output`; the exact recognized terminal instead
records `provider_quota_exhausted` with exit `24` and the same failure stage.

For bugs or improvement reports, use the local draft-first `bug-report.sh` flow. It
requires review of the exact sanitized body and its matching SHA-256 before any GitHub
submission; never submit feedback automatically.

Before changing agy-facing behavior, run `./ground-truth.sh` and inspect `agy --help`.
agy can exit zero with empty output; the answer is `result.structured_output`, not the
echoed schema. Before delivery, run the relevant offline suite and the project checks
you selected. Do not claim provider success, completeness, or release status from
offline evidence alone.
