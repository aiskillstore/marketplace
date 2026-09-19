#!/usr/bin/env bash
# Validate or advise for Model Intelligence v1; side-effect-free offline advisory.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec /usr/bin/python3 -I -S -B "$SCRIPT_DIR/scripts/model_intelligence.py" "$@"
