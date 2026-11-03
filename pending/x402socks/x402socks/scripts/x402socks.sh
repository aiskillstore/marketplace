#!/usr/bin/env bash
# x402socks helper: health, catalog, nodes, quote, token status/validation/rotation,
# recovery, and egress test.
#
# Secrets never appear in argv: the token is read from a 0600 file (or the
# environment) and every token-bearing request passes curl options on stdin.
# Rotation and recovery save the replacement token instead of printing it.
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

token_file() {
  printf '%s' "${X402SOCKS_TOKEN_FILE:-${XDG_CONFIG_HOME:-$HOME/.config}/x402socks/token}"
}

# Escape a value for a double-quoted curl config entry.
cfg_escape() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }

# Run one curl request whose options arrive on stdin. This keeps the token out
# of the process list; only the URL is passed as an argument.
req_secret() {
  local url="$1"
  shift
  local cfg
  cfg="$(cat)"
  {
    printf '%s\n' "$cfg"
    printf 'url = "%s"\n' "$(cfg_escape "$url")"
  } | curl -sS --max-time "${X402SOCKS_TIMEOUT:-30}" --config - "$@"
}

json_token_body() {
  python3 -c 'import json, sys; print(json.dumps({"token": sys.stdin.read()}))'
}

resolve_token() {
  local file
  file="$(token_file)"
  if [ -s "$file" ]; then
    tr -d '\r\n' < "$file"
  elif [ "${X402SOCKS_TOKEN:-}" != "" ]; then
    printf '%s' "$X402SOCKS_TOKEN"
  else
    die "no token: run 'save-token' after purchase, or export X402SOCKS_TOKEN"
  fi
}

# Persist a token returned by rotate/recover and print a redacted response.
# The parser uses `python3 -c` on purpose: a heredoc would replace stdin, so the
# piped response would read as empty and the replacement token would be lost.
store_token_response() {
  local file
  file="$(token_file)"
  mkdir -p "$(dirname "$file")"
  chmod 700 "$(dirname "$file")" 2>/dev/null || true
  python3 -c '
import json, os, sys

path = sys.argv[1]
raw = sys.stdin.read()
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    sys.stdout.write(raw)
    sys.stderr.write("\nno token in response; nothing was saved\n")
    sys.exit(1)
token = data.get("token")
if not token:
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    sys.exit("response did not include a token; nothing was saved")

fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as fh:
    fh.write(token)
os.chmod(path, 0o600)

data["token"] = "<redacted: saved to %s (mode 600)>" % path
json.dump(data, sys.stdout, indent=2)
sys.stdout.write("\n")
' "$file"
}

