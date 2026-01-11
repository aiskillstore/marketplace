#!/bin/bash
# SessionStart Hook: Inject Context
# Provides project context to Claude at session start
#
# Usage in settings.json:
# {
#   "hooks": {
#     "SessionStart": [{
#       "hooks": [{
#         "type": "command",
#         "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/context-injector.sh\""
#       }]
#     }]
#   }
# }

set -euo pipefail

INPUT=$(cat)
IS_RESUME=$(echo "$INPUT" | jq -r '.is_resume // false')

# Build context based on project state
CONTEXT=""

# Example: Add project type
if [ -f "$CLAUDE_PROJECT_DIR/package.json" ]; then
  CONTEXT+="This is a Node.js project. "
fi

if [ -f "$CLAUDE_PROJECT_DIR/Cargo.toml" ]; then
  CONTEXT+="This is a Rust project. "
fi

if [ -f "$CLAUDE_PROJECT_DIR/go.mod" ]; then
  CONTEXT+="This is a Go project. "
fi

# Example: Add active feature context
if [ -f "$CLAUDE_PROJECT_DIR/.spec/state/session.json" ]; then
  FEATURE=$(jq -r '.current_feature // empty' "$CLAUDE_PROJECT_DIR/.spec/state/session.json")
  if [ -n "$FEATURE" ]; then
    CONTEXT+="Currently working on feature: $FEATURE. "
  fi
fi

# Example: Add recent git context
if [ -d "$CLAUDE_PROJECT_DIR/.git" ]; then
  BRANCH=$(git -C "$CLAUDE_PROJECT_DIR" branch --show-current 2>/dev/null || echo "")
  if [ -n "$BRANCH" ]; then
    CONTEXT+="On git branch: $BRANCH. "
  fi
fi

# Output context as JSON
if [ -n "$CONTEXT" ]; then
  jq -n --arg ctx "$CONTEXT" '{"additionalContext": $ctx}'
fi

exit 0
