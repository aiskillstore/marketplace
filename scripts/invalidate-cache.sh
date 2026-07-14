#!/usr/bin/env bash

set -euo pipefail

MAX_BATCH_SIZE=30
BATCH_SIZE="${BATCH_SIZE:-10}"
MAX_ITEMS="${MAX_ITEMS:-100}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-3}"
RETRY_BASE_SECONDS="${RETRY_BASE_SECONDS:-5}"
CURL_CONNECT_TIMEOUT="${CURL_CONNECT_TIMEOUT:-10}"
CURL_MAX_TIME="${CURL_MAX_TIME:-30}"
CONTENT_TYPE="${CONTENT_TYPE:-}"
SLUGS_STR="${SLUGS_STR:-}"
SLUGS_FILE="${SLUGS_FILE:-}"
SITE_URL="${SITE_URL:-}"
CACHE_SECRET="${CACHE_SECRET:-}"

if ! WORK_DIR="$(mktemp -d)"; then
  echo "::error::Failed to create temporary workspace" >&2
  exit 1
fi
ITEMS_FILE="$WORK_DIR/items"
trap 'rm -rf "$WORK_DIR"' EXIT
: > "$ITEMS_FILE"

write_output() {
  if [ -n "${GITHUB_OUTPUT:-}" ]; then
    printf '%s=%s\n' "$1" "$2" >> "$GITHUB_OUTPUT"
  fi
}

write_counts() {
  write_output total_count "$1"
  write_output success_count "$2"
  write_output failed_count "$3"
}

normalize_items() {
  tr ',[:space:]' '\n' | sed '/^$/d'
}

if [ -n "$SLUGS_FILE" ]; then
  if [ ! -f "$SLUGS_FILE" ]; then
    echo "::error::slugs-file does not exist: $SLUGS_FILE" >&2
    exit 1
  fi
  normalize_items < "$SLUGS_FILE" >> "$ITEMS_FILE"
fi

if [ -n "$SLUGS_STR" ]; then
  printf '%s\n' "$SLUGS_STR" | normalize_items >> "$ITEMS_FILE"
fi

SLUGS=()
while IFS= read -r slug; do
  SLUGS+=("$slug")
done < "$ITEMS_FILE"

TOTAL=${#SLUGS[@]}
if ! [[ "$MAX_ITEMS" =~ ^[1-9][0-9]*$ ]]; then
  echo "::error::MAX_ITEMS must be a positive integer" >&2
  exit 1
fi

if [ "${#TOTAL}" -gt "${#MAX_ITEMS}" ] ||
  { [ "${#TOTAL}" -eq "${#MAX_ITEMS}" ] && [[ "$TOTAL" > "$MAX_ITEMS" ]]; }; then
  echo "::error::item count $TOTAL exceeds MAX_ITEMS $MAX_ITEMS" >&2
  exit 1
fi

if [ "$TOTAL" -eq 0 ]; then
  write_counts 0 0 0
  echo "No items to invalidate"
  exit 0
fi

case "$CONTENT_TYPE" in
  skills|packs|plugins|releases) ;;
  *)
    echo "::error::Unsupported cache content type: $CONTENT_TYPE" >&2
    exit 1
    ;;
esac

if ! [[ "$BATCH_SIZE" =~ ^[0-9]+$ ]] ||
  [ "$BATCH_SIZE" -lt 1 ] ||
  [ "$BATCH_SIZE" -gt "$MAX_BATCH_SIZE" ]; then
  echo "::error::batch-size must be between 1 and $MAX_BATCH_SIZE" >&2
  exit 1
fi

if ! [[ "$MAX_ATTEMPTS" =~ ^[0-9]+$ ]] ||
  [ "$MAX_ATTEMPTS" -lt 1 ] ||
  [ "$MAX_ATTEMPTS" -gt 10 ]; then
  echo "::error::MAX_ATTEMPTS must be between 1 and 10" >&2
  exit 1
fi

if ! [[ "$RETRY_BASE_SECONDS" =~ ^[0-9]+$ ]] ||
  [ "$RETRY_BASE_SECONDS" -gt 300 ]; then
  echo "::error::RETRY_BASE_SECONDS must be between 0 and 300" >&2
  exit 1
fi

if ! [[ "$CURL_CONNECT_TIMEOUT" =~ ^[0-9]+$ ]] ||
  [ "$CURL_CONNECT_TIMEOUT" -lt 1 ] ||
  ! [[ "$CURL_MAX_TIME" =~ ^[0-9]+$ ]] ||
  [ "$CURL_MAX_TIME" -lt 1 ]; then
  echo "::error::curl timeouts must be positive integers" >&2
  exit 1
