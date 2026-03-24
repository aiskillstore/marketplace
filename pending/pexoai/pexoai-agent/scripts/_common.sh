#!/usr/bin/env bash
# Shared configuration for Pexo scripts.
# Sources ~/.pexo/config automatically; env vars override.
# Agent scripts source this file -- no need to handle auth manually.
set -euo pipefail

_PEXO_CONFIG="${PEXO_CONFIG:-$HOME/.pexo/config}"
[[ -f "$_PEXO_CONFIG" ]] && source "$_PEXO_CONFIG"

PEXO_LAST_HTTP_CODE=0
_PEXO_CONNECT_TIMEOUT="${PEXO_CONNECT_TIMEOUT:-10}"
_PEXO_REQUEST_TIMEOUT="${PEXO_REQUEST_TIMEOUT:-60}"

pexo_require_config() {
  local missing=()

  if [[ -z "${PEXO_BASE_URL:-}" ]]; then
    missing+=("PEXO_BASE_URL")
  fi

  if [[ -z "${PEXO_API_KEY:-}" ]]; then
    missing+=("PEXO_API_KEY")
  fi

  if [[ ${#missing[@]} -gt 0 ]]; then
    printf 'Missing required config: %s\n' "${missing[*]}" >&2
    printf 'Set them in %s or in the environment.\n' "$_PEXO_CONFIG" >&2
    return 1
  fi
}

_pexo_auth_header() {
  printf 'Authorization: Bearer %s' "$PEXO_API_KEY"
}

pexo_tmp_dir() {
  local tmp_dir="${PEXO_TMP_DIR:-$HOME/.pexo/tmp}"
  mkdir -p "$tmp_dir"
  printf '%s\n' "$tmp_dir"
}

_pexo_is_json() {
  local payload="${1:-}"
  [[ -n "$payload" ]] && jq -e . >/dev/null 2>&1 <<<"$payload"
}

_pexo_extract_http_code() {
  local header_file="$1"
  awk '/^HTTP\// { code = $2 } END { print code + 0 }' "$header_file"
}

_pexo_extract_content_type() {
  local header_file="$1"
  awk '
    tolower($1) == "content-type:" {
      value = $0
    }
    END {
      sub(/\r$/, "", value)
      sub(/^[^:]*:[[:space:]]*/, "", value)
      print tolower(value)
    }
  ' "$header_file"
}

_pexo_emit_success() {
  local body="${1:-}"

  if [[ -z "$body" ]]; then
    return 0
  fi

  if _pexo_is_json "$body"; then
    if jq -e 'type == "object" and has("code") and has("data")' >/dev/null 2>&1 <<<"$body"; then
      jq '.data' <<<"$body"
      return 0
    fi

    jq '.' <<<"$body"
    return 0
  fi

  printf '%s\n' "$body"
}

_pexo_emit_error() {
  local http_code="${1:-0}"
  local body="${2:-}"
  local transport_error="${3:-}"

  export PEXO_LAST_HTTP_CODE="$http_code"

  if [[ "$http_code" == "0" && -n "$transport_error" ]]; then
    jq -nc \
      --argjson httpCode 0 \
      --arg message "Network request failed" \
      --arg details "$transport_error" \
      '{ok:false, httpCode:$httpCode, message:$message, details:$details}' >&2
    return 1
  fi

  if _pexo_is_json "$body"; then
    jq -c --argjson httpCode "${http_code:-0}" '
      def maybe(field; value):
        if value == null or value == "" then {} else { (field): value } end;

      {
        ok: false,
        httpCode: $httpCode,
        message: (
          if (.data | type) == "object" and (.data.message? // "") != "" then .data.message
          elif (.message? // "") != "" then .message
          elif (.error? // "") != "" then .error
          else "request failed"
          end
        )
      }
      + (
        if (.data | type) == "object" and (.data.code? != null) then
          {businessCode: .data.code}
        else
          {}
        end
      )
      + (
        if (.data | type) == "object" and (.data.error? // "") != "" then
          {error: .data.error}
        elif (.error? // "") != "" then
          {error: .error}
        else
          {}
        end
      )
      + (
        if (.data | type) == "object" and (.data.details? // "") != "" then
          {details: .data.details}
        elif (.details? // "") != "" then
          {details: .details}
        else
          {}
        end
      )
    ' <<<"$body" >&2
    return 1
  fi

  jq -nc \
    --argjson httpCode "${http_code:-0}" \
    --arg message "request failed" \
    --arg details "${transport_error:-$body}" \
    '{ok:false, httpCode:$httpCode, message:$message} + (if $details != "" then {details:$details} else {} end)' >&2
  return 1
}

_pexo_request_json() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  shift 3 || true

  pexo_require_config

  local body_file header_file err_file
  local response http_code curl_status=0

  body_file=$(mktemp)
  header_file=$(mktemp)
  err_file=$(mktemp)

  if [[ -n "$body" ]]; then
    http_code=$(curl -sS \
      --connect-timeout "$_PEXO_CONNECT_TIMEOUT" \
      --max-time "$_PEXO_REQUEST_TIMEOUT" \
      -X "$method" \
      -H "$(_pexo_auth_header)" \
      -H "Content-Type: application/json" \
      -D "$header_file" \
      -o "$body_file" \
      -w '%{http_code}' \
      -d "$body" \
      "$@" \
      "${PEXO_BASE_URL}${path}" 2>"$err_file") || curl_status=$?
  else
    http_code=$(curl -sS \
      --connect-timeout "$_PEXO_CONNECT_TIMEOUT" \
      --max-time "$_PEXO_REQUEST_TIMEOUT" \
      -X "$method" \
      -H "$(_pexo_auth_header)" \
      -H "Content-Type: application/json" \
      -D "$header_file" \
      -o "$body_file" \
      -w '%{http_code}' \
      "$@" \
      "${PEXO_BASE_URL}${path}" 2>"$err_file") || curl_status=$?
  fi

  response=$(cat "$body_file")
  export PEXO_LAST_HTTP_CODE="${http_code:-0}"

  if [[ $curl_status -ne 0 && "${http_code:-0}" == "000" ]]; then
    _pexo_emit_error 0 "" "$(cat "$err_file")"
    rm -f "$body_file" "$header_file" "$err_file"
    return 1
  fi

  if [[ "${http_code:-0}" -ge 400 ]] 2>/dev/null; then
    _pexo_emit_error "$http_code" "$response" "$(cat "$err_file")"
    rm -f "$body_file" "$header_file" "$err_file"
    return 1
  fi

  _pexo_emit_success "$response"
  rm -f "$body_file" "$header_file" "$err_file"
}

# GET -> extracts .data from BFF wrapper when present
pexo_get() {
  local path="$1"
  shift || true
  _pexo_request_json GET "$path" "" "$@"
}

# POST with optional JSON body -> extracts .data
pexo_post() {
  local path="$1"
  local body="${2:-}"
  shift 2 || true
  _pexo_request_json POST "$path" "$body" "$@"
}

pexo_post_sse_ack() {
  local path="$1"
  local body="${2:-}"
  local timeout="${3:-20}"

  pexo_require_config

  local body_file header_file err_file
  local response http_code content_type

  body_file=$(mktemp)
  header_file=$(mktemp)
  err_file=$(mktemp)

  set +o pipefail
  if [[ -n "$body" ]]; then
    curl -sS -N \
      --connect-timeout "$_PEXO_CONNECT_TIMEOUT" \
      --max-time "$timeout" \
      -X POST \
      -H "$(_pexo_auth_header)" \
      -H "Content-Type: application/json" \
      -H "Accept: text/event-stream" \
      -D "$header_file" \
      -d "$body" \
      "${PEXO_BASE_URL}${path}" 2>"$err_file" | tee "$body_file" | sed '/^: stream opened$/q' >/dev/null
  else
    curl -sS -N \
      --connect-timeout "$_PEXO_CONNECT_TIMEOUT" \
      --max-time "$timeout" \
      -X POST \
      -H "$(_pexo_auth_header)" \
      -H "Content-Type: application/json" \
      -H "Accept: text/event-stream" \
      -D "$header_file" \
      "${PEXO_BASE_URL}${path}" 2>"$err_file" | tee "$body_file" | sed '/^: stream opened$/q' >/dev/null
  fi
  set -o pipefail

  response=$(cat "$body_file")
  http_code=$(_pexo_extract_http_code "$header_file")
  content_type=$(_pexo_extract_content_type "$header_file")
  export PEXO_LAST_HTTP_CODE="${http_code:-0}"

  if [[ "${http_code:-0}" -ge 400 ]] 2>/dev/null; then
    _pexo_emit_error "$http_code" "$response" "$(cat "$err_file")"
    rm -f "$body_file" "$header_file" "$err_file"
    return 1
  fi

  if [[ "$http_code" == "200" && "$content_type" == text/event-stream* && "$response" == *": stream opened"* ]]; then
    rm -f "$body_file" "$header_file" "$err_file"
    return 0
  fi

  if [[ "$http_code" == "0" ]]; then
    _pexo_emit_error 0 "" "$(cat "$err_file")"
    rm -f "$body_file" "$header_file" "$err_file"
    return 1
  fi

  _pexo_emit_error 0 "" "Timed out waiting for SSE acknowledgement from ${path}"
  rm -f "$body_file" "$header_file" "$err_file"
  return 1
}

# Detect asset type from file extension
detect_asset_type() {
  local ext="${1##*.}"
  ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
  case "$ext" in
    jpg|jpeg|png|webp|bmp|tiff|heic|heif) echo "IMAGE" ;;
    mp4|mov|avi)                          echo "VIDEO" ;;
    mp3|wav|aac|m4a|ogg|flac)            echo "AUDIO" ;;
    *) echo "UNKNOWN" ;;
  esac
}

# Detect MIME type
detect_mime() {
  file --brief --mime-type "$1" 2>/dev/null || echo "application/octet-stream"
}

mime_supported_for_asset_type() {
  local mime_type
  local asset_type="$2"

  mime_type=$(echo "$1" | tr '[:upper:]' '[:lower:]')

  case "${asset_type}:${mime_type}" in
    IMAGE:image/jpeg|IMAGE:image/jpg|IMAGE:image/png|IMAGE:image/webp|IMAGE:image/tiff|IMAGE:image/bmp|IMAGE:image/heic|IMAGE:image/heif)
      return 0
      ;;
    VIDEO:video/mp4|VIDEO:video/x-msvideo|VIDEO:video/avi|VIDEO:video/quicktime)
      return 0
      ;;
    AUDIO:audio/mpeg|AUDIO:audio/wav|AUDIO:audio/wave|AUDIO:audio/aac|AUDIO:audio/mp4|AUDIO:audio/x-m4a|AUDIO:audio/ogg|AUDIO:audio/flac)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}
