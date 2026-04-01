#!/usr/bin/env bash
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"

usage() {
  cat <<'EOF'
Usage:
  pexo-upload.sh <project_id> <file_path>
  pexo-upload.sh -h | --help

Description:
  Upload a local media file to a project in three steps:
  1. Request upload credential
  2. PUT bytes to the presigned URL
  3. Finalize the asset

Supported file types:
  Images: jpg, jpeg, png, webp, bmp, tiff, heic, heif
  Videos: mp4, mov, avi
  Audio:  mp3, wav, aac, m4a, ogg, flac

Returns:
  asset_id string on stdout

Common errors:
  400  Invalid file metadata or unsupported media type
  401  Invalid API key or auth failure
  404  Asset not found during finalize
  412  Asset is no longer in UPLOADING state during finalize
  500  Upload credential/finalize backend failure
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
filepath="$2"

[[ -f "$filepath" ]] || { echo "Error: file not found: $filepath" >&2; exit 1; }

filename=$(basename "$filepath")
filesize=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null)
asset_type=$(detect_asset_type "$filename")
mime_type=$(detect_mime "$filepath")
finalize_mime_type="$mime_type"

[[ -n "${filesize:-}" ]] || { echo "Error: failed to determine file size: $filepath" >&2; exit 1; }

[[ "$asset_type" != "UNKNOWN" ]] || {
  echo "Error: unsupported file type: $filename" >&2
  echo "Allowed: jpg jpeg png webp bmp tiff heic heif mp4 mov avi mp3 wav aac m4a ogg flac" >&2
  exit 1
}

if ! mime_supported_for_asset_type "$mime_type" "$asset_type"; then
  finalize_mime_type=""
fi

# Phase 1: get upload credential
cred=$(pexo_post "/api/biz/projects/${pid}/assets/upload-credential" \
  "{\"file_name\":\"$filename\",\"file_size\":$filesize}")

upload_url=$(echo "$cred" | jq -r '.uploadUrl')
asset_id=$(echo "$cred" | jq -r '.assetId')
storage_path=$(echo "$cred" | jq -r '.storagePath')

[[ -n "$upload_url" && "$upload_url" != "null" ]] || { echo "Error: failed to get upload credential" >&2; echo "$cred" >&2; exit 1; }
[[ -n "$asset_id" && "$asset_id" != "null" ]] || { echo "Error: upload credential missing assetId" >&2; echo "$cred" >&2; exit 1; }
[[ -n "$storage_path" && "$storage_path" != "null" ]] || { echo "Error: upload credential missing storagePath" >&2; echo "$cred" >&2; exit 1; }

# Phase 2: PUT raw bytes to presigned URL
http_code=$(curl -sS -X PUT -H "Content-Type: $mime_type" \
  --data-binary "@$filepath" -o /dev/null -w '%{http_code}' "$upload_url" 2>/dev/null || echo "000")

[[ "$http_code" =~ ^2 ]] || { echo "Error: upload failed with HTTP $http_code" >&2; exit 1; }

# Phase 3: finalize
finalize_body=$(jq -nc \
  --arg name "$filename" \
  --arg type "$asset_type" \
  --arg fname "$filename" \
  --argjson size "$filesize" \
  --arg mime "$finalize_mime_type" \
  --arg spath "$storage_path" \
  '{
    asset_name:$name,
    asset_type:$type,
    file_name:$fname,
    file_size:$size,
    storage_path:$spath
  } + (if $mime != "" then {mime_type:$mime} else {} end)')

pexo_post "/api/biz/projects/${pid}/assets/${asset_id}/finalize" "$finalize_body" > /dev/null

printf '%s\n' "$asset_id"
