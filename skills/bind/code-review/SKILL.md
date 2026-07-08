---
name: code-review
description: Automated PR code review with multi-agent analysis
version: 1.0.0
license: MIT
compatibility: opencode
---

## Overview

Automated code review for pull requests using multiple specialized agents with confidence-based scoring to filter false positives.

## Prerequisites

- [GitHub CLI](https://cli.github.com/) installed and authenticated
- `github-pr` skill installed (bundled automatically)
- AGENTS.md files in your repository (optional but recommended)

## Slash Command

### `/code-review [--comment]`

Performs automated code review on a pull request using multiple specialized agents.

**Options:**
- `--comment` - Post the review as inline comments on the PR (default: outputs to terminal only)

**Example:**
```bash
# Review current branch's PR (output to terminal)
/code-review

# Post review as PR comments
/code-review --comment
```

## What It Does

1. **Pre-check**: Determines if review is needed (skips closed, draft, trivial, or already-reviewed PRs)
2. **Guideline Discovery**: Gathers relevant AGENTS.md files from the repository
3. **PR Summary**: Summarizes the pull request changes
4. **Parallel Review**: Launches 4 agents to independently review:
   - **Agents 1 & 2**: Audit for AGENTS.md compliance
   - **Agent 3**: Scan for obvious bugs in the diff
   - **Agent 4**: Analyze for logic issues in changed code
5. **Validation**: Each issue is validated by a sub-agent
6. **Output**: Posts inline comments or outputs to terminal

## Agent Orchestration Instructions

Follow these steps precisely when executing `/code-review`:

### Step 1: Pre-check

Run the review check script:

```bash
bun .opencode/skill/github-pr/check-review-needed.js
```

If `shouldReview` is `false`, stop and report the reason. Do not proceed with review.

**Note:** Still review Claude/AI-generated PRs - only skip if Claude has already *commented* on the PR.

### Step 2: Gather Guidelines

Run the guideline discovery script:

```bash
bun .opencode/skill/github-pr/list-guideline-files.js --json
```

This returns all AGENTS.md files relevant to the PR. Store these for use in compliance checking.

### Step 3: Summarize PR

Launch a haiku agent to view the PR and return a summary of the changes:

```bash
gh pr view --json title,body,files,additions,deletions
gh pr diff
```

The summary should include:
- PR title and description
- List of changed files with brief descriptions
- Overall nature of the changes

### Step 4: Parallel Review Agents

Launch 4 agents in parallel to independently review the changes. Each agent should return a list of issues with:
- Description of the issue
- Reason it was flagged (e.g., "AGENTS.md compliance", "bug", "logic error")
- File path and line number(s)
- Confidence score (0-100)

Provide each agent with the PR title, description, and summary from Step 3.

#### Agents 1 & 2: AGENTS.md Compliance (Sonnet)

Audit changes for AGENTS.md compliance. When evaluating compliance:
- Only consider AGENTS.md files that share a file path with the file being reviewed (or its parents)
- Verify the guideline explicitly mentions the rule being violated
- Quote the exact rule from AGENTS.md in the issue description

#### Agent 3: Bug Detection (Opus)

Scan for obvious bugs. Focus only on the diff itself without reading extra context:
- Flag only significant bugs that will cause incorrect behavior
- Ignore nitpicks and likely false positives
- Do not flag issues that cannot be validated from the diff alone

#### Agent 4: Logic Analysis (Opus)

Look for problems in the introduced code:
- Security issues
- Incorrect logic
- Race conditions
- Resource leaks

Only flag issues within the changed code.

**CRITICAL: HIGH SIGNAL ONLY**

We want:
- Objective bugs that will cause incorrect behavior at runtime
- Clear, unambiguous AGENTS.md violations with quoted rules

We do NOT want:
- Subjective concerns or "suggestions"
- Style preferences not in AGENTS.md
- Potential issues that "might" be problems
- Anything requiring interpretation

If uncertain, do not flag. False positives erode trust.

### Step 5: Validate Issues

For each issue found in Step 4, launch a validation sub-agent:

- **Bugs/logic issues**: Use Opus agent
- **AGENTS.md violations**: Use Sonnet agent

The validator receives:
- PR title and description
- Issue description and location
- Relevant code context

The validator must confirm:
- The issue is real and verifiable
- For AGENTS.md issues: the rule exists and applies to this file
- The issue was introduced in this PR (not pre-existing)

### Step 6: Filter Results

Remove any issues that:
- Failed validation in Step 5
- Are pre-existing (not introduced in this PR)
- Appear correct but look like bugs
- Are pedantic nitpicks
- Would be caught by linters
- Are general quality concerns not in AGENTS.md
- Have lint ignore comments

### Step 7: Post Results

If issues were found, post inline comments using:

```bash
bun .opencode/skill/github-pr/post-inline-comment.js <pr-number> \
  --path <file> \
  --line <line> \
  [--start-line <start>] \
  --body "<comment>"
```

**Comment format:**

For small fixes (up to 5 lines changed), include a suggestion:

````markdown
Brief description of the issue

```suggestion
corrected code here
```
````

For larger fixes, describe the issue and provide a prompt:

```markdown
Description of the issue and suggested fix at a high level.

Fix prompt:
`Fix [file:line]: [brief description]`
```

**Important:**
- Only post ONE comment per unique issue
- Suggestions must be COMPLETE - no follow-up work required
- Link to AGENTS.md when citing compliance issues

If NO issues were found and `--comment` flag is provided, post a summary:

```bash
gh pr comment <pr-number> --body "## Code review

No issues found. Checked for bugs and AGENTS.md compliance."
```

## Confidence Scoring

Each issue is scored 0-100:

| Score | Meaning |
|-------|---------|
| 0 | Not confident, false positive |
| 25 | Somewhat confident, might be real |
| 50 | Moderately confident, real but minor |
| 75 | Highly confident, real and important |
| 100 | Absolutely certain, definitely real |

Only issues scoring **80 or higher** are reported.

## False Positive Filters

These are NOT issues (do not flag):

- Pre-existing issues not introduced in this PR
- Code that looks like a bug but is actually correct
- Pedantic nitpicks a senior engineer would ignore
- Issues linters will catch (don't run linter to verify)
- General quality concerns unless in AGENTS.md
- Code with lint ignore comments

## Code Link Format

When linking to code in comments, use this exact format:

```
https://github.com/owner/repo/blob/[full-sha]/path/file.ext#L[start]-L[end]
```

Requirements:
- Must use full git SHA (not abbreviated)
- Must use `#L` notation for lines
- Include at least 1 line of context before and after

## Best Practices

### For Better Reviews

- Maintain clear AGENTS.md files with specific rules
- Include context in PR descriptions
- Keep PRs focused and reasonably sized

### When to Use

- All PRs with meaningful changes
- PRs touching critical code paths
- PRs where guideline compliance matters

### When Not to Use

- Draft PRs (automatically skipped)
- Closed PRs (automatically skipped)
- Trivial automated PRs (automatically skipped)
- Urgent hotfixes requiring immediate merge
