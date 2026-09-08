# Safe Patterns Cookbook

When the scanner flags a dangerous pattern, the user almost always wants the safe replacement, not just the diagnosis. This file is the cookbook: each entry pairs a common goal with the safe way to accomplish it.

## "I want to comment on PRs from forks with test results"

**Wrong:** `pull_request_target` with `pull-requests: write`, checkout head, run tests, post comment.

**Right, in order of preference:**

1. **Use `GITHUB_STEP_SUMMARY` in a regular `pull_request` workflow.** The summary renders in the PR's checks UI, anyone can see it, no comment needed.

   ```yaml
   - name: Summarize test results
     run: |
       echo "## Test Results" >> $GITHUB_STEP_SUMMARY
       echo "- Passed: $PASS" >> $GITHUB_STEP_SUMMARY
       echo "- Failed: $FAIL" >> $GITHUB_STEP_SUMMARY
   ```

2. **Put results in the workflow logs.** Click-through is free. Most maintainers do this and never miss the comment.

3. **If you genuinely need a PR comment**, the only safe path is a GitHub App that listens for `check_run` events and posts from outside Actions. Not an Actions workflow with `pull_request_target`.

## "I want to label PRs based on title, branch name, or file paths"

**Wrong:**
```yaml
on: pull_request_target
jobs:
  label:
    steps:
      - run: |
          if [[ "${{ github.event.pull_request.title }}" == *"bug"* ]]; then
            gh pr edit ${{ github.event.pull_request.number }} --add-label bug
          fi
```

Two problems: `pull_request_target` is dangerous, and the title is interpolated into shell (template injection).

**Right:** use a vetted labeling action that reads config from a checked-in file, not from interpolated values.

```yaml
on: pull_request_target
permissions:
  contents: read
  pull-requests: write
jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@<sha>  # config in .github/labeler.yml
```

This is one of the few legitimate uses of `pull_request_target`: the action receives PR metadata via parameters (which are stringified by Actions, blocking injection), config lives in the trusted base branch, and no shell interpolation occurs. Still pin to SHA. Still set minimal permissions. Still no `checkout` of head.

## "I want to run benchmarks on PRs with a comparison vs main"

**Wrong:** `pull_request_target`, checkout head, run benchmark, compare to cached main, comment with diff. The cache step alone is a P0 (see Pass 6).

**Right:** split into two workflows.

Workflow A (`benchmark-pr.yml`) — unprivileged:
```yaml
on: pull_request
permissions: {}
jobs:
  benchmark:
    permissions:
      contents: read
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<sha>
      - run: ./run-benchmark.sh > benchmark.txt
      # Validate before upload: only numbers and separators
      - run: grep -E '^[0-9.,]+$' benchmark.txt > /dev/null || exit 1
      - uses: actions/upload-artifact@<sha>
        with:
          name: pr-benchmark
          path: benchmark.txt
      - run: echo ${{ github.event.number }} > pr-number.txt
      - run: grep -E '^[0-9]+$' pr-number.txt > /dev/null || exit 1
      - uses: actions/upload-artifact@<sha>
        with:
          name: pr-number
          path: pr-number.txt
```

Workflow B (`benchmark-comment.yml`) — privileged, but doesn't touch untrusted code:
```yaml
on:
  workflow_run:
    workflows: ["benchmark-pr"]
    types: [completed]
permissions: {}
jobs:
  comment:
    if: github.event.workflow_run.conclusion == 'success'
    permissions:
      pull-requests: write
      actions: read
    runs-on: ubuntu-latest
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@<sha>
        # ... download both artifacts, validate strictly again
      - name: Validate
        run: |
          grep -E '^[0-9.,]+$' benchmark.txt || exit 1
          grep -E '^[0-9]+$' pr-number.txt || exit 1
      - name: Post comment
        env:
          PR_NUM: $(cat pr-number.txt)
          BENCH: $(cat benchmark.txt)
        run: gh pr comment "$PR_NUM" --body "Benchmark: $BENCH"
```

Even this is dangerous enough that a GitHub App is better. But this two-workflow pattern with strict artifact validation is the OpenSSF-blessed compromise.

## "I want to use the PR branch name in a step"

**Wrong:**
```yaml
- run: echo "Building branch ${{ github.head_ref }}"
```

**Right:**
```yaml
- env:
    BRANCH: ${{ github.head_ref }}
  run: echo "Building branch $BRANCH"
```

The `env:` indirection treats the value as data, not as a shell command fragment. Same pattern for any `${{ github.event.* }}`, `inputs.*`, or other potentially attacker-controlled field.

