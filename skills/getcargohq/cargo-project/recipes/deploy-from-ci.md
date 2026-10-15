# Recipe: deploy from CI

**Use when** the user wants `cargo-ai project deploy` to run non-interactively — on
push, on merge, or on a schedule — so the workspace stays in sync with the repo.

## Prerequisites

- **A workspace-scoped API token** (not OAuth) from **Settings → API**. Store it as
  a CI secret (`CARGO_API_TOKEN`). Token values are shown once — capture at
  creation. See [`../../cargo-workspace-management/SKILL.md`](../../cargo-workspace-management/SKILL.md)
  for `token create`.
- **`cargo.state.json` committed** in the repo. On a current project that file is just the
  pointer `{"stateUuid": "…"}`; CI resolves the workspace-held state from it. Without the
  pointer CI can't find the state, and the deploy fails rather than silently recreating
  everything.
- **Any `secret()` env vars** set as CI secrets too (e.g. `HUBSPOT_API_KEY`).

## The CI steps

```bash
# 1. Install the CLI (project already depends on @cargo-ai/cdk via package.json)
npm install -g @cargo-ai/cli@latest
npm ci

# 2. Authenticate non-interactively with the token (selects the token's workspace)
cargo-ai login --token "$CARGO_API_TOKEN"

# 3. Deploy — --yes is REQUIRED (no TTY to confirm at); --json for machine-readable output
cargo-ai project deploy --yes --json
```

## Critical CI rules

- **`--yes` is mandatory.** `deploy`/`destroy` prompt for confirmation and refuse
  to run non-interactively without it.
- **The workspace guard still applies.** The state records the workspace it was deployed
  to; deploy refuses if the token's workspace ≠ the state's workspace. One state per
  environment (a branch or directory per environment, each with its own pointer).
- **CI does not need to commit state back.** This is the part remote state changed: a
  deploy writes new uuids into the **workspace-held** state, not into your repo, so the
  next run sees them without a commit. The pointer only changes when you run
  `project state create` or `state bind`. A pre-remote-state project — one whose
  `cargo.state.json` still holds the resource map inline — *does* still need the
  commit-back dance; migrate it with `project state create` and the problem goes away.
- **Preview safely** with `cargo-ai project plan --json` (offline, no API calls) on pull
  requests, and gate `deploy` to the protected branch.
- **Prune deliberately.** Add `--prune` only when you want CI to delete resources
  removed from code; leave it off to make deploys purely additive.

## A GitHub Actions sketch

```yaml
# .github/workflows/deploy.yml
- run: npm install -g @cargo-ai/cli@latest && npm ci
- run: cargo-ai login --token "$CARGO_API_TOKEN"
  env:
    CARGO_API_TOKEN: ${{ secrets.CARGO_API_TOKEN }}
- run: cargo-ai project deploy --yes --json
  env:
    HUBSPOT_API_KEY: ${{ secrets.HUBSPOT_API_KEY }}
```
