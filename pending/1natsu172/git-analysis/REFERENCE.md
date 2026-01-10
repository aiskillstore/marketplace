# Git Analysis Reference

Detailed reference for git commands and advanced usage patterns.

## Core Git Commands

### Branch Information

#### Get Default Branch
```bash
git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'
```

Alternative methods:
```bash
# Method 2: Query remote
git remote show origin | grep 'HEAD branch' | awk '{print $NF}'

# Method 3: List remote branches
git ls-remote --symref origin HEAD | awk '/^ref:/ {sub(/refs\/heads\//, "", $2); print $2}'
```

#### Get Current Branch
```bash
git branch --show-current
```

Alternative:
```bash
git rev-parse --abbrev-ref HEAD
```

### Merge Base Operations

#### Find Merge Base
```bash
# Between current branch and remote default branch
git merge-base origin/main HEAD

# Between two branches
git merge-base branch1 branch2

# Find all merge bases (for complex histories)
git merge-base --all origin/main HEAD
```

#### Verify Merge Base
```bash
# Show merge base commit details
MERGE_BASE=$(git merge-base origin/main HEAD)
git show --no-patch --format="%H %s (%an, %ar)" $MERGE_BASE
```

### Commit History

#### Basic Commit Listing
```bash
# One-line format
git log --oneline <merge-base>..HEAD

# Detailed format
git log <merge-base>..HEAD

# With stats
git log --stat <merge-base>..HEAD
```

#### Custom Formats
```bash
# Structured data (pipe-separated)
git log --format="%H|%s|%an|%ae|%ad" --date=iso <merge-base>..HEAD

# JSON-like format
git log --format='{"hash":"%H","subject":"%s","author":"%an","email":"%ae","date":"%ad"}' --date=iso <merge-base>..HEAD

# Commit with changed files
git log --name-status <merge-base>..HEAD

# Commit with file statistics
git log --stat --format="%H|%s" <merge-base>..HEAD
```

#### Filtering Commits
```bash
# By author
git log --author="John Doe" <merge-base>..HEAD

# By date
git log --since="2 weeks ago" <merge-base>..HEAD
git log --after="2025-01-01" --before="2025-01-31" <merge-base>..HEAD

# By file
git log <merge-base>..HEAD -- path/to/file

# By pattern in commit message
git log --grep="feat:" <merge-base>..HEAD
```

### Diff Operations

#### Basic Diffs
```bash
# Summary statistics
git diff --stat <merge-base>..HEAD

# Short statistics
git diff --shortstat <merge-base>..HEAD

# Name only
git diff --name-only <merge-base>..HEAD

# Name and status
git diff --name-status <merge-base>..HEAD
```

#### Detailed Diffs
```bash
# Full diff
git diff <merge-base>..HEAD

# Ignore whitespace
git diff -w <merge-base>..HEAD

# Word diff
git diff --word-diff <merge-base>..HEAD

# Specific file
git diff <merge-base>..HEAD -- path/to/file
```

#### Diff Statistics
```bash
# Count changed lines per file
git diff --numstat <merge-base>..HEAD

# Count changed files by type
git diff --stat <merge-base>..HEAD | grep -E '\.(js|ts|py|go)' | wc -l
```

### Status Operations

#### Working Directory Status
```bash
# Standard status
git status

# Short format
git status -s

# Untracked files only
git ls-files --others --exclude-standard

# Modified files only
git diff --name-only

# Staged files only
git diff --cached --name-only
```

#### Branch Status
```bash
# Compare with remote
git status -sb

# Check if branch is ahead/behind
git rev-list --left-right --count origin/main...HEAD

# Check if branch needs push
git cherry -v origin/$(git branch --show-current)
```

## Advanced Patterns

### Pattern 1: Complete Branch Analysis
```bash
#!/usr/bin/env bash
# Get comprehensive branch analysis

DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
CURRENT_BRANCH=$(git branch --show-current)
MERGE_BASE=$(git merge-base origin/$DEFAULT_BRANCH HEAD)

echo "Branch Analysis"
echo "==============="
echo "Default branch: $DEFAULT_BRANCH"
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Merge base info
echo "Merge Base:"
git show --no-patch --format="  Commit: %H%n  Date: %ad%n  Author: %an%n  Subject: %s" --date=iso $MERGE_BASE
echo ""

# Commit stats
COMMIT_COUNT=$(git log --oneline $MERGE_BASE..HEAD | wc -l | tr -d ' ')
echo "Commits ahead: $COMMIT_COUNT"

# File stats
git diff --shortstat $MERGE_BASE..HEAD
echo ""

# Recent commits
echo "Recent commits:"
git log --oneline --max-count=5 $MERGE_BASE..HEAD
```

### Pattern 2: Structured Data Extraction
```bash
#!/usr/bin/env bash
# Extract structured data for machine consumption

DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
MERGE_BASE=$(git merge-base origin/$DEFAULT_BRANCH HEAD)

# Output as JSON-like structure
cat <<EOF
{
  "default_branch": "$DEFAULT_BRANCH",
  "current_branch": "$(git branch --show-current)",
  "merge_base": "$MERGE_BASE",
  "commits": $(git log --oneline $MERGE_BASE..HEAD | wc -l | tr -d ' '),
  "files_changed": $(git diff --name-only $MERGE_BASE..HEAD | wc -l | tr -d ' '),
  "insertions": $(git diff --shortstat $MERGE_BASE..HEAD | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo 0),
  "deletions": $(git diff --shortstat $MERGE_BASE..HEAD | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo 0)
}
EOF
```

