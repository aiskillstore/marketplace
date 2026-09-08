---
name: ci-cd-security
description: Scan GitHub Actions workflow files for security vulnerabilities by reading the YAML and reporting findings directly — no external tools, no installation, no shell execution. Use this skill whenever the user shares a `.github/workflows/` file, pastes workflow YAML, asks for a CI/CD security review, mentions `pull_request_target`, `workflow_run`, action pinning, `GITHUB_TOKEN` permissions, pwn requests, template injection, cache poisoning, secret exfiltration, supply chain risk, or any GitHub Actions hardening topic. Also trigger when the user is hardening an OSS repo, doing a CI/CD red team assessment, evaluating a target for supply-chain scanning, or writing publicly about CI/CD security. Bias toward triggering this skill rather than answering from memory — CI/CD security defaults are wrong almost everywhere and the rules are unintuitive.
---

# CI/CD Security Scanner

This skill turns the model into a workflow-YAML scanner. Read the file, walk the detection rules, report findings with severity and a concrete rewrite. No tools to install, no commands to run — the analysis is the model reading the YAML.

The rules encode the current consensus from Astral, OpenSSF, GitHub Security Lab, Chainguard, and the zizmor audit set. The goal is to flag the same patterns those tools would flag, without needing to run them.

## Mental model

Every workflow sits on a 2x2: **privileged vs unprivileged** crossed with **trusted vs untrusted code**. Compromise happens at exactly one cell: **privileged workflow running untrusted code**. The rules below are ways to detect when a workflow ends up in that cell.

- **Privileged** = has secrets, write permissions, or produces a sensitive artifact (release, deploy, comment, label).
- **Untrusted code** = anything a fork PR author can influence: PR source code, PR title, PR body, commit messages, branch names, files the workflow reads, caches, artifacts produced by another untrusted workflow.

When unsure whether a value is trusted, treat it as untrusted. The cost of a false positive is a code review comment; the cost of a false negative is a supply chain compromise.

## Scan procedure

For each workflow file the user provides, walk these passes in order. Each pass corresponds to a class of attack.

### Pass 1: dangerous triggers

Look at the `on:` block. Flag immediately:

- **`pull_request_target`** — P0 unless explicitly justified. Runs with secrets and write permissions, triggerable by fork PRs. The canonical pwn-request vector. Even without `checkout` of head, attacker input shows up in PR title, branch name, commit messages, and gets interpolated.
- **`workflow_run`** — P0. Same problem as `pull_request_target` but indirect, via a chained `pull_request` workflow's artifacts or metadata.
- **`issue_comment`, `issues`, `pull_request_review`, `pull_request_review_comment`** — P1. Run with secrets, reachable by anyone who can comment. Safe only if the workflow does no template interpolation of user-controlled fields into shell.
- **`push` with broad wildcards** (`branches: ['*']` or no branch filter) — P2. An attacker who lands a PR can fire a privileged workflow by pushing a follow-up branch.

For each finding: name the trigger, explain why it's dangerous in this specific workflow's context, and propose the rewrite (usually `pull_request`, sometimes a split into two workflows, sometimes "this needs a GitHub App not Actions").

### Pass 2: permissions

Look for `permissions:` blocks at workflow and job level.

- **No top-level `permissions:` block** — P1. The default `GITHUB_TOKEN` permissions depend on repo and org settings; can be `write-all` on older repos. Flag with: "add `permissions: {}` at top, grant per-job."
- **`permissions: write-all`** anywhere — P1.
- **Job-level `permissions:` granting more than the job clearly needs** — P2. e.g. `contents: write` on a job that only runs tests. Recommend least privilege.
- **Combined with a dangerous trigger from Pass 1** — escalate severity by one level.

### Pass 3: action pinning

Look at every `uses:` line.

