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

# Reject line breaks and other control characters before a value reaches a
# curl config. A newline would end the quoted value and start a new directive,
# which is how an environment token or URL could inject curl options.
reject_unsafe_text() {
  local name="$1" value="$2"
  case "$value" in
    *$'\r'*|*$'\n'*) die "$name must not contain a line break" ;;
  esac
  if printf '%s' "$value" | LC_ALL=C grep -q '[[:cntrl:]]'; then
    die "$name must not contain control characters"
  fi
}

# Endpoint overrides are parsed once, before any credential is read. Only a
# plain http(s) URL with a host and no embedded credentials is accepted; this
# also blocks quotes, backslashes, whitespace, and fragments that would make
# the quoted curl config ambiguous.
validate_endpoint_url() {
  local name="$1" url="$2"
  reject_unsafe_text "$name" "$url"
  python3 - "$name" "$url" <<'PY'
import sys
from urllib.parse import urlsplit

name, url = sys.argv[1], sys.argv[2]
if any(c.isspace() or c in '"\\' for c in url):
    sys.exit("%s must not contain whitespace, quotes, or backslashes" % name)
try:
    parts = urlsplit(url)
    host = parts.hostname
except ValueError as exc:
    sys.exit("%s is not a valid URL: %s" % (name, exc))
if parts.scheme not in ("https", "http"):
    sys.exit("%s must be an http(s) URL" % name)
if not host:
    sys.exit("%s must include a host" % name)
if parts.username is not None or parts.password is not None:
    sys.exit("%s must not embed credentials" % name)
if parts.fragment:
    sys.exit("%s must not include a fragment" % name)
PY
}

# A valid certificate proves which host answered, not that the host is allowed
# to receive a token. Credential-bearing commands only target x402socks hosts.
# A test override needs the explicit insecure opt-in.
require_trusted_host() {
  local name="$1" url="$2"
  python3 - "$name" "$url" <<'PY'
import sys
from urllib.parse import urlsplit
name, url = sys.argv[1], sys.argv[2]
host = (urlsplit(url).hostname or "").lower()
if host == "x402socks.com" or host.endswith(".x402socks.com"):
    raise SystemExit(0)
sys.exit(
    "%s host '%s' is not an x402socks host; set "
    "X402SOCKS_ALLOW_INSECURE_API=1 only for a trusted test" % (name, host)
)
PY
}

# Credential-bearing requests must target https://. A plaintext URL (for
# example a local test harness) is refused before the token or signature is
# read, unless the operator explicitly opts in for that trusted environment.
require_https() {
  local name="$1" url="$2"
  validate_endpoint_url "$name" "$url"
  case "$url" in
    https://*) ;;
    http://*)
      if [ "${X402SOCKS_ALLOW_INSECURE_API:-}" = "1" ]; then
        note "WARNING: $name is plaintext http ($url); credentials will be sent unencrypted"
        return 0
      fi
      die "$name must be an https:// URL (got '$url'); set X402SOCKS_ALLOW_INSECURE_API=1 only for a trusted local test"
      ;;
    *) die "$name must be an https:// URL (got '$url')" ;;
  esac
  if [ "${X402SOCKS_ALLOW_INSECURE_API:-}" = "1" ]; then
    note "WARNING: $name host override allowed by X402SOCKS_ALLOW_INSECURE_API=1"
    return 0
  fi
  require_trusted_host "$name" "$url"
}

need() { command -v "$1" >/dev/null 2>&1 || die "$1 is required"; }

req() { curl -q -sS --max-time "${X402SOCKS_TIMEOUT:-30}" "$@"; }

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