### Pattern 3: Parallel Information Gathering
```bash
#!/usr/bin/env bash
# Run multiple git commands in parallel for efficiency

# Start background jobs
git status > /tmp/git_status.txt 2>&1 &
PID_STATUS=$!

git diff --cached > /tmp/git_diff_staged.txt 2>&1 &
PID_DIFF_STAGED=$!

git diff > /tmp/git_diff_unstaged.txt 2>&1 &
PID_DIFF_UNSTAGED=$!

DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
MERGE_BASE=$(git merge-base origin/$DEFAULT_BRANCH HEAD)

git log --oneline $MERGE_BASE..HEAD > /tmp/git_commits.txt 2>&1 &
PID_COMMITS=$!

git diff --stat $MERGE_BASE..HEAD > /tmp/git_stats.txt 2>&1 &
PID_STATS=$!

# Wait for all jobs
wait $PID_STATUS $PID_DIFF_STAGED $PID_DIFF_UNSTAGED $PID_COMMITS $PID_STATS

# Process results
echo "=== Status ==="
cat /tmp/git_status.txt

echo ""
echo "=== Staged Changes ==="
cat /tmp/git_diff_staged.txt

echo ""
echo "=== Unstaged Changes ==="
cat /tmp/git_diff_unstaged.txt

echo ""
echo "=== Commits ==="
cat /tmp/git_commits.txt

echo ""
echo "=== Statistics ==="
cat /tmp/git_stats.txt

# Cleanup
rm -f /tmp/git_*.txt
```

### Pattern 4: Change Classification
```bash
#!/usr/bin/env bash
# Classify changes by file type and operation

DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
MERGE_BASE=$(git merge-base origin/$DEFAULT_BRANCH HEAD)

echo "Change Classification"
echo "===================="

# Get changed files with status
git diff --name-status $MERGE_BASE..HEAD | while IFS=$'\t' read status file; do
    case $status in
        A) operation="Added" ;;
        M) operation="Modified" ;;
        D) operation="Deleted" ;;
        R*) operation="Renamed" ;;
        C*) operation="Copied" ;;
        *) operation="Unknown" ;;
    esac

    extension="${file##*.}"
    echo "$operation: $file (.$extension)"
done | sort

echo ""
echo "Summary by file type:"
git diff --name-only $MERGE_BASE..HEAD | awk -F. '{print $NF}' | sort | uniq -c | sort -rn
```

## Performance Optimization

### Efficient Commands

#### Use Plumbing Commands
Plumbing commands are faster for scripting:
```bash
# Instead of: git branch --show-current
git rev-parse --abbrev-ref HEAD

# Instead of: git status
git diff-index --quiet HEAD -- || echo "Changes detected"
```

#### Limit Output
```bash
# Limit commit history depth
git log --max-count=10 <merge-base>..HEAD

# Limit diff context
git diff --unified=1 <merge-base>..HEAD

# Shallow clone for analysis
git clone --depth=1 --single-branch <url>
```

#### Parallel Execution
Run independent git commands in parallel using background jobs (`&`) and `wait`.

### Caching Results
```bash
# Cache expensive operations
if [ ! -f .git/cached_merge_base ]; then
    git merge-base origin/main HEAD > .git/cached_merge_base
fi
MERGE_BASE=$(cat .git/cached_merge_base)
```

## Error Handling

### Common Errors

#### Not in Git Repository
```bash
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository" >&2
    exit 1
fi
```

#### Remote Not Found
```bash
if ! git ls-remote origin > /dev/null 2>&1; then
    echo "Error: Remote 'origin' not found" >&2
    exit 1
fi
```

#### No Commits in Branch
```bash
MERGE_BASE=$(git merge-base origin/main HEAD)
if [ -z "$(git log --oneline $MERGE_BASE..HEAD)" ]; then
    echo "Warning: No commits in current branch" >&2
fi
```

#### Detached HEAD
```bash
if ! git symbolic-ref HEAD > /dev/null 2>&1; then
    echo "Warning: In detached HEAD state" >&2
fi
```

### Robust Script Template
```bash
#!/usr/bin/env bash
set -euo pipefail

# Error handler
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Check prerequisites
git rev-parse --git-dir > /dev/null 2>&1 || error_exit "Not in a git repository"
git ls-remote origin > /dev/null 2>&1 || error_exit "Remote 'origin' not found"

# Get branch info safely
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@') || \
    error_exit "Could not determine default branch"

MERGE_BASE=$(git merge-base origin/"$DEFAULT_BRANCH" HEAD 2>/dev/null) || \
    error_exit "Could not determine merge base"

# Continue with analysis...
```

## Integration Tips

### With PR Creation
```bash
# Extract all info needed for PR
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
MERGE_BASE=$(git merge-base origin/$DEFAULT_BRANCH HEAD)

# Get commits for PR description
git log --format="- %s" $MERGE_BASE..HEAD

# Get changed files for context
git diff --name-only $MERGE_BASE..HEAD
```

### With Commit Message Generation
```bash
# Analyze staged changes
git diff --cached --name-status

# Get context from recent commits
git log --oneline -5

# Identify scope from changed files
git diff --cached --name-only | awk -F/ '{print $1}' | sort | uniq
```

### With Code Review
```bash
# Get files to review
git diff --name-only origin/main..HEAD

# Get detailed changes per file
git diff origin/main..HEAD -- <file>

# Get commits introducing changes
git log origin/main..HEAD -- <file>
```

## Related Resources

- [Git Documentation](https://git-scm.com/doc)
- [Git Manual Pages](https://git-scm.com/docs)
- [Pro Git Book](https://git-scm.com/book/en/v2)
