#!/usr/bin/env bash
set -euo pipefail

URL="${1:-}"
OUT_DIR="${2:-./agent-browser-output}"

if [ -z "$URL" ]; then
  printf "Usage: %s <url> [output-dir]\n" "$0"
  exit 1
fi

mkdir -p "$OUT_DIR"

agent-browser open "$URL"
agent-browser wait --load networkidle
agent-browser snapshot -i > "$OUT_DIR/snapshot.txt"
agent-browser screenshot "$OUT_DIR/page.png"
agent-browser close

printf "Saved snapshot and screenshot in %s\n" "$OUT_DIR"
