---
name: ship-it
description: Use when asked to "ship it", commit and open a PR, or get CI green. Verifies locally, commits, opens the PR, and loops on CI until every check passes.
user-invocable: true
---

# Ship it: commit, open the PR, get CI green

Finish with the change committed, pushed, open as a ready pull request, and green
in CI. Invoking `$ship-it` authorizes that complete workflow. Pause only for a
material ambiguity, a required approval, or a failure that cannot be resolved
with the available access.

Work on a feature branch, never the default branch (in a worktree if that is the
repo's flow). If you are already on a feature branch, stay on it. Follow the
repo's branch-naming convention. When the repo has none and a branch is needed,
use the `agent/` prefix.

## 1. Verify locally before you commit

Never push work you have not proven builds and passes. Run the repo's own checks,
cheapest first. Find them in the contributor docs or the CI config; do not assume
a toolchain.

- **Generate first if the repo has a codegen step.** If some code is generated
  (and may be gitignored or must be refreshed after a source edit), run that step
  before building; skipping it produces confusing "undefined symbol" build errors
  that are not real.
- **Mirror what CI runs.** Read the CI config (or the contributor docs) to see the
  real checks, then run them locally so CI is not the first place you see a
  failure: the repo's formatter, its linter, its pre-commit checks, its build, and
  the tests for what you touched.
- **Know your local gaps.** Some checks cannot run on your machine (a tool or
  platform CI has that you do not). Run what you can, note the gap, and let CI
  cover it rather than treating a local-environment limitation as a real failure.
- **Run the full or integration suite when the change reaches it.** Include tests
  that need services or extra setup: those often skip silently when unconfigured,
  so a green run can be hollow. Make sure the relevant ones actually ran. A change
  that does not reach that layer may not need it.

When a fix breaks a test, do not just patch the one failure: scan for other call
sites or fixtures that relied on the old behavior, so the next CI run does not
surface a sibling break.

## 2. Commit

Inspect the complete diff and the working tree before staging. Preserve unrelated
user changes. Group related files into logical commits and stage explicit paths.
Write each message with a clean body:

```sh
git add <paths>
git commit -m "$(cat <<'EOF'
<Imperative subject line, no trailing period>

<Body: explain WHY the change is needed and what it does, not a restatement of
the diff. Wrap at ~80 columns.>

<attribution trailer required by the active global instructions, if any>
EOF
)"
```

Rules that always hold:

- Imperative subject ("Fix the stale cache read...", "Reject empty payloads...").
- The body carries the reasoning. Bump any shared version or sequence constants
  the change requires and say so.
- Apply the standing attribution, punctuation, and `stop-slop` rules to the
  message and the PR body.

## 3. Open the PR

Push the branch and check whether it already has an open PR:

```sh
gh pr list --state open --head <branch> --json number,title,url,isDraft,baseRefName,headRefName
```

Reuse the existing PR when present. Update its title and body, correct its base if
needed, and mark it ready with `gh pr ready <n>` when it is a draft. Otherwise,
create a ready PR with a self-contained body:

```sh
gh pr create --base <default-branch> --head <branch> \
  --title "<same imperative style as the commit subject>" \
  --body "$(cat <<'EOF'
## Why this change

Fixes #<issue>.

<What is wrong today and why it matters.>

## What changed

<What the change does, as a short bulleted list.>

## Testing

<Exact commands run and their results. If a check was not run, say why.>

<attribution footer required by the active global instructions, if any>
EOF
)"
```

Notes:

- Reference the issue with `Fixes #<n>` (or `Closes #<n>`) when the work started
  from one; many workstreams open with "plan and implement a fix for issue N".
- Flex headings to fit the change while keeping the reason, implementation, and
  concrete verification easy to find. Include configuration instructions only
  when setup or runtime configuration changed. A short fenced code block for a
  key type or signature is useful when it clarifies the change.
- Add an attribution footer only when the active global instructions require it.
- Base the default branch. Create a normal ready PR, with no labels or reviewers
  unless asked. Do not add an agent-specific title prefix.
- Before watching CI, verify the final PR's base, head, readiness, title, body,
  and URL with `gh pr view`.

## 4. Get CI green

CI is not green until **every** check passes: the build (across whatever matrix it
runs), the test job, and the formatter and linter checks.

Wait with `gh pr checks <n> --watch --interval 20` (it blocks until the run
resolves), in the foreground or as a background job. Watch the complete check set
so a filtered view cannot hide a failure. When a check fails, start with the complete
failed-job log, then search within it as needed:

```sh
gh run view <run-id> --log-failed
```

Then loop: **diagnose the failure, fix it, re-run the local gates from step 1,
commit the fix, push, and re-poll.** A first red run is normal and useful (it
catches hidden dependencies like a fixture that relied on old behavior); keep
going until it is all green. Do not declare done on a partial pass.

## 5. Report

Close with the PR link and the concrete green state: which check groups passed,
what shipped as a short list of commits, and any first-run failure fixed along
the way. State plainly that CI is fully green.
