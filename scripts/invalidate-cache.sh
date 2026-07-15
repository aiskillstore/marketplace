#!/usr/bin/env bash

set -euo pipefail

MAX_BATCH_SIZE=30
BATCH_SIZE="${BATCH_SIZE:-10}"
MAX_ITEMS="${MAX_ITEMS:-100}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-3}"
RETRY_BASE_SECONDS="${RETRY_BASE_SECONDS:-5}"
CURL_CONNECT_TIMEOUT="${CURL_CONNECT_TIMEOUT:-10}"
CURL_MAX_TIME="${CURL_MAX_TIME:-30}"
FALLBACK_MAX_ATTEMPTS="${FALLBACK_MAX_ATTEMPTS:-4}"
FALLBACK_RETRY_BASE_SECONDS="${FALLBACK_RETRY_BASE_SECONDS:-5}"
FALLBACK_CURL_MAX_TIME="${FALLBACK_CURL_MAX_TIME:-90}"
MAX_RUNTIME_SECONDS="${MAX_RUNTIME_SECONDS:-1200}"
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

if ! awk '!seen[$0]++' "$ITEMS_FILE" > "$WORK_DIR/items-unique"; then
  echo "::error::Failed to normalize cache invalidation items" >&2
  exit 1
fi
mv "$WORK_DIR/items-unique" "$ITEMS_FILE"

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

if ! [[ "$FALLBACK_MAX_ATTEMPTS" =~ ^[0-9]+$ ]] ||
  [ "$FALLBACK_MAX_ATTEMPTS" -lt 1 ] ||
  [ "$FALLBACK_MAX_ATTEMPTS" -gt 10 ]; then
  echo "::error::FALLBACK_MAX_ATTEMPTS must be between 1 and 10" >&2
  exit 1
fi

if ! [[ "$RETRY_BASE_SECONDS" =~ ^[0-9]+$ ]] ||
  [ "$RETRY_BASE_SECONDS" -gt 300 ]; then
  echo "::error::RETRY_BASE_SECONDS must be between 0 and 300" >&2
  exit 1
fi

if ! [[ "$FALLBACK_RETRY_BASE_SECONDS" =~ ^[0-9]+$ ]] ||
  [ "$FALLBACK_RETRY_BASE_SECONDS" -gt 300 ]; then
  echo "::error::FALLBACK_RETRY_BASE_SECONDS must be between 0 and 300" >&2
  exit 1
fi

if ! [[ "$MAX_RUNTIME_SECONDS" =~ ^[0-9]+$ ]] ||
  [ "$MAX_RUNTIME_SECONDS" -lt 1 ] ||
  [ "$MAX_RUNTIME_SECONDS" -gt 1200 ]; then
  echo "::error::MAX_RUNTIME_SECONDS must be between 1 and 1200" >&2
  exit 1
fi

if ! [[ "$CURL_CONNECT_TIMEOUT" =~ ^[0-9]+$ ]] ||
  [ "$CURL_CONNECT_TIMEOUT" -lt 1 ] ||
  ! [[ "$CURL_MAX_TIME" =~ ^[0-9]+$ ]] ||
  [ "$CURL_MAX_TIME" -lt 1 ] ||
  ! [[ "$FALLBACK_CURL_MAX_TIME" =~ ^[0-9]+$ ]] ||
  [ "$FALLBACK_CURL_MAX_TIME" -lt 1 ]; then
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

DEADLINE_EPOCH=$(($(date +%s) + MAX_RUNTIME_SECONDS))

remaining_seconds() {
  local remaining=$((DEADLINE_EPOCH - $(date +%s)))
  if [ "$remaining" -lt 0 ]; then
    remaining=0
  fi
  printf '%s\n' "$remaining"
}

request_batch_once() {
  local body_file="$1"
  local response_file="$2"
  local max_time="$3"
  local status
  local curl_exit
  local remaining

  remaining=$(remaining_seconds)
  if [ "$remaining" -lt 1 ]; then
    echo "    Global cache invalidation runtime budget exhausted" >&2
    return 77
  fi
  if [ "$max_time" -gt "$remaining" ]; then
    max_time="$remaining"
  fi

  if status=$(curl -sS -o "$response_file" -w "%{http_code}" \
      --connect-timeout "$CURL_CONNECT_TIMEOUT" \
      --max-time "$max_time" \
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
      local canonical_type="$CONTENT_TYPE"
      if [ "$canonical_type" = "plugins" ]; then
        canonical_type="packs"
      fi

      if jq -e \
        --arg canonical_type "$canonical_type" \
        --slurpfile request "$body_file" \
        'def non_negative_integer:
          type == "number" and isfinite and floor == . and . >= 0;
        ($request | length) == 1
          and .preflight == false
          and .type == $canonical_type
          and (.slugs | type) == "array"
          and ((.slugs | sort) == ($request[0].slugs | sort))
          and (.invalidated | type) == "object"
          and (.invalidated.total | non_negative_integer)
          and (.invalidated.page | non_negative_integer)
          and (.invalidated.api | non_negative_integer)
          and (.invalidated.artifacts | non_negative_integer)
          and (.invalidated.total > 0)
          and (.invalidated.total ==
            (.invalidated.page + .invalidated.api + .invalidated.artifacts))
          and (.invalidated.listVersionBumped | type) == "boolean"
          and (if ($canonical_type == "skills" or $canonical_type == "packs")
            then .invalidated.listVersionBumped == true
            else .invalidated.listVersionBumped == false
          end)
          and .invalidated.listMaxStaleSeconds == 0' \
        "$response_file" >/dev/null 2>&1; then
        return 0
      fi

      echo "    Cache invalidation response violated the requested contract" >&2
      return 76
      ;;
    408|429|5[0-9][0-9])
      echo "    Transient HTTP $status" >&2
      return 75
      ;;
    409)
      if jq -e \
        '.message == "Dependent pack closure exceeds the 100-pack cap"' \
        "$response_file" >/dev/null 2>&1; then
        echo "    Cache closure overflow is safe to split into single-item requests" >&2
        return 76
      fi
      echo "    Non-transient HTTP 409" >&2
      return 1
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
  local request_label="$2"
  local max_attempts="$3"
  local retry_base_seconds="$4"
  local max_time="$5"
  local attempt
  local delay
  local request_status
  local remaining
  local response_file="$WORK_DIR/response-$request_label"

  for ((attempt = 1; attempt <= max_attempts; attempt++)); do
    : > "$response_file"
    if request_batch_once "$body_file" "$response_file" "$max_time"; then
      request_status=0
    else
      request_status=$?
    fi

    if [ "$request_status" -eq 0 ]; then
      return 0
    fi

    if [ "$request_status" -ne 75 ]; then
      return "$request_status"
    fi

    if [ "$attempt" -lt "$max_attempts" ]; then
      delay=$((attempt * retry_base_seconds))
      remaining=$(remaining_seconds)
      if [ "$delay" -ge "$remaining" ]; then
        echo "    Global cache invalidation runtime budget exhausted before retry" >&2
        return 77
      fi
      echo "    Attempt $attempt/$max_attempts failed; retrying in ${delay}s" >&2
      sleep "$delay"
    fi
  done

  echo "    Retry budget exhausted after $max_attempts attempts" >&2
  return 75
}

