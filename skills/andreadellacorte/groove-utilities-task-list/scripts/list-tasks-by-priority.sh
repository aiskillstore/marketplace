#!/usr/bin/env bash
# List active beans by priority order: critical, high, normal, low, deferred.
# Stops when we have at least LIMIT tasks (default 15).
# Usage: list-tasks-by-priority.sh [LIMIT]
# Output: JSON array of bean objects (to stdout).
# Requires: beans CLI, jq. Run from repo root.

set -e
LIMIT="${1:-15}"
OPTS="--no-status completed --no-status scrapped --json"
TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT

# Fetch each priority in order; merge and take first LIMIT (no unique_by: each bean has one priority, and unique_by reorders)
for pri in critical high normal low deferred; do
  beans list -p "$pri" $OPTS 2>/dev/null > "$TMP/$pri.json" || echo "[]" > "$TMP/$pri.json"
done
jq -s 'add | .[0:'"$LIMIT"']' "$TMP"/critical.json "$TMP"/high.json "$TMP"/normal.json "$TMP"/low.json "$TMP"/deferred.json
