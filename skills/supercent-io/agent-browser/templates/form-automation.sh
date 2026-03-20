#!/usr/bin/env bash
set -euo pipefail

URL="${1:-}"
if [ -z "$URL" ]; then
  printf "Usage: %s <form-url>\n" "$0"
  exit 1
fi

agent-browser open "$URL"
agent-browser wait --load networkidle
agent-browser snapshot -i

printf "Snapshot complete. Use returned refs (@eN) to fill fields and submit.\n"