create_body() {
  local body_file="$1"
  shift

  if ! printf '%s\n' "$@" |
    jq -Rsc --arg type "$CONTENT_TYPE" \
      '{type: $type, slugs: (split("\n") | map(select(length > 0))), invalidateApi: true}' \
      > "$body_file"; then
    echo "::error::Failed to construct cache invalidation JSON" >&2
    return 1
  fi
}

SUCCESS=0
SUCCESS_ITEMS_FILE="$WORK_DIR/success-items"
: > "$SUCCESS_ITEMS_FILE"

record_success() {
  printf '%s\n' "$1" >> "$SUCCESS_ITEMS_FILE"
  SUCCESS=$((SUCCESS + 1))
}

finish_invalidation() {
  local failed_items_file="$WORK_DIR/failed-items"
  local failed_json
  local slug

  : > "$failed_items_file"
  for slug in "${SLUGS[@]}"; do
    if ! grep -Fqx -- "$slug" "$SUCCESS_ITEMS_FILE"; then
      printf '%s\n' "$slug" >> "$failed_items_file"
    fi
  done

  FAILED=$((TOTAL - SUCCESS))
  write_counts "$TOTAL" "$SUCCESS" "$FAILED"

  if [ "$FAILED" -eq 0 ]; then
    echo "Cache invalidation complete: $SUCCESS item(s)"
    return 0
  fi

  failed_json=$(jq -Rsc 'split("\n") | map(select(length > 0))' < "$failed_items_file")
  echo "::error::Cache invalidation failed for $FAILED item(s): $failed_json" >&2
  return 1
}

BATCHES=$(((TOTAL + BATCH_SIZE - 1) / BATCH_SIZE))

echo "Invalidating $TOTAL $CONTENT_TYPE item(s) in $BATCHES batch(es)"

for ((offset = 0; offset < TOTAL; offset += BATCH_SIZE)); do
  BATCH=("${SLUGS[@]:offset:BATCH_SIZE}")
  BATCH_NUMBER=$((offset / BATCH_SIZE + 1))
  BODY_FILE="$WORK_DIR/body-$BATCH_NUMBER.json"

  if ! create_body "$BODY_FILE" "${BATCH[@]}"; then
    finish_invalidation || true
    exit 1
  fi

  echo "  Batch $BATCH_NUMBER/$BATCHES (${#BATCH[@]} items)"
  if invalidate_batch \
    "$BODY_FILE" \
    "batch-$BATCH_NUMBER" \
    "$MAX_ATTEMPTS" \
    "$RETRY_BASE_SECONDS" \
    "$CURL_MAX_TIME"; then
    for slug in "${BATCH[@]}"; do
      record_success "$slug"
    done
    continue
  else
    batch_status=$?
  fi
  if { [ "$batch_status" -ne 75 ] && [ "$batch_status" -ne 76 ]; } ||
    [ "${#BATCH[@]}" -eq 1 ]; then
    echo "::error::Cache invalidation batch $BATCH_NUMBER/$BATCHES failed without a safe fallback" >&2
    continue
  fi

  echo "::warning::Batch $BATCH_NUMBER/$BATCHES failed; falling back to ${#BATCH[@]} single-item request(s)" >&2
  for index in "${!BATCH[@]}"; do
    slug="${BATCH[$index]}"
    FALLBACK_BODY_FILE="$WORK_DIR/body-$BATCH_NUMBER-fallback-$index.json"
    if ! create_body "$FALLBACK_BODY_FILE" "$slug"; then
      finish_invalidation || true
      exit 1
    fi

    echo "    Fallback $((index + 1))/${#BATCH[@]}: $slug"
    if invalidate_batch \
      "$FALLBACK_BODY_FILE" \
      "batch-$BATCH_NUMBER-fallback-$index" \
      "$FALLBACK_MAX_ATTEMPTS" \
      "$FALLBACK_RETRY_BASE_SECONDS" \
      "$FALLBACK_CURL_MAX_TIME"; then
      record_success "$slug"
      continue
    fi

  done
done

if ! finish_invalidation; then
  exit 1
fi
