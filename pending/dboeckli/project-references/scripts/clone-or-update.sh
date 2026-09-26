#!/usr/bin/env bash
# Clone a single GitHub repository into ~/projects/referenzen/ or pull if it exists.
# Usage: clone-or-update.sh <owner/repo>
# Exit codes: 0=ok, 1=argument missing, 2=local changes present (pull skipped), 3=clone/pull failed

set -euo pipefail

REFERENZEN_DIR="${REFERENZEN_DIR:-$HOME/projects/referenzen}"

if [[ $# -lt 1 ]]; then
	echo "Usage: $0 <owner/repo>" >&2
	exit 1
fi

REPO="$1"
NAME="${REPO##*/}"
TARGET="$REFERENZEN_DIR/$NAME"

mkdir -p "$REFERENZEN_DIR"

if [[ -d "$TARGET/.git" ]]; then
	STATUS=$(git -C "$TARGET" status --porcelain)
	if [[ -n "$STATUS" ]]; then
		echo "SKIP  $REPO — local changes present, not pulling:"
		git -C "$TARGET" status --short | sed 's/^/      /'
		exit 2
	else
		echo "PULL  $REPO"
		if git -C "$TARGET" pull --ff-only 2>&1; then
			echo "      OK"
		else
			echo "      FAILED (not fast-forward or network error)" >&2
			exit 3
		fi
	fi
else
	echo "CLONE $REPO → $TARGET"
	if gh repo clone "$REPO" "$TARGET" -- --quiet 2>&1; then
		echo "      OK"
	else
		echo "      FAILED" >&2
		exit 3
	fi
fi
