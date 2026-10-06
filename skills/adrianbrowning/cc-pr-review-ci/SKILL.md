---
name: cc-pr-review-ci
description: Comprehensive TypeScript/React PR review. Outputs structured review.json consumed by a posting script that creates a GitHub Review with inline comments. Agent runs read-only; the workflow script holds write permissions.
---

# PR Review (single-agent, CI-safe)

Review a PR across 12 domains sequentially, then write `review.json`. A separate posting script turns the JSON into GitHub inline review comments.

*If no PR number provided, diff against `origin/main` and print JSON to stdout.*

---

## Step 0 — Load prior dismissals (PR runs only)

Skip if no PR number provided.

Fetch all existing bot reviews on this PR:

```bash
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews \
  --jq '[.[] | select(.body | test("<!-- cc-pr-review -->";  "i")) | {id: .id, commit_id: .commit_id, submitted_at: .submitted_at}]'
```

For each bot review found, fetch its inline comments:

```bash
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews/$REVIEW_ID/comments \
  --jq '[.[] | {id: .id, body: .body, path: .path, line: (.line // .original_line), reactions: .reactions}]'
```

Also fetch any reply threads on those inline comments:

```bash
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments \
  --jq '[.[] | select(.in_reply_to_id != null) | {id: .id, in_reply_to_id: .in_reply_to_id, body: .body}]'
```

Build **`SUPPRESSED_FINDINGS`**: one entry per dismissed finding, `{ id, path, line, commit_id }`, where `commit_id` is the commit the prior review was posted against.

A finding is dismissed if its prior inline comment has:
- A 👎 reaction (`.reactions["-1"] > 0`), **or**
- A human reply containing dismissal language: "intentional", "by design", "won't fix", "false positive", "ignore", "not applicable", "expected"

Extract the finding `id` from the prior comment body — each inline comment posted by the script contains an HTML comment `<!-- id: {finding-id} -->` in the first line.

**Escape hatch — re-evaluate if the code changed since the dismissal.** The PR diff always contains every PR-changed line, so compare against the prior review's commit instead:

```bash
HEAD_SHA=$(gh pr view $PR_NUMBER --json headRefOid --jq .headRefOid)
gh api repos/{owner}/{repo}/compare/$COMMIT_ID...$HEAD_SHA \
  --jq '[.files[] | {filename: .filename, previous_filename: .previous_filename, patch: .patch}]'
```

Run this once per distinct `commit_id`. Remove an entry from `SUPPRESSED_FINDINGS` when its `path` matches a file's `filename` or `previous_filename` and any of these hold:
- A hunk overlaps the finding. For each hunk header `@@ -start,count +...`, the old-side interval is `start` to `start + max(count, 1) - 1` (`count` is 1 when omitted). It overlaps if that interval intersects `line - 5` to `line + 5`. Check the whole interval, not just `start`: a hunk that begins well before the finding can still span it.
- The entry has no `line` (file-level finding).
- The file has no `patch` (binary or too large to diff).

Also remove every entry for a `commit_id` whose compare call fails (for example, the commit was force-pushed away).

If no prior reviews or no dismissals: `SUPPRESSED_FINDINGS` is empty.

---

## Step 1 — Get the diff and PR metadata

- PR number given → `gh pr view $PR_NUMBER` (title and body, used by the scope domain) and `gh pr diff $PR_NUMBER`
- No PR number → `git diff origin/main` (no metadata; the scope domain skips PR hygiene)

---

## Step 2 — Run 12 domain reviews sequentially

Read the reference file for each domain, then analyze the diff. Record findings with their exact file path and line number.

**Before recording any finding**: if its computed `id` (`{domain}-{kebab-title}`) is still in `SUPPRESSED_FINDINGS` after Step 0, skip it silently.

1. **Security**         — `Read .claude/skills/cc-pr-review-ci/references/security.md`
2. **Performance**      — `Read .claude/skills/cc-pr-review-ci/references/performance.md`
3. **React/TypeScript** — `Read .claude/skills/cc-pr-review-ci/references/react-ts.md`
4. **Testing**          — `Read .claude/skills/cc-pr-review-ci/references/testing.md`
5. **Test Validity**    — `Read .claude/skills/cc-pr-review-ci/references/test-validity.md`
6. **DevOps/CI**        — `Read .claude/skills/cc-pr-review-ci/references/devops.md`
7. **Holistic**         — `Read .claude/skills/cc-pr-review-ci/references/holistic.md`
8. **Duplication**      — `Read .claude/skills/cc-pr-review-ci/references/duplication.md`
9. **Bug Hunting**      — `Read .claude/skills/cc-pr-review-ci/references/bug.md`
10. **Scope/Hygiene**   — `Read .claude/skills/cc-pr-review-ci/references/scope.md`
11. **Maintainability** — `Read .claude/skills/cc-pr-review-ci/references/thermo.md`
12. **Comments**        — `Read .claude/skills/cc-pr-review-ci/references/comments.md`

---

## Step 3 — Write review.json

1. Read `.claude/skills/cc-pr-review-ci/references/format.md` for the exact schema.

2. Merge all domain findings into a single `findings` array. Assign each finding a stable `id` following the `{domain}-{kebab-title}` convention.

3. Determine verdict:
   - Any `critical` → `CHANGES_REQUESTED`
   - `high` only → `APPROVED_WITH_SUGGESTIONS`
   - `observations` only or none → `APPROVED`

4. Write the JSON:
   - **PR run**: write to `$REVIEW_OUTPUT_PATH` (default `/tmp/review.json`)
   - **Local run (no PR number)**: print to stdout

**Do not call `gh` to post anything.** The workflow's `post-review.js` step handles all GitHub writes.
