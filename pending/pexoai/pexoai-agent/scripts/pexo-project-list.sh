#!/usr/bin/env bash
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"

usage() {
  cat <<'EOF'
Usage:
  pexo-project-list.sh [page_size]
  pexo-project-list.sh [--page <n>] [--page-size <n>]
  pexo-project-list.sh -h | --help

Description:
  List projects for the authenticated user.

Options:
  --page <n>       Page number (default: 1)
  --page-size <n>  Page size (default: 20, effective max: 100)

Returns:
  Projects JSON from /api/biz/projects

Common errors:
  401  Invalid API key or auth failure
  500  Backend/internal failure
EOF
}

source "$(dirname "$0")/_common.sh"

page=1
page_size=20
legacy_page_size=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --page)
      [[ $# -ge 2 ]] || { echo 'Error: --page requires a value' >&2; exit 2; }
      page="$2"
      shift 2
      ;;
    --page-size)
      [[ $# -ge 2 ]] || { echo 'Error: --page-size requires a value' >&2; exit 2; }
      page_size="$2"
      shift 2
      ;;
    -*)
      echo "Error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$legacy_page_size" ]]; then
        echo "Error: unexpected argument: $1" >&2
        usage >&2
        exit 2
      fi
      legacy_page_size="$1"
      shift
      ;;
  esac
done

if [[ -n "$legacy_page_size" ]]; then
  page_size="$legacy_page_size"
fi

if [[ ! "$page" =~ ^[0-9]+$ || "$page" == "0" ]]; then
  echo "Error: page must be a positive integer: $page" >&2
  exit 2
fi

if [[ ! "$page_size" =~ ^[0-9]+$ || "$page_size" == "0" ]]; then
  echo "Error: page_size must be a positive integer: $page_size" >&2
  exit 2
fi

pexo_get "/api/biz/projects?page=${page}&page_size=${page_size}"
