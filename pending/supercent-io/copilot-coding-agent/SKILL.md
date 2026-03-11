---
name: copilot-coding-agent
description: GitHub Copilot Coding Agent automation. Apply the ai-copilot label to an issue → GitHub Actions auto-assigns Copilot via GraphQL → Copilot creates a Draft PR. One-click issue-to-PR pipeline.
allowed-tools: Read Write Bash Grep Glob
metadata:
  tags: copilot, copilotview, github-actions, issue-to-pr, draft-pr, graphql, automation, ai-agent
  platforms: Claude, Codex, Gemini
  keyword: copilotview
  version: 1.0.0
  source: "https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent"
---


# GitHub Copilot Coding Agent — Issue → Draft PR automation

> If you add the `ai-copilot` label to an issue, GitHub Actions automatically assigns it to Copilot,
> and Copilot creates a branch → writes code → opens a Draft PR.

## When to use this skill

- When PMs/designers create issues and Copilot starts implementation without a developer
- When offloading backlog issues (refactors/docs/tests) to Copilot
- When delegating follow-up work created by Vibe Kanban / Conductor to Copilot
- When automating pipelines like Jira → GitHub Issue → Copilot PR

---

## Prerequisites

- **GitHub plan**: Copilot Pro+, Business, or Enterprise
- **Copilot Coding Agent enabled**: Must be enabled in repo settings
- **gh CLI**: Authenticated
- **PAT**: Personal Access Token with `repo` scope

---

## One-time setup

```bash
# One-click setup (register token + deploy workflow + create label)
bash scripts/copilot-setup-workflow.sh
```

This script does:
1. Register `COPILOT_ASSIGN_TOKEN` as a repo secret
2. Deploy `.github/workflows/assign-to-copilot.yml`
3. Create the `ai-copilot` label

---

## Usage

### Option 1: GitHub Actions automation (recommended)

```bash
# Create issue + ai-copilot label → auto-assign Copilot
gh issue create \
  --label ai-copilot \
  --title "Add user authentication" \
  --body "Implement JWT-based auth with refresh tokens. Include login, logout, refresh endpoints."
```

### Option 2: Add a label to an existing issue

```bash
# Add label to issue #42 → trigger Actions
gh issue edit 42 --add-label ai-copilot
```

### Option 3: Assign directly via script

```bash
export COPILOT_ASSIGN_TOKEN=<your-pat>
bash scripts/copilot-assign-issue.sh 42
```

---

## How it works (technical)

```
Issue created/labeled
    ↓
GitHub Actions triggered (assign-to-copilot.yml)
    ↓
Look up Copilot bot ID via GraphQL
    ↓
replaceActorsForAssignable → set Copilot as assignee
    ↓
Copilot Coding Agent starts processing the issue
    ↓
Create branch → write code → open Draft PR
    ↓
Auto-assign you as PR reviewer
```

Required GraphQL header:
```
GraphQL-Features: issues_copilot_assignment_api_support,coding_agent_model_selection
```

---

## GitHub Actions workflows

| Workflow | Trigger | Purpose |
|---------|--------|------|
| `assign-to-copilot.yml` | Issue labeled `ai-copilot` | Auto-assign to Copilot |
| `copilot-pr-ci.yml` | PR open/update | Run CI (build + tests) |

---

## Copilot PR limitations

> Copilot is treated like an **external contributor**.

- PRs are created as Draft by default
- Before the first Actions run, a **manual approval** from someone with write access is required
- After approval, `copilot-pr-ci.yml` CI runs normally

```bash
# Check CI after manual approval
gh pr list --search 'head:copilot/'
gh pr view <pr-number>
```

---

## planno (plannotator) integration — optional

Review the issue spec in planno before assigning to Copilot (independent skill, not required):

```text
Review and approve this issue spec in planno
```

After approval, add the `ai-copilot` label → trigger Actions.

---

## Common use cases

### 1. Label-based Copilot queue

```
PM writes an issue → add ai-copilot label
→ Actions auto-assigns → Copilot creates Draft PR
→ Team only performs PR review
```

### 2. Combined with Vibe Kanban / Conductor

```
Follow-up issues created by Vibe Kanban:
  refactors/docs cleanup/add tests
  → ai-copilot label → Copilot handles
→ Team focuses on main feature development
```

### 3. External system integration

```
Jira issue → Zapier/webhook → auto-create GitHub Issue
→ ai-copilot label → Copilot PR
→ Fully automated pipeline
```

### 4. Refactoring backlog processing

```bash
# Bulk-add label to backlog issues
gh issue list --label "tech-debt" --json number \
  | jq '.[].number' \
  | xargs -I{} gh issue edit {} --add-label ai-copilot
```

---

## Check results

```bash
# List PRs created by Copilot
gh pr list --search 'head:copilot/'

# Specific issue status
gh issue view 42

# PR CI status
gh pr checks <pr-number>
```

---

## References

- [GitHub Copilot Coding Agent overview](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)
- [Ask Copilot to create a PR (GraphQL example)](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr)
- [Official docs: assign Copilot to an issue](https://docs.github.com/copilot/using-github-copilot/coding-agent/asking-copilot-to-create-a-pull-request)
- [Copilot PR permissions/limitations](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)
- [GitHub Copilot coding agent (VSCode docs)](https://code.visualstudio.com/docs/copilot/copilot-coding-agent)

---

## Quick Reference

```
=== Setup ===
bash scripts/copilot-setup-workflow.sh   one-time setup

=== Issue assignment ===
gh issue create --label ai-copilot ...  new issue + auto-assign
gh issue edit <num> --add-label ai-copilot  existing issue
bash scripts/copilot-assign-issue.sh <num>  manual assign

=== Verify results ===
gh pr list --search 'head:copilot/'    Copilot PR list
gh pr view <num>                        PR details
gh pr checks <num>                      CI status

=== Constraints ===
Copilot Pro+/Business/Enterprise required
First PR requires manual approval (treated as an external contributor)
PAT: repo scope required
```