# Validate the replacement-token destination and reserve a private, writable
# staging file BEFORE a request that invalidates the old token. Rotation cannot
# be undone, so a bad token directory must abort before the API call.
TOKEN_STAGING=""
prepare_token_storage() {
  local file
  file="$(token_file)"
  TOKEN_STAGING="$(python3 -c '
import os, stat, sys, tempfile
path = os.path.abspath(sys.argv[1])
directory = os.path.dirname(path) or "."
try:
    os.makedirs(directory, mode=0o700, exist_ok=True)
except OSError as exc:
    sys.exit("token directory is not usable: %s" % exc)
if os.path.islink(directory) or not os.path.isdir(directory):
    sys.exit("token directory is not a real directory: %s" % directory)
st = os.stat(directory)
if st.st_uid != os.getuid() or (st.st_mode & 0o022):
    sys.exit("token directory is not private to the current user: %s" % directory)
if (st.st_mode & 0o777) != 0o700:
    sys.exit("token directory must already be mode 700: %s" % directory)
if os.path.lexists(path):
    pst = os.lstat(path)
    if not stat.S_ISREG(pst.st_mode):
        sys.exit("refusing to replace a non-regular token file: %s" % path)
    if pst.st_uid != os.getuid():
        sys.exit("token file is not owned by the current user: %s" % path)
    if pst.st_mode & 0o077:
        sys.exit("token file is accessible to group/other (mode %o): %s"
                 % (pst.st_mode & 0o777, path))
try:
    fd, staging = tempfile.mkstemp(prefix=".token.", dir=directory)
except OSError as exc:
    sys.exit("cannot reserve token storage in %s: %s" % (directory, exc))
os.close(fd)
os.chmod(staging, 0o600)
print(staging)
' "$file")"
}

# Escape a value for a double-quoted curl config entry. Line breaks and other
# control characters are refused instead of escaped: curl treats a newline as
# the end of a directive, so escaping it would still allow config injection.
cfg_escape() {
  case "$1" in
    *$'\r'*|*$'\n'*) die "refusing a curl config value that contains a line break" ;;
  esac
  if printf '%s' "$1" | LC_ALL=C grep -q '[[:cntrl:]]'; then
    die "refusing a curl config value that contains control characters"
  fi
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

# Tokens are opaque base64url (proxy-api) or hex (payment service) strings.
# Anything outside that alphabet is a mistake or an injection attempt, and a
# colon would corrupt the proxy-user credential pair.
validate_token() {
  local token="$1"
  case "$token" in
    "") die "empty token" ;;
    *[!A-Za-z0-9_-]*) die "token contains unsupported characters (expected base64url or hex)" ;;
  esac
  if [ "${#token}" -lt 8 ] || [ "${#token}" -gt 512 ]; then
    die "token length is out of range"
  fi
}

# Run one curl request whose options arrive on stdin. This keeps the token out
# of the process list; only the URL is passed as an argument. The transfer and
# every redirect are restricted to the URL's own scheme, so a credential request
# can never be silently downgraded to plaintext.
req_secret() {
  local url="$1"
  shift
  local cfg proto
  # Defense in depth: reject injection here even if a future caller forgets
  # require_https, because this is where the URL enters the curl config.
  reject_unsafe_text "credential URL" "$url"
  cfg="$(cat)"
  case "$url" in
    https://*) proto=(--proto '=https' --proto-redir '=https') ;;
    http://*)  proto=(--proto '=http,https' --proto-redir '=http,https') ;;
    *)         die "unsupported credential URL scheme: $url" ;;
  esac
  {
    printf '%s\n' "$cfg"
    printf 'url = "%s"\n' "$(cfg_escape "$url")"
  } | curl -q -sS --max-time "${X402SOCKS_TIMEOUT:-30}" "${proto[@]}" --config - "$@"
}

json_token_body() {
  python3 -c 'import json, sys; print(json.dumps({"token": sys.stdin.read()}))'
}

