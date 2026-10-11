# agy-worker package

`agy-worker` is an Agent Skill for delegating repository exploration and
implementation to Google Antigravity CLI (`agy`) while keeping acceptance with
the driver. The package includes its complete portable core runtime, so an installed
skill does not need a repository checkout or a network fetch for ordinary workflows.
Maintenance tools require a repository checkout.

Use it when a repository task benefits from delegated discovery or edits and the driver
can independently inspect the candidate and run the relevant project checks. It is
not a general-purpose provider client, a security sandbox, or evidence that worker
output is correct.

## Requirements

- OpenAI Codex CLI or Claude Code
- Bash, Python 3, and Git
- `agy` on `PATH` with provider access for live dispatch
- A branch-backed disposable Git worktree whose complete provider-readable content
  has been reviewed and approved

A provider model slug containing `claude` does not establish driver-host support.

## Start from your driver

After installing the skill, start a new driver session and make the scope and checks
concrete. For example:

> Use the agy-worker skill to add parser error-path tests in this repository. Allow
> edits only under tests, verify with the existing parser test suite, and preserve
> useful partial work if a check fails.

Before a live dispatch, the driver must show the owner the exact task and selected
settings beside the content digest; a later provider notice may use a public-safe
summary. Obtain any missing provider-transmission approval, and ensure secrets,
denied paths, and unrelated private files are absent from the disposable worktree.
Installation alone grants none of those permissions.

Prefer selected-content `--provider-scope` for bounded jobs. Whole-worktree dispatch
remains an explicit content-bound exception, and neither the ordinary facade nor the
advanced raw initial launch has an implicit transmission mode.

## Resolve the bundled runtime

`SKILL_ROOT` is the directory containing `SKILL.md`; Claude Code substitutes
`${CLAUDE_SKILL_DIR}` in skill content. Set it explicitly in each Bash call; do not
read a Claude path variable from the environment. Resolve the runtime
instead of assuming a repository path:

```bash
PIPELINE="$(bash "$SKILL_ROOT/scripts/resolve-pipeline.sh")" || exit $?
"$PIPELINE/doctor.sh" --repo /absolute/path/to/target
```

The resolver accepts a complete plugin, an explicit standalone installation marker,
or this folder with its bundled `runtime/`. It fails closed when required components
are missing. `doctor.sh` is an offline prerequisite check; `ready` does not prove
provider authentication or future job success.

For ordinary work, the driver uses the resolved `workflow.sh` facade to preview the
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
