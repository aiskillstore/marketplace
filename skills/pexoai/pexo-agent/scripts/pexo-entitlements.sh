#!/usr/bin/env bash
[ -n "${BASH_VERSION:-}" ] || exec bash "$0" "$@"

usage() {
  cat <<'EOF'
Usage:
  pexo-entitlements.sh
  pexo-entitlements.sh -h | --help

Description:
  Fetch the current user's credit balance and plan entitlements.
  Useful for proactively checking available credits before starting
  production, or diagnosing why a previous request failed with 429.

Returns (stdout):
  JSON object with shape:
    {
      "userId": "...",
      "credits": {
        "availableCredits": 120,
        "subscriptionCredits": 100,
        "bonusCredits": 20,
        "purchaseCredits": 0,
        "frozenCredits": 0,
        "lifetimeGranted": 1000,
        "lifetimeConsumed": 880,
        "lifetimeExpired": 0
      },
      "plan": { ... }
    }

  When availableCredits is 0, a top-up URL is also printed to stderr.

Common errors:
  401  Invalid API key or auth failure
  500  Backend/internal failure
EOF
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac

source "$(dirname "$0")/_common.sh"

topup_url="${PEXO_BASE_URL:-https://pexo.ai}/home"

result=$(pexo_get "/api/biz/auth/entitlements")

available=$(printf '%s' "$result" \
  | jq -r '.credits.availableCredits // empty' 2>/dev/null) || true

printf '%s\n' "$result"

if [[ -n "$available" ]] && \
   { [[ "$available" == "0" ]] || \
     { [[ "$available" =~ ^[0-9]+$ ]] && [[ "$available" -le 0 ]]; }; }; then
  printf '\nCredits balance: 0 — your account has no available credits.\n' >&2
  printf 'To purchase credits: visit %s → click Credits (top-right) → Buy Credits → Extra Credits\n' "$topup_url" >&2
fi