# Read a token only from a private regular file. A symlink, a group/world
# readable file, or a file owned by another user is refused before the bytes
# are used.
read_token_file() {
  python3 - "$1" <<'PY'
import os, sys
path = sys.argv[1]
try:
    st = os.lstat(path)
except OSError as exc:
    sys.exit("cannot read token file: %s" % exc)
if os.path.islink(path) or not os.path.isfile(path):
    sys.exit("token file is not a regular file: %s" % path)
if st.st_uid != os.getuid():
    sys.exit("token file is not owned by the current user: %s" % path)
if st.st_mode & 0o077:
    sys.exit("token file is accessible to group/other (mode %o): %s"
             % (st.st_mode & 0o777, path))
with open(path, "r", encoding="utf-8") as fh:
    sys.stdout.write(fh.read().replace("\r", "").replace("\n", ""))
PY
}

resolve_token() {
  local file token
  file="$(token_file)"
  if [ -e "$file" ] || [ -L "$file" ]; then
    token="$(read_token_file "$file")"
  elif [ "${X402SOCKS_TOKEN:-}" != "" ]; then
    token="$X402SOCKS_TOKEN"
  else
    die "no token: run 'save-token' after purchase, or export X402SOCKS_TOKEN"
  fi
  validate_token "$token"
  printf '%s' "$token"
}

# Persist a token returned by rotate/recover and print a redacted response.
# The parser uses `python3 -c` on purpose: a heredoc would replace stdin, so the
# piped response would read as empty and the replacement token would be lost.
store_token_response() {
  local file
  file="$(token_file)"
  mkdir -p "$(dirname "$file")"
  python3 -c '
import json, os, stat, sys, tempfile

path = os.path.abspath(sys.argv[1])
token_dir = os.path.dirname(path) or "."
staging = os.environ.get("X402SOCKS_TOKEN_STAGING") or None
raw = sys.stdin.read()

def drop_staging():
    if not staging:
        return
    try:
        # Only remove the reservation this helper created in the token
        # directory; never unlink an arbitrary path from the environment.
        if os.path.dirname(os.path.abspath(staging)) == token_dir:
            os.unlink(staging)
    except OSError:
        pass

try:
    data = json.loads(raw)
except json.JSONDecodeError:
    # Never echo the raw response: a truncated body can still contain the
    # replacement token. Print a fixed error instead.
    drop_staging()
    sys.exit("response was not valid JSON; nothing was saved")
if not isinstance(data, dict):
    drop_staging()
    sys.exit("unexpected response shape; nothing was saved")
token = data.get("token")
if not token:
    # Print field names only, never their values.
    drop_staging()
    sys.exit(
        "response did not include a token; nothing was saved (fields: %s)"
        % (", ".join(sorted(data.keys())) or "none")
    )
if not isinstance(token, str) or not (8 <= len(token) <= 512):
    drop_staging()
    sys.exit("response token is not a usable string; nothing was saved")
if any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-" for c in token):
    drop_staging()
    sys.exit("response token contains unsupported characters; nothing was saved")

directory = os.path.dirname(path) or "."
if os.path.islink(directory) or not os.path.isdir(directory):
    drop_staging()
    sys.exit("token directory is not a real directory: %s" % directory)
st = os.stat(directory)
if st.st_uid != os.getuid() or (st.st_mode & 0o022):
    drop_staging()
    sys.exit("token directory is not private to the current user: %s" % directory)
if (st.st_mode & 0o777) != 0o700:
    drop_staging()
    sys.exit("token directory must already be mode 700: %s" % directory)
if os.path.lexists(path):
    pst = os.lstat(path)
    if not stat.S_ISREG(pst.st_mode):
        drop_staging()
        sys.exit("refusing to replace a non-regular token file: %s" % path)
    if pst.st_uid != os.getuid():
        drop_staging()
        sys.exit("token file is not owned by the current user: %s" % path)
    if pst.st_mode & 0o077:
        drop_staging()
        sys.exit("token file is accessible to group/other (mode %o): %s"
                 % (pst.st_mode & 0o777, path))

if staging:
    staging = os.path.abspath(staging)
    if os.path.dirname(staging) != directory or os.path.islink(staging):
        drop_staging()
        sys.exit("invalid token staging path")
    sst = os.stat(staging)
    if sst.st_uid != os.getuid() or (sst.st_mode & 0o077):
        drop_staging()
        sys.exit("token staging file is not private: %s" % staging)
    try:
        with open(staging, "w") as fh:
            fh.write(token)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(staging, path)
    except OSError as exc:
        # The old token is already invalid. Keep the replacement in the
        # private staging file instead of discarding the only copy.
        sys.exit(
            "replacement token saved to %s (mode 600); move it to %s (%s)"
            % (staging, path, exc)
        )
else:
    # mkstemp creates the file 0600. Write and fsync it, then atomically replace
    # the destination, so a symlink or a concurrent reader cannot see a partial
    # token or redirect the write.
    fd, tmp = tempfile.mkstemp(prefix=".token.", dir=directory)
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(token)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        tmp = None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass

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
  test [exit_id]                confirm egress IP; TLS CONNECT 3129 only
  recover-message <tx_hash>     print the message to EIP-191 sign (no newline)
  recover <tx_hash> <issued_at> re-issue a lost token; signature on stdin
                                (pass the issued_at from recover-message)

Token source (never argv):
  X402SOCKS_TOKEN_FILE  token file (default ~/.config/x402socks/token, mode 600)
  X402SOCKS_TOKEN       environment variable fallback
  Run 'save-token' once to create the file.

Budget guard:
  X402SOCKS_MAX_USDC    approved maximum in USD; 'quote' fails above it
  X402SOCKS_TIMEOUT     per-request timeout in seconds (default 30)

Endpoint overrides (advanced):
  X402SOCKS_WEB / X402SOCKS_API / X402SOCKS_PAY
                        must be https:// x402socks hosts; credential-bearing
                        commands refuse any other host before reading the token
  X402SOCKS_ALLOW_INSECURE_API=1
                        override the host and scheme checks for a trusted test
                        only

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
  local token body
  token="$(tr -d '\r\n')"
  [ -n "$token" ] || die "no token on stdin"
  validate_token "$token"
  # Reserve a private staging file here instead of inheriting an environment
  # path, then reuse the hardened writer used by rotate/recover.
  prepare_token_storage
  export X402SOCKS_TOKEN_STAGING="$TOKEN_STAGING"
  body="$(printf '%s' "$token" | json_token_body)"
  printf '%s' "$body" | store_token_response
  unset X402SOCKS_TOKEN_STAGING
}

