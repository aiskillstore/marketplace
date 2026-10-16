#!/usr/bin/env bash
# Manage one explicit branch-backed local job; never dispatch or publish externally.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec python3 -I -S -B "$SCRIPT_DIR/scripts/job_lifecycle.py" "$@"
