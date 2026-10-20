# Project lifecycle and verification

This guide owns the operational lifecycle after the repository, task, provider
transmission, and caller-selected model inputs are approved. The worker envelope is
input, never acceptance evidence. The driver reviews the bound candidate and supplies the
verification evidence.

Read [Security and compatibility](SECURITY_AND_COMPATIBILITY.md) before a first live
dispatch. Use [Troubleshooting](TROUBLESHOOTING.md) when a preflight, provider,
lifecycle, or verifier step fails.

## Approval, bindings, and launch notices

Human approval covers exact work and provider exposure. Preview, transmission, state,
candidate and dispatch SHA values bind their specified controller inputs; they grant
no authority by themselves. Refresh them only for an action still covered and
mechanically available. Whole-worktree launch approval binds content, kinds, full
file mode bits, symlink target hashes, readable manifest, provider isolation and
native grant profile.
Scoped transmission approval binds canonical read/write policy, readable path/kind
manifest, selected bytes and executable bits, isolation and grant profile; scoped
mode rejects symlinks and does not bind full POSIX permissions. These content
subdigests are inputs to the single human-approved `launch_approval_sha256`.
Its canonical `launch_authority` also binds the destination and Git base, normalized
task, constructed prompt and fixed transport templates, workflow/edit mode, model/effort,
cycle/time budgets, scoped repair, private self-verification manifest digest,
provider-env names, slash policy, additional directories and provider schema digest.
The preview displays the full task and every bound field. UTF-8 task input rejects
NUL and removes trailing LF only; stdin and `--task` use the same rule.
The controller recomputes actual initial authority before provider start; a stale
record names the changed field. The facade saves that record in private workflow
state. Advanced raw launches require the saved mode-0600 preview JSON through
`--approval-record`, alongside the human-approved digest.

The constructed task prompt and transport-template hashes bind fixed instructions.
The controller adds the validated attempt root and bounded current change hint;
these dynamic annotations are checked with the final provider `--print` bytes at
spawn, including native containment. Same-conversation repair feedback stays outside
the initial task hash and uses the existing approved repair lineage. Environment
values and private manifest contents are excluded from approval metadata.
Before an initial provider launch, show the owner a private review packet with:

- The exact task text (not the shorter public-safe launch notice), workflow/edit
  mode, selected model/effort or unresolved default, and retry/time budget.
- The exact scope policy and preview digest, or whole-worktree manifest and digest;
  the provider isolation mode and native grant profile when selected.
- Whether `--allow-scoped-repair` is enabled and, if self-verification is enabled,
  each manifest check's exact `argv`, ID, required/optional flag, timeout and output
  limit, plus the manifest's total time limit.
- Each `--provider-env` and `--verify-env` name and its resulting child exposure.

Keep any owner-private self-verification manifest outside the worktree and out of
the provider preview and prompt. The manifest's digest binds the reviewed private
commands; a later launch notice may summarize the task safely.
One upfront approval may cover predictable same-scope repairs; use initial
`--allow-scoped-repair` for multi-turn scoped work. New exposure, destination,
isolation, permissions or budget requires authority. A normal job needs neither
hand-authored JSON nor Goal. Capability preflight and the executable recheck still
run before every launch.

Before every provider-launch attempt (initial start/run, resume, continue, and restart), tell the user what task is being sent to AGY.
Include a short public-safe task label and the exact resolved model slug when known.
For default selection, say the provider default is used and the model is unresolved; do not invent a slug.
Report caller-supplied effort when present; otherwise say effort is unresolved, without inferring backend reasoning.
The notice must precede every dispatch attempt and remain accurate afterward.
If preflight fails before provider launch, explicitly state that the task was not sent to AGY.
If provider reach is genuinely uncertain, state that it is unverified rather than claiming success.
Direct model and effort selection remain caller-owned.

The notice is status, not another approval request. Covered repairs do not authorize
Git actions, acceptance, publication, installation, account actions or provider work
outside the approved job.

