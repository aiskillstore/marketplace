#!/bin/bash

set -e

BRANCH_NAME=""
BASE_BRANCH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --from)
            BASE_BRANCH="$2"
            shift 2
            ;;
        *)
            if [ -z "$BRANCH_NAME" ]; then
                BRANCH_NAME="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$BRANCH_NAME" ]; then
    echo "Usage: $0 <branch-name> [--from <base-branch>]"
    echo "Example: $0 feature/new-feature"
    echo "Example: $0 feature/new-feature --from main"
    exit 1
fi

WORKTREE_NAME=$(echo "$BRANCH_NAME" | tr '/' '-')
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
WORKTREE_PATH="$REPO_ROOT/../${REPO_NAME}-worktrees/$WORKTREE_NAME"

if [ -z "$BASE_BRANCH" ]; then
    BASE_BRANCH=$(git branch --show-current)
fi

echo "Creating worktree for branch: $BRANCH_NAME"
echo "Base branch: $BASE_BRANCH"
echo "Worktree path: $WORKTREE_PATH"

cd "$REPO_ROOT"

git checkout "$BASE_BRANCH"
git pull

mkdir -p "$REPO_ROOT/../${REPO_NAME}-worktrees"

if [ -d "$WORKTREE_PATH" ]; then
    echo ""
    echo "✓ Worktree already exists at: $WORKTREE_PATH"
    echo ""
    echo "Next steps:"
    echo "1. cd $WORKTREE_PATH"
    echo "2. Continue working on your task"
    echo ""
    exit 0
fi

if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    git worktree add "$WORKTREE_PATH" "$BRANCH_NAME"
else
    git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH"
fi

if [ -f .env ]; then
    cp .env "$WORKTREE_PATH/.env"
    echo "Copied .env file to worktree"
fi

cd "$WORKTREE_PATH"

echo ""
echo "✓ Worktree created successfully!"
echo ""
echo "Next steps:"
echo "1. cd $WORKTREE_PATH"
echo "2. Start working on your task"
echo ""
