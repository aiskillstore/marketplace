#!/bin/bash
# Runtime detection — dispatch to Python or Node.js client.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v python3 &>/dev/null; then
    exec python3 "$SCRIPT_DIR/python/join.py" "$@"
elif command -v node &>/dev/null; then
    exec node "$SCRIPT_DIR/node/join.js" "$@"
else
    echo "Error: python3 or node required" >&2
    exit 1
fi
