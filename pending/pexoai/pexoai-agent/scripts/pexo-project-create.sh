#!/usr/bin/env bash
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"

usage() {
  cat <<'EOF'
Usage:
  pexo-project-create.sh [project_name]
  pexo-project-create.sh --name <project_name>
  pexo-project-create.sh -h | --help

Description:
  Create a new Pexo project.
  If no project name is provided, the script uses "Untitled".

Returns:
  project_id string on stdout

Common errors:
  400  Invalid project name
  401  Invalid API key or auth failure
  429  Creation limit reached (concurrent-project limit or insufficient credits)
       Credit balance and a top-up link are printed to stderr automatically.
  500  Backend/internal failure
EOF
}

source "$(dirname "$0")/_common.sh"

project_name=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --name)
      [[ $# -ge 2 ]] || { echo 'Error: --name requires a value' >&2; exit 2; }
      project_name="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$project_name" ]]; then
        echo "Error: unexpected argument: $1" >&2
        usage >&2
        exit 2
      fi
      project_name="$1"
      shift
      ;;
  esac
done

if [[ $# -gt 0 ]]; then
  echo "Error: unexpected argument: $1" >&2
  usage >&2
  exit 2
fi

[[ -n "$project_name" ]] || project_name="Untitled"

body=$(jq -nc --arg n "$project_name" '{project_name: $n}')
result=$(pexo_post "/api/biz/projects" "$body") || {
  [[ "$PEXO_LAST_HTTP_CODE" == "429" ]] && _pexo_credit_hint
  exit 1
}
project_id=$(echo "$result" | jq -r '.projectId // empty')

if [[ -z "$project_id" ]]; then
  echo 'Error: create project response missing projectId' >&2
  echo "$result" >&2
  exit 1
fi

printf '%s\n' "$project_id"
