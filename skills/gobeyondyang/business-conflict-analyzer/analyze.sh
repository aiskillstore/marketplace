#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python "$SCRIPT_DIR/scripts/diff_analyzer.py" "$@" \
    | python "$SCRIPT_DIR/scripts/impact_mapper.py" \
    | python "$SCRIPT_DIR/scripts/report_generator.py"

echo "Done. Report saved to: $(pwd)/conflict-report.md"
