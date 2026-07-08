# GitHub Label Conventions

This document defines the label conventions for GitHub issues in projects using the github-workflows plugin.

## Required Labels

**Every issue MUST have labels from ALL THREE of these categories:**

### 1. Type Labels

Indicates the nature of the work.

| Label | Description | When to Use |
|-------|-------------|-------------|
| `bug` | Something isn't working | Broken functionality, errors, crashes |
| `feature` | New functionality | Completely new capability |
| `enhancement` | Improvement to existing | Better UX, performance, behavior |
| `documentation` | Documentation only | README, guides, API docs |
| `refactor` | Code improvement | No behavior change, better structure |
| `chore` | Maintenance tasks | Dependencies, CI/CD, cleanup |

**Rule**: Choose exactly ONE type label per issue.

### 2. Priority Labels

Indicates urgency and importance.

| Label | Description | When to Use |
|-------|-------------|-------------|
| `priority:critical` | Emergency | Security issues, data loss, complete failure |
| `priority:high` | Critical path | Blocking others, production issues |
| `priority:medium` | Important | Should do this sprint, significant impact |
| `priority:low` | Nice to have | Can wait, minor improvements |

**Rule**: Choose exactly ONE priority label per issue.

### 3. Scope Labels (REQUIRED)

Identifies which component or area of the system is affected.

**Format**: `scope:<component-name>`

**Examples**:
- `scope:auth` - Authentication/authorization
- `scope:api` - API endpoints
- `scope:frontend` - User interface
- `scope:github-workflows` - GitHub workflows plugin
- `scope:claude-component-builder` - Claude component builder plugin

**Rule**: Choose AT LEAST ONE scope label per issue.

## Why Scope Labels Are Required

Scope labels are mandatory because they:

1. **Enable Context-Aware Filtering**
   - `/issue-track context` filters by scope
   - `/issue-track scope` shows only scope-relevant issues
   - `/workflow-status` groups issues by branch scope

2. **Improve Commit Integration**
   - `/commit-smart` detects related issues by scope
   - Auto-suggests `Closes #N` for matching scope issues
   - Better relevance scoring for issue references

3. **Enhance Organization**
   - Easy filtering in GitHub UI
   - Better searchability
   - Clear ownership and responsibility

4. **Prevent Orphan Issues**
   - Every issue belongs to a component
   - No ambiguity about which team/area owns the issue

## Scope Detection

The plugin automatically detects scope from:

1. **Branch context** (`env.json` → `branch.scopeLabel`)
2. **Branch name** (e.g., `feature/auth-login` → `scope:auth`)
3. **Project structure** (plugin directories, configured scopes)

### How Detection Works

```python
# Priority order for scope detection:
1. env.json branch.scopeLabel (highest)
2. Match branch name to suggested scopes
3. Manual user input (lowest - only if can't detect)
```

### Configuring Scopes

Scopes can be configured in:

1. **git-conventional-commits.json**:
   ```json
   {
     "convention": {
       "commitScopes": ["auth", "api", "ui", "docs"]
     }
   }
   ```

2. **Project structure** (auto-detected):
   - Plugin directories with `plugin.json`
   - Top-level directories (excluding node_modules, etc.)

3. **Manual initialization**:
   - Run `/github-workflows:init`
   - Scopes are analyzed and stored in `env.json`

## Optional Labels

### Branch Labels

Associate issue with a specific branch.

**Format**: `branch:<branch-name>`

**Examples**:
- `branch:feature/auth`
- `branch:release/v2.0`
- `branch:plugin/github-workflows`

### Status Labels (Discouraged)

**DO NOT use status labels**. Status should be managed via project board columns:
- ❌ `status:in-progress`
- ❌ `status:blocked`
- ✅ Use project board "In Progress" column instead

### Phase Labels (Discouraged)

**DO NOT use phase labels**. Phases should be managed via milestones:
- ❌ `phase:planning`
- ❌ `phase:implementation`
- ✅ Use milestones like "Phase: Planning" instead

## Label Combinations

### Good Examples

```
bug, priority:high, scope:auth
# A high-priority bug in the authentication system

feature, priority:medium, scope:api
# A new API feature with medium priority

enhancement, priority:low, scope:frontend, scope:api
# A low-priority enhancement affecting both frontend and API
```

### Bad Examples

```
bug, enhancement, priority:high
# ❌ Multiple type labels - choose one

feature, scope:api
# ❌ Missing priority label

bug, priority:high
# ❌ Missing scope label

bug, priority:high, status:open
# ❌ Status should be on project board, not label
```

## Enforcement

### Automatic Validation

The `/github-workflows:issue-create` command:

1. **Auto-detects scope** from branch context
2. **Validates all required labels** before creating
3. **Blocks creation** if scope is missing
4. **Prompts user** to select scope if not auto-detected

### Manual Issue Creation

When creating issues manually with `gh issue create`:

```bash
# Always include all three label categories:
gh issue create \
  --title "Fix login timeout" \
  --label "bug,priority:high,scope:auth" \
  --body "..."
```

### Issue Triage

The `/github-workflows:issue-triage` command:

1. Checks for missing required labels
2. Suggests scope based on issue content
3. Recommends priority based on keywords

## Best Practices

1. **One Type, One Priority, One+ Scope**: Always follow the 1-1-1+ rule
2. **Auto-Detect First**: Let the plugin detect scope when possible
3. **Be Specific**: Use the most specific scope that applies
4. **Multiple Scopes OK**: If an issue spans components, use multiple scope labels
5. **Review Labels**: During triage, verify all required labels are present

## Migration Guide

If you have existing issues without scope labels:

1. **Bulk update with GitHub CLI**:
   ```bash
   # Add scope to all issues with a specific label
   gh issue list --label "bug" --json number \
     | jq -r '.[].number' \
     | xargs -I {} gh issue edit {} --add-label "scope:unknown"
   ```

2. **Use issue-triage to suggest scopes**:
   ```bash
   /github-workflows:issue-triage 42
   # Will suggest appropriate scope based on content
   ```

3. **Manual review**:
   - Filter issues by label in GitHub UI
   - Add appropriate scope labels to each

## Related Commands

- `/github-workflows:issue-create` - Create issues with scope enforcement
- `/github-workflows:issue-triage` - Triage and add missing labels
- `/github-workflows:issue-track context` - Filter by scope
- `/github-workflows:label-suggest --create` - Create suggested scope labels
