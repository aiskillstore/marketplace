#!/usr/bin/env bash
# List or show fixed data-only workload profiles. This command never dispatches.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec /usr/bin/python3 -I -S -B "$SCRIPT_DIR/scripts/workload_profiles.py" "$@"
