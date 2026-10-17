---
name: brag-doc-from-git
description: Build an evidence-based brag document or self-review draft from your merged pull requests and commits, leaving visible gaps where results are unknown. Use for review season, promotion cases or resume updates.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Brag document from git history

Goal: turn what you actually shipped into a draft you can edit, without inventing impact. A brag document lists work and results; this skill collects the work and marks every missing result as a gap for you to fill.

## Step 1: collect the evidence

Ask for the time window (default: the last 6 months) and the repositories. Then, with the GitHub CLI signed in:

```
gh search prs --author @me --merged --merged-at ">=YYYY-MM-DD" --json title,url,closedAt,repository --limit 200
```

For code not on GitHub, use `git log --author="<name or email>" --since="YYYY-MM-DD" --no-merges --pretty="%h %ad %s" --date=short` in each repository. Also ask the user to paste anything git cannot show: incidents handled, mentoring, reviews done, talks, docs, on-call, design decisions, kind words from colleagues.

Do not read private repositories the user did not name. Do not guess names, teams or numbers.

## Step 2: group, do not summarize yet

Group the items into themes (for example: reliability, new features, performance, tooling, mentoring, cross-team work). List each item under its theme with date and link. Merge duplicates (a feature PR plus its follow-up fixes).

## Step 3: draft each theme

For every theme write:

- **What I did**: one or two sentences in plain verbs, using only what the titles, diffs and user notes support.
- **Result**: only if a number, quote or outcome was provided. Otherwise write `[GAP: what changed for users or the team? any metric before/after?]`.
- **Evidence**: links.
- **Scope signal** (if supported): led it, did it alone, worked across teams, was on call, reviewed others.

## Step 4: finish with gaps and questions

End with a list of every `[GAP]`, ranked by how much it would strengthen the case, and the three questions whose answers would add the most. Offer to turn the final version into a self-review, a promotion packet outline or resume bullets.

## Rules

- Never invent metrics, percentages, customer names, titles or scope. A visible gap is better than a made-up number.
- Do not inflate: "contributed to" stays "contributed to". Match verbs to the evidence.
- Keep the user's credit honest: if a PR was a team effort, say what part was theirs.
- Keep private or confidential details out unless the user says the document is internal.
- Output Markdown the user can paste into their notes.
