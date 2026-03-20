#!/usr/bin/env bash
set -euo pipefail

if ! command -v rg >/dev/null 2>&1; then
  echo "ERROR: ripgrep (rg) not found. Install it first, then rerun." >&2
  exit 1
fi

search_root="."
if [[ -d "prompt" ]]; then
  search_root="prompt"
fi

usage() {
  cat <<'EOF'
Usage:
  impact_scan.sh <keyword...>

Examples:
  impact_scan.sh oauth refresh_token
  impact_scan.sh sidepanel toast
  impact_scan.sh manifest service_worker

Notes:
  - Defaults to search in ./prompt if it exists, otherwise searches in current directory.
  - Prints a short list of likely entrypoints first, then keyword matches.
EOF
}

if [[ "${1-}" == "-h" || "${1-}" == "--help" || $# -eq 0 ]]; then
  usage
  exit 0
fi

echo "Search root: ${search_root}"
echo
echo "Likely entrypoints (if present):"
for f in \
  "${search_root}/manifest.json" \
  "${search_root}/service_worker.js" \
  "${search_root}/src" \
  "${search_root}/sidepanel" \
  "${search_root}/options" \
  "${search_root}/tests"
do
  [[ -e "${f}" ]] && echo "  - ${f}"
done

echo
echo "Keyword matches:"

rg_args=(
  "-S"
  "--hidden"
  "--glob" "!.git/**"
  "--glob" "!**/node_modules/**"
  "--glob" "!**/dist/**"
  "--glob" "!**/build/**"
  "--glob" "!**/archive/**"
  "-l"
)

patterns=()
for kw in "$@"; do
  patterns+=("-e" "${kw}")
done

rg "${rg_args[@]}" "${patterns[@]}" "${search_root}" \
  | sed "s|^|  - |" \
  || true
