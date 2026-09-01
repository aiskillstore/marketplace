# Troubleshooting

Start from the first failing boundary. Do not turn a local preflight, provider,
lifecycle, or verification failure into an automatic retry, a changed model, or a
weaker check. Preserve the current candidate and state until the cause is classified.

For the normal command sequence, read
[Project lifecycle and verification](PROJECT_LIFECYCLE_AND_VERIFICATION.md). For
provider, environment, and verifier limits, read
[Security and compatibility](SECURITY_AND_COMPATIBILITY.md).

## The runtime does not resolve

**Symptom:** `resolve-pipeline.sh` reports that the pipeline or complete bundle is
missing.

**Action:** Reinstall or recopy the whole `skills/agy-worker/` package, including
`runtime/`, `scripts/`, `references/`, and `agents/`. Do not point the resolver at a
partial runtime or edit `.pipeline-root` by hand. A standalone marker must be an
absolute path to a complete installation.

## Doctor reports `review-required` or `not-ready`

`review-required` means reviewed matrix resolution is unavailable or stale. It does
not block the provider-owned default or an explicitly approved literal model, but it
does require the documented compatibility review before a reviewed direct selection.

`not-ready` is a dispatch blocker. Fix the named local prerequisite, then rerun the
offline doctor. Do not claim that a later live dispatch will work merely because the
doctor becomes `ready`; it does not test authentication, provider availability, or
task quality.

## Transmission preview fails

The preview requires a real canonical branch-backed linked Git worktree. Common
causes are an ordinary directory copy, a detached or unregistered worktree, a root
`.git` layout that does not match the contract, an outward/broken symlink, a special
node, path drift between scans, or a configured enumeration limit.

Create or repair the disposable worktree using Git, remove unapproved content, and
rerun the provider-free preview. Do not bypass the preview or interpret a preview
failure as provider rejection. If using a narrow provider-scope policy, recompute and
review its unified transmission SHA after any content or policy change.

## Preflight fails before provider launch

Tell the user that the task was not sent to AGY. Keep the caller's model, effort,
permissions, authentication, scope, and task unchanged while classifying the local
failure. A model change cannot repair a permission, missing executable, invalid
worktree, approval, environment, quota, or human-decision blocker.

Before every reviewed direct dispatch, including an exact-version match, Codex must inspect current bounded raw `agy --help` evidence. Structural acceptance is not proof
that the caller-selected model or effort is semantically available. On installed
version drift, review the bounded help bytes and approve their exact SHA only when
the selection can still be honored. A final selection reprobe failure does not permit
same-job resume or restart; create a new job only after the evidence is reviewed.

## agy exits zero but ordinary output is empty

This can be valid CLI behavior. Parse `result.structured_output`; do not treat the
echoed schema or empty display text as the worker result. If the structured report is
missing or invalid, preserve the sanitized failure and do not invent an envelope.

## Authentication, quota, timeout, or provider failure

Classify only from reviewed, bounded evidence. Do not infer account health, billing,
model acceptance, or provider availability from local controller state.

An exact agy `1.1.13` terminal quota response can produce exit `24` with a sanitized
`retry_after_seconds`. Treat it as a stop and explicit-resume decision: do not sleep,
retry, restart, or change the selected model automatically. Wrong-version or altered quota terminals without a
recognized report remain `invalid_envelope`, exit `4`, with
`failure_stage=missing_structured_output`; never generalize the narrow classifier.

For a candidate-free failure, consult `available_actions`. A mechanically eligible
`resume` keeps the exact stored conversation; a fresh `restart` requires explicit user
direction. Both require the current state SHA and a new provider notice.

## A provider error or cancellation still has a candidate

A structurally valid `ERROR` candidate is reviewable. Retrieve `result`, inspect the
diff, create Verification v2 from driver-owned evidence, then choose an eligible
same-conversation `continue` or `finalize`. Do not use `resume`.

A structurally valid `CANCELED` or `CANCELLED` candidate is preserved for review and
finalization, or an explicitly directed fresh restart. It is never resumed or
continued. Local cancellation proves local process closure only; report remote
cancellation as unverified unless independently established.

## State approval is stale

Mutating lifecycle commands require the current `state_sha256`; `wait` uses
`--after-state-sha`. Read `status` again, understand what changed, rebuild any
candidate-bound evidence, and use the newly reported approval only if the intended
action remains available. Never copy a stale digest forward blindly.

For facade finalization of a bound dispatch, use `dispatch.state_sha256` as
`--approve-dispatch-sha`. It is distinct from a convenient current facade state hash.
The deprecated facade `--approve-state-sha` spelling is only an exact alias for the
same dispatch-state approval.

## Candidate drift or verification-copy failure

Tracked, untracked, deleted, and ignored paths participate in candidate binding. A
cache file, bytecode file, generated artifact, or manual cleanup can invalidate the
snapshot. Do not delete or regenerate files to force equality. Stop writes to the
candidate, inspect it read-only, and create a new isolated verification copy.

The copy fails closed for source drift, an existing or non-private destination,
outward/broken/Git-administration symlinks, or an invalid destination boundary. A
failed copy is not usable evidence. Preserve the original candidate and report the
unresolved failure.

## The gate rejects scope or verifier input

- A declared-path mismatch means Git found changes outside the envelope declaration.
- `--only` rejects every changed path outside its repeatable policy; `--allow` only
  permits known undeclared artifacts and does not override `--only`.
- A no-op with `--expect-edits` is a rejection, not a verified result.
- Non-empty worker `commands_run` or `tests_run` fields are untrusted claims and cause
  rejection; choose commands independently.
- `--verify-argv` must be a canonical JSON array and cannot smuggle an implicit shell.
- A verifier that mutates the candidate invalidates the exercised state.

Fix a real candidate defect through a bounded same-conversation repair when budget
remains. Fix a driver invocation error locally. Never weaken the gate simply to make
it green.

## A verifier needs environment or network access

The default verifier baseline excludes `HOME`. Add an ordinary variable only by exact
name with `--verify-env NAME`. Credential-like names, including `HOME`, require
`--verify-credential-env NAME` and the credential-access acknowledgement. Explicit
shell verification separately requires network and credential-access
acknowledgements.

Acknowledgements do not provide a value or network isolation and do not authorize an
external write. Candidate code can import unreviewed code, so expose no credential
merely to reproduce an ambient shell setup. Prefer a narrower offline verifier.

## The repair budget ends with failed or missing checks

Keep the useful candidate and report `partially_verified` with the exact failed,
missing, or unavailable checks and unresolved gaps. Do not erase the candidate,
silently start a new conversation, or call it verified. A fresh restart is a separate
explicit user decision.
