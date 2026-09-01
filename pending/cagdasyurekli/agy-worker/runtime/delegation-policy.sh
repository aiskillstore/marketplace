#!/usr/bin/env bash
# Evaluate explicit opt-in delegation-first coordinator policy; side-effect-free closed evaluator.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec /usr/bin/python3 -I -S -B "$SCRIPT_DIR/scripts/delegation_policy.py" "$@"