## Lifecycle at a glance

1. Bind an immutable base and branch-backed disposable worktree; keep private state outside it.
2. Review the content-free preview and obtain exact transmission/execution approval.
3. Dispatch, retrieve the bound candidate and inspect its actual Git diff.
4. Run driver-selected checks in an isolated copy; bind sanitized Verification v2 findings.
5. Repair in the same conversation within budget, or finalize and preserve useful work.

Whole-worktree approval covers every entry; provider scope stages reviewed content
and limits reconciliation. Session mode retains normal host access. Native mode adds
supported macOS scoped containment without fallback. See
[Security and compatibility](SECURITY_AND_COMPATIBILITY.md).

## Primary `run`, `status`, `verify-finalize` path

`SKILL_ROOT` is the directory containing `SKILL.md`; in Claude Code, use its
inline `${CLAUDE_SKILL_DIR}` substitution, not a Bash environment variable.
Resolve the installed runtime first:

```bash
PIPELINE="$(bash "$SKILL_ROOT/scripts/resolve-pipeline.sh")" || exit $?
```

For ordinary use, the facade creates the branch-backed disposable worktree and
owner-private state on the first preview call. Choose a unique job ID and a scope
file outside the target repository. Both `read` and `write` entries must be sorted
by path; `write` must be covered by `read`. For example, after selecting actual paths
that exist in the reviewed repository:

```json
{"schema_version":1,"kind":"agy-worker-provider-scope","read":[{"path":"src/parser.py","kind":"file"},{"path":"tests","kind":"tree"}],"write":[{"path":"tests","kind":"tree"}]}
```

Create the file with `umask 077` and keep it owner-private mode `0600`. The smallest
ordinary preview is:

```bash
TARGET=/absolute/path/to/approved-repository
JOB_ID=job-12345
SCOPE=/absolute/private/provider-scope.json
TASK='the exact approved bounded task'
"$PIPELINE/workflow.sh" run --preview --repo "$TARGET" --job-id "$JOB_ID" \
  --provider-scope "$SCOPE" --task "$TASK"
```

The preview gives `launch_approval_sha256`; the facade derives its state path under
`XDG_STATE_HOME` or `HOME/.local/state` as described below. Review the preview's
content and selected settings with the user before the approved run. Repeat the same
binding without `--preview`, supplying the exact approved digest and task:

```bash
STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"
STATE_HOME="$(cd "$STATE_HOME" && pwd -P)" || exit $?
REPO_KEY="$(python3 -c 'import hashlib,pathlib,sys; p=str(pathlib.Path(sys.argv[1]).resolve(strict=True)); print(hashlib.sha256(p.encode()).hexdigest()[:24])' "$TARGET")"
STATE="$STATE_HOME/agy-worker/workflows/$REPO_KEY/$JOB_ID/workflow.json"
TRANSMISSION_SHA='paste the exact reviewed launch_approval_sha256'
TASK='paste the exact privately reviewed task text'
ENVELOPE="$(dirname "$STATE")/envelope.json"
test ! -e "$ENVELOPE" || { echo "envelope path already exists" >&2; exit 64; }
( umask 077
  "$PIPELINE/workflow.sh" run --repo "$TARGET" --job-id "$JOB_ID" \
    --provider-scope "$SCOPE" --approve-transmission-sha "$TRANSMISSION_SHA" \
    --workflow task --task "$TASK" > "$ENVELOPE"
) || exit $?
test -s "$ENVELOPE" || { echo "approved run produced no envelope" >&2; exit 1; }
"$PIPELINE/workflow.sh" status --state "$STATE" --format json
```

This path creates the worktree; do not create one manually for ordinary use. The
preview starts no provider process and grants no approval. Record the returned state
path, keep it owner-private and outside the worktree, and emit the provider notice
immediately before the approved run. Whole-worktree approval is an explicit
exception; the advanced invocation below illustrates owner-chosen paths:

