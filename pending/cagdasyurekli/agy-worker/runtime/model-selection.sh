#!/usr/bin/env bash
# Resolve one explicit caller-selected model/effort input without dispatching a job.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec python3 -B "$SCRIPT_DIR/scripts/model_selection.py" "$@"
