#!/usr/bin/env bash
# x402socks helper: health, catalog, nodes, token status/validation/rotation, recovery, egress test.
#
# Tokens are read from $X402SOCKS_TOKEN by preference so they never appear in
# process listings. Passing a token as an argument works but is less safe.
set -euo pipefail

WEB="${X402SOCKS_WEB:-https://x402socks.com}"
PAY="${X402SOCKS_PAY:-https://payments.x402socks.com}"
API="${X402SOCKS_API:-https://api.x402socks.com}"

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
note() { printf '%s\n' "$*" >&2; }

need() { command -v "$1" >/dev/null 2>&1 || die "$1 is required"; }

req() { curl -sS --max-time "${X402SOCKS_TIMEOUT:-30}" "$@"; }

pretty() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool 2>/dev/null || cat
  else
    cat
  fi
}

json_token_body() {
  python3 -c 'import json,sys; print(json.dumps({"token": sys.argv[1]}))' "$1"
}

resolve_token() {
  if [ "${X402SOCKS_TOKEN:-}" != "" ]; then
    printf '%s' "$X402SOCKS_TOKEN"
  elif [ "${1:-}" != "" ]; then
    note "note: token passed as an argument is visible in process listings"
    printf '%s' "$1"
  else
    die "no token: export X402SOCKS_TOKEN, or pass it as the last argument"
  fi
}

usage() {
  cat <<'EOF'
x402socks helper

  health                        service liveness
  nodes [--available]           exit points, optionally only usable ones
  catalog [--summary]           package catalog with prices
  price <package_id>            one package's price and entitlements
  status [token]                account status and usage
  validate [token]              cheap token check (exit 0 = valid)
  rotate [token]                rotate token; old one dies immediately
  test [exit_id]                confirm egress IP through the proxy
  recover-message <tx_hash>     print the message to EIP-191 sign (no newline)
  recover <tx_hash> <sig> [issued_at]
                                re-issue a lost token after a settled payment

Env:
  X402SOCKS_TOKEN    proxy token (preferred over argv)
  X402SOCKS_TIMEOUT  per-request timeout in seconds (default 30)
EOF
}

cmd_health() {
  req "$WEB/api/health" | pretty
}

cmd_nodes() {
  local only=""
  [ "${1:-}" = "--available" ] && only="--available"
  req "$WEB/nodes.json" | python3 -c '
import sys, json
data = json.load(sys.stdin)["nodes"]
only = len(sys.argv) > 1 and sys.argv[1] == "--available"
shown = 0
for n in sorted(data, key=lambda x: x["id"]):
    if only and (n.get("disabled") or n.get("health") != "healthy"):
        continue
    print("%-15s %-38s :%s  %-8s %s" % (
        n["id"], n["hostname"], n["port"], n["health"], n.get("label", "")))
    shown += 1
print("(%d exits%s)" % (shown, ", usable only" if only else ""), file=sys.stderr)
' $only
}

cmd_catalog() {
  if [ "${1:-}" = "--summary" ]; then
    req "$WEB/catalog.json" | python3 -c '
import sys, json
d = json.load(sys.stdin)
for p in d["packages"]:
    print("%-14s $%-7s %-16s %s" % (
        p["id"], p["price_usd"], p["name"], "; ".join(p.get("entitlements", []))))
'
  else
    req "$WEB/catalog.json" | pretty
  fi
}

cmd_price() {
  [ $# -ge 1 ] || die "usage: price <package_id>"
  req "$WEB/catalog.json" | python3 -c '
import sys, json
want = sys.argv[1]
for p in json.load(sys.stdin)["packages"]:
    if p["id"] == want:
        print(json.dumps(p, indent=2))
        break
else:
    sys.exit("package not found: " + want)
' "$1"
}

cmd_status() {
  local token body
  token="$(resolve_token "${1:-}")"
  body="$(json_token_body "$token")"
  req -X POST "$WEB/api/token/status" \
      -H 'content-type: application/json' --data "$body" | pretty
}

cmd_validate() {
  local token body code
  token="$(resolve_token "${1:-}")"
  body="$(json_token_body "$token")"
  code="$(req -o /dev/null -w '%{http_code}' -X POST "$WEB/api/token/validate" \
          -H 'content-type: application/json' --data "$body")"
  if [ "$code" = "204" ]; then
    note "valid"
    return 0
  fi
  note "invalid (HTTP $code)"
  return 1
}

cmd_rotate() {
  local token
  token="$(resolve_token "${1:-}")"
  note "rotating: the old token stops working everywhere, immediately"
  req -X POST "$API/api/v1/token/rotate" -H "Authorization: Bearer $token" | pretty
}

cmd_test() {
  local exit_id token body code ip
  exit_id="${1:-us-central1}"
  token="$(resolve_token "${2:-}")"
  body="$(json_token_body "$token")"
  code="$(req -o /dev/null -w '%{http_code}' -X POST "$WEB/api/token/validate" \
          -H 'content-type: application/json' --data "$body")"
  [ "$code" = "204" ] || die "token invalid before test (HTTP $code)"
  ip="$(req --proxy "socks5h://${exit_id}.x402socks.com:1080" \
            --proxy-user "$token:$token" https://api.ipify.org)" \
       || die "egress failed via $exit_id"
  printf 'exit: %s\negress IP: %s\n' "$exit_id" "$ip"
  note "compare with your direct IP: curl -s https://api.ipify.org"
}

cmd_recover_message() {
  [ $# -ge 1 ] || die "usage: recover-message <tx_hash>"
  local tx issued_at
  tx="$1"
  issued_at="$(date +%s)"
  note "sign these exact bytes with EIP-191 personal_sign (no trailing newline):"
  printf 'x402socks credential recovery v1\ntx_hash: %s\nissued_at: %s' "$tx" "$issued_at"
  printf '\n\nissued_at: %s (valid +/-10 minutes)\n' "$issued_at" >&2
}

cmd_recover() {
  [ $# -ge 2 ] || die "usage: recover <tx_hash> <signature> [issued_at]"
  local tx sig issued_at body
  tx="$1"; sig="$2"; issued_at="${3:-$(date +%s)}"
  body="$(python3 -c 'import json,sys; print(json.dumps({"transaction": sys.argv[1], "signature": sys.argv[2], "issued_at": int(sys.argv[3])}))' "$tx" "$sig" "$issued_at")"
  req -X POST "$PAY/v1/access/recover" \
      -H 'content-type: application/json' --data "$body" | pretty
}

main() {
  need curl
  local cmd="${1:-help}"
  shift || true
  case "$cmd" in
    health)          cmd_health ;;
    nodes)           need python3; cmd_nodes "${1:-}" ;;
    catalog)         need python3; cmd_catalog "${1:-}" ;;
    price)           need python3; cmd_price "$@" ;;
    status)          need python3; cmd_status "${1:-}" ;;
    validate)        need python3; cmd_validate "${1:-}" ;;
    rotate)          cmd_rotate "${1:-}" ;;
    test)            need python3; cmd_test "${1:-}" "${2:-}" ;;
    recover-message) cmd_recover_message "$@" ;;
    recover)         need python3; cmd_recover "$@" ;;
    -h|--help|help)  usage ;;
    *)               usage; exit 2 ;;
  esac
}

main "$@"
