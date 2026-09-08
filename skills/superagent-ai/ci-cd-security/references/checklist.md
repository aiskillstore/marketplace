# CI/CD Security Checklist

A flat checklist for PR review or repo audit. Walk it top to bottom. If anything fails, the workflow needs work before merge.

## Per workflow

### Trigger

- [ ] No `pull_request_target` (or written exception in PR description, narrowly scoped, no checkout of head, no interpolation of event fields into shell)
- [ ] No `workflow_run` (or same exception above)
- [ ] If `issue_comment`, `issues`, `pull_request_review*`: no interpolation of user-controlled fields into `run:` blocks
- [ ] `push` triggers are scoped to specific branches/tags, not `*`

### Permissions

- [ ] Top-level `permissions: {}` is set
- [ ] Each job grants only the permissions it actually needs
- [ ] No job has `write-all` or unscoped `contents: write` unless it's a release job in a protected environment

### Action pinning

- [ ] Every `uses:` line is pinned to a full-length commit SHA, not a tag or branch
- [ ] Each pinned SHA has a YAML comment showing the human-readable version: `uses: actions/checkout@<sha> # v4.1.1`
- [ ] No SHAs reference impostor commits (zizmor's `impostor-commit` audit passes, or manually verified the commit doesn't show GitHub's "doesn't belong to any branch" warning)
- [ ] Indirect (nested) action usages are also SHA-pinned — easiest enforced via GitHub's "require actions pinned to full-length commit SHA" org policy

### Shell injection

- [ ] No `${{ github.event.* }}` interpolation in any `run:` block
- [ ] No `${{ github.head_ref }}`, `github.event.issue.body`, `github.event.pull_request.title`, etc. interpolated into shell
- [ ] User-controlled values are passed via env vars and referenced as `$VAR` in shell
- [ ] `$GITHUB_ENV` and `$GITHUB_OUTPUT` writes are not built from untrusted content

### Checkout

- [ ] No `actions/checkout` with `ref: ${{ github.event.pull_request.head.sha }}` in any privileged workflow
- [ ] `persist-credentials: false` is set on `actions/checkout` unless the workflow specifically needs the token persisted

### Cache

- [ ] No `cache:` in release/publish workflows
- [ ] No `cache:` in workflows that handle secrets
- [ ] If `cache:` is used: untrusted PR workflows can't write to the same cache key as default-branch builds (use distinct keys, or scope by `github.run_id`)
- [ ] No sensitive data in cache contents

### Artifacts

- [ ] If artifacts flow from `pull_request` workflow to `workflow_run` workflow: contents validated strictly before use (e.g. PR-number-only files reject non-digits)
- [ ] No `eval`-like patterns reading artifact contents into shell or `$GITHUB_ENV`

### Release workflows specifically

- [ ] Uses a dedicated deployment environment (e.g. `release`)
- [ ] Environment has required reviewers (at least one non-actor)
- [ ] Environment scoped to `main` branch only
- [ ] Trusted Publishing / OIDC used wherever the registry supports it (PyPI, crates.io, npm, GHCR, AWS)
- [ ] Long-lived registry tokens (if unavoidable) are scoped to the release environment, not org/repo secrets
- [ ] Sigstore attestations generated for released artifacts
- [ ] Tag protection ruleset prevents release tag creation until the deploy succeeds
- [ ] Immutable releases enabled at repo level
- [ ] No `cache:` anywhere in the release path

## Per repository

### Settings

- [ ] Default `GITHUB_TOKEN` permissions set to read-only (org-level)
- [ ] "Require actions to be pinned to a full-length commit SHA" enabled (org-level)
- [ ] `pull_request_target` and `workflow_run` forbidden at org level (via rulesets or zizmor's `forbidden-uses`)
- [ ] Branch protection on `main`: no force push, PR required, status checks required
- [ ] Branch protection enforced for admins too (no bypass)
- [ ] Tag protection: release tags can't be created outside the release process, can't be updated or deleted
- [ ] Forbidden branch patterns set for sensitive prefixes (`advisory-*`, `internal-*`, etc.) if you use those

### Identity

- [ ] All org members enforce 2FA (TOTP minimum; WebAuthn/Passkeys when available)
- [ ] Admin role limited to as few accounts as possible
- [ ] PATs and deploy keys audited periodically; expired ones revoked
- [ ] Self-hosted runners are scoped to specific repos/orgs and don't run on fork PRs

### Dependency management

- [ ] Dependency update bot enabled for actions, language packages, and Docker
- [ ] Cooldowns configured: 3–7 days minimum for third-party packages (so compromised releases get caught before they land)
- [ ] First-party / internal deps can have shorter cooldowns
- [ ] Security alerts enabled

## Per organization

- [ ] Written policy on which triggers are allowed
- [ ] Written exception process for unusual cases (e.g. legitimate `pull_request_target` use)
- [ ] Audit log streamed to SIEM or polled regularly; alerts on:
  - Self-hosted runner registration (`self_hosted_runners.register`)
  - Repository creation
  - Secret access from unexpected workflows
  - Admin role grants
- [ ] Onboarding includes CI/CD security training (or at least a pointer to this checklist)

## Triage priorities when scanning at scale

When you have hundreds of findings across an org, work in this order:

1. **`pull_request_target` and `workflow_run` workflows that check out head code** — these are pwn-request patterns, treat as P0.
2. **Template injection in privileged workflows** — `${{ github.event.* }}` in `run:` blocks. P0 if the workflow has secrets or write permissions.
3. **Release workflows without environment isolation** — unprotected publish credentials, no approval, no immutable releases. P0 for any repo whose package is on a registry.
4. **Unpinned actions in any workflow with secrets** — P1. Convert to SHA pinning, verify no impostor commits.
5. **Missing `permissions: {}`** — P1. Mostly mechanical to fix; do it in bulk PRs.
6. **Cache usage in privileged paths** — P1. Remove, especially in release flows.
7. **Imposter commits** — P2 if the pinned SHA is intact but lives only on a fork; verify before changing anything since the maintainer may have a reason.
8. **Stylistic findings (missing `name:`, superfluous actions, etc.)** — P3.

Don't file a ticket for a P0–P2 finding without a fix proposal. Tickets without fixes rot. A PR with the right rewrite gets merged.
