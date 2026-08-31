# Project lifecycle and verification

This guide owns the operational lifecycle after the repository, task, provider
transmission, and caller-selected model inputs are approved. The worker envelope is
input, never acceptance evidence. Codex reviews the bound candidate and supplies the
verification evidence.

Read [Security and compatibility](SECURITY_AND_COMPATIBILITY.md) before a first live
dispatch. Use [Troubleshooting](TROUBLESHOOTING.md) when a preflight, provider,
lifecycle, or verifier step fails.

## Lifecycle at a glance

1. Capture an immutable base commit and create a branch-backed disposable worktree.
2. Keep owner-private controller state outside the worktree.
3. Generate the content-free transmission preview and review its exact digest.
4. Obtain approval for the complete provider-readable content and dispatch with the
   same repository, worktree, base, branch, and job bindings.
5. Retrieve the bound candidate, inspect its Git diff, and select checks independently
   of worker prose.
6. Run writable checks in an isolated verification copy.
7. Bind sanitized findings to the current candidate in Verification v2.
8. Continue the same conversation for a bounded repair or finalize an honest
   disposition. Preserve useful partial work when the budget ends.

Whole-worktree mode requires its current manifest SHA acknowledgement; requested paths
and gate policies constrain writes or candidate acceptance, not provider reads.
Provider-scope mode
narrows staged content as described below, but it is not a security sandbox.

## Primary `run`, `status`, `verify-finalize` path

Resolve the installed runtime first:

```bash
PIPELINE="$(bash "$SKILL_ROOT/scripts/resolve-pipeline.sh")" || exit $?
```

Codex creates and reviews the branch-backed disposable worktree. The following names
are illustrative local variables; the actual repository and state paths remain
caller-owned:

```bash
TARGET=/absolute/path/to/approved-repository
BASE="$(git -C "$TARGET" rev-parse HEAD)"
STATE_DIR="$(mktemp -d -t agyworker-state.XXXXXX)"
WT="$(mktemp -d -t agyworker-worktree.XXXXXX)"
rmdir "$WT"
JOB_ID=job-12345
JOB_BRANCH=agy/job-12345
git -C "$TARGET" worktree add -b "$JOB_BRANCH" "$WT" "$BASE"
```

Keep `STATE_DIR` owner-private and outside both the repository and worktree. Before
provider approval, obtain the canonical content-free preview:

```bash
"$PIPELINE/workflow.sh" run --preview \
  --state "$STATE_DIR/workflow.json" --repo "$TARGET" --worktree "$WT" \
  --branch "$JOB_BRANCH" --base "$BASE" --job-id "$JOB_ID" \
  > "$STATE_DIR/preview.json"
```

Review the preview and its exact `manifest_sha256`. It lists path names and kinds,
not file contents, starts no provider process, and grants no approval. After the user
approves that exact boundary, capture the approved run's envelope in the owner-private
state directory. Emit the required user-facing provider notice immediately before this
attempt:

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

Omitting both modes fails before provider launch. The old `--approve-preview-sha`
spelling remains available through at least v0.15.x only when paired with
`--legacy-preview-approval`; it emits a deprecation warning and never restores an
implicit whole-worktree default.

The facade does not choose a model, assurance label, repair, retry, Git action, or
external write. `status --state "$STATE_DIR/workflow.json"` is read-only. For a bound
controller dispatch, copy `dispatch.state_sha256` from facade status and pass it as
`--approve-dispatch-sha` to `verify-finalize`; the deprecated facade spelling
`--approve-state-sha` is an exact mutually exclusive alias. Rejected or routed gate
receipts are preserved without calling the lifecycle finalizer.

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
  --verify-argv '["python3","-m","pytest","-q"]' \
  --verification-json "$STATE_DIR/verification-v2.json" \
  --assurance verified
```

Choose commands from the candidate repository and its configured automation. Never
execute `commands_run` or `tests_run` from the worker envelope. An explicit
`--verify-shell SCRIPT` is an advanced compatibility surface requiring both verifier
network and credential-access acknowledgements. Historical `--verify SCRIPT` also
requires the legacy-shell acknowledgement.

## Controller state and actions

Use `status` first. Treat `available_actions` as the canonical mechanical action set;
deprecated `next_action`, `next_action_command`, `phase`, and `has_prior_candidate`
are compatibility aliases, not recommendations or acceptance facts.

Current V11 uses `dispatching` for an active initial, resume, or restart attempt;
`attempt-failed` for a pre-candidate failure; `awaiting-verification` for a recognized
candidate; `repairing` for an active continuation; and `repair-failed` for a failed
continuation. Terminal controller phases are `completed` and `blocked`. Driver
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

Controller-private V11 state also preserves a sanitized
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

## Isolated verification copy

Driver checks may create bytecode, caches, coverage data, generated files, or other
artifacts. Do not alter or clean the bound candidate to make those outputs disappear.
Inspect Git-dependent facts read-only against the candidate, then create a separate
copy for writable checks:

```bash
VERIFY_PARENT="$(mktemp -d -t agyworker-verify.XXXXXX)" || exit $?
VERIFY_PARENT="$(CDPATH= cd -- "$VERIFY_PARENT" && pwd -P)" || exit $?
VERIFY_DIR="$VERIFY_PARENT/candidate"
"$PIPELINE/agy-worker.sh" verification-copy --job-id "$JOB_ID" \
  --destination "$VERIFY_DIR" --format text
( cd "$VERIFY_DIR" && /usr/bin/python3 -m pytest -q )
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

Build the record only from driver-owned observations. Do not include prompts, source
bytes, raw logs, secrets, worker prose, account data, or private paths. This example
records one passing check and a completed diff review:

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
results, coverage gaps, or review findings. It must continue the same conversation
while budget remains and must be preceded by the provider notice.

## Assurance and preservation

The controller validates and persists Codex's exact disposition; it does not infer a
different label from counters.

- `verified`: for `task` and `project`, at least one driver check passed, none failed
  or are missing, and diff review is complete. `explore` additionally requires
  complete coverage and no unresolved gaps.
- `partially_verified`: useful candidate with a failed, missing, unavailable, or
  incomplete check, or an unresolved coverage gap.
- `rejected`: Codex has reviewed and declines the candidate.
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
  --verify-argv '["/usr/bin/git","diff","--check"]' \
  --verify-argv '["python3","-m","pytest","-q","tests/test_parser.py"]'
```

Exit zero means only that the gate accepted the exact exercised state and verifier
commands. It is not a merge, security certification, or general correctness proof.
Use `verify-job.sh` when a private unsigned receipt is required; receipt serialization
does not create a second acceptance authority.