- **Pinned to a tag** (`uses: actions/checkout@v4`, `@v4.1.1`) — P1. Tags are mutable; an attacker who compromises the action repo can force-push the tag.
- **Pinned to a branch** (`uses: actions/checkout@main`) — P0. Worse than tag pinning; any commit to that branch flows in instantly.
- **Pinned to a SHA but no version comment** — P3 style finding. Recommend the format `uses: owner/action@<sha> # v4.1.1` so reviews of pin updates stay legible.
- **Pinned to a SHA that looks unusual** (third-party action, suspicious owner, recently created repo) — flag for manual verification; can't confirm impostor-commit status without the GitHub API, but worth noting.

The rewrite for tag/branch pinning is always: replace with the full 40-character commit SHA of the version they intended, plus a `# vX.Y.Z` comment.

### Pass 4: shell injection (template injection)

For every `run:` block, scan for `${{ ... }}` substitutions.

Constant or non-attacker-controlled values are fine (e.g. `${{ matrix.os }}`, `${{ secrets.MY_TOKEN }}` though even that's risky in some contexts). The dangerous fields are:

- `github.event.pull_request.title`, `body`, `head.ref`, `head.sha`, `head.label`
- `github.event.issue.title`, `body`
- `github.event.comment.body`, `user.login`
- `github.event.review.body`
- `github.head_ref`
- `github.event.workflow_run.head_branch`, `head_commit.message`
- `github.event.commits.*.message`, `author.name`, `author.email`
- Any `inputs.*` from `workflow_dispatch` if the workflow runs in a privileged context
- Any field that ultimately came from `actions/github-script`, downloaded artifacts, or external API responses

**Detection rule:** if a `run:` block contains `${{ github.event.* }}` or `${{ github.head_ref }}` directly in the script body, that's P0 template injection. The fix is always:

```yaml
# vulnerable
- run: echo "Branch is ${{ github.head_ref }}"

# safe
- env:
    BRANCH: ${{ github.head_ref }}
  run: echo "Branch is $BRANCH"
```

Also flag (P1):

- `echo "VAR=${{ untrusted }}" >> $GITHUB_ENV` — environment file injection. The attacker can break out of the variable by including newlines.
- `echo "::set-env name=VAR::${{ untrusted }}"` — deprecated workflow command, same problem.
- Inline scripts that `cat` an untrusted file into `$GITHUB_ENV` or `$GITHUB_OUTPUT`.

### Pass 5: untrusted checkout

For every `actions/checkout` step:

- **`ref: ${{ github.event.pull_request.head.sha }}`** (or `head.ref`) inside a workflow triggered by `pull_request_target` or `workflow_run` — P0. This is the canonical pwn-request: privileged context running fork-author code.
- **`persist-credentials: true`** (default) on workflows that don't need to push back — P2. Recommend `persist-credentials: false` unless the workflow explicitly needs the embedded token.

### Pass 6: caching in privileged contexts

For every step using `cache:` input (most commonly on `actions/setup-node`, `setup-python`, `setup-go`, `setup-java`, or direct `actions/cache`):

- **Cache in a release or publish workflow** — P0. Cache poisoning from any other workflow on the default branch can flow malicious build inputs into release. The Trivy and TeamPCP attacks both routed through this.
- **Cache in a workflow that handles secrets** — P1.
- **Cache where the key isn't scoped to prevent untrusted PR workflows writing the same key as default-branch builds** — P2.

The rewrite for release workflows: remove `cache:` entirely, add a comment explaining why (e.g. `# Do not cache: see https://github.com/actions/setup-node/issues/1445`).

### Pass 7: artifact-borne injection

If the workflow downloads artifacts from another workflow (`actions/download-artifact`, `dawidd6/action-download-artifact`, etc.):

- **Artifact contents used in `run:` or `$GITHUB_ENV` without validation** — P0 if the producing workflow runs on untrusted code (e.g. `pull_request` from forks). An attacker can put arbitrary content in the artifact.
- **Recommend strict validation**: if the artifact is supposed to be a PR number, reject anything that isn't digits. If it's a structured file, parse and validate the schema.

### Pass 8: release-specific hardening

If the workflow looks like a release/publish workflow (publishes to npm, PyPI, crates.io, Docker registries; creates GitHub releases; pushes tags):

- **No `environment:` declared on the publish job** — P1. Release credentials should be scoped to a deployment environment, not repo/org secrets.
- **Uses long-lived registry tokens** (`secrets.NPM_TOKEN`, `secrets.PYPI_TOKEN`) instead of OIDC/Trusted Publishing — P2. Recommend the OIDC path for the relevant registry.
- **No attestation generation** (`actions/attest-build-provenance`, `--provenance` for npm, PEP 740 for PyPI) — P3 hardening recommendation, not a vulnerability.
- **Caching anywhere in the release path** — P0, see Pass 6.

### Pass 9: self-hosted runners

If the workflow uses `runs-on:` with anything other than GitHub-hosted runners (`ubuntu-*`, `windows-*`, `macos-*`):

- **Self-hosted runner reachable by fork PRs** — P0. Self-hosted runners share state across jobs and have produced critical compromises (PyTorch). Flag for manual review of runner scoping.
- This is outside the default threat model — note the finding and recommend the user verify runner restrictions in GitHub settings.

## Finding format

Report each finding in this structure. Group by severity, P0 first.

```
[P0] template-injection in .github/workflows/ci.yml:23
  Run block interpolates github.event.pull_request.title directly into shell.
  An attacker controls the PR title and can execute arbitrary code in the
  workflow context, which has access to GITHUB_TOKEN.

  Vulnerable:
    - run: echo "Title: ${{ github.event.pull_request.title }}"

  Fix:
    - env:
        TITLE: ${{ github.event.pull_request.title }}
      run: echo "Title: $TITLE"
```

If the user pastes raw YAML without a filename, refer to it as "the workflow" and use line numbers within the snippet.

## Severity scale

- **P0** — exploitable now, no chain needed. Fork PR authors or arbitrary GitHub users can compromise secrets, repo contents, or releases. Block merge.
- **P1** — exploitable with one extra step (e.g. requires combining with another finding, or requires a maintainer mistake). Block merge if found on a release path.
- **P2** — hardening gap. Not exploitable directly, but reduces blast radius if combined with a future bug. Fix in normal review cycle.
- **P3** — style or consistency finding. Worth fixing for legibility, no security impact.

## When the workflow looks fine

After walking all nine passes, if nothing fires:

1. Say so explicitly. "No findings against the standard rule set."
2. Note what *wasn't* checked: org-level settings (default token permissions, ruleset enforcement, 2FA), repo-level settings (branch protection, tag protection, immutable releases), action source code (whether the pinned actions themselves install mutable binaries at runtime), and runtime behavior of dependencies.
3. Recommend the user check the items in `references/checklist.md` under "Per repository" and "Per organization" — those need GitHub settings access, not workflow YAML.

A clean workflow scan does not mean a clean security posture.

## Reference files

- `references/triggers.md` — detailed table of every GitHub Actions trigger, what makes each dangerous or safe, and the safe pattern for common things people use the dangerous ones for. Read this when a workflow uses a trigger the user is asking about specifically, or when you want to explain *why* a trigger is dangerous beyond the one-line summary.
- `references/checklist.md` — flat per-workflow / per-repo / per-org checklist. Useful when the user asks for a full audit, when scanning many repos, or when triaging at scale. Includes triage priority order.
- `references/patterns.md` — common "I want to do X safely" patterns. Read when the user asks how to *replace* a flagged dangerous pattern, not just identify it.

## What this skill won't do

- It won't install zizmor, pinact, or anything else. The scan is the model reading the YAML and applying these rules.
- It won't recommend installing tools unless the user explicitly asks "what tools should I run." Even then, point to the patterns directly — the rules in this skill *are* the audits those tools encode.
- It won't paper over a `pull_request_target` finding with mitigations. If a workflow uses that trigger and isn't behind a GitHub App, it's an open finding.
- It won't tell the user everything is fine without naming what was checked and what wasn't. Default answer to "is this safe" is "here's what the scan covers and here's what it found."