```bash
BASE="$(git -C "$TARGET" rev-parse HEAD)"
STATE_DIR="$(mktemp -d -t agyworker-state.XXXXXX)"
WT="$(mktemp -d -t agyworker-worktree.XXXXXX)"
STATE_DIR="$(cd "$STATE_DIR" && pwd -P)" || exit $?
WT="$(cd "$WT" && pwd -P)" || exit $?
rmdir "$WT"
JOB_BRANCH=agy/job-12345
git -C "$TARGET" worktree add -b "$JOB_BRANCH" "$WT" "$BASE"
"$PIPELINE/workflow.sh" run --preview \
  --state "$STATE_DIR/workflow.json" --repo "$TARGET" --worktree "$WT" \
  --branch "$JOB_BRANCH" --base "$BASE" --job-id "$JOB_ID" \
  --workflow task --task "$TASK" \
  > "$STATE_DIR/preview.json"
```

Keep `STATE_DIR` owner-private and outside both the repository and worktree. Review
the preview's whole-worktree manifest and `launch_approval_sha256` before this run:

```bash
ENVELOPE="$STATE_DIR/envelope.json"
test ! -e "$ENVELOPE" || { echo "envelope path already exists" >&2; exit 64; }

( umask 077
  "$PIPELINE/workflow.sh" run \
    --state "$STATE_DIR/workflow.json" --repo "$TARGET" --worktree "$WT" \
    --branch "$JOB_BRANCH" --base "$BASE" --job-id "$JOB_ID" \
    --approve-whole-worktree "$PREVIEW_SHA" --workflow task --task "$TASK" \
    > "$ENVELOPE"
) || exit $?
test -s "$ENVELOPE" || { echo "approved run produced no envelope" >&2; exit 1; }
```

This facade invocation explicitly approves whole-worktree dispatch; `--add-dir` does
not narrow provider reads. For selected-content dispatch, pass `--provider-scope FILE`
to both facade calls and approve the scoped preview with
`--approve-transmission-sha SHA256`. It stages only selected entries, but remains subject to
the boundaries in [Security and compatibility](SECURITY_AND_COMPATIBILITY.md).

Omitting both transmission modes fails before provider launch; use only the current
approval flags above.

The facade does not choose a model, assurance label, repair, retry, Git action, or
external write. `status --state "$STATE_DIR/workflow.json"` is read-only. For a bound
controller dispatch, copy `dispatch.state_sha256` from facade status and pass it as
`--approve-dispatch-sha` to `verify-finalize`; its former facade alias
`--approve-state-sha` is rejected. Advanced dispatcher and job lifecycle commands
retain their own `--approve-state-sha` flag. Rejected or routed gate receipts are
preserved without calling the lifecycle finalizer.

Pass each driver-owned verifier as a canonical JSON argv array:

```bash
RECEIPT="$STATE_DIR/evidence-receipt.json"
test ! -e "$RECEIPT" || { echo "receipt path already exists" >&2; exit 64; }

"$PIPELINE/workflow.sh" verify-finalize \
  --state "$STATE_DIR/workflow.json" \
  --receipt "$RECEIPT" \
  --envelope "$ENVELOPE" \
  --approve-dispatch-sha "$DISPATCH_STATE_SHA" \
  --verify-argv '["/usr/bin/git","diff","--check"]' \
  --verification-json "$STATE_DIR/verification-v2.json" \
  --assurance verified
```

Gate and `verify-finalize --verify-argv` verifiers run in the bound candidate; use
only commands known to be read-only there. Snapshot rejection detects changes to bound candidate state after
they happen, not isolation. Verifiers run untrusted candidate code with the user's
authority; the gate does not detect changes outside the candidate, including Git
hooks and configuration. Run Python, build, and test commands in the verification
copy below with `PYTHONDONTWRITEBYTECODE=1`, and record those driver results in
Verification v2. Never execute `commands_run` or `tests_run` from the worker envelope. An explicit
`--verify-shell SCRIPT` is an advanced compatibility surface requiring both verifier
network and credential-access acknowledgements. Historical `--verify SCRIPT` also
requires the legacy-shell acknowledgement.

