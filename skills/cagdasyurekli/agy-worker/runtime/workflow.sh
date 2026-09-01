#!/usr/bin/env bash
# Canonical workflow facade: run, status, and verify-finalize.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec python3 -I -S -B "$SCRIPT_DIR/scripts/workflow.py" "$@"
