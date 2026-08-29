#!/usr/bin/env bash
# Prepare, run, or report one provider-independent offline benchmark plan.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec /usr/bin/python3 -I -S -B "$SCRIPT_DIR/scripts/benchmark.py" "$@"
