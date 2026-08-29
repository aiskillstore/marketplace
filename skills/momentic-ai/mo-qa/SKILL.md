---
name: mo-qa
description: Use Momentic's `mo` CLI to run and control Mo, Momentic's cloud autonomous QA agent. Use when starting or continuing Mo sessions, reading their output or status, stopping active work, answering Mo, or moving files between the local machine and Mo's hosted sandbox.
---

# Run QA with Mo

Mo is Momentic's autonomous QA engineer. It runs in a hosted sandbox, where it
can test web applications with a browser, inspect network traffic, run code and
shell commands, delegate exploration, and report test cases and product bugs.
Treat its filesystem and environment as remote, not as the user's machine.

## Setup

Run `mo --version`. If it fails, read
[Installation](references/installation.md).

Assume authentication is already configured. If an operational command reports
an authentication error, read [Authentication](references/authentication.md).

Use the target implied by the conversation. If it is unclear, ask the user what
to test. For a local or private target, read
[Tunneling](references/tunneling.md) and retain its `tunnel_id`. For a public
target, use its exact URL.

## Write the QA brief

Treat the brief as the whole input. State:

1. **Target URL:** Include the exact path and query the change affects.
2. **Expected behavior:** Explain what changed and what it should now do in
   product terms.
3. **Sign-in instructions:** Name the login method and test account to use.
4. **Test data rules:** State what Mo may create and what it must not touch.
5. **Out-of-bounds actions:** Call out deletions, payments, emails, production
   data, bulk operations, and any other destructive action. Mo may take
   destructive actions if the brief invites them.
6. **Acceptance criteria:** List the checks that decide pass or fail.

Ask the user for any missing item before starting Mo. Do not invent scope,
credentials, test data permissions, or acceptance criteria.

## Run a session

Write the brief before invoking the CLI, then pass it as one quoted argument:

```bash
brief=$(cat <<'EOF'
Target URL: https://preview.example.com/checkout?variant=express
Expected behavior: Express checkout now keeps the selected shipping method when the customer returns from payment.
Sign-in: Use the staging QA buyer account already provisioned for Mo.
Test data: Create test carts and orders only. Do not modify shared catalog data.
Out of bounds: Do not submit payment, send emails, delete data, or run bulk operations.
Acceptance criteria:
- The selected shipping method remains selected after returning from payment.
- The order total does not change.
- Standard checkout still works.
EOF
)
session_json=$(mo start "$brief")
session_id=$(jq -r .sessionId <<<"$session_json")
web_url=$(jq -r .webUrl <<<"$session_json")
```

Starting returns before Mo finishes. Preserve both values: every later command
needs `session_id`, and the user can watch or join through `web_url`.

Use start settings only when needed:

- `--tunnel "$tunnel_id"` connects the session to a configured tunnel.
- `--momentic-mode` uses smarter Momentic browser tools; omit it for faster
  Playwright MCP.
- `--max-concurrency <count>` caps concurrent sub-agents. Omit it by default;
  pass it only when the user specifies a limit before the session starts.

These settings are chosen when the session starts.

Concurrency cannot be changed on an existing session. A lower value reduces
parallel model and browser load, which can help when Mo hits provider rate
limits or overwhelms a local target server. If either happens, stop the current
session and start a fresh one with a lower `--max-concurrency`; do not try to
repair the affected chat by sending a lower limit after it has started.

## Follow the turn reliably

Poll the active session with `status`:

```bash
mo status "$session_id"
```

It returns the current run state, latest visible message, web URL, and
structured QA findings. Always inspect `findings.testCases`, `findings.bugs`,
`findings.controls`, and `findings.verdicts`; they contain more evidence than
Mo's closing prose. Before reporting a bug, check whether the product or the
brief's expected behavior is stale.

Use `read` when waiting for output or retrieving the transcript and pending
input. Prefer bounded 30-60 second reads so the caller stays responsive:

```bash
mo read "$session_id" --from start --timeout 45s --json
```

Use `--from start` for reliable polling. It replays the visible transcript, so
deduplicate messages when automating. Repeat until the expected assistant reply
appears and `state` is `idle`, `waitingOnUser`, or `stopped`. A `timedOut: true`
response means Mo is still working. If `pendingInput` is present, answer it with
`send`.

Do not rely on `--from latest` after `start` or `send`: it only captures output
produced after the read begins, so a fast turn can finish and return no
messages. A timeout accepts `0`, milliseconds, seconds, or minutes such as
`500ms`, `45s`, or `4m`, up to `290s`.

`status.state` reports the backend run state, while `read.state` reports the
visible turn state. They can briefly disagree; use `read.state` to decide
whether the visible turn reached an attention boundary.

## Continue, stop, or archive

For a follow-up or answer, prefer `--wait` so the next attention boundary is
returned directly:

```bash
mo send --session-id "$session_id" \
  --wait 45s 'Use the staging account and continue'
```

If Mo is working, `send` stops the active turn, interrupts in-flight tool work,
and starts a new turn from saved history. It does not steer the live turn. Send
only when that interruption is intended. Without `--wait`, success only means
the message was accepted; confirm a new assistant reply with `read`.

Stop only the active turn:

```bash
mo stop "$session_id"
```

Allow a few seconds for propagation, then verify with
`read --from start --timeout 0 --json` that the state is `stopped`. Stopping
does not delete the session, and already-running sub-agents may finish
independently.

Archive a finished session when it should leave the active list:

```bash
mo archive "$session_id"
```

Archive stops active work. Further `send` calls are rejected until the session
is unarchived in the web UI; the CLI has no unarchive command.

## Transfer files

`upload` needs an existing session and prints the authoritative sandbox path.
Send that returned path to Mo; a local path is meaningless inside its hosted
machine.

```bash
remote_path=$(mo upload --session-id "$session_id" ./fixture.csv fixture.csv)
mo send --session-id "$session_id" "Use the sandbox file at $remote_path."

mkdir -p .momentic-artifacts
mo download --session-id "$session_id" --output .momentic-artifacts "$remote_path"
```

If `--output` names a directory, create it first. A nonexistent output path is
treated as a target filename. Without `--output`, downloads use
`MOMENTIC_ARTIFACTS_DIR`, then `<current-directory>/.momentic-artifacts`.

## Command reference

Run `mo <command> --help` for exact options. Global `--log-level` accepts
`debug`, `info`, `warn`, or `error`.

| Command                                              | Purpose and important options                                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `mo start <message>`                                 | Start a session; `--tunnel`, `--momentic-mode`, `--max-concurrency`.                                    |
| `mo send <message> --session-id <id>`                | Interrupt active work or start a turn; `--wait` returns the next attention boundary.                    |
| `mo read <session-id>`                               | Read transcript and visible state; `--from`, `--timeout`, `--json`.                                     |
| `mo status <session-id>`                             | Read backend state, web URL, latest message, and structured findings.                                   |
| `mo stop <session-id>`                               | Stop the active turn without deleting the session.                                                      |
| `mo archive <session-id>`                            | Stop and archive the session; unarchive is web-only.                                                    |
| `mo upload <source> [destination] --session-id <id>` | Upload one file and print its sandbox path.                                                             |
| `mo download <source> --session-id <id>`             | Download a sandbox path; `--output` selects the local target.                                           |
| `mo tunnel start <address...>`                       | Start local/private access; `--foreground` keeps it attached. See [Tunneling](references/tunneling.md). |
| `mo tunnel list`                                     | List tunnels started by Mo on this machine.                                                             |
| `mo tunnel stop <tunnel-id>`                         | Stop a tunnel and revoke access.                                                                        |
