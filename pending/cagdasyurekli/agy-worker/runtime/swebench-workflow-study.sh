#!/usr/bin/env bash
# Prepare, import, report, or advise for SWE-bench workflow study v1.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec /usr/bin/python3 -I -S -B "$SCRIPT_DIR/scripts/swebench_workflow_study.py" "$@"
