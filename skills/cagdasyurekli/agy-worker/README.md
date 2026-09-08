# agy-worker package

`agy-worker` is a Codex Agent Skill for delegating repository exploration and
implementation to Google Antigravity CLI (`agy`) while keeping acceptance with
Codex. The package includes its complete portable runtime, so an installed skill does
not need a repository checkout or a network fetch to resolve its commands.

Use it when a repository task benefits from delegated discovery or edits and Codex
can independently inspect the candidate and run the relevant project checks. It is
not a general-purpose provider client, a security sandbox, or evidence that worker
output is correct.

## Requirements

- OpenAI Codex CLI
- Bash, Python 3, and Git
- `agy` on `PATH` with provider access for live dispatch
- A branch-backed disposable Git worktree whose complete provider-readable content
  has been reviewed and approved

Claude and Claude Code hosts are not supported. A provider model slug containing
`claude` does not change the host requirement.

## Start from Codex

After installing the skill, start a new Codex session and make the scope and checks
concrete. For example:

> Use the agy-worker skill to add parser error-path tests in this repository. Allow
> edits only under tests, verify with the existing parser test suite, and preserve
> useful partial work if a check fails.

Before a live dispatch, Codex must show the public-safe task and caller-owned model
selection, obtain any missing provider-transmission approval, and ensure secrets,
denied paths, and unrelated private files are absent from the disposable worktree.
Installation alone grants none of those permissions.

Prefer selected-content `--provider-scope` for bounded jobs. Whole-worktree dispatch
remains an explicit manifest-bound exception, and neither the ordinary facade nor the
advanced raw initial launch has an implicit transmission mode.

For an explicitly accepted higher-authority experiment, the advanced raw dispatcher
supports one-cycle `--boost` task mode. Its first provider-free invocation prints the
job-bound risk digest required by `--approve-boost-risk-sha`; review the warning before
rerunning. Boost may invoke provider-side subagents and protected tools, but the digest
does not grant permissions, widen the approved transmission, or authorize Git or
publication. Boost results require a matching provider init identity and are never
eligible for resume, restart, or continuation.

## Resolve the bundled runtime

The skill instructions receive the package root as `SKILL_ROOT`. Resolve the runtime
instead of assuming a repository path:

```bash
PIPELINE="$(bash "$SKILL_ROOT/scripts/resolve-pipeline.sh")" || exit $?
"$PIPELINE/doctor.sh" --repo /absolute/path/to/target
```

The resolver accepts a complete plugin, an explicit standalone installation marker,
or this folder with its bundled `runtime/`. It fails closed when required components
are missing. `doctor.sh` is an offline prerequisite check; `ready` does not prove
provider authentication or future job success.

For ordinary work, Codex uses the resolved `workflow.sh` facade to preview the
provider-readable path boundary, run an approved workflow, inspect status, and bind
driver-owned verification before finalization. The lower-level dispatcher, lifecycle,
gate, and receipt commands remain advanced recovery surfaces.

## Package guide

- [Skill router](SKILL.md): when to use the skill, workflow selection, dispatch
  notices, hard stops, and delivery rules.
- [Project lifecycle and verification](references/PROJECT_LIFECYCLE_AND_VERIFICATION.md):
  preview, run/status/finalize, Verification v2, isolated verification copies, and
  bounded repair.
- [Security and compatibility](references/SECURITY_AND_COMPATIBILITY.md): provider
  transmission, environment, verifier, host, and distribution boundaries.
- [Troubleshooting](references/TROUBLESHOOTING.md): actionable preflight, provider,
  lifecycle, candidate, and verification failures.

These package-owned links work in a standalone copy. Repository release notes,
contributor history, and public-site material intentionally remain outside this
runtime guide.