usage() {
  cat <<'EOF'
x402socks helper

  health                        service liveness
  nodes [--available]           exit points, optionally only usable ones
  catalog [--summary]           package catalog with prices
  price <package_id>            one package's price and entitlements
  quote <package_id>            live 402 amount; enforces X402SOCKS_MAX_USDC
  save-token                    read a token from stdin and store it (mode 600)
  status                        account status and usage
  validate                      cheap token check (exit 0 = valid)
  rotate                        rotate token; saves the new one, prints no secret
  test [--tls|--plaintext|--socks5] [exit_id]
                                confirm egress IP; TLS CONNECT 3129 by default
  recover-message <tx_hash>     print the message to EIP-191 sign (no newline)
  recover <tx_hash> <sig> [issued_at]
                                re-issue a lost token after a settled payment

Token source (never argv):
  X402SOCKS_TOKEN_FILE  token file (default ~/.config/x402socks/token, mode 600)
  X402SOCKS_TOKEN       environment variable fallback
  Run 'save-token' once to create the file.

Budget guard:
  X402SOCKS_MAX_USDC    approved maximum in USD; 'quote' fails above it
  X402SOCKS_TIMEOUT     per-request timeout in seconds (default 30)

Plaintext transports (opt-in):
  X402SOCKS_ALLOW_PLAINTEXT=1   required for SOCKS5 1080 and plaintext CONNECT 3128
                                both send the reusable token unencrypted
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

# Print the live 402 amount and fail if it exceeds the approved cap. The
# challenge, not the catalog, is what a payment would actually authorize.
# Every accepts[] option is checked: a client may select any of them.
cmd_quote() {
  local pkg="${1:-}" cap="${X402SOCKS_MAX_USDC:-}" hdr decoded
  [ -n "$pkg" ] || die "usage: quote <package_id>"

  hdr="$(req -D - -o /dev/null -X POST "$PAY/v1/access/$pkg" \
        -H 'content-type: application/json' -d '{}' \
        | tr -d '\r' | awk 'tolower($1) == "payment-required:" { print $2; exit }')"
  [ -n "$hdr" ] || die "no PAYMENT-REQUIRED header for '$pkg'"

  decoded="$(printf '%s' "$hdr" | python3 -c '
import base64, json, sys
raw = sys.stdin.read().strip()
raw += "=" * (-len(raw) % 4)
try:
    data = json.loads(base64.urlsafe_b64decode(raw))
except Exception:
    data = json.loads(base64.b64decode(raw))
options = data.get("accepts") or []
if not options:
    sys.exit("402 has no accepts[] options")
rows = [{
    "scheme": a.get("scheme"),
    "network": a.get("network"),
    "amount_atomic": a.get("amount"),
    "amount_usd": int(a["amount"]) / 10**6,
    "asset": a.get("asset"),
    "pay_to": a.get("payTo"),
    "asset_name": (a.get("extra") or {}).get("name"),
    "asset_version": (a.get("extra") or {}).get("version"),
    "max_timeout_seconds": a.get("maxTimeoutSeconds"),
} for a in options]
out = {"package": sys.argv[1]}
if len(rows) == 1:
    out.update(rows[0])
else:
    out["options"] = rows
print(json.dumps(out, indent=2))
' "$pkg")"

  printf '%s\n' "$decoded"

  if [ -n "$cap" ]; then
    printf '%s' "$decoded" | python3 -c '
import json, sys
cap = float(sys.argv[1])
data = json.load(sys.stdin)
rows = data.get("options") or [data]
over = [r for r in rows if r["amount_usd"] > cap]
if over:
    sys.exit("approved cap is $%.2f but an option asks $%.2f"
             % (cap, max(r["amount_usd"] for r in over)))
print("within approved cap ($%.2f; %d option%s)"
      % (cap, len(rows), "" if len(rows) == 1 else "s"))
' "$cap"
  else
    note "no X402SOCKS_MAX_USDC set; re-check every amount above before approving"
  fi
}

cmd_save_token() {
  local file token
  file="$(token_file)"
  mkdir -p "$(dirname "$file")"
  chmod 700 "$(dirname "$file")" 2>/dev/null || true
  token="$(tr -d '\r\n')"
  [ -n "$token" ] || die "no token on stdin"
  ( umask 077; printf '%s' "$token" > "$file" )
  chmod 600 "$file"
  printf 'saved token to %s (mode 600)\n' "$file"
}

cmd_status() {
  local token body cfg
  token="$(resolve_token)"
  body="$(printf '%s' "$token" | json_token_body)"
  cfg="$(printf 'header = "content-type: application/json"\ndata = "%s"' "$(cfg_escape "$body")")"
  printf '%s' "$cfg" | req_secret "$WEB/api/token/status" -X POST | pretty
}

cmd_validate() {
  local token body cfg code
  token="$(resolve_token)"
  body="$(printf '%s' "$token" | json_token_body)"
  cfg="$(printf 'header = "content-type: application/json"\ndata = "%s"' "$(cfg_escape "$body")")"
  code="$(printf '%s' "$cfg" | req_secret "$WEB/api/token/validate" \
          -X POST -o /dev/null -w '%{http_code}')"
  if [ "$code" = "204" ]; then
    note "valid"
    return 0
  fi
  note "invalid (HTTP $code)"
  return 1
}

cmd_rotate() {
  local token cfg
  token="$(resolve_token)"
  note "rotating: the old token stops working everywhere, immediately"
  cfg="$(printf 'header = "Authorization: Bearer %s"' "$(cfg_escape "$token")")"
  printf '%s' "$cfg" | req_secret "$API/api/v1/token/rotate" -X POST | store_token_response
}

# Exit ids are lowercase DNS labels. Reject anything that could add a curl
# config line, then confirm the id is present and usable in the live feed.
valid_exit_id() {
  case "$1" in
    ""|*[!a-z0-9-]*|-*|*-) return 1 ;;
  esac
  [ "${#1}" -le 63 ]
}

