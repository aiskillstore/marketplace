---
name: git-workspace-init
description: "Initialize a new git worktree and branch for feature development or bug fixes. Use when: (1) Starting work on a new feature, (2) Beginning a bug fix, (3) Creating an isolated workspace for any task, (4) You want to work in parallel on multiple branches. This skill handles branch naming with conventional branch conventions, worktree creation, and remote push setup."
---

# Git Workspace Init

Initialize an isolated git worktree with a properly named branch following [conventional branch naming](https://conventional-branch.github.io/) conventions.

## When to Use

- Starting a new feature
- Beginning a bug fix
- Creating a hotfix
- Documentation updates
- Refactoring work
- Any task needing an isolated workspace

## Prerequisites

- Git repository with a remote configured
- Write access to push branches

## Workflow Overview

1. **Get task details** → Ask for type and description (or accept from command)
2. **Generate branch name** → Apply conventional branch naming
3. **Create worktree** → Set up isolated workspace
4. **Push to remote** → Track branch on origin
5. **Navigate** → Switch to new workspace

## Step 1: Gather Task Information

Ask the user for or accept from command arguments:

### Task Type

| Type | Use Case | Example |
|------|----------|---------|
| `feat` | New feature | `feat/user-authentication` |
| `fix` | Bug fix | `fix/login-validation-error` |
| `hotfix` | Urgent production fix | `hotfix/security-patch` |
| `docs` | Documentation | `docs/api-reference` |
| `refactor` | Code restructuring | `refactor/extract-service` |
| `test` | Test additions | `test/auth-integration` |
| `chore` | Maintenance | `chore/upgrade-dependencies` |
| `perf` | Performance improvement | `perf/optimize-queries` |
| `ci` | CI/CD changes | `ci/add-deploy-workflow` |
| `style` | Code style/formatting | `style/apply-prettier` |

### Task Description

A brief description that will become the branch name suffix:
- Use lowercase
- Use hyphens for spaces
- Keep it concise but descriptive

**Examples:**
- "user authentication" → `user-authentication`
- "fix validation error" → `validation-error`
- "add dark mode" → `dark-mode`

## Step 2: Generate Branch Name

Format: `<type>/<description>`

```bash
# Examples
feat/user-authentication
fix/null-pointer-exception
hotfix/xss-vulnerability
docs/installation-guide
refactor/extract-user-service
```

### Naming Rules

1. **Lowercase only** - `feat/Add-User` → `feat/add-user`
2. **Hyphens for spaces** - `fix/login error` → `fix/login-error`
3. **No special characters** - Only `a-z`, `0-9`, `-`, `/`
4. **Concise** - Keep under 50 characters total
5. **Descriptive** - Should indicate the work being done

### Helper Function

```python
import re

def generate_branch_name(task_type: str, description: str) -> str:
    """Generate conventional branch name from type and description."""
    valid_types = ["feat", "fix", "hotfix", "docs", "refactor", "test", "chore", "perf", "ci", "style"]

    if task_type not in valid_types:
        raise ValueError(f"Invalid type '{task_type}'. Must be one of: {', '.join(valid_types)}")

    # Normalize description
    normalized = description.lower().strip()
    # Replace spaces and underscores with hyphens
    normalized = re.sub(r'[\s_]+', '-', normalized)
    # Remove invalid characters
    normalized = re.sub(r'[^a-z0-9-]', '', normalized)
    # Remove consecutive hyphens
    normalized = re.sub(r'-+', '-', normalized)
    # Trim hyphens from ends
    normalized = normalized.strip('-')

    return f"{task_type}/{normalized}"
```

## Step 3: Create Git Worktree

Worktrees allow working on multiple branches simultaneously without stashing or switching.

### Default Worktree Location

Worktrees are created in a `.worktrees` directory at the repository root:

```
my-project/
├── .worktrees/
│   ├── feat-user-auth/      # Worktree for feat/user-auth
│   └── fix-login-error/     # Worktree for fix/login-error
├── src/
└── ...
```

### Create Worktree Commands

```bash
# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel)

# Define worktree directory (replace / with - for directory name)
BRANCH_NAME="feat/user-authentication"
WORKTREE_DIR="$REPO_ROOT/.worktrees/${BRANCH_NAME//\//-}"

# Ensure .worktrees directory exists
mkdir -p "$REPO_ROOT/.worktrees"

# Create worktree with new branch from main/master
git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" origin/main
```

### Workflow

```python
import subprocess
import os

def create_worktree(branch_name: str, base_branch: str = "main") -> str:
    """Create a new worktree for the given branch."""
    # Get repo root
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True
    )
    repo_root = result.stdout.strip()

    # Create worktree directory name (replace / with -)
    worktree_dir_name = branch_name.replace("/", "-")
    worktree_path = os.path.join(repo_root, ".worktrees", worktree_dir_name)

    # Ensure .worktrees directory exists
    os.makedirs(os.path.join(repo_root, ".worktrees"), exist_ok=True)

    # Fetch latest from remote
    subprocess.run(["git", "fetch", "origin"], check=True)

    # Create worktree with new branch
    subprocess.run(
        ["git", "worktree", "add", "-b", branch_name, worktree_path, f"origin/{base_branch}"],
        check=True
    )

    return worktree_path
```

## Step 4: Push Branch to Remote

Set up tracking with the remote repository:

```bash
# From within the new worktree
cd "$WORKTREE_DIR"

# Push and set upstream
git push -u origin "$BRANCH_NAME"
```

### Workflow

```python
def push_branch(worktree_path: str, branch_name: str):
    """Push the new branch to remote with tracking."""
    subprocess.run(
        ["git", "-C", worktree_path, "push", "-u", "origin", branch_name],
        check=True
    )
```

## Step 5: Navigate to Workspace

After creation, navigate to the new worktree:

```bash
cd "$WORKTREE_DIR"
pwd
git status
```

**Important:** Inform the user of the new workspace path so they can navigate there in their terminal.

## Complete Example

```python
import subprocess
import os
import re

def generate_branch_name(task_type: str, description: str) -> str:
    """Generate conventional branch name."""
    valid_types = ["feat", "fix", "hotfix", "docs", "refactor", "test", "chore", "perf", "ci", "style"]

    if task_type not in valid_types:
        raise ValueError(f"Invalid type. Must be one of: {', '.join(valid_types)}")

    normalized = description.lower().strip()
    normalized = re.sub(r'[\s_]+', '-', normalized)
    normalized = re.sub(r'[^a-z0-9-]', '', normalized)
    normalized = re.sub(r'-+', '-', normalized)
    normalized = normalized.strip('-')

    return f"{task_type}/{normalized}"


def init_workspace(task_type: str, description: str, base_branch: str = "main") -> dict:
    """
    Initialize a new git worktree with conventional branch naming.

    Args:
        task_type: Type of work (feat, fix, hotfix, docs, refactor, test, chore, perf, ci, style)
        description: Brief description of the task
        base_branch: Branch to base the new branch on (default: main)

    Returns:
        dict with branch_name, worktree_path, and success status
    """
    # Generate branch name
    branch_name = generate_branch_name(task_type, description)
    print(f"Branch name: {branch_name}")

    # Get repo root
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True
    )
    repo_root = result.stdout.strip()

    # Create worktree path
    worktree_dir_name = branch_name.replace("/", "-")
    worktree_path = os.path.join(repo_root, ".worktrees", worktree_dir_name)

    # Ensure .worktrees exists
    os.makedirs(os.path.join(repo_root, ".worktrees"), exist_ok=True)

    # Fetch latest
    print("Fetching latest from origin...")
    subprocess.run(["git", "fetch", "origin"], check=True)

    # Create worktree with new branch
    print(f"Creating worktree at: {worktree_path}")
    subprocess.run(
        ["git", "worktree", "add", "-b", branch_name, worktree_path, f"origin/{base_branch}"],
        check=True
    )

    # Push branch to remote
    print(f"Pushing {branch_name} to origin...")
    subprocess.run(
        ["git", "-C", worktree_path, "push", "-u", "origin", branch_name],
        check=True
    )

    # Verify
    print(f"\nWorkspace initialized!")
    print(f"  Branch: {branch_name}")
    print(f"  Path: {worktree_path}")
    print(f"\nTo start working:")
    print(f"  cd {worktree_path}")

    return {
        "branch_name": branch_name,
        "worktree_path": worktree_path,
        "success": True
    }


# Example usage:
# init_workspace("feat", "user authentication")
# init_workspace("fix", "login validation error")
# init_workspace("docs", "API reference update")
```

## Quick Reference

### Branch Type Cheat Sheet

| Type | When to Use |
|------|-------------|
| `feat` | Adding new functionality |
| `fix` | Fixing a bug |
| `hotfix` | Urgent production fix |
| `docs` | Documentation only |
| `refactor` | Restructuring without behavior change |
| `test` | Adding or fixing tests |
| `chore` | Build, deps, tooling |
| `perf` | Performance improvements |
| `ci` | CI/CD pipeline changes |
| `style` | Formatting, whitespace |

### Worktree Commands

```bash
# List all worktrees
git worktree list

# Remove a worktree (when done)
git worktree remove <path>

# Prune stale worktrees
git worktree prune
```

### Cleanup After Merge

After your PR is merged:

```bash
# Remove the worktree
git worktree remove .worktrees/feat-user-authentication

# Delete the local branch (if not auto-deleted)
git branch -d feat/user-authentication

# Prune remote tracking branches
git fetch --prune
```

## Error Handling

### Branch Already Exists

```bash
fatal: A branch named 'feat/user-auth' already exists.
```

**Solution:** Choose a more specific name or check if work is already in progress.

### Worktree Path Already Exists

```bash
fatal: '<path>' already exists
```

**Solution:** The worktree already exists. Use `git worktree list` to find it.

### No Remote Configured

```bash
fatal: No configured push destination.
```

**Solution:** Add a remote first: `git remote add origin <url>`
