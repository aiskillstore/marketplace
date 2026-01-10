#!/usr/bin/env bash
#
# get_commit_history.sh
#
# Extracts detailed commit history in structured format from merge base to HEAD.
#
# Usage: bash get_commit_history.sh [merge-base]
#
# If merge-base is not provided, it will be automatically determined.
#
# Output format (one commit per line):
#   hash|subject|author_name|author_email|date

set -euo pipefail

# Check if in git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository" >&2
    exit 1
fi

MERGE_BASE="$1"

# If merge base not provided, determine it automatically
if [ -z "$MERGE_BASE" ]; then
    DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
    MERGE_BASE=$(git merge-base origin/"$DEFAULT_BRANCH" HEAD 2>/dev/null || echo "")

    if [ -z "$MERGE_BASE" ]; then
        echo "Error: Could not determine merge base" >&2
        exit 1
    fi
fi

# Get structured commit history
# Format: hash|subject|author_name|author_email|date
git log --format="%H|%s|%an|%ae|%ad" --date=iso "$MERGE_BASE"..HEAD