check_exit_id() {
  local want="$1"
  valid_exit_id "$want" || die "invalid exit id '$want' (lowercase letters, digits, hyphen only)"
  req "$WEB/nodes.json" | python3 -c '
import json, sys

want = sys.argv[1]
for node in json.load(sys.stdin).get("nodes", []):
    if node.get("id") == want:
        if node.get("disabled") or node.get("health") != "healthy":
            sys.exit("exit %s is not usable (health=%s disabled=%s)"
                     % (want, node.get("health"), node.get("disabled")))
        sys.exit(0)
sys.exit("unknown exit id %s; re-read /nodes.json" % want)
' "$want"
}

# TLS HTTP CONNECT is the default: curl verifies the exit certificate and the
# token is not sent in cleartext. SOCKS5 (1080) and plaintext CONNECT (3128)
# are opt-in because both expose the reusable token on the client-to-exit hop.
cmd_test() {
  local mode="tls" exit_id="eu-north1" have_exit=0 token body cfg code ip proxy
  while [ $# -gt 0 ]; do
    case "$1" in
      --tls)       mode="tls" ;;
      --plaintext) mode="plaintext" ;;
      --socks5)    mode="socks5" ;;
      --)          shift; break ;;
      -*)          die "unknown option: $1" ;;
      *)
        [ "$have_exit" -eq 0 ] || die "only one exit id may be given"
        exit_id="$1"
        have_exit=1
        ;;
    esac
    shift
  done
  [ $# -eq 0 ] || die "unexpected argument: $1"

  check_exit_id "$exit_id"

  case "$mode" in
    tls)
      proxy="https://$exit_id.x402socks.com:3129"
      ;;
    plaintext|socks5)
      [ "${X402SOCKS_ALLOW_PLAINTEXT:-}" = "1" ] || \
        die "$mode sends the reusable token unencrypted; set X402SOCKS_ALLOW_PLAINTEXT=1 to opt in"
      if [ "$mode" = "plaintext" ]; then
        proxy="http://$exit_id.x402socks.com:3128"
      else
        proxy="socks5h://$exit_id.x402socks.com:1080"
      fi
      note "WARNING: $mode authentication is plaintext on the client-to-exit hop"
      ;;
  esac

  token="$(resolve_token)"
  body="$(printf '%s' "$token" | json_token_body)"
  cfg="$(printf 'header = "content-type: application/json"\ndata = "%s"' "$(cfg_escape "$body")")"
  code="$(printf '%s' "$cfg" | req_secret "$WEB/api/token/validate" \
          -o /dev/null -w '%{http_code}')"
  [ "$code" = "204" ] || die "token invalid before test (HTTP $code)"
  cfg="$(printf 'proxy = "%s"\nproxy-user = "%s:%s"' \
        "$(cfg_escape "$proxy")" "$(cfg_escape "$token")" "$(cfg_escape "$token")")"
  ip="$(printf '%s' "$cfg" | req_secret https://api.ipify.org)" \
       || die "egress failed via $exit_id ($mode)"
  printf 'exit: %s\ntransport: %s\negress IP: %s\n' "$exit_id" "$mode" "$ip"
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
  local tx sig issued_at body cfg
  tx="$1"; sig="$2"; issued_at="${3:-$(date +%s)}"
  body="$(python3 -c 'import json, sys; print(json.dumps({"transaction": sys.argv[1], "signature": sys.argv[2], "issued_at": int(sys.argv[3])}))' "$tx" "$sig" "$issued_at")"
  cfg="$(printf 'header = "content-type: application/json"\ndata = "%s"' "$(cfg_escape "$body")")"
  printf '%s' "$cfg" | req_secret "$PAY/v1/access/recover" -X POST | store_token_response
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
    quote)           need python3; cmd_quote "${1:-}" ;;
    save-token)      cmd_save_token ;;
    status)          need python3; cmd_status ;;
    validate)        need python3; cmd_validate ;;
    rotate)          need python3; cmd_rotate ;;
    test)            need python3; cmd_test "$@" ;;
    recover-message) cmd_recover_message "$@" ;;
    recover)         need python3; cmd_recover "$@" ;;
    -h|--help|help)  usage ;;
    *)               usage; exit 2 ;;
  esac
}

main "$@"
