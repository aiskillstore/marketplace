# Gitgraph Reference

Visualize Git branching strategies and commit history in Obsidian.

---

## Basic Structure

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    checkout main
    merge develop
```

**Keywords:**
- `commit` - Add a commit
- `branch name` - Create branch
- `checkout name` - Switch branch
- `merge name` - Merge branch into current

---

## Direction

| Keyword | Direction |
|---------|-----------|
| (default) | Left to Right |
| `LR:` | Left to Right |
| `TB:` | Top to Bottom |
| `BT:` | Bottom to Top |

```mermaid
gitGraph TB:
    commit
    commit
    branch feature
    commit
```

---

## Commits

### Basic Commit

```mermaid
gitGraph
    commit
    commit
    commit
```

### With ID and Message

```mermaid
gitGraph
    commit id: "init"
    commit id: "feat-1"
    commit id: "fix-bug"
```

### Commit Types

| Type | Display | Use Case |
|------|---------|----------|
| `NORMAL` | Filled circle | Standard commit |
| `REVERSE` | X-marked circle | Reverted commit |
| `HIGHLIGHT` | Filled square | Important commit |

```mermaid
gitGraph
    commit id: "Normal" type: NORMAL
    commit id: "Reverted" type: REVERSE
    commit id: "Important" type: HIGHLIGHT
```

---

## Branches

### Create and Switch

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "dev-1"
    checkout main
    commit id: "hotfix"
```

### Multiple Branches

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit
    branch feature-a
    checkout feature-a
    commit
    checkout develop
    branch feature-b
    checkout feature-b
    commit
```

---

## Merge

### Basic Merge

```mermaid
gitGraph
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
    commit
```

### Merge with Tag

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "feat"
    checkout main
    merge develop id: "merge" tag: "v1.0.0"
```

### Merge with Attributes

```mermaid
gitGraph
    commit
    branch feature
    checkout feature
    commit
    checkout main
    merge feature id: "release" tag: "v2.0" type: HIGHLIGHT
```

---

## Tags

Add version tags to commits:

```mermaid
gitGraph
    commit id: "init" tag: "v0.1.0"
    commit
    commit id: "release" tag: "v1.0.0" type: HIGHLIGHT
    commit
    commit tag: "v1.1.0"
```

---

## Cherry-pick

Copy specific commits to another branch:

### Basic Cherry-pick

```mermaid
gitGraph
    commit
    branch feature
    checkout feature
    commit id: "important-fix"
    checkout main
    commit
    cherry-pick id: "important-fix"
```

### Cherry-pick from Merge Commit

Use `parent` to specify which parent's changes:

```mermaid
gitGraph
    commit id: "A"
    branch develop
    commit id: "B"
    checkout main
    commit id: "C"
    merge develop id: "MERGE"
    branch release
    checkout release
    cherry-pick id: "MERGE" parent: "B"
```

---

## Configuration

### YAML Frontmatter

```mermaid
---
config:
  gitGraph:
    showBranches: true
    showCommitLabel: true
    mainBranchName: 'master'
---
gitGraph
    commit id: "init"
    branch develop
    commit
    checkout master
    merge develop
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `showBranches` | Show branch labels | true |
| `showCommitLabel` | Show commit labels | true |
| `mainBranchName` | Main branch name | "main" |
| `mainBranchOrder` | Main branch position | 0 |
| `rotateCommitLabel` | Rotate labels | true |

### Branch Order

Control branch display order with `order`:

```mermaid
gitGraph
    commit
    branch release order: 1
    branch develop order: 2
    branch feature order: 3
    checkout feature
    commit
    checkout develop
    commit
    checkout release
    commit
```

---

## Practical Examples

### Example 1: Git Flow Workflow

```mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "setup"

    branch feature/login
    checkout feature/login
    commit id: "login-ui"
    commit id: "login-api"
    checkout develop
    merge feature/login

    branch release/1.0
    checkout release/1.0
    commit id: "bump-version" type: HIGHLIGHT
    checkout main
    merge release/1.0 tag: "v1.0.0"
    checkout develop
    merge release/1.0
```

### Example 2: Hotfix Workflow

```mermaid
gitGraph
    commit id: "v1.0" tag: "v1.0.0"
    branch develop
    checkout develop
    commit id: "feat-A"

    checkout main
    branch hotfix/critical
    checkout hotfix/critical
    commit id: "fix-bug" type: HIGHLIGHT

    checkout main
    merge hotfix/critical tag: "v1.0.1"
    checkout develop
    merge hotfix/critical
    commit id: "feat-B"
```

### Example 3: Feature Branch Strategy

```mermaid
gitGraph LR:
    commit id: "init"

    branch feature-1
    checkout feature-1
    commit id: "f1-1"
    commit id: "f1-2"

    checkout main
    branch feature-2
    checkout feature-2
    commit id: "f2-1"

    checkout main
    merge feature-1

    checkout feature-2
    commit id: "f2-2"

    checkout main
    merge feature-2 tag: "v1.0"
```

### Example 4: Release Cycle

```mermaid
gitGraph
    commit id: "1.0" tag: "v1.0.0"
    branch develop
    checkout develop
    commit id: "feat: api"
    commit id: "fix: bug"

    branch release/1.1
    checkout release/1.1
    commit id: "docs" type: HIGHLIGHT

    checkout main
    merge release/1.1 tag: "v1.1.0"

    checkout develop
    merge release/1.1
    commit id: "feat: next"
```

---

## Obsidian Notes

**Branch Names**: Use simple names. Special characters may cause parsing issues.

**Commit IDs**: Must be unique for cherry-pick references.

**Theme Colors**: Branch colors adapt to Obsidian theme. Each branch gets a distinct color automatically.

**Performance**: Complex graphs with many branches may render slowly.

**No Interaction**: Click events are disabled in Obsidian.

---

## Quick Reference

| Action | Syntax | Example |
|--------|--------|---------|
| Commit | `commit` | `commit id: "init"` |
| Commit type | `type: TYPE` | `commit type: HIGHLIGHT` |
| Tag | `tag: "name"` | `commit tag: "v1.0"` |
| Branch | `branch name` | `branch develop` |
| Switch | `checkout name` | `checkout main` |
| Merge | `merge name` | `merge feature` |
| Cherry-pick | `cherry-pick id: "id"` | `cherry-pick id: "fix"` |
| Direction | `gitGraph DIR:` | `gitGraph TB:` |
| Config | `---config:...---` | See examples above |
