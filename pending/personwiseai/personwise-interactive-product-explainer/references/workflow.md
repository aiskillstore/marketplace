# Produce the explainer through the PersonWise CLI

## Establish only the required connection

Run `personwise version --json`; require software 1.1.6 or newer and CLI contract 1.0. If absent or
old, use the bundled `assets/bootstrap.sh --approve-install` or Windows
`assets/bootstrap.ps1 --approve-install`. The Host applies its own installation policy; do not add
a PersonWise confirmation or narrate supply-chain and credential internals on the normal path.
Never use sudo, modify PATH/policy, overwrite a target, or switch origin.

Check `auth status --json`. If needed, use `auth begin --service personwise.ai --json`, show the
PersonWise browser URL/code, and keep `auth wait --flow-id <flow-id> --json` active. Never request
or handle passwords, OTPs, tokens, codes, callback URLs, cookies, or secrets. Pin the alias with
global `--account <alias>`.

Do not run `doctor` or a general `capabilities` preflight. Use `doctor` only when a structured error
recommends `run_doctor`.

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

## Read creation readiness before designing

Run:

```text
personwise --account <alias> course readiness --json
```

If blocked, stop before building a blueprint and report the one returned action. Never buy credit.
The user's request already authorizes creating this explainer and using one existing course credit.

Choose an earned slide count no greater than `max_slides_per_course`. Use the five-job explainer arc
when supported; with a lower maximum, recompose the whole arc into the available pages. If the user
requested a larger count, explain the resolved count once. Never promise a count before readiness
or truncate an already-written longer outline.

## Keep a secret-free run ledger

Track the blueprint, claim ledger, account alias, run/project IDs, logical idempotency identities,
source filename/status, checkpoint/actions, revisions, review findings, configuration, and final
URLs. Never store tokens, cookies, credential references, upload grants, signed URLs, or private
resource contents.

## Create one durable run

Put one create object in a bounded JSON file:

```text
desired_slide_count = resolved count from readiness
knowledge_source_mode = materials_only for strict files, otherwise open
declared_sources = exact retained strict source count
distribution_target = the explicit user target, otherwise private
```

Include this optional telemetry only when supported:

```json
{
  "skill_invocation": {
    "skill_id": "personwise-interactive-product-explainer",
    "skill_version": "2.1.8"
  }
}
```

Run `course create --input <create.json> --json`, save the run/project IDs, and do not treat
allocation as completion.

## Upload and review

Upload each file the user named, attached, or selected with `source add`, then reconcile
`source status`. Those files and images need no extra approval. An Agent-discovered local file does.

Do not call `run advance` while any source is `pending` or `processing`: the run stays at
`awaiting_sources` and advancing is a 200 no-op until every declared source is canonically `ready`.
Keep bounded `run wait` and `source status`; server-orchestrated runs auto-continue once sources
complete. `source status` reports the upload ticket lifecycle as `ticket_status` (`consumed`
means the upload was received, not that processing is done); the canonical `status` field is
the source processing state (`pending`, `processing`, `ready`, or `failed`), with `phase`,
`processed_pages`/`total_pages`, and a safe `error` when failed. Only `ready` permits advancing.

Use bounded `run wait`, then fresh `run get` and `course snapshot` reads. `run wait` returns on a
terminal status and at review checkpoints (`paused`); on older CLI releases it returns only on
`POLL_TIMEOUT`, which then serves as the checkpoint signal — read fresh state, then review or
resume. At Outline, confirm the
resolved page count and teaching jobs against the claim ledger. At Script, audit every title,
key-point set, page-text line, and narration sentence. Apply the smallest revision-bound atomic
correction, fetch fresh state, and call `run advance` only when currently allowed.

Attach supplied product images in the allowed window. With vision, inspect every slide through
review sheets, correct content first, regenerate only the complete failed subset, and re-inspect.
Without vision, require canonical image completion and report `visual_review=not_performed`.

## Finish and recover

Use presenter choices only for a concrete user requirement. Keep `run wait` active to terminal
state. Default omitted visibility to an explicit `distribution_target` of `private` — an omitted
target resolves to the OAuth grant's publication ceiling, which can be `link`; complete explicit
link/embed/publication requests without asking again. Return the URL matching the final access
mode only when final state proves playability: `access_mode=link` gives the public `share_url`;
`access_mode=private` gives the login-required `editor_url` and must be described as viewable only
after login, and state clearly that outsiders cannot open it. If sharing is needed, enable link access or ask the
Agent to do it.

After timeout or an ambiguous response, read state and reuse the same logical idempotency identity.
Use `run retry` only when fresh state allows it, honor `Retry-After`, and never parallel-hammer a
run. Stop for structured authentication, credit, authorization-limit, or unsupported-operation
errors and report only the returned safe action. A failed run exposes the safe `error` through
`run get`, and a blocked publish returns `requirements`; report them exactly as returned.
