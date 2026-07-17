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

for ((attempt = 1; attempt <= max_attempts; attempt++)); do
  response="$({
    curl --fail --silent --show-error \
      --proto '=https' \
      --tlsv1.2 \
      --connect-timeout 30 \
      --max-time 120 \
      --request GET \
      --header @- \
      -- "$usage_url" \
      <<<"Authorization: Bearer $HELM_API_KEY"
  })"
  curl_status=$?

  if [[ "$curl_status" -eq 0 ]]; then
    printf '%s' "$response"
    exit 0
  fi

  case "$curl_status" in
    28 | 35 | 52 | 55 | 56)
      if ((attempt < max_attempts)); then
        delay=$((retry_base_seconds * (1 << (attempt - 1))))
        echo "::warning::audit compute Helm GET attempt ${attempt}/${max_attempts} failed with curl exit ${curl_status}; retrying in ${delay}s" >&2
        sleep "$delay"
        continue
      fi
      echo "::error::audit compute Helm GET exhausted ${max_attempts} attempts; final curl exit ${curl_status}" >&2
      ;;
    *)
      echo "::error::audit compute Helm GET failed with non-retryable curl exit ${curl_status}" >&2
      ;;
  esac

  exit "$curl_status"
done
