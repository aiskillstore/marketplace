#!/usr/bin/env bash
# Sync all repositories to ~/projects/referenzen/.
# Reads from ~/claude-shared/projekte.txt if present, otherwise uses gh repo list.
# Usage: sync-all.sh [--list <file>] [--limit <n>]
#   --list  <file>  override the default projekte.txt path
#   --limit <n>     max repos when using gh repo list (default: 200)

set -euo pipefail

REFERENZEN_DIR="${REFERENZEN_DIR:-$HOME/projects/referenzen}"
PROJEKTE_FILE="${PROJEKTE_FILE:-$HOME/claude-shared/projekte.txt}"
GH_LIMIT=200
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while [[ $# -gt 0 ]]; do
	case "$1" in
	--list)
		PROJEKTE_FILE="$2"
		shift 2
		;;
	--limit)
		GH_LIMIT="$2"
		shift 2
		;;
	*)
		echo "Unknown option: $1" >&2
		exit 1
		;;
	esac
done

mkdir -p "$REFERENZEN_DIR"

# --- Determine repo list ---
if [[ -f "$PROJEKTE_FILE" ]]; then
	echo "Source: $PROJEKTE_FILE"
	REPOS=$(grep -v '^\s*#' "$PROJEKTE_FILE" | grep -v '^\s*$' || true)
else
	echo "Source: gh repo list (limit $GH_LIMIT) — projekte.txt not found at $PROJEKTE_FILE"
	REPOS=$(gh repo list --limit "$GH_LIMIT" --json nameWithOwner --jq '.[].nameWithOwner')
fi

TOTAL=$(echo "$REPOS" | grep -c . || true)
echo "Repositories to sync: $TOTAL"
echo "Target directory:     $REFERENZEN_DIR"
echo "---"

CLONED=0
PULLED=0
SKIPPED=0
FAILED=0

inc() { eval "$1=\$(( \${$1} + 1 ))"; }

while IFS= read -r REPO; do
	[[ -z "$REPO" ]] && continue

	NAME="${REPO##*/}"
	TARGET="$REFERENZEN_DIR/$NAME"

	if [[ -d "$TARGET/.git" ]]; then
		STATUS=$(git -C "$TARGET" status --porcelain)
		if [[ -n "$STATUS" ]]; then
			echo "SKIP  $REPO — local changes present:"
			git -C "$TARGET" status --short | sed 's/^/      /'
			inc SKIPPED
		else
			echo "PULL  $REPO"
			if git -C "$TARGET" pull --ff-only 2>&1 | sed 's/^/      /'; then
				inc PULLED
			else
				echo "      FAILED" >&2
				inc FAILED
			fi
		fi
	else
		echo "CLONE $REPO → $TARGET"
		if gh repo clone "$REPO" "$TARGET" -- --quiet 2>&1 | sed 's/^/      /'; then
			echo "      OK"
			inc CLONED
		else
			echo "      FAILED" >&2
			inc FAILED
		fi
	fi
done <<<"$REPOS"

echo "---"
echo "Done.  Cloned: $CLONED  Pulled: $PULLED  Skipped (local changes): $SKIPPED  Failed: $FAILED"
