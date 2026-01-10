#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <branch-name>"
    echo "Example: $0 feature/new-feature"
    exit 1
fi

BRANCH_NAME="$1"
WORKTREE_NAME=$(echo "$BRANCH_NAME" | tr '/' '-')
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
WORKTREE_PATH="$REPO_ROOT/../${REPO_NAME}-worktrees/$WORKTREE_NAME"

echo "Removing worktree for branch: $BRANCH_NAME"
echo "Worktree path: $WORKTREE_PATH"

if [ ! -d "$WORKTREE_PATH" ]; then
    echo "Error: Worktree not found at $WORKTREE_PATH"
    exit 1
fi

git worktree remove "$WORKTREE_PATH"
echo "Worktree removed."

if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    git branch -D "$BRANCH_NAME"
    echo "Branch '$BRANCH_NAME' deleted."
fi

echo ""
echo "Done."
echo ""
