# Connect and authorize the PersonWise CLI

## Use the executable bound to this Skill

This package uses the international PersonWise service and one pinned `personwise` CLI. There is
no alternate endpoint, issuer, resource, origin, credential path, or market fallback.

Run `personwise version --json` and require software version 1.1.6 or newer with CLI contract 1.0.
If it is missing or old, use the bundled bootstrap:

```text
Linux/macOS: assets/bootstrap.sh --approve-install
Windows:     assets/bootstrap.ps1 --approve-install
```

The Host may ask for installation permission under its own policy. The Skill must not add a
second PersonWise approval or narrate installation internals on the normal path. Never use sudo,
edit PATH/profile/execution policy, start a daemon, overwrite an occupied path, follow `latest`,
or use another origin.

Do not run `doctor` as a prerequisite. Run it only when a structured CLI failure recommends
`run_doctor`; it is a read-only diagnostic unless the user explicitly requests a bundle path.

## Update discipline — keep the CLI and this Skill current

This is a standing discipline, not optional maintenance: the Skill and the CLI are one governed
pair and must stay aligned before any business command. PersonWise ratchets minimum versions to
the current release, so an outdated CLI or Skill is normally unusable rather than merely stale.

Before the first business command, run this freshness check once:

```text
personwise update check --service personwise.ai --json
```

Every status other than `up_to_date` is stop-until-updated, except `no_active_release`, which
means no release is published yet: in that case continue and rely on service responses. Every
successful CLI response may also carry a top-level `updates` block. Handle it deterministically:

- If `updates.cli.status` or `updates.skill.status` is `update_available` or `below_minimum`,
  tell the user once which component is outdated (installed versus latest) and quote the exact
  `action` command. The task cannot continue until that update is installed. Ask for approval;
  with approval, run exactly that command (it already carries the required `--approve-upgrade`
  argument). If the user declines, stop and do not run business commands with the outdated
  component, and do not ask again in this session unless the user changes that decision.
- If a command fails with `CLI_VERSION_BELOW_MINIMUM` or `SKILL_VERSION_BELOW_MINIMUM`, the task
  cannot continue until the update is installed. Explain this, ask for approval, run exactly the
  printed update command, then retry the failed step once.
- When both are outdated, update the CLI first, then the Skill.

When the `action` is `personwise update skill --at <skill-directory> --approve-upgrade`, replace
`<skill-directory>` with the directory of this installed Skill (the directory containing this
Skill's SKILL.md). Never run `doctor` or a generic capability preflight to check freshness; the
`update check` command above is the freshness check. Never ask more than once per component per
session, and never substitute another command, flag, origin, or download path for the printed
`action`. If the CLI answers `Unknown command` for `personwise update`, the installed CLI
predates this Skill's update tooling: upgrade the CLI with this Skill's bundled bootstrap
instead (`assets/bootstrap.sh --approve-upgrade` on Linux/macOS,
`assets/bootstrap.ps1 --approve-upgrade` on Windows; use `--approve-install` when no recognized
executable exists), then retry the failed step once. Reinstalling the Skill alone does not update
the CLI. If the service returns `SERVICE_RESPONSE_MISMATCH` while the installed CLI is older than
the bootstrap-pinned version, upgrade the CLI through the bundled bootstrap first and retry the
failed command once; only report `stop_and_verify_service` when the current pinned CLI still fails.

## Authenticate through the browser

Check `personwise auth status --json`. If needed, use:

```text
personwise auth begin --service personwise.ai --json
personwise auth wait --flow-id <flow-id> --timeout-seconds 1800 --json
```

Show the returned PersonWise URL and user code promptly. The user signs in, chooses an organization,
and approves access in the browser. The Agent never asks for or receives a password, OTP, token,
authorization code, callback URL, cookie, or credential-store content.

The CLI owns private user-local credential storage on every supported operating system; Skills and
Agents never inspect or implement it. Existing pre-1.1.0 logins are not migrated, so complete
browser OAuth once when no compatible local login is present.

## Pin the account and check only relevant readiness

Use global `--account <alias>` on every business command and keep the account bound to this Skill's
international service. Cross-service state must fail closed.

Do not run a general `capabilities` checklist before every task. Query, refine, resume, repair,
publish, and access tasks go directly to their relevant read/business command, which returns a
structured unsupported or authorization error when necessary.

Before each new course only, run:

```text
personwise --account <alias> course readiness --json
```

Use `can_create`, `max_slides_per_course`, and `authorization_courses_remaining` to decide whether
and how large a new course can be. Do not infer page count or credit availability before this read.

## Authorization boundary

An explicit request to create courses authorizes exactly that course count and the normal existing
credit consumption. It also authorizes using files and images the user named, attached, or selected.
Do not ask again before `course create`.

Require new authorization only for additional courses, payment or credit purchase, broader
visibility than requested, deletion, ownership transfer, organization administration, or a local
file the Agent discovered itself. When the user did not name a visibility target, set
`distribution_target` to `private` explicitly; an omitted target resolves to the OAuth grant's
publication ceiling, which can be `link`. Explicit link access,
publication, or Topics submission is part of the original request.

## Handle failures once

| Structured signal | Action |
|---|---|
| CLI absent/old | Use the pinned bootstrap; let the Host apply its install policy. |
| `AUTHENTICATION_REQUIRED` | Start one browser OAuth flow and keep the wait active. |
| `LOCAL_CREDENTIALS_UNAVAILABLE` | Report `repair_local_credentials`; do not inspect external credential systems or ask for a system password. |
| `CREDIT_INSUFFICIENT` | Stop before create and provide the returned credit/purchase action; never purchase automatically. |
| `AUTHORIZATION_LIMIT_REACHED` | Stop the additional create and report renewal/reauthorization action. |
| Unsupported operation | Stop only that operation and report the returned safe action. |
| Retryable remote error | Honor structured retry guidance and `Retry-After`; reuse the same idempotency identity. |
| `run_doctor` | Run read-only `doctor` once and report only the resulting user action. |

`auth logout` removes local state. `auth revoke` first revokes the server grant and then removes
local state; use revoke only when requested.
