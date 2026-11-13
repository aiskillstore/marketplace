#!/bin/sh
# Check the public DNS records that decide whether a sending domain's mail is
# accepted: MX, SPF, DMARC and DKIM. Read-only; it only queries public DNS.
#
# Usage: sh check-sending-domain.sh <domain> [dkim-selector ...]
#   Without selectors it tries a few common ones. DKIM selectors cannot be
#   listed from DNS, so "not found" for guessed selectors proves nothing: take
#   the real one from the s= tag of the DKIM-Signature header on a sent message.

set -u

if [ $# -lt 1 ]; then
  echo "usage: sh check-sending-domain.sh <domain> [dkim-selector ...]" >&2
  exit 2
fi

domain=$(printf '%s' "$1" | tr 'A-Z' 'a-z' | sed 's/^https*:\/\///; s/\/.*$//; s/^www\.//; s/\.$//')
shift

if command -v dig >/dev/null 2>&1; then
  txt() { dig +short +time=3 +tries=2 TXT "$1" 2>/dev/null | sed 's/" "//g; s/^"//; s/"$//'; }
  mx() { dig +short +time=3 +tries=2 MX "$1" 2>/dev/null; }
  cname() { dig +short +time=3 +tries=2 CNAME "$1" 2>/dev/null; }
elif command -v host >/dev/null 2>&1; then
  txt() { host -t TXT "$1" 2>/dev/null | grep 'descriptive text' | sed 's/.*descriptive text //; s/" "//g; s/^"//; s/"$//'; }
  mx() { host -t MX "$1" 2>/dev/null | grep 'mail is handled' | sed 's/.*handled by //'; }
  cname() { host -t CNAME "$1" 2>/dev/null | grep 'alias for' | sed 's/.*alias for //'; }
else
  echo "needs dig or host on PATH" >&2
  exit 2
fi

fails=0
warns=0
fail() { echo "FAIL  $*"; fails=$((fails + 1)); }
warn() { echo "WARN  $*"; warns=$((warns + 1)); }
pass() { echo "PASS  $*"; }
info() { echo "INFO  $*"; }

echo "Sending domain: $domain"
echo

# MX: a domain that cannot receive mail cannot receive replies or bounces.
mxs=$(mx "$domain")
if [ -n "$mxs" ]; then
  pass "MX: $(printf '%s' "$mxs" | tr '\n' ' ')"
else
  fail "MX: no MX record; replies and bounces to this domain will not arrive"
fi

# SPF: exactly one v=spf1 TXT record at the domain itself.
spf=$(txt "$domain" | grep -i '^v=spf1')
spf_count=$(printf '%s\n' "$spf" | grep -ci '^v=spf1')
if [ -z "$spf" ]; then
  fail "SPF: no v=spf1 record"
elif [ "$spf_count" -gt 1 ]; then
  fail "SPF: $spf_count v=spf1 records; more than one is a permanent error (RFC 7208 4.5). Merge them."
else
  pass "SPF: $spf"
  case "$spf" in
    *"+all"*) fail "SPF: +all authorises every server on the internet" ;;
    *"?all"*) warn "SPF: ?all is neutral; use ~all or -all" ;;
    *"-all"* | *"~all"*) : ;;
    *"redirect="*) info "SPF: policy comes from a redirect= target" ;;
    *) warn "SPF: no all mechanism at the end" ;;
  esac
  terms=$(printf '%s' "$spf" | tr ' ' '\n' | grep -ciE '^[+~?-]?(include:|a$|a:|a/|mx$|mx:|mx/|ptr|exists:|redirect=)')
  if [ "$terms" -gt 10 ]; then
    fail "SPF: $terms DNS-lookup terms at the top level alone; the limit is 10 (RFC 7208 4.6.4)"
  else
    info "SPF: $terms DNS-lookup terms at the top level (limit 10 including nested includes, which this script does not expand)"
  fi
fi

# DMARC: at _dmarc.<domain>; if absent, receivers look up the organisational
# domain. This walks up one label at a time, which is close to but not exactly
# the RFC 9989 tree walk.
dmarc=""
lookup="$domain"
while :; do
  rec=$(txt "_dmarc.$lookup" | grep -i '^v=DMARC1')
  if [ -n "$rec" ]; then dmarc="$rec"; break; fi
  case "$lookup" in
    *.*.*) lookup=${lookup#*.} ;;
    *) break ;;
  esac
done
if [ -z "$dmarc" ]; then
  fail "DMARC: no v=DMARC1 record at _dmarc.$domain or a parent domain"
else
  if [ "$lookup" = "$domain" ]; then
    pass "DMARC: $dmarc"
  else
    pass "DMARC (inherited from _dmarc.$lookup): $dmarc"
  fi
  pol=$(printf '%s' "$dmarc" | tr ';' '\n' | sed 's/ //g' | grep -i '^p=' | head -1 | cut -d= -f2)
  if [ "$lookup" != "$domain" ]; then
    # A subdomain gets the parent's sp= policy when one is set.
    sp=$(printf '%s' "$dmarc" | tr ';' '\n' | sed 's/ //g' | grep -i '^sp=' | head -1 | cut -d= -f2)
    [ -n "$sp" ] && pol="$sp"
  fi
  case "$pol" in
    none) info "DMARC: p=none meets the Gmail/Yahoo bulk minimum; it protects nothing until you move to quarantine or reject" ;;
    quarantine | reject) pass "DMARC: enforcing policy p=$pol" ;;
    *) fail "DMARC: missing or invalid p= tag" ;;
  esac
  printf '%s' "$dmarc" | grep -qi 'rua=' || warn "DMARC: no rua= reporting address, so you will not see who sends as this domain"
fi

# DKIM: only checkable per selector.
if [ $# -eq 0 ]; then
  set -- google selector1 selector2 default k1 s1 s2 dkim mail
  guessed=1
else
  guessed=0
fi
found=0
for sel in "$@"; do
  name="$sel._domainkey.$domain"
  rec=$(txt "$name" | grep -i 'p=')
  alias=$(cname "$name")
  if [ -n "$rec" ]; then
    case "$rec" in
      *"p=;"* | *"p=") [ "$guessed" -eq 0 ] && warn "DKIM $sel: key is empty (revoked)" ;;
      *) pass "DKIM $sel: key published"; found=1 ;;
    esac
  elif [ -n "$alias" ]; then
    pass "DKIM $sel: CNAME to $alias (provider-hosted key)"; found=1
  elif [ "$guessed" -eq 0 ]; then
    fail "DKIM $sel: no key at $name"
  fi
done
if [ "$found" -eq 0 ] && [ "$guessed" -eq 1 ]; then
  warn "DKIM: none of the common selectors answered. Send yourself a message and read s= in its DKIM-Signature header, then rerun with that selector."
fi

echo
echo "Result: $fails fail, $warns warn"
echo "DNS shows what is published, not what passes. Confirm on a real sent message: Gmail > Show original lists SPF, DKIM and DMARC as PASS or FAIL."
[ "$fails" -eq 0 ]
