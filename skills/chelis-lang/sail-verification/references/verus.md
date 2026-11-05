# Verus workflows

## Existing projects and files

For a Cargo/Verus project, run `sail verify --output json` from the project
directory. Existing `cargo verus verify` arguments can be passed to `sail verify`.
In managed mode Sail builds in its own target directory; a reported `SAIL3112`
fallback uses the project target directory. Switching back is running
`cargo verus verify` again.

Standalone files are available in published `0.2.0` and the earlier registry
prerelease `0.2.0-rc.1`, absent from 0.1.0.
Check `sail --help` for standalone `.rs` support; older development builds may
retain an older version string. On a build that includes it:

```sh
sail verify proof.rs --output json
sail verify proof.rs -- --crate-type lib
sail watch proof.rs
```

Run watch from a directory containing the source and its modules/includes.
The full standalone workflow and its release status are maintained at:
https://github.com/Chelis-Lang/sail/blob/main/docs/standalone-verification.md

## Preparation after return

Published 0.2.0 and the earlier registry prerelease can prepare the next unchanged Cargo invocation in the
background after a successful Current result. The command returns its own
result first; preparation is additional CPU and disk work. Foreground work takes
priority. Check `sail status --json` for preparation activity, and use
`SAIL_BACKGROUND_PREPARE=0 sail verify` to opt out. Activity counters do not
establish a proof. The next call still checks its inputs and reports scope,
verdict and currentness. This behavior is not in published 0.1.0.

This automatic preparation differs from `sail verify --background`: the latter
submits the requested verification as a job whose completed result must be read.
See the [preparation guide](https://github.com/Chelis-Lang/sail/blob/main/docs/background-preparation.md).

## MCP

Use an already configured Sail server's `verify` tool. Read the installed tool
schema rather than guessing arguments. Submission tools accept `project_dir`;
job/status/result tools use the server's service and reject that argument.
On builds with standalone support, `source_file` selects an existing `.rs` file.
For proof failures, `explain_failure` and `counterexample` provide more focused
feedback than the initial summary; use their installed schemas.

If the user wants to connect Claude Code, run from the project directory:

```sh
claude mcp add --transport stdio sail -- sail mcp
```

Other clients launch the stdio command `sail mcp`. Use an absolute binary path
when Sail is not on the client's PATH. If you override `SAIL_CACHE_DIR` or
`SAIL_DAEMON_SOCKET`, set the same absolute values in the server and CLI
environments so both address the same service.

For a longer verification, use `start_verification`, then
`verification_status` and `verification_result` with the returned job ID.
The CLI equivalent is `sail verify --background --output json`, followed by
`sail jobs status JOB_ID` and `sail jobs result JOB_ID`.

MCP schemas and result details:
https://github.com/Chelis-Lang/sail/blob/main/docs/mcp.md

## Check a proof repair

The agent writes a candidate repair; Sail checks it. A repair check tests the
selected function first and accepts the repair only after the whole target
verifies. It needs the interactive engine installed in the same Sail cache.
Use `sail engine --help` and the walkthrough for engine setup before a first
repair check.

In a Cargo project, select the real package and function, for example:

```sh
sail repair-check --engine interactive --package demo --lib --function demo::sum_to
```

The registry prerelease and stable candidate also support a standalone repair check:

```sh
sail repair-check proof.rs --function proof::lemma --engine interactive --output json
```

Inspect `sail repair-check --help` and the installed MCP schema before using
this form; published 0.1.0 lacks it. Older development builds may report 0.1.0.
Where exposed, `standalone_repair` in capabilities identifies this support.
A focused pass remains provisional until the independent full-target check
passes with Current evidence.

Through MCP, use `start_repair_validation`, then the job tools to read its
result. Read the completed result and accept a repair only when the whole
target verifies.

Repair walkthrough:
https://github.com/Chelis-Lang/sail/blob/main/docs/proof-repair-walkthrough.md

Currentness and partial verification:
https://github.com/Chelis-Lang/sail/blob/main/docs/freshness.md

## Keep reusable work and manage disk use

For CI, persist solver replies and, in managed mode, project targets and receipts
from trusted workflows. Read the [CI cache guide](https://github.com/Chelis-Lang/sail/blob/main/docs/ci-cache.md)
for paths, tool/path requirements and the limits of restored caches.

On builds with `sail cache projects budget`, an optional soft byte cap can prune
old idle workspaces. Inspect help and use a dry run before manual pruning:

```sh
sail cache projects prune --to-bytes 21474836480 --dry-run --json
```

The newest and active workspaces are protected, so a configured cap can remain
exceeded. Defaults do not evict automatically. Pruning removes targets and
receipts together; later calls verify again. The [disk-use guide](https://github.com/Chelis-Lang/sail/blob/main/docs/workspace-hygiene.md)
describes configuration and reporting. These budget commands are available in
published `0.2.0` and registry prerelease `0.2.0-rc.1`, absent from 0.1.0.
