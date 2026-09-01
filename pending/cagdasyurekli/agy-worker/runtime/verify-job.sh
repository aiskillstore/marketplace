#!/usr/bin/env bash
# Run the canonical gate and publish one private Evidence Receipt v1.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec python3 -I -S -B "$SCRIPT_DIR/scripts/evidence_receipt.py" verify "$@"