## "I want to set an environment variable from a file's contents"

**Wrong:**
```yaml
- run: echo "VERSION=$(cat version.txt)" >> $GITHUB_ENV
```

If `version.txt` came from an untrusted source (artifact from another workflow, file in PR), this is environment file injection — the attacker can include newlines to define arbitrary variables.

**Right:**
```yaml
- name: Read and validate version
  run: |
    VERSION=$(cat version.txt)
    # Validate strictly: only the format you expect
    if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      echo "Invalid version format"
      exit 1
    fi
    echo "VERSION=$VERSION" >> $GITHUB_ENV
```

Or better: don't pass through `$GITHUB_ENV` at all. Read the value, use it in the same step.

## "I want to publish to npm/PyPI on tag push"

**Wrong:**
```yaml
on:
  push:
    tags: ['v*']
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

Three problems: long-lived `NPM_TOKEN`, no environment isolation, no approval gate, no attestation.

**Right:**
```yaml
on:
  push:
    tags: ['v*']
permissions: {}
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release  # required reviewers, scoped to main, restricted secrets
    permissions:
      contents: read
      id-token: write       # OIDC for Trusted Publishing
      attestations: write   # for Sigstore attestation
    steps:
      - uses: actions/checkout@<sha>
      - uses: actions/setup-node@<sha>
        # NOTE: no `cache:` — release workflows must not cache
      - run: npm ci
      - run: npm publish --provenance  # OIDC + attestation in one
```

Tag protection ruleset prevents the `v*` tag from existing until this deploy succeeds. Immutable releases enabled on the repo. Approver clicks once on the environment gate. No long-lived tokens anywhere.

For PyPI: use `pypa/gh-action-pypi-publish` with no token argument (it picks up OIDC from `id-token: write`).

## "I want to download a release binary and use it in CI"

**Wrong:**
```yaml
- run: |
    curl -L https://github.com/owner/tool/releases/latest/download/tool > tool
    chmod +x tool
    ./tool
```

Two problems: `latest` is mutable (attacker can replace it), and no integrity check on the binary.

**Right:**
```yaml
- run: |
    curl -L https://github.com/owner/tool/releases/download/v1.2.3/tool > tool
    echo "abc123...expected_sha256...  tool" | sha256sum -c -
    chmod +x tool
    ./tool
```

Pin the version, check the hash. If the action you're using wraps this download, verify the action itself embeds an expected hash (not just a download URL). This is the "hash-pinning is necessary but not sufficient" problem: a SHA-pinned action that curl-pipes-bash to a release URL is no safer than an unpinned action.

## "I need a workflow to comment on third-party issues / PRs"

This is the legitimate use case that `pull_request_target` is most often reached for. The right answer is **don't use Actions for this** — use a GitHub App that listens for the relevant webhook events and acts in an isolated context.

A GitHub App:
- Receives the same event data Actions would have received
- Runs outside the workflow context, so it can't be poisoned by template injection
- Has explicit, scoped credentials (the App's installation token)
- Is reviewable as code in its own repo, not buried in YAML

The Mariatta Python tutorial and `gidgethub` library are the canonical references for building these. Astral's `astral-sh-bot` is the production pattern.

This is more work than a workflow, which is the actual reason most projects keep their `pull_request_target` workflows: hosting and maintaining an App is non-trivial. But if the workflow handles privileged operations triggered by external contributors, an App is the only safe option.

## "I want to skip the checks for a specific bot account"

**Wrong:**
```yaml
if: github.actor == 'dependabot[bot]'
```

The actor field on certain triggers can be forged or spoofed in chained workflows. If an attacker can get *any* code path to run on behalf of `dependabot[bot]` (or your CI bot), they bypass the check.

**Right:** use signed commits and verify the GPG signature, or check the App's installation token rather than the actor name. Or — better — don't bypass checks for bots at all; let Dependabot's PRs go through the same gates as humans, and accept the friction.

## When in doubt: split the workflow

The single most-applicable safety pattern is "split a workflow that needs to do an untrusted thing AND a privileged thing into two workflows that share a strictly-validated artifact." It works for:

- Test results → PR comment
- Build artifacts → release publish
- PR metadata → labeling / triage
- External API call → repo write

The cost is one extra workflow file and a strict-validation step on the artifact. The benefit is that the privileged side never touches untrusted code.

If you find yourself recommending mitigations for a single dangerous workflow, stop and recommend the split instead.
