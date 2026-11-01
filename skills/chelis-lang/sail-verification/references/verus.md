# Verus workflows

## Existing projects and files

For a Cargo/Verus project, run `sail verify --output json` from the project
directory. Existing `cargo verus verify` arguments can be passed to `sail verify`.
Sail builds in its own target directory. Switching back is running
`cargo verus verify` again.

Standalone files are supported on main for the next release, not published
0.1.0. Check `sail --help` for standalone `.rs` support. Development builds can
also report version 0.1.0, so the version string alone does not identify this
capability. On a build that includes it:

```sh
sail verify proof.rs --output json
sail verify proof.rs -- --crate-type lib
sail watch proof.rs
```

Run watch from a directory containing the source and its modules/includes.
The full standalone workflow and its release status are maintained at:
https://github.com/Chelis-Lang/sail/blob/main/docs/standalone-verification.md

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

Through MCP, use `start_repair_validation`, then the job tools to read its
result. Read the completed result and accept a repair only when the whole
target verifies.

Repair walkthrough:
https://github.com/Chelis-Lang/sail/blob/main/docs/proof-repair-walkthrough.md

Currentness and partial verification:
https://github.com/Chelis-Lang/sail/blob/main/docs/freshness.md
