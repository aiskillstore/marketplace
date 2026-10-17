---
name: pr-description
description: Write a pull request title and description from the actual diff and commits, with what changed, why, how it was tested and what to review. Use when asked to write or improve a PR description.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Write a PR description a reviewer can use

Goal: let a reviewer decide in two minutes what to look at, and let a future reader understand why the change exists.

## Gather

1. Find the base branch and run `git log --oneline <base>..HEAD` and `git diff --stat <base>...HEAD`, then read the diff.
2. Look for the reason: linked issue or ticket number in commits or branch name, the user's request, comments added in the diff. If the reason is not in any of these, ask the user; do not invent a motivation.
3. Check what was tested: test files in the diff, and commands the user ran. If tests were not run, say so plainly.
4. Look for a `.github/pull_request_template.md` or `PULL_REQUEST_TEMPLATE`. If one exists, fill it in instead of using the structure below.

## Structure

```
<Title: imperative, under 70 characters, names the behavior change, not the files>

## Why
<The problem or request, in 1 to 3 sentences. Link the issue if there is one.>

## What changed
- <Behavior-level bullets grouped by area, not a file list.>

## How to review
- Start with <file or area>; the rest follows from it.
- Risky part: <the part most likely to be wrong, and why>.
- Not changed on purpose: <anything a reviewer may expect and will not find>.

## Testing
- <Exact commands run and results.>
- <Manual steps and what was seen. "Not tested: ..." if applicable.>

## Rollout / risk
<Migrations, config, feature flags, compatibility, how to roll back. "None" only if true.>
```

## Rules

- Describe what the diff does, not what you wish it did. Re-read the diff after drafting and delete any claim it does not support.
- Do not list every file. Do list behavior changes, new config, new dependencies and deleted code.
- No filler ("This PR aims to..."). No emojis unless the repo uses them.
- Screenshots or output examples: say where one would help; never describe a screenshot you did not see.
- Output the title and body in a code block so it can be copied. Do not run `gh pr create` unless asked.
