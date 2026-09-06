#!/usr/bin/env bash
# Print a recommendation-only model-tier decision. This entry point never dispatches a
# worker, runs the QA gate, or changes the caller-selected tier.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$SCRIPT_DIR/scripts/model-recommendation.py" "$@"