cmd_status() {
  local token body cfg
  require_https "X402SOCKS_WEB" "$WEB"
  token="$(resolve_token)"
  body="$(printf '%s' "$token" | json_token_body)"
  cfg="$(printf 'header = "content-type: application/json"\ndata = "%s"' "$(cfg_escape "$body")")"
  printf '%s' "$cfg" | req_secret "$WEB/api/token/status" -X POST | pretty
}

cmd_validate() {
  local token body cfg code
  require_https "X402SOCKS_WEB" "$WEB"
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
  require_https "X402SOCKS_API" "$API"
  token="$(resolve_token)"
  # Rotation invalidates the old token immediately. Reserve private, writable
  # storage first so a bad token directory cannot cost the replacement token.
  prepare_token_storage
  export X402SOCKS_TOKEN_STAGING="$TOKEN_STAGING"
  note "rotating: the old token stops working everywhere, immediately"
  cfg="$(printf 'header = "Authorization: Bearer %s"' "$(cfg_escape "$token")")"
  printf '%s' "$cfg" | req_secret "$API/api/v1/token/rotate" -X POST | store_token_response
  unset X402SOCKS_TOKEN_STAGING
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

# TLS HTTP CONNECT is the only transport this helper uses: curl verifies the
# exit certificate and the token is never sent in cleartext. SOCKS5 and
# plaintext CONNECT are legacy browser transports; the helper does not offer
# them.
cmd_test() {
  local exit_id="eu-north1" have_exit=0 token body cfg code ip direct proxy
  while [ $# -gt 0 ]; do
    case "$1" in
      --tls) ;;
      --)    shift; break ;;
      -*)    die "unknown option: $1" ;;
      *)
        [ "$have_exit" -eq 0 ] || die "only one exit id may be given"
        exit_id="$1"
        have_exit=1
        ;;
    esac
    shift
  done
  [ $# -eq 0 ] || die "unexpected argument: $1"

  require_https "X402SOCKS_WEB" "$WEB"
  check_exit_id "$exit_id"
  proxy="https://$exit_id.x402socks.com:3129"

  token="$(resolve_token)"
  body="$(printf '%s' "$token" | json_token_body)"
  cfg="$(printf 'header = "content-type: application/json"\ndata = "%s"' "$(cfg_escape "$body")")"
  code="$(printf '%s' "$cfg" | req_secret "$WEB/api/token/validate" \
          -o /dev/null -w '%{http_code}')"
  [ "$code" = "204" ] || die "token invalid before test (HTTP $code)"

  # Ignore ambient curl config and any NO_PROXY list so the comparison is real:
  # the direct baseline must not use the proxy, and the proxied request must.
  direct="$(curl -q -sS --max-time "${X402SOCKS_TIMEOUT:-30}" --noproxy '*' https://api.ipify.org)" \
    || die "direct egress baseline failed"
  [ -n "$direct" ] || die "direct egress baseline was empty"

  cfg="$(printf 'proxy = "%s"\nproxy-user = "%s:%s"' \
        "$(cfg_escape "$proxy")" "$(cfg_escape "$token")" "$(cfg_escape "$token")")"
  ip="$(printf '%s' "$cfg" | req_secret https://api.ipify.org --noproxy '')" \
       || die "egress failed via $exit_id (tls)"
  [ -n "$ip" ] || die "egress IP was empty"
  [ "$ip" != "$direct" ] || die "egress IP did not change ($ip); the proxy was bypassed"

  printf 'exit: %s\ntransport: tls\ndirect IP: %s\negress IP: %s\n' \
    "$exit_id" "$direct" "$ip"
}