## Controller state and actions

Use `status` first. Treat `available_actions` as the canonical mechanical action set;
deprecated `next_action`, `next_action_command`, `phase`, and `has_prior_candidate`
are compatibility aliases, not recommendations or acceptance facts.
For a facade-backed advanced `restart`, pass the same `--state "$WORKFLOW_STATE"`
alongside `--job-id "$JOB_ID"` and the current `--approve-state-sha "$STATE_SHA"`;
the workflow state resolves the bound log root. A fresh restart still needs an
explicit user decision and the usual provider notice.

Current bound jobs expose `provider_isolation` (`session` or `native`) and
`provider_execution` facts (`scope`, `agy_sandbox`, `native_containment`, `legacy`,
with `legacy` false). Unbound jobs may have no execution facts yet.

Only current dispatch/command formats load; finish or discard older jobs with their
creating release. Keep old artifacts untouched: there is no in-place migration or
capability-approval bypass. Format constants are `CURRENT_STATE_SCHEMA` and
`CURRENT_COMMAND_SCHEMA` in `runtime/scripts/agy_dispatch.py`, and
`BOUND_SCHEMA_VERSION`/`BOUND_FACADE_SCHEMA_VERSION` in `runtime/scripts/workflow.py`.
This also applies to ordinary old-format jobs that used no removed feature.

The current state (defined by `CURRENT_STATE_SCHEMA` in
`runtime/scripts/agy_dispatch.py`) uses `dispatching` for an active initial, resume, or restart attempt;
`attempt-failed` for a pre-candidate failure; `awaiting-verification` for a recognized
candidate; `repairing` for an active continuation; and `repair-failed` for a failed
continuation. `self-verifying` denotes the optional local check action. Terminal controller phases are `completed` and `blocked`. Driver
dispositions are separately `verified`, `partially_verified`, `rejected`, or
`blocked`.

Read public lifecycle JSON in this order:

1. `state_sha256`, `controller_phase`, `cycle`, `max_cycles`, `failure_stage`, and
   `available_actions` from `status`.
2. `candidate_sha256` only when `result_available` is `true`.
3. `result` only when its mechanically derived action is available.
4. Driver review and Verification v2 before choosing an eligible `continue` or
   `finalize`.

A null candidate hash is never Verification v2 input. Every emitted action or stale-approval rerun command uses the caller-resolved
symbolic launcher `"$PIPELINE/agy-worker.sh"`; export `PIPELINE` before copying it.

Controller-private state also preserves a sanitized
`provider_terminal_status` (`unknown`, `success`, `error`, or `cancelled`) for the
specific attempt. Public status omits it. It is not provider health, quota, routing,
model acceptance, task acceptance, billing evidence, or candidate acceptance.

There is no automatic retry or continuation:

- A candidate-free failed state may mechanically allow an exact-conversation
  `resume` or a fresh `restart`, each approved against current state. `restart`
  requires explicit user direction.
- A structurally valid provider `ERROR` candidate is retrieved and reviewed before
  an eligible `continue` or `finalize`; it is not resumed.
- A structurally valid `CANCELED` or `CANCELLED` candidate is preserved for review
  and finalization or an explicit fresh restart; it is neither resumed nor continued.
- `status`, `wait`, `result`, `extend`, and `cancel` describe local controller state,
  not proven remote-provider state.

## Optional checks and scoped repair

Initial `--allow-scoped-repair` binds the approved write scope, model, conversation
and budgets for task/project continuation. Covered candidate evolution can reuse that
approval; external drift or changed grants reject before another turn. Without the
initial grant, a changed scoped candidate is result/finalize-only.

The optional `--self-verification-manifest PATH` is driver-authored and owner-private.
It binds exact commands, required checks, optional IDs and limits at initial task/project
dispatch; explore does not support it. The worker may request approved optional IDs,
but required checks always run. Both options are available through `workflow.sh run`.

