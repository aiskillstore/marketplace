# GitHub Actions Triggers Reference

The trigger determines what context the workflow runs in: what permissions it has by default, whether it has access to secrets, and whether the code it runs can be influenced by fork PR authors. Most CI/CD compromises start with picking the wrong trigger.

## Quick table

| Trigger | Runs with secrets? | Default permissions | Triggerable by fork PR? | Verdict |
|---|---|---|---|---|
| `pull_request` | No (forks); Yes (same-repo) | Read-only on forks | Yes | **Safe**. Default for anything touching PR content. |
| `pull_request_target` | Yes | Write-all (or repo default) | Yes | **Ban**. Privileged workflow + fork-triggerable. Canonical pwn-request vector. |
| `workflow_run` | Yes | Write-all (or repo default) | Indirectly, via the triggering workflow | **Ban**. Same problem as `pull_request_target`. |
| `push` | Yes | Repo default | No (only repo writers) | Safe for trusted branches. Be careful with branch filters. |
| `issue_comment` | Yes | Repo default | Yes (any contributor) | **Dangerous**. Treat all comment content as untrusted input. |
| `issues` | Yes | Repo default | Yes | **Dangerous**. Issue title/body are attacker-controlled. |
| `pull_request_review` / `pull_request_review_comment` | Yes | Repo default | Yes | **Dangerous**. Review body is attacker-controlled. |
| `schedule` | Yes | Repo default | No | Safe. |
| `workflow_dispatch` | Yes | Repo default | No (requires write access) | Safe. |
| `release` | Yes | Repo default | No | Safe — but the release process itself needs hardening (see SKILL.md §release). |

## The banned triggers

### `pull_request_target`

What it does: runs in the context of the base repo (yours, with secrets and write permissions), but is triggered by PRs from forks.

Why it's dangerous: every other trigger that's reachable from a fork either runs without secrets (`pull_request`) or runs in a context the fork author can't influence (`push` to your branches). `pull_request_target` is the only one that hands fork authors a path into a privileged execution environment.

The canonical attack: workflow checks out `${{ github.event.pull_request.head.sha }}` and then runs build/test scripts. An attacker submits a PR that modifies `package.json`'s `postinstall`, or adds a malicious test, or anything else that runs code. The workflow executes it with full secrets.

Even workflows that *don't* check out PR head code are often vulnerable, because attacker input shows up in many other places (PR title, branch name, commit message) and gets interpolated into `run:` blocks.

**The fix:** use `pull_request` instead. If you need to comment on the PR or label it, do that from a separate `workflow_run` (still dangerous, see below) or — better — a GitHub App that lives outside Actions.

If you absolutely must keep it, the absolute minimum hardening is:
- `permissions: {}` at top, grant only what's needed
- Never check out `head.sha` or `head.ref` — only check out `github.ref` (the base) or omit checkout entirely
- Never interpolate any `github.event.*` into a `run:` block
- Add `if: github.repository == 'owner/repo'` so the workflow doesn't run in forks
- Treat this as a finding that needs review every time the workflow changes

### `workflow_run`

What it does: triggered after another workflow completes. Runs in the context of the *base* repo with secrets and write permissions.

Why it's dangerous: same as `pull_request_target` but indirect. If workflow A runs on `pull_request` (safely, unprivileged), and workflow B runs on `workflow_run: A`, then B is a privileged workflow whose execution is downstream of code an attacker can write.

Specific attack vectors:
- **Artifact-borne injection**: A uploads a file the attacker controls (e.g. PR number, but the contents are arbitrary). B downloads it and uses it in a `run:` block without validation. Code execution.
- **Cache poisoning**: A writes to the cache. B reads from it during setup. Cache contents flow into B's privileged context.
- **`github.event.workflow_run.*` interpolation**: B uses fields from the triggering workflow's metadata. Some of those fields (head_branch, head_commit.message) are attacker-controlled.

**The fix:** the legitimate use case for `workflow_run` is "I need to do something privileged based on a thing that happened in an unprivileged workflow." Almost always, the right answer is to move the privileged step to a GitHub App that listens for webhook events directly. The App framework Astral uses (`astral-sh-bot`) and the Mariatta tutorial linked from their blog are good starting points.

If you must keep it: validate artifact contents strictly, never use `cache:`, never interpolate `workflow_run` event fields into shell, and use a dedicated deployment environment with approval gating.

## The grey-area triggers

### `issue_comment`, `issues`, `pull_request_review*`

These run with secrets and write permissions, and they're reachable by anyone who can comment on issues or PRs (which on public repos is anyone with a GitHub account).

The risk is not "fork PR runs malicious code in your context" — that's `pull_request_target`'s problem. The risk is template injection: the comment body or issue title shows up in `${{ ... }}` somewhere and gets interpolated into a `run:` block.

**The rule:** these triggers are OK if you (a) never interpolate any user-controlled field into shell, and (b) keep the workflow's permissions to the minimum needed. A "label PR if title matches" workflow on `pull_request_target` should be `permissions: { pull-requests: write }` and nothing else, with the title accessed through an env var.

### `push` with broad branch filters

`push` is safe in the sense that it can only be triggered by someone with write access — but if your branch protection is weak and the trigger fires on `*` or `feature/*`, an attacker who lands a PR can then push a follow-up branch that fires a workflow with full repo permissions.

**The rule:** restrict `push` triggers to specific branches you actually want to build on (`main`, release branches, tags). Don't fire on arbitrary feature branches unless you mean to.

## Safe patterns for common needs

### "I want to comment on PRs from forks with test results"

Wrong: `pull_request_target` with `pull-requests: write`, checkout head, run tests, post comment.

Right (in order of preference):
1. Use `GITHUB_STEP_SUMMARY` in a regular `pull_request` workflow. The summary shows up in the PR's checks UI, accessible to everyone, no comment needed.
2. Just put the results in the workflow logs. Anyone can click through.
3. If you really need a comment: a small GitHub App that listens for `check_run` events and posts comments from outside Actions.

### "I want to label PRs based on file paths or title"

Wrong: `pull_request_target` interpolating `github.event.pull_request.title` into a `run:` block.

Right: `pull_request_target` with `permissions: { pull-requests: write }` only, using a vetted action like `actions/labeler` that takes its config from a checked-in file (not from PR contents). No interpolation into shell. No checkout of head.

### "I want to run benchmarks on PRs with a comparison vs main"

Wrong: `pull_request_target`, checkout head, run benchmark, compare to cached main result, comment with diff.

Right: split into two workflows.
- Workflow A: `pull_request`, no secrets, runs the benchmark on the PR's code, uploads the result as an artifact (just the numbers, validated as numbers).
- Workflow B: `workflow_run` chained off A, downloads the artifact, validates that the file contains only digits and a separator, compares to main, posts the comment. No `cache:`. Use `permissions: { pull-requests: write }`.

This is dangerous enough that a GitHub App is better. But the two-workflow pattern with strict artifact validation is the OpenSSF-blessed compromise.

### "I want to publish to npm/PyPI on tag push"

Wrong: `on: push` with `tags: ['v*']`, secret `NPM_TOKEN` from repo-level secrets, no environment, no approval.

Right:
- `on: push` with `tags: ['v*']` to trigger
- Job uses `environment: release` (configured with required reviewers)
- Trusted Publishing (OIDC) instead of `NPM_TOKEN` where the registry supports it
- Tag protection ruleset prevents the tag from being created until the release deploy succeeds (use a separate `release-gate` env if you have many release jobs)
- No `cache:` in any step
- Sigstore attestation generated for the artifact
- Immutable releases enabled on the repo