fi

if [ -z "$SITE_URL" ]; then
  echo "::error::Site URL is empty" >&2
  exit 1
fi

if [ -z "$CACHE_SECRET" ]; then
  echo "::error::Cache invalidation secret is empty" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "::error::jq is required for cache invalidation" >&2
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "::error::curl is required for cache invalidation" >&2
  exit 1
fi

request_batch_once() {
  local body_file="$1"
  local response_file="$2"
  local status
  local curl_exit

  if status=$(curl -sS -o "$response_file" -w "%{http_code}" \
      --connect-timeout "$CURL_CONNECT_TIMEOUT" \
      --max-time "$CURL_MAX_TIME" \
      -X POST "$SITE_URL/api/cache/invalidate" \
      -H "Authorization: Bearer $CACHE_SECRET" \
      -H "Content-Type: application/json" \
      -H "User-Agent: GitHub-Actions/SkillstoreBot" \
      -H "X-Skillstore-Callback: true" \
      --data-binary @"$body_file"); then
    curl_exit=0
  else
    curl_exit=$?
  fi

  case "$status" in
    2[0-9][0-9])
      return 0
      ;;
    408|429|5[0-9][0-9])
      echo "    Transient HTTP $status" >&2
      return 75
      ;;
    ''|000)
      if [ "$curl_exit" -ne 0 ]; then
        case "$curl_exit" in
          5|6|7|16|18|28|35|52|55|56|92)
            echo "    Transient curl transport failure (exit $curl_exit)" >&2
            return 75
            ;;
          *)
            echo "    Non-transient curl failure (exit $curl_exit)" >&2
            return 1
            ;;
        esac
      fi

      echo "    Invalid HTTP status '$status'" >&2
      return 1
      ;;
    [0-9][0-9][0-9])
      echo "    Non-transient HTTP $status" >&2
      return 1
      ;;
    *)
      echo "    Invalid HTTP status '$status'" >&2
      return 1
      ;;
  esac
}

invalidate_batch() {
  local body_file="$1"
  local batch_number="$2"
  local attempt
  local delay
  local request_status
  local response_file="$WORK_DIR/response-$batch_number"

  for ((attempt = 1; attempt <= MAX_ATTEMPTS; attempt++)); do
    : > "$response_file"
    if request_batch_once "$body_file" "$response_file"; then
      request_status=0
    else
      request_status=$?
    fi

    if [ "$request_status" -eq 0 ]; then
      return 0
    fi

    if [ "$request_status" -ne 75 ]; then
      return 1
    fi

    if [ "$attempt" -lt "$MAX_ATTEMPTS" ]; then
      delay=$((attempt * RETRY_BASE_SECONDS))
      echo "    Attempt $attempt/$MAX_ATTEMPTS failed; retrying in ${delay}s" >&2
      sleep "$delay"
    fi
  done

  echo "    Retry budget exhausted after $MAX_ATTEMPTS attempts" >&2
  return 1
}

write_output total_count "$TOTAL"
BATCHES=$(((TOTAL + BATCH_SIZE - 1) / BATCH_SIZE))
SUCCESS=0

echo "Invalidating $TOTAL $CONTENT_TYPE item(s) in $BATCHES batch(es)"

for ((offset = 0; offset < TOTAL; offset += BATCH_SIZE)); do
  BATCH=("${SLUGS[@]:offset:BATCH_SIZE}")
  BATCH_NUMBER=$((offset / BATCH_SIZE + 1))
  BODY_FILE="$WORK_DIR/body-$BATCH_NUMBER.json"

  if ! printf '%s\n' "${BATCH[@]}" |
    jq -Rsc --arg type "$CONTENT_TYPE" \
      '{type: $type, slugs: (split("\n") | map(select(length > 0))), invalidateApi: true}' \
      > "$BODY_FILE"; then
    echo "::error::Failed to construct cache invalidation JSON" >&2
    write_counts "$TOTAL" "$SUCCESS" "$((TOTAL - SUCCESS))"
    exit 1
  fi

  echo "  Batch $BATCH_NUMBER/$BATCHES (${#BATCH[@]} items)"
  if ! invalidate_batch "$BODY_FILE" "$BATCH_NUMBER"; then
    write_counts "$TOTAL" "$SUCCESS" "$((TOTAL - SUCCESS))"
    echo "::error::Cache invalidation batch $BATCH_NUMBER/$BATCHES failed" >&2
    exit 1
  fi

  SUCCESS=$((SUCCESS + ${#BATCH[@]}))
done

write_counts "$TOTAL" "$SUCCESS" 0
echo "Cache invalidation complete: $SUCCESS item(s)"
