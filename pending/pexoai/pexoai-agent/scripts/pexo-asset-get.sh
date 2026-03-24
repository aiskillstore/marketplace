#!/usr/bin/env bash
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"

usage() {
  cat <<'EOF'
Usage:
  pexo-asset-get.sh <project_id> <asset_id>
  pexo-asset-get.sh -h | --help

Description:
  Fetch asset details for a project.
  If the asset has a downloadUrl, this script also downloads the file into
  ~/.pexo/tmp/ (or $PEXO_TMP_DIR when set) and returns both the signed URL and
  the local file path.

Returns:
  Asset JSON from /api/biz/projects/:project_id/assets/:asset_id
  plus:
    - url: original signed download URL
    - localPath: downloaded local cache path, or null when downloadUrl is absent

Common errors:
  401  Invalid API key or auth failure
  404  Asset not found, or asset does not belong to the project/user
  403  Signed asset URL expired or object storage denied download
  500  Backend/internal failure
EOF
}

source "$(dirname "$0")/_common.sh"

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac

if [[ $# -ne 2 ]]; then
  usage >&2
  exit 2
fi

pid="$1"
aid="$2"

asset=$(pexo_get "/api/biz/projects/${pid}/assets/${aid}")
download_url=$(echo "$asset" | jq -r '.downloadUrl // empty')

if [[ -z "$download_url" ]]; then
  echo "$asset" | jq '. + {url:(.downloadUrl // null), localPath:null}'
  exit 0
fi

tmp_dir=$(pexo_tmp_dir)
file_name=$(echo "$asset" | jq -r '.fileName // .assetName // empty')
[[ -n "$file_name" && "$file_name" != "null" ]] || file_name="${aid}.bin"

safe_name=$(printf '%s' "$file_name" | sed 's#[/[:space:]]#_#g')
local_path="${tmp_dir}/${aid}-${safe_name}"
part_path="${local_path}.part.$$"
err_file=$(mktemp)
http_code=""
curl_status=0

http_code=$(curl -sS -L \
  --connect-timeout "$_PEXO_CONNECT_TIMEOUT" \
  --max-time "$_PEXO_REQUEST_TIMEOUT" \
  -o "$part_path" \
  -w '%{http_code}' \
  "$download_url" 2>"$err_file") || curl_status=$?

if [[ $curl_status -ne 0 && "${http_code:-0}" == "000" ]]; then
  err_text=$(cat "$err_file")
  rm -f "$part_path" "$err_file"
  _pexo_emit_error 0 "" "${err_text:-Failed to download asset from signed URL}"
fi

if [[ ! "${http_code:-}" =~ ^2 ]]; then
  err_text=$(cat "$err_file")
  rm -f "$part_path"
  rm -f "$err_file"
  _pexo_emit_error "${http_code:-0}" "" "${err_text:-Failed to download asset from signed URL}"
fi

mv -f "$part_path" "$local_path"
rm -f "$err_file"

echo "$asset" | jq --arg url "$download_url" --arg localPath "$local_path" '. + {url:$url, localPath:$localPath}'
