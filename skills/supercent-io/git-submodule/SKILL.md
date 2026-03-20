---
name: git-submodule
description: Manage Git submodules for including external repositories within a main repository. Use when working with external libraries, shared modules, or managing dependencies as separate Git repositories.
metadata:
  tags: git, submodule, dependencies, version-control, modular
  platforms: Claude, ChatGPT, Gemini
---


# Git Submodule

## When to use this skill
- Including external Git repositories within your main project
- Managing shared libraries or modules across multiple projects
- Locking external dependencies to specific versions
- Working with monorepo-style architectures with independent components
- Cloning repositories that contain submodules
- Updating submodules to newer versions
- Removing submodules from a project

## Instructions

### Step 1: Understanding submodules

Git submodule is a feature for including other Git repositories within a main Git repository.

**Key concepts**:
- Submodules lock version by referencing a specific commit
- Submodule paths and URLs are recorded in the `.gitmodules` file
- Changes within a submodule are managed as separate commits

### Step 2: Adding submodules

**Basic addition**:
```bash
# Add submodule
git submodule add <repository-url> <path>

# Example: Add library to libs/lib path
git submodule add https://github.com/example/lib.git libs/lib
```

**Track a specific branch**:
```bash
# Add to track a specific branch
git submodule add -b main https://github.com/example/lib.git libs/lib
```

**Commit after adding**:
```bash
git add .gitmodules libs/lib
git commit -m "feat: add lib as submodule"
```

### Step 3: Cloning with submodules

**When cloning fresh**:
```bash
# Method 1: --recursive option when cloning
git clone --recursive <repository-url>

# Method 2: Initialize after cloning
git clone <repository-url>
cd <repository>
git submodule init
git submodule update
```

**Initialize and update in one line**:
```bash
git submodule update --init --recursive
```

### Step 4: Updating submodules

**Update to latest remote version**:
```bash
# Update all submodules to latest remote
git submodule update --remote

# Update a specific submodule only
git submodule update --remote libs/lib

# Update + merge
git submodule update --remote --merge

# Update + rebase
git submodule update --remote --rebase
```

**Checkout to the referenced commit**:
```bash
# Checkout submodule to the commit referenced by the main repository
git submodule update
```

### Step 5: Working inside submodules

**Working inside a submodule**:
```bash
# Navigate to submodule directory
cd libs/lib

# Checkout branch (exit detached HEAD)
git checkout main

# Work on changes
# ... make changes ...

# Commit and push within submodule
git add .
git commit -m "feat: update library"
git push origin main
```

**Reflect submodule changes in main repository**:
```bash
# Move to main repository
cd ..

# Update submodule reference
git add libs/lib
git commit -m "chore: update lib submodule reference"
git push
```

### Step 6: Batch operations

**Run commands on all submodules**:
```bash
# Pull in all submodules
git submodule foreach 'git pull origin main'

# Check status in all submodules
git submodule foreach 'git status'

# Checkout branch in all submodules
git submodule foreach 'git checkout main'

# Also run command on nested submodules
git submodule foreach --recursive 'git fetch origin'
```

### Step 7: Removing submodules

**Completely remove a submodule**:
```bash
# 1. Deinitialize submodule
git submodule deinit <path>

# 2. Remove from Git
git rm <path>

# 3. Remove cache from .git/modules
rm -rf .git/modules/<path>

# 4. Commit changes
git commit -m "chore: remove submodule"
```

**Example: Remove libs/lib**:
```bash
git submodule deinit libs/lib
git rm libs/lib
rm -rf .git/modules/libs/lib
git commit -m "chore: remove lib submodule"
git push
```

### Step 8: Checking submodule status

**Check status**:
```bash
# Check submodule status
git submodule status

# Detailed status (recursive)
git submodule status --recursive

# Summary information
git submodule summary
```

**Interpreting output**:
```
 44d7d1... libs/lib (v1.0.0)      # Normal (matches referenced commit)
+44d7d1... libs/lib (v1.0.0-1-g...)  # Local changes present
-44d7d1... libs/lib               # Not initialized
```

## Examples

### Example 1: Adding an External Library to a Project

```bash
# 1. Add submodule
git submodule add https://github.com/lodash/lodash.git vendor/lodash

# 2. Lock to a specific version (tag)
cd vendor/lodash
git checkout v4.17.21
cd ../..

# 3. Commit changes
git add .
git commit -m "feat: add lodash v4.17.21 as submodule"

# 4. Push
git push origin main
```

### Example 2: Setup After Cloning a Repository with Submodules

```bash
# 1. Clone the repository
git clone https://github.com/myorg/myproject.git
cd myproject

# 2. Initialize and update submodules
git submodule update --init --recursive

# 3. Check submodule status
git submodule status

# 4. Checkout submodule branch (for development)
git submodule foreach 'git checkout main || git checkout master'
```

