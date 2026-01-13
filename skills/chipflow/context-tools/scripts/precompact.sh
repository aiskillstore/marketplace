#!/usr/bin/env bash
# PreCompact Hook for context-tools plugin
# Runs before context compaction to ensure context is refreshed
# Note: Repo map is maintained by MCP server, no need to regenerate here

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PWD}"

echo "=== PreCompact Hook (context-tools) ==="
echo ""
echo "📝 IMPORTANT: Update .claude/learnings.md with what you built/learned this session:"
echo "   • New features/APIs implemented"
echo "   • Integration points added (e.g., Python bindings, new modules)"
echo "   • Non-obvious design decisions or debugging insights"
echo "   Without this, context compaction will forget what you just built!"
echo "================================================"
