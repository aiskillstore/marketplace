#!/usr/bin/env bash
#
# get_branch_diff.sh
#
# Extracts branch differences including default branch, merge base,
# commit count, and changed files summary.
#
# Usage: bash get_branch_diff.sh
#
# Output format:
#   DEFAULT_BRANCH: main
#   MERGE_BASE: abc123def456
#   COMMITS: 5
#   CHANGED_FILES: 12
#   INSERTIONS: 234
#   DELETIONS: 89

set -euo pipefail

# Check if in git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository" >&2
    exit 1
fi

# Get default branch
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

# Get merge base
MERGE_BASE=$(git merge-base origin/"$DEFAULT_BRANCH" HEAD 2>/dev/null || echo "")

if [ -z "$MERGE_BASE" ]; then
    echo "Error: Could not determine merge base" >&2
    exit 1
fi

# Get commit count
COMMIT_COUNT=$(git log --oneline "$MERGE_BASE"..HEAD | wc -l | tr -d ' ')

# Get file statistics
STATS=$(git diff --shortstat "$MERGE_BASE"..HEAD)

# Extract changed files, insertions, deletions
if [ -n "$STATS" ]; then
    CHANGED_FILES=$(echo "$STATS" | grep -oE '[0-9]+ file' | grep -oE '[0-9]+' || echo "0")
    INSERTIONS=$(echo "$STATS" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")
    DELETIONS=$(echo "$STATS" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+' || echo "0")
else
    CHANGED_FILES="0"
    INSERTIONS="0"
    DELETIONS="0"
fi

# Output structured data
echo "DEFAULT_BRANCH: $DEFAULT_BRANCH"
echo "MERGE_BASE: $MERGE_BASE"
echo "COMMITS: $COMMIT_COUNT"
echo "CHANGED_FILES: $CHANGED_FILES"
echo "INSERTIONS: $INSERTIONS"
echo "DELETIONS: $DELETIONS"