Use the offered `self-verify` action once per candidate attempt. It runs in a fresh
approved-content copy, without network or ambient credentials on supported macOS.
Approved system interpreters and explicit relative shell scripts are supported;
unqualified toolchains fail before execution. Logs stay private, preparation/execution
spend the existing total budget, and interrupted work is charged without automatic replay.

Bound advisory results may be reused with the offered `continue --use-self-verification`.
The driver decides whether to repair and emits the provider notice; manual Verification v2
remains available. These checks are optional when a focused command is known, never
finalize work and never substitute for independent diff review and driver acceptance.

## Isolated verification copy

Driver build/test commands and Python imports may create bytecode, caches, coverage
data, generated files, or other artifacts. Do not alter or clean the bound candidate
to make those outputs disappear. Inspect Git-dependent facts read-only against the
candidate, then run those checks in a separate copy with
`PYTHONDONTWRITEBYTECODE=1`:
For the ordinary facade path, `$STATE` above is the saved workflow state. In the
advanced path, replace the `WORKFLOW_STATE` assignment below with
`WORKFLOW_STATE="$STATE_DIR/workflow.json"`. The explicit state binds the existing
job and resolves its private log root.

```bash
WORKFLOW_STATE="$STATE"
VERIFY_PARENT="$(mktemp -d -t agyworker-verify.XXXXXX)" || exit $?
VERIFY_PARENT="$(CDPATH= cd -- "$VERIFY_PARENT" && pwd -P)" || exit $?
VERIFY_DIR="$VERIFY_PARENT/candidate"
"$PIPELINE/agy-worker.sh" verification-copy --job-id "$JOB_ID" --state "$WORKFLOW_STATE" \
  --destination "$VERIFY_DIR" --format text
( cd "$VERIFY_DIR" && PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m pytest -q )
```

The helper rebinds result, command, schemas, root, and candidate before and after a
no-follow copy. It preserves regular bytes and executable bits, rebases contained
symlinks within the copy, excludes `.git`, and rejects broken, outward, or
Git-administration links. The destination must be new, canonical, private, and outside
the candidate. This is an owner-controlled quiescence check, not same-UID tamper
resistance.

## Verification v2

Verification v2 has no separate public schema. The canonical validator is
`_validate_verification` plus `_require_current_candidate_verification` in
`"$PIPELINE/scripts/agy_dispatch.py"` after runtime resolution. It rejects unknown
fields and requires the current public candidate digest.

Use only sanitized driver observations, never prompts, source, raw logs, secrets,
worker prose, account data or private paths. Reuse checks only for identical candidate
bytes and relevant environment. This example records a passing check and completed
diff review:

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
    "summary": "driver reviewed the bound candidate and the focused check passed",
    "passed_checks": ["focused"],
    "failed_checks": [],
    "advisory_checks": 0,
    "missing_checks": 0,
    "candidate_sha256": sys.argv[1],
    "coverage": "complete",
    "verified_findings": 0,
    "unresolved_gaps": 0,
    "diff_review_complete": True,
}, sys.stdout, sort_keys=True, separators=(",", ":"))
sys.stdout.write("\n")
PY

"$PIPELINE/agy-worker.sh" continue --job-id "$JOB_ID" \
  --approve-state-sha "$STATE_SHA" < "$STATE_DIR/verification-v2.json"
