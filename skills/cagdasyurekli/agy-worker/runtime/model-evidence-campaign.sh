#!/usr/bin/env bash
# Model Evidence Campaign: provider-independent, offline incremental new-model evidence campaign workflow.
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec /usr/bin/python3 -I -S -B "$SCRIPT_DIR/scripts/model_evidence_campaign.py" "$@"
