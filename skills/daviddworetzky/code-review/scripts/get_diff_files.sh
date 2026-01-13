#!/bin/bash
# Helper script to get list of files that have been changed in git

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Get list of changed files in git repository"
    echo ""
    echo "Options:"
    echo "  -s, --staged         Only show staged files"
    echo "  -u, --unstaged       Only show unstaged files"
    echo "  -a, --all            Show all changes (staged and unstaged) [default]"
    echo "  -c, --commits N      Show files changed in last N commits"
    echo "  -h, --help           Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0                   # Show all changed files"
    echo "  $0 --staged          # Show only staged files"
    echo "  $0 --commits 3       # Show files changed in last 3 commits"
}

# Default mode
MODE="all"
COMMITS=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--staged)
            MODE="staged"
            shift
            ;;
        -u|--unstaged)
            MODE="unstaged"
            shift
            ;;
        -a|--all)
            MODE="all"
            shift
            ;;
        -c|--commits)
            COMMITS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get changed files based on mode
if [ "$COMMITS" -gt 0 ]; then
    # Show files changed in last N commits
    git diff --name-only HEAD~"$COMMITS"..HEAD
elif [ "$MODE" = "staged" ]; then
    # Only staged files
    git diff --cached --name-only
elif [ "$MODE" = "unstaged" ]; then
    # Only unstaged files
    git diff --name-only
else
    # All changes (staged and unstaged)
    git diff --name-only HEAD
fi
