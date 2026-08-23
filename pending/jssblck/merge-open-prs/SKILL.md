---
name: merge-open-prs
description: Use when asked to "merge all open PRs" or land the open PRs together. Snapshots the open set, builds one gh stack, resolves conflicts, and merges once.
user-invocable: true
---

# Merge the open PRs as one stack

Snapshot the open PRs. That list is the work set. Assemble it into one native
GitHub stack, resolve conflicts until the top branch is the intended post-merge
tree, then merge the whole stack with one `gh stack merge`.

Standing rules:

- **The work set does not grow.** A PR opened after the snapshot is ignored.
  After every `sync`, `submit`, and `view`, compare stack membership to the work
  set; drop extras (unstack and rebuild) and never merge them.
- **A default-branch move is in scope.** Sync, resolve, and re-verify before
  merging.
- **Every PR lands through the forge.** Never merge into a local default branch
  and push, and never push straight to the default branch. Do local git work
  only on the PRs' own branches, in a temporary worktree you remove afterwards.
- **Read the `gh-stack` skill before any `gh stack` command** and use its
  non-interactive flags.

## 1. Snapshot the work set

```sh
gh api --paginate 'repos/{owner}/{repo}/pulls?state=open&per_page=100' \
  --jq '.[] | {number,title,headRefName:.head.ref,headRefOid:.head.sha,baseRefName:.base.ref,isDraft:.draft}'
```

Read every page. If the user named specific PRs, those are the work set;
otherwise every open PR is. Record numbers, head SHAs, and head branches.

For anything but a single obvious PR, build a file-overlap map:

```sh
gh pr view <n> --json files,headRefName,headRefOid,baseRefName,isDraft,reviewDecision,statusCheckRollup,isCrossRepository,maintainerCanModify
gh pr diff <n>
```

An unready PR (draft, requested changes, failing checks) stays in the work set.
Make it mergeable; do not drop it, and do not merge over unanswered requested
changes without user direction.

Check whether the PRs are already in a native stack:

```sh
gh api graphql -f owner={owner} -f repo={repo} -f query='
query($owner:String!,$repo:String!){
  repository(owner:$owner,name:$repo){
    pullRequests(states:OPEN, first:100){
      nodes{ number headRefName baseRefName
        stack{ number entries(first:50){ nodes{ position pullRequest{ number } } } } } } } }'
```

`stack` is `null` on an unstacked PR, even one chained by base.

If the work set is empty, stop. If it is one PR, skip to the single-PR merge in
section 6. Two or more PRs become one stack, even when files-disjoint; never
merge them individually with `gh pr merge`.

## 2. Choose the stack order

Files-disjoint PRs cannot conflict textually in any order, so order for
semantics and verifiability. In priority order:

- Small, isolated PRs at the bottom (config tweaks, dependency bumps, tooling
  that helps verify the layers above).
- Foundational before dependent: when one PR calls what another adds, the
  dependency sits lower.
- Shared-state PRs at the top: a version constant, migration number, or
  checked-in generated artifact compounds with everything below.
- Otherwise by blast radius, smallest at the bottom.

An existing base chain is evidence for that order. A user-stated order wins.
State the order and a one-line reason per layer before you build.

## 3. Know the gate

```sh
gh repo view --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed
gh api repos/{owner}/{repo}/branches/{branch}/protection   # may 404 even when gated
gh api repos/{owner}/{repo}/rulesets
```

Pass the repo's merge method explicitly on `gh stack merge`. Rulesets and
classic protection are separate; check both for required checks, required
reviews, and strict up-to-date policy. `gh stack merge` cannot bypass any of
them.

## 4. Assemble one native stack

A native stack requires one repository (no fork PRs), stacked PRs enabled
(`submit` and `link` exit 9 otherwise), and permission to rewrite the branches:
building a chain from PRs that each target the default branch rebases and
force-pushes every branch above the bottom. Get explicit approval before
rewriting a branch you do not own, and disclose every rewrite. If any condition
fails, use `references/fallback-collapse.md`.

If GitHub already records exactly the planned stack, do not rebuild:

```sh
gh stack checkout <anyWorkSetPR>   # gh stack unstack --local first if a local stack overlaps
gh stack view --json
```

If the PRs already chain by base in the planned order and `stack` is null,
`gh stack link <bottomPR> <nextPR> <topPR>` registers them without rewriting.

Otherwise rebuild. `link` only appends and never removes, so unstack any
grouping that overlaps, then:

```sh
git fetch origin
# init CREATES a missing local branch from the one below, silently producing an
# empty layer. Materialize them first:
for b in <bottomBranch> <nextBranch> <topBranch>; do
  git show-ref --verify --quiet "refs/heads/$b" || git branch "$b" "origin/$b"
done
gh stack init --base <default-branch> <bottomBranch> <nextBranch> <topBranch>
gh stack rebase          # exit 3: resolve, git add, gh stack rebase --continue
gh stack submit --auto
gh stack view --json     # membership and order must match the work set
```

## 5. Keep the stack current, resolve, verify

Record the default-branch tip after every fetch. When it moves, or any layer
reports `needsRebase`:

```sh
gh stack sync
```

`sync` cascade-rebases and pushes. Exit 3 is a conflict (run `gh stack rebase`,
resolve, continue). Exit 0 with `Sync aborted` means local and remote diverged;
see gh-stack troubleshooting. `sync` can also pull in PRs someone linked on
GitHub; re-check membership.

If a teammate pushes to a work-set branch or closes a work-set PR, stop and
ask. If someone merges a work-set PR to the default branch, that is a trunk
move: sync and continue.

Fix a layer's conflict on that layer, then `gh stack rebase --upstack`; do not
dump fixes onto the top branch. `references/conflicts.md` covers textual
resolution, lockfiles, and the semantic conflicts Git cannot see (version
bumps, migration numbers, combined-tree breaks). Before pushing a fix, confirm
`isCrossRepository` and `maintainerCanModify` match the remote you will update.

Verify with the repo's own checks:

- Baseline the default branch in the worktree so failures are attributable.
- On the top branch (the post-merge tree): build, format, lint, and run the
  tests for the stack's blast radius.
- Let each PR's required checks finish; they still gate `gh stack merge`.
- After the merge, run the full suite on the actual default branch and confirm
  integration tests ran rather than skipped.

Re-verify after every successful sync, and immediately before the merge.

## 6. Merge once

Re-read `gh stack view --json` and the default-branch tip. Membership must
equal the work set and no head may have moved since verification.

```sh
gh stack merge <stack-number> --yes <verified-method-flag>
```

All-or-nothing: if any PR cannot merge, none do. Drafts block; `gh pr ready`
first, with user direction where the draft was deliberate. A merge queue queues
the stack instead and picks its own method; watch the PRs land. Afterwards
`gh stack sync --prune` and remove the worktree.

Single PR:

```sh
gh pr view <n> --json headRefOid
gh pr merge <n> <verified-method-flag> --delete-branch --match-head-commit <sha>
```

`--admin` only with explicit approval, disclosed in the report.

## 7. Report

1. Work-set PRs, PRs ignored as later arrivals, and whether files overlapped.
2. Stack number and layers bottom to top with a reason each; found or built.
   Any work-set PR not merged, and why.
3. Conflicts resolved, branches rewritten, PRs folded, any bypass.
4. Default-branch moves and what you did about them.
5. What you ran and what passed, including on the final default branch.
6. Final default-branch SHA and remaining open PRs.

If the request chains a release, use `$tag-release` after CI is green on the
merged commit.
