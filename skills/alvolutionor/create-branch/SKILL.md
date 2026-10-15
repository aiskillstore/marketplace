---
name: create-branch
description: Create Jira Cloud issues and related Bitbucket Cloud branches, or reuse an existing issue and branches, with preview-first helpers and verified assignment, status and active sprint. Use when the user requests a Jira issue or branches for one; reading an issue alone creates nothing.
---

# Create issues and branches

Resolve the requested issue content and repositories from the conversation and Git remotes. Ask only for missing facts that prevent execution. Use `scripts/create_branch.py` relative to this skill; `scripts/create_jira.py` is its internal Jira helper. The helpers need Python 3.10+ and `requests`. See [setup](references/setup.md) for private configuration and complete examples.

Creating or changing this skill does not run it. An explicit request to create issues or branches authorizes those requested operations and established defaults. Do not add Slack messages, commits, merges, deployments or working-tree switches. A preview request stays read-only.

## Choose the requested operation

- New issue only: `--input <request.json>` without `--repo`. Bitbucket access is unnecessary.
- Branches for an existing issue: provide its key and repeat `--repo <slug>` for each requested repository. Reuse the issue; never create a replacement.
- New issue and branches: provide `--input` and the requested repositories. Use the newly returned issue key.
- Read existing issue: pass its key without repositories. This stays read-only even with `--apply`.

Commands preview by default. Add `--apply` only for the user-requested writes. A new-issue preview lists the issue defaults and requested repositories; final branch names and base commits are resolved after Jira supplies the real key.

## Write the issue

Use a concise, factual summary and description in the project's language. For a defect, include observed and expected behavior, reproduction or a concrete example, and the environment when known. Do not invent requirements or include unresolved scope decisions in a created card. Ask the missing questions first. Preserve explicit assignee and status choices from the conversation.

Input requires `summary` and `description`. Description accepts text or an Atlassian Document Format document: structured JSON with `type: doc`, `version: 1` and nonempty `content`. Optional keys are `project`, `issue_type`, `assignee_account_id` and `status`. Project defaults to private configuration; type defaults to `Task`, status to `To Do`, and assignee to the authenticated Jira user. Use `Bug` for a defect when that type exists.

Resolve exactly one active sprint on the configured board before issue creation. If none or several are active, resolve the target instead of guessing. Set assignment during creation, transition if needed, add sprint membership, then read all three back. Do not report an accepted create response as complete until the final verification succeeds.

## Resolve and create branches

Read the issue and determine the repositories from the requested scope. Do not add frontend/backend repositories simply because they exist. Obtain branch-type prefixes and development/production bases from each repository's branching model. Default to `bugfix` for a Bug and `feature` otherwise; `--type` and `--from` override when requested. Hotfix uses the production base by default.

The branch suffix is `KEY-summary-slug`, capped at 40 characters before the configured prefix. Reuse an existing branch containing the issue key; if several candidates exist, establish the intended branch before continuing. Preserve a card's in-progress or later status unless the user explicitly requests moving it.

The helper validates the local clone's origin against the configured workspace and repository. It fetches the selected base commit and pushes that commit to the new branch ref without switching the user's worktree. Never force-push, delete/recreate a branch to refresh indexing, or claim immediate Jira Development-panel indexing: that depends on the consuming team's integration.

Read back the remote branch and Jira assignment/status/sprint before reporting success. An unknown create/push outcome requires inspection before retrying. If the issue already exists after a partial failure, continue on its returned key and reuse existing branches; never rerun the new-issue create operation blindly.

Return the issue URL, verified assignee, status and sprint, and each requested branch URL. State incomplete steps explicitly. Add attachments or issue links only when separately requested and verified.