```

Use the current `STATE_SHA` with eligible lower-level `continue` or `finalize`
commands. A bounded repair request may cite failed checks, missing checks, advisory
results, coverage gaps, or review findings. Failed product checks return concrete
sanitized feedback to the same AGY conversation for bounded repair; do not allow
silent direct-driver fallback after provider failure or exhausted budget. It must
continue the same conversation while budget remains and must be preceded by the
provider notice.

## Material planning governance

For trust-boundary changes, write a short design note covering options considered and residual risk, and obtain independent review.
No author is the sole acceptor of material work.
Verification v2 binds candidate evidence; it does not establish reviewer identity.

## Assurance and preservation

The controller validates and persists the driver's exact disposition; it does not infer a
different label from counters.

- `verified`: for `task` and `project`, at least one driver check passed, none failed
  or are missing, and diff review is complete. `explore` additionally requires
  complete coverage and no unresolved gaps.
- `partially_verified`: useful candidate with a failed, missing, unavailable, or
  incomplete check, or an unresolved coverage gap.
- `rejected`: the driver has reviewed and declines the candidate.
- `blocked`: a real authority, repository-boundary, provider, or execution block.

Keep accepted or useful partial work on its branch when a repair or time budget ends.
Neither a gate pass nor a finalized disposition commits, pushes, merges, releases, or
publishes anything.

## Advanced gate and receipt surface

The facade composes the lower-level dispatcher, lifecycle, gate, and receipt commands;
it does not replace their authority. For direct candidate gating, bind the immutable
full base commit, repeatable `--only` paths where appropriate, `--expect-edits` when a
no-op is unacceptable, and at least one driver-authored verifier:

```bash
"$PIPELINE/qa-gate.sh" --envelope "$ENVELOPE" --repo "$WT" --base "$BASE" \
  --only 'tests/**' --expect-edits \
  --verify-argv '["/usr/bin/git","diff","--check"]'
```

Exit zero means only that the gate accepted the exact exercised state and verifier
commands. It is not a merge, security certification, or general correctness proof.
Use `verify-job.sh` when a private unsigned receipt is required; receipt serialization
does not create a second acceptance authority.

## Claude Code host operation

Claude Code was live-tested with synthetic jobs. The Bash tool has a default
two-minute foreground timeout and a ten-minute default ceiling. In interactive
sessions, an approved long `workflow.sh run` may use Bash `run_in_background: true`;
this is a host tool parameter, not a workflow flag or shell `&`. In non-interactive
`claude -p` or SDK runs, use foreground execution within the host ceiling or keep
the turn alive and monitor the background task until it exits. Never end a turn while
a job runs: headless session exit cancels background work. Do not launch a second
dispatch for the same job. A Bash timeout/background notification is not a provider
failure; inspect the existing task and bound workflow status.

Bash variables do not persist between Claude tool calls. In every call, repeat the
reviewed path/value assignments from the example or replace them with the reviewed
absolute values. Status itself needs only the resolved runtime and saved state:

```bash
/absolute/path/to/runtime/workflow.sh status \
  --state /absolute/private/state/workflow.json --format json
```

Read `dispatch.status`, `dispatch.reason`, `dispatch.state_sha256`, `phase`,
`controller_phase`, and `available_actions`. A missing or unreadable dispatch record
is unresolved, not success or permission to start another job. While queued/running,
observe the same host task. Once it exits, inspect its output and the saved envelope,
review the candidate, then run the existing `verify-finalize` command with fresh
bound verification. Status never grants acceptance or further provider authority.

Keep the main driver session active until completion. Foreground subagent background
commands end when that subagent returns; non-interactive `claude -p` background tasks
end shortly after its final result. Session exit also cleans up background tasks.
If background tools are disabled or unavailable, report that host limitation rather
than inventing a detach/restart path. See the official
[Bash tools reference](https://code.claude.com/docs/en/tools-reference) and
[background behavior](https://code.claude.com/docs/en/interactive-mode#background-bash-commands).

Bash permission approval is separate from provider-transmission approval. If the
host sandbox blocks execution, discover exact required paths/hosts through violation
reports and grant narrowly with `sandbox.filesystem.allowWrite` and
`sandbox.network.allowedDomains`. AGY session state under `~/.gemini`, private
controller/staging paths, and the disposable worktree may need access outside cwd/tmp.
Offline tests do not establish the complete write/domain allowlist. Do not disable
sandboxing or exempt AGY via `excludedCommands`; see the official
[sandbox guide](https://code.claude.com/docs/en/sandboxing).
