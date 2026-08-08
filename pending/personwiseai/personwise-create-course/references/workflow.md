# PersonWise CLI workflow and recovery

## Keep one secret-free ledger

Record the course brief, requested target, account alias, stable logical idempotency identity,
run/project IDs, source filenames/checksums/statuses, checkpoint/allowed actions, revisions, review
findings, image state, presenter/voice/configuration evidence, and final access/playability state.

Never record tokens, cookies, credential references, upload authorizations, signed URLs, private
file contents, browser secrets, or local diagnostic data.

## Use structured commands only

Automation adds global `--json` and, after login, `--account <alias>`. Parse the JSON envelope and
stable error/exit classes; never scrape human prose. Put untrusted course text in a bounded JSON
file and pass it through `--input`.

## Create a topic-led or supplied-text run

First run `course readiness --json`. If it is blocked, stop before blueprint design and report the
returned action. Otherwise resolve `desired_slide_count` from the live maximum, recomposing any
oversized request rather than truncating it. Then prepare a create object with the blueprint fields,
`knowledge_source_mode=open`, truthful visual capability, an explicit `distribution_target`
(`private` unless the user requested broader access — an omitted target resolves to the OAuth
grant's publication ceiling, which can be `link`), and
optional Skill attribution. Run:

```text
personwise --account <alias> course create --input <create.json> --json
```

Save `run_id` immediately. The response allocates durable work; it is not completion.

## Create a document-backed run

For strict documents, set `materials_only` and the exact retained source count before creation.
The explicit `distribution_target` rule above applies to every create object.
For each user-named, attached, or selected PDF, PPTX, DOCX, Markdown, or TXT file (maximum 50 MiB),
run:

```text
personwise --account <alias> source add --run-id <run-id> --path <exact-path> --json
personwise --account <alias> source status --run-id <run-id> --json
```

The CLI verifies a regular non-symlink file, computes its checksum, initializes one transfer,
uploads bytes without sending the bearer token to object storage, reconciles ambiguous transfer
results, and confirms canonical state. Do not issue another upload until the first is reconciled.
Never loosen `materials_only` because one source failed.

After upload, do not call `run advance` while any source is `pending` or `processing`. The run stays
at `awaiting_sources` until every declared source is canonically `ready`; during that window
`run advance` is a 200 no-op (it returns the current run state without claiming or changing the
run) and `allowed_actions` does not yet include `continue`. Keep bounded `run wait` and
`source status`; server-orchestrated runs auto-continue once sources complete. For guided runs,
call `run advance` only after a fresh read shows every source `ready`.

`source status` reports the upload ticket lifecycle as `ticket_status` (`consumed` means the
upload was received and processing started, not that the source is complete); the canonical
`status` field is the source processing state (`pending`, `processing`, `ready`, or `failed`),
with `phase`, `processed_pages`/`total_pages`, and a safe `error` when failed. Only `ready`
permits advancing.

If a source fails, read fresh `allowed_actions` from `run get`. When `retry_source` is allowed,
run once:

```text
personwise --account <alias> source retry --run-id <run-id> --source-id <source-id> --json
```

then continue bounded `run wait`/`source status`; if the same error returns, stop and report the
structured error. When the failed source must be replaced (for example `page_quota_exceeded` and
a smaller file), detach it first:

```text
personwise --account <alias> source detach --run-id <run-id> --source-id <source-id> --json
```

then upload the replacement with `source add`. Never create a replacement run to work around a
failed source, and never loosen `materials_only`.

## Wait for and review checkpoints

```text
personwise --account <alias> run wait --run-id <run-id> --timeout-seconds 1800 --json
personwise --account <alias> run get --run-id <run-id> --json
personwise --account <alias> course snapshot --project-id <project-id> --json
```

`run wait` exits on a terminal status (`succeeded`, `failed`, `cancelled`) and at review
checkpoints (`paused`): a paused run cannot progress until the Agent reviews and advances, so
waiting ends there immediately. It also exits on `POLL_TIMEOUT`/`WAIT_CANCELLED`. Older CLI
releases do not return at `paused`; there `POLL_TIMEOUT` is the checkpoint signal instead — read
fresh `run get` state, then review or resume the wait.

At Outline, inspect every stable slide title and key-point set. If objective corrections are
required, put one atomic patch in JSON and run:

```text
personwise --account <alias> course update --project-id <project-id> \
  --input <patch.json> --expected-revision <revision> --json
```

Fetch a complete fresh snapshot, then advance only if permitted:

```text
personwise --account <alias> run advance --run-id <run-id> --json
```

`run advance`, `run retry`, and `run cancel` derive a deterministic per-run idempotency key; prefer
the default and pass `--idempotency-key` only to name one logical mutation with a stable identity,
reused only with an identical payload.

Repeat at Script, reviewing title, key points, page text, and narration together. Never add/delete/
reorder slides through this workflow and never chain blind mutations.

## Attach a reference image

Only during an allowed review window and for a user-named, attached, or selected bounded
PNG/JPEG/WebP (Agent-discovered files require approval):

```text
personwise --account <alias> image attach-reference --project-id <project-id> \
  --slide <zero-based-index> --path <exact-path> --expected-revision <revision> --json
```

The CLI validates the file and owns multipart transfer. Re-read snapshot state before another image
mutation.

## Review and regenerate images

For a vision-capable Agent, create a new destination and request at most six slides per sheet:

```text
personwise --account <alias> image review-sheet --project-id <project-id> \
  --slides 0,1,2 --dest <new-path.jpg> --json
```

Inspect every required page according to `visual-quality.md`. Fix content first. Put bounded
per-slide regeneration instructions in JSON and invoke:

```text
personwise --account <alias> image regenerate --project-id <project-id> \
  --slides <failed-indexes> --input <instructions.json> \
  --expected-revision <revision> --json
```

Wait for durable state and re-inspect changed slides. Without vision, record `not_performed` and do
not fabricate findings or regenerate blindly.

## Optional presenter and configuration changes

Use `presenter list --json`, `presenter preview --presenter-id <id> --dest <new-path> --json`, and
revision-bound `presenter select` only for a concrete casting requirement. Structured compatibility
and voice readiness govern selection. A preview supports casting observations, not identity claims.

For a user-requested supported layout/configuration change, put the exact patch in JSON and run
revision-bound `course configure`; then read a fresh snapshot to verify persistence.

## Finish and distribute

Continue the stored durable target from fresh allowed state. Explicit repair commands are:

```text
personwise --account <alias> course publish --project-id <project-id> --json
personwise --account <alias> course set-access --project-id <project-id> --mode private|link --json
personwise --account <alias> topic submit --project-id <project-id> --json
```

Use them only when user intent and fresh state authorize them. Never submit Topics
without explicit intent, and never describe submission as approval.

After terminal success:

```text
personwise --account <alias> course get --project-id <project-id> --json
personwise --account <alias> course snapshot --project-id <project-id> --json
```

Report the URL that matches the final access mode: for `access_mode=link`, give `share_url` as the
public link; for `access_mode=private`, give `editor_url` as the login-required view link and state
that outsiders cannot open it. If the user wants to share a private course, enable link access or
ask the Agent to change it with `course set-access`. Report a link URL only when the returned state
proves playability.

Failed runs expose the safe `error` object through `run get`, a blocked publish returns
`requirements`, and `topic submit`/`topic status` return `submission` with any message or
review note; report them exactly as returned.

## Query courses

Use `course list --limit <1-100> --json` and preserve its opaque cursor. Use `course get` for one
record and `course snapshot` only when authorized detail is needed. Do not invent an offset or total.

## Recover safely

| Signal | Action |
|---|---|
| Lost response or timeout | Read fresh run/course state. Replay the exact same logical mutation only when state does not prove it completed. |
| Revision conflict | Fetch a fresh snapshot, merge actual changes, and use the new exact revision. |
| `CONFLICT` (`read_current_state`) | Call `run get` and inspect fresh `status`/`allowed_actions`; use `source status --run-id` for source states, then act on the new state. If `continue` is still allowed, one bounded retry (wait `poll_after_seconds`, then one `run advance`) is reasonable; if the same conflict repeats after 2-3 spaced attempts, stop and report the exact blocking state. Never create a replacement course or run. |
| Sources still `pending`/`processing` at `awaiting_sources` | `run advance` returns the current run state as a 200 no-op and `allowed_actions` omits `continue` until every declared source is `ready` | Keep bounded `run wait` and `source status`; server-orchestrated runs auto-continue once sources complete. This is normal processing, not a deadlock; do not stop, cancel, or create a replacement run. |
| Interrupted `run wait` | The remote run continues; resume with the same account and run ID. |
| Failed run with `retry` allowed | Invoke `run retry` once with the stable logical identity, then wait/read again. |
| Failed run without `retry` | Report the safe server state; do not mutate around it. |
| Source failed with `retry_source` allowed | Run `source retry --run-id <id> --source-id <id>` once, then bounded `run wait`/`source status`; if the same error returns, stop and report the structured error. |
| Failed source must be replaced (e.g., `page_quota_exceeded`) | Run `source detach --run-id <id> --source-id <id>` first, then `source add` the replacement file; do not create a second run. |
| Source transfer ambiguous | Use `source status`; never blindly upload again. |
| 401 or revoked grant | Reauthorize, pin the matching account, then read state before mutation. |
| Insufficient credit | Stop before blueprint design and report the returned action; do not purchase or create another run. |
| 429 / retryable dependency | Honor structured retry timing and reduce concurrency. |
| Cancellation requested | Use `run cancel`, then poll until terminal; cancellation is cooperative. |

## Completion evidence

Report exact run/project IDs, terminal state, sources, revisions, objective changes, per-slide image
readiness, visual review status, presenter/voice/configuration, publication/access/playability, and
Topics status only when requested. Never report an earlier checkpoint as the final state.