cmd_recover_message() {
  [ $# -ge 1 ] || die "usage: recover-message <tx_hash>"
  local tx issued_at
  tx="$1"
  issued_at="$(date +%s)"
  note "sign these exact bytes with EIP-191 personal_sign (no trailing newline):"
  printf 'x402socks credential recovery v1\ntx_hash: %s\nissued_at: %s' "$tx" "$issued_at"
  printf '\n\nissued_at: %s (valid +/-10 minutes)\n' "$issued_at" >&2
  printf 'pass the same issued_at to: recover %s %s\n' "$tx" "$issued_at" >&2
}

cmd_recover() {
  [ $# -ge 2 ] || die "usage: recover <tx_hash> <issued_at> (signature on stdin)"
  local tx sig issued_at body cfg
  require_https "X402SOCKS_PAY" "$PAY"
  tx="$1"; issued_at="$2"
  IFS= read -r sig || die "no signature on stdin"
  [ -n "$sig" ] || die "empty signature on stdin"
  # The signature is an ownership proof and must not reach a process list.
  # Pass it to the JSON builder on stdin; only the public tx hash and timestamp
  # are argv.
  body="$(
    printf '%s\n%s\n%s\n' "$tx" "$sig" "$issued_at" |
      python3 -c 'import json, sys
lines = sys.stdin.read().splitlines()
tx, sig, issued_at = lines[0], lines[1], int(lines[2])
print(json.dumps({"transaction": tx, "signature": sig, "issued_at": issued_at}))'
  )"
  cfg="$(printf 'header = "content-type: application/json"\ndata = "%s"' "$(cfg_escape "$body")")"
  # Recovery is safe to retry, but still reserve storage before the request so
  # a bad directory does not discard the replacement token.
  prepare_token_storage
  export X402SOCKS_TOKEN_STAGING="$TOKEN_STAGING"
  printf '%s' "$cfg" | req_secret "$PAY/v1/access/recover" -X POST | store_token_response
  unset X402SOCKS_TOKEN_STAGING
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
