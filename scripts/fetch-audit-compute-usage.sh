#!/usr/bin/env bash
set -uo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 <https-usage-url>" >&2
  exit 64
fi

usage_url="$1"
if [[ "$usage_url" != https://* ]]; then
  echo "audit compute usage URL must use https" >&2
  exit 64
fi

: "${HELM_API_KEY:?HELM_API_KEY is required}"

max_attempts="${AUDIT_READ_MAX_ATTEMPTS:-3}"
retry_base_seconds="${AUDIT_READ_RETRY_BASE_SECONDS:-2}"

if ! [[ "$max_attempts" =~ ^[1-3]$ ]]; then
  echo "AUDIT_READ_MAX_ATTEMPTS must be an integer from 1 to 3" >&2
  exit 64
fi
if ! [[ "$retry_base_seconds" =~ ^[0-9]+$ ]] || ((retry_base_seconds > 60)); then
  echo "AUDIT_READ_RETRY_BASE_SECONDS must be an integer from 0 to 60" >&2
  exit 64
fi

temp_root="$(mktemp -d "${TMPDIR:-/tmp}/audit-compute-usage.XXXXXX")" || {
  echo "failed to create audit compute usage temp directory" >&2
  exit 1
}
cleanup() {
  rm -rf -- "$temp_root"
}
trap cleanup EXIT

for ((attempt = 1; attempt <= max_attempts; attempt++)); do
  attempt_dir="$temp_root/attempt-$attempt"
  body_file="$attempt_dir/body"
  header_file="$attempt_dir/headers"
  mkdir -m 700 -- "$attempt_dir" || exit 1
  : > "$body_file"
  : > "$header_file"

  http_status="$(
    curl --disable \
      --silent --show-error \
      --proto '=https' \
      --proto-redir '=https' \
      --tlsv1.2 \
      --retry 0 \
      --connect-timeout 30 \
      --max-time 120 \
      --request GET \
      --header @- \
      --output "$body_file" \
      --dump-header "$header_file" \
      --write-out '%{http_code}' \
      -- "$usage_url" \
      <<<"Authorization: Bearer $HELM_API_KEY"
  )"
  curl_status=$?

  if [[ "$curl_status" -eq 0 && "$http_status" == "200" ]]; then
    cat "$body_file"
    exit 0
  fi

  if [[ "$curl_status" -eq 0 ]]; then
    echo "::error::audit compute Helm GET returned HTTP ${http_status:-unknown}; expected 200" >&2
    exit 22
  fi

  allowlisted=false
  retryable=false
  case "$curl_status" in
    28 | 35 | 52 | 55 | 56)
      allowlisted=true
      if [[ "$http_status" == "000" && ! -s "$body_file" && ! -s "$header_file" ]]; then
        retryable=true
      fi
      ;;
  esac

  if [[ "$retryable" == true && "$attempt" -lt "$max_attempts" ]]; then
    delay=$((retry_base_seconds * (1 << (attempt - 1))))
    echo "::warning::audit compute Helm GET attempt ${attempt}/${max_attempts} failed with curl exit ${curl_status}; retrying in ${delay}s" >&2
    sleep "$delay"
    continue
  fi

  if [[ "$retryable" == true ]]; then
    echo "::error::audit compute Helm GET exhausted ${max_attempts} attempts; final curl exit ${curl_status}" >&2
  elif [[ "$allowlisted" == false ]]; then
    echo "::error::audit compute Helm GET failed with non-retryable curl exit ${curl_status}" >&2
  else
    echo "::error::audit compute Helm GET failed closed with curl exit ${curl_status}, HTTP ${http_status:-unknown}, body bytes $(wc -c < "$body_file"), and header bytes $(wc -c < "$header_file")" >&2
  fi

  exit "$curl_status"
done
