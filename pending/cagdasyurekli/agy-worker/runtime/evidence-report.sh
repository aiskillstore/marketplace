#!/usr/bin/env bash
# Render one validated Evidence Receipt v1 without dispatch, routing, or gate work.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec python3 -I -S -B "$SCRIPT_DIR/scripts/evidence_report.py" "$@"
