#!/usr/bin/env bash
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"

# Pexo environment diagnostic tool.
# Checks config, dependencies, connectivity, and API key validity.
# Run this when first setting up or when scripts fail unexpectedly.
#
# Usage: pexo-doctor.sh
set -uo pipefail

usage() {
  cat <<'EOF'
Usage:
  pexo-doctor.sh
  pexo-doctor.sh -h | --help

Description:
  Run environment checks for the Pexo shell scripts:
  - config file presence
  - required variables
  - local dependencies
  - network reachability
  - API key/auth validity check

Notes:
  API keys are expected to use the sk- prefix.
EOF
}

extract_message() {
  local payload="${1:-}"
  echo "$payload" | jq -r '.data.message // .message // .error // "unknown"' 2>/dev/null || echo "unknown"
}

extract_error_code() {
  local payload="${1:-}"
  echo "$payload" | jq -r '.data.error // .error // empty' 2>/dev/null || true
}

mask_secret() {
  local value="${1:-}"

  if [[ -z "$value" ]]; then
    printf '%s\n' ""
    return 0
  fi

  if [[ ${#value} -le 12 ]]; then
    printf '%s\n' "$value"
    return 0
  fi

  printf '%s...%s\n' "${value:0:8}" "${value: -4}"
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac

PASS="✓"
FAIL="✗"
WARN="!"
errors=0

echo "=== Pexo Environment Diagnostic ==="
echo ""

config_path="${PEXO_CONFIG:-$HOME/.pexo/config}"

# 1. Config file
if [[ -f "$config_path" ]]; then
  echo "$PASS Config file found: $config_path"
  source "$config_path"
else
  echo "$FAIL Config file not found: $config_path"
  echo "  Create it with:"
  echo '  mkdir -p ~/.pexo && cat > ~/.pexo/config << EOF'
  echo '  PEXO_BASE_URL="https://pexo.ai"'
  echo '  PEXO_API_KEY="sk-<your-api-key>"'
  echo '  EOF'
  errors=$((errors + 1))
fi

# 2. Required variables
if [[ -n "${PEXO_BASE_URL:-}" ]]; then
  echo "$PASS PEXO_BASE_URL is set: $PEXO_BASE_URL"
else
  echo "$FAIL PEXO_BASE_URL is not set"
  errors=$((errors + 1))
fi

if [[ -n "${PEXO_API_KEY:-}" ]]; then
  masked=$(mask_secret "$PEXO_API_KEY")
  echo "$PASS PEXO_API_KEY is set: $masked"
  if [[ "$PEXO_API_KEY" != sk-* ]]; then
    echo "$WARN PEXO_API_KEY does not start with sk-"
    echo "  API keys are expected to start with sk-."
  fi
else
  echo "$FAIL PEXO_API_KEY is not set"
  echo "  Get your API key at: https://pexo.ai"
  errors=$((errors + 1))
fi

# 3. Dependencies
echo ""
for cmd in curl jq file; do
  if command -v "$cmd" &>/dev/null; then
    ver=$("$cmd" --version 2>&1 | head -1)
    echo "$PASS $cmd is installed: $ver"
  else
    echo "$FAIL $cmd is not installed"
    if [[ "$cmd" == "file" ]]; then
      echo "  Install the package that provides file(1) for your OS. It is usually preinstalled on macOS."
    else
      echo "  Install: brew install $cmd (macOS) or apt-get install $cmd (Linux)"
    fi
    errors=$((errors + 1))
  fi
done

# 4. Network connectivity
echo ""
if [[ -n "${PEXO_BASE_URL:-}" ]]; then
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "${PEXO_BASE_URL}" 2>/dev/null || echo "000")
  if [[ "$http_code" != "000" ]]; then
    echo "$PASS Network: can reach $PEXO_BASE_URL (HTTP $http_code)"
  else
    echo "$FAIL Network: cannot reach $PEXO_BASE_URL"
    echo "  Check your network connection, firewall, and DNS settings."
    errors=$((errors + 1))
  fi
else
  echo "$WARN Network: skipped (PEXO_BASE_URL not set)"
fi

# 5. API key validation
echo ""
if [[ -n "${PEXO_BASE_URL:-}" && -n "${PEXO_API_KEY:-}" ]]; then
  tmp_body=$(mktemp)
  tmp_err=$(mktemp)
  http_code=$(curl -sS \
    --connect-timeout 10 \
    -H "Authorization: Bearer $PEXO_API_KEY" \
    -H "Content-Type: application/json" \
    -o "$tmp_body" \
    -w '%{http_code}' \
    "${PEXO_BASE_URL}/api/biz/projects?page_size=1" 2>"$tmp_err" || echo "000")
  resp=$(cat "$tmp_body")
  curl_err=$(cat "$tmp_err")
  rm -f "$tmp_body" "$tmp_err"

  if [[ "$http_code" == "200" ]]; then
    echo "$PASS API key is valid (projects endpoint responded OK)"
  elif [[ "$http_code" == "401" ]]; then
    auth_error=$(extract_error_code "$resp")
    message=$(extract_message "$resp")
    if [[ "$auth_error" == "INVALID_API_KEY" ]]; then
      echo "$FAIL API key is invalid or expired (HTTP 401)"
      echo "  Message: $message"
      echo "  Get a new key at: https://pexo.ai"
      errors=$((errors + 1))
    elif [[ "$auth_error" == "INTERNAL_ERROR" ]]; then
      echo "$WARN API check returned HTTP 401 with INTERNAL_ERROR"
      echo "  This is a temporary service issue, not a problem with the API key. Wait and retry."
      echo "  Message: $message"
    else
      echo "$FAIL API check returned HTTP 401"
      echo "  Message: $message"
      errors=$((errors + 1))
    fi
  elif [[ "$http_code" == "409" ]]; then
    echo "$WARN API check returned HTTP 409"
    echo "  Message: $(extract_message "$resp")"
    echo "  This is normal for JWT session replacement, but unusual for API-key auth."
  elif [[ "$http_code" == "000" ]]; then
    echo "$FAIL API validation request failed before receiving a response"
    echo "  Curl error: ${curl_err:-unknown}"
    errors=$((errors + 1))
  else
    echo "$WARN API check returned HTTP $http_code"
    echo "  Message: $(extract_message "$resp")"
  fi
else
  echo "$WARN API key validation: skipped (missing config)"
fi

# Summary
echo ""
echo "=== Summary ==="
if [[ $errors -eq 0 ]]; then
  echo "$PASS All checks passed. Pexo is ready to use."
else
  echo "$FAIL $errors issue(s) found. Fix the items marked with $FAIL above."
fi

exit $errors