### Example 3: Updating Submodules to the Latest Version

```bash
# 1. Update all submodules to latest remote
git submodule update --remote --merge

# 2. Review changes
git diff --submodule

# 3. Commit changes
git add .
git commit -m "chore: update all submodules to latest"

# 4. Push
git push origin main
```

### Example 4: Using Shared Components Across Multiple Projects

```bash
# In Project A
git submodule add https://github.com/myorg/shared-components.git src/shared

# In Project B
git submodule add https://github.com/myorg/shared-components.git src/shared

# When updating shared components (in each project)
git submodule update --remote src/shared
git add src/shared
git commit -m "chore: update shared-components"
```

### Example 5: Handling Submodules in CI/CD

```yaml
# GitHub Actions
jobs:
  build:
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive  # or 'true'

# GitLab CI
variables:
  GIT_SUBMODULE_STRATEGY: recursive

# Jenkins
checkout scm: [
  $class: 'SubmoduleOption',
  recursiveSubmodules: true
]
```

## Advanced workflows

### Nested Submodules

```bash
# Initialize all nested submodules
git submodule update --init --recursive

# Update all nested submodules
git submodule update --remote --recursive
```

### Changing Submodule URL

```bash
# Edit the .gitmodules file
git config -f .gitmodules submodule.libs/lib.url https://new-url.git

# Sync local configuration
git submodule sync

# Update submodule
git submodule update --init --recursive
```

### Converting a Submodule to a Regular Directory

```bash
# 1. Back up submodule contents
cp -r libs/lib libs/lib-backup

# 2. Remove submodule
git submodule deinit libs/lib
git rm libs/lib
rm -rf .git/modules/libs/lib

# 3. Restore backup (excluding .git)
rm -rf libs/lib-backup/.git
mv libs/lib-backup libs/lib

# 4. Add as regular files
git add libs/lib
git commit -m "chore: convert submodule to regular directory"
```

### Saving Space with Shallow Clones

```bash
# Add submodule with shallow clone
git submodule add --depth 1 https://github.com/large/repo.git libs/large

# Update existing submodule as shallow clone
git submodule update --init --depth 1
```

## Best practices

1. **Version locking**: Always lock submodules to a specific commit/tag for reproducibility
2. **Documentation**: Specify submodule initialization steps in README
3. **CI configuration**: Use `--recursive` option in CI/CD pipelines
4. **Regular updates**: Regularly update submodules for security patches and more
5. **Branch tracking**: Configure branch tracking during development for convenience
6. **Permission management**: Verify access permissions for submodule repositories
7. **Shallow clone**: Use `--depth` option for large repositories to save space
8. **Status check**: Verify status with `git submodule status` before committing

## Common pitfalls

- **detached HEAD**: Submodules are in detached HEAD state by default. Checkout a branch when working
- **Missing initialization**: `git submodule update --init` is required after cloning
- **Reference mismatch**: Must update reference in main repository after submodule changes
- **Permission issue**: Private submodules require SSH key or token configuration
- **Relative paths**: Using relative paths in `.gitmodules` can cause issues in forks
- **Incomplete removal**: Must also delete `.git/modules` cache when removing a submodule

## Troubleshooting

### Submodule not initialized

```bash
# Force initialize
git submodule update --init --force
```

### Submodule conflict

```bash
# Check submodule status
git submodule status

# After resolving conflict, checkout desired commit
cd libs/lib
git checkout <desired-commit>
cd ..
git add libs/lib
git commit -m "fix: resolve submodule conflict"
```

### Permission error (private repository)

```bash
# Use SSH URL
git config -f .gitmodules submodule.libs/lib.url git@github.com:org/private-lib.git
git submodule sync
git submodule update --init
```

### Submodule in dirty state

```bash
# Check changes within submodule
cd libs/lib
git status
git diff

# Discard changes
git checkout .
git clean -fd

# Or commit
git add .
git commit -m "fix: resolve changes"
git push
```

## Configuration

### Useful Configuration

```bash
# Show submodule changes in diff
git config --global diff.submodule log

# Show submodule summary in status
git config --global status.submoduleSummary true

# Check submodule changes on push
git config --global push.recurseSubmodules check

# Also fetch submodules when fetching
git config --global fetch.recurseSubmodules on-demand
```

### .gitmodules Example

```ini
[submodule "libs/lib"]
    path = libs/lib
    url = https://github.com/example/lib.git
    branch = main

[submodule "vendor/tool"]
    path = vendor/tool
    url = git@github.com:example/tool.git
    shallow = true
```

## References

- [Git Submodules - Official Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Git Submodule Tutorial - Atlassian](https://www.atlassian.com/git/tutorials/git-submodule)
- [Managing Dependencies with Submodules](https://github.blog/2016-02-01-working-with-submodules/)
- [Git Submodule Cheat Sheet](https://gist.github.com/gitaarik/8735255)
