#!/usr/bin/env bash
set -euo pipefail

readonly EVALUATOR_USER=packeval
readonly IPV4_CHAIN=PACK_EVALUATOR_EGRESS
readonly IPV6_CHAIN=PACK_EVALUATOR_EGRESS
readonly IPV4_GUARD_CHAIN=PACK_EVALUATOR_GUARD
readonly IPV6_GUARD_CHAIN=PACK_EVALUATOR_GUARD
readonly PROXY_ADDRESS=127.0.0.1
readonly PROXY_PORT=18765

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo 'Pack evaluator egress configuration must run as root' >&2
  exit 1
fi

for command_name in getent iptables ip6tables; do
  command -v "$command_name" >/dev/null
done

readonly EVALUATOR_UID="$(id -u "$EVALUATOR_USER")"
test "$EVALUATOR_UID" -gt 0

remove_output_jumps() {
  local tool="$1"
  local chain="$2"
  while "$tool" -w 5 -C OUTPUT \
    -m owner --uid-owner "$EVALUATOR_UID" -j "$chain" 2>/dev/null; do
    "$tool" -w 5 -D OUTPUT \
      -m owner --uid-owner "$EVALUATOR_UID" -j "$chain"
  done
}

prepare_guard() {
  local tool="$1"
  local chain="$2"
  shift 2
  if "$tool" -w 5 -S "$chain" >/dev/null 2>&1; then
    local rule_count
    rule_count=$("$tool" -w 5 -S "$chain" | awk '$1 == "-A" {count += 1} END {print count + 0}')
    test "$rule_count" -eq 1
    "$tool" -w 5 -C "$chain" "$@"
  else
    "$tool" -w 5 -N "$chain"
    "$tool" -w 5 -A "$chain" "$@"
  fi
  "$tool" -w 5 -I OUTPUT 1 \
    -m owner --uid-owner "$EVALUATOR_UID" -j "$chain"
}

finish_guard() {
  local tool="$1"
  local chain="$2"
  remove_output_jumps "$tool" "$chain"
  "$tool" -w 5 -F "$chain"
  "$tool" -w 5 -X "$chain"
}

# Install fail-closed guards before touching either referenced policy chain.
# If this script is interrupted, a guard remains and blocks packeval egress.
prepare_guard iptables "$IPV4_GUARD_CHAIN" \
  -j REJECT --reject-with icmp-admin-prohibited
prepare_guard ip6tables "$IPV6_GUARD_CHAIN" \
  -j REJECT --reject-with icmp6-adm-prohibited

iptables -w 5 -N "$IPV4_CHAIN" 2>/dev/null || true
iptables -w 5 -F "$IPV4_CHAIN"
iptables -w 5 -A "$IPV4_CHAIN" \
  -p tcp -d "$PROXY_ADDRESS/32" --dport "$PROXY_PORT" -j ACCEPT
iptables -w 5 -A "$IPV4_CHAIN" -j REJECT --reject-with icmp-admin-prohibited
remove_output_jumps iptables "$IPV4_CHAIN"
iptables -w 5 -I OUTPUT 1 \
  -m owner --uid-owner "$EVALUATOR_UID" -j "$IPV4_CHAIN"

ip6tables -w 5 -N "$IPV6_CHAIN" 2>/dev/null || true
ip6tables -w 5 -F "$IPV6_CHAIN"
ip6tables -w 5 -A "$IPV6_CHAIN" -j REJECT --reject-with icmp6-adm-prohibited
remove_output_jumps ip6tables "$IPV6_CHAIN"
ip6tables -w 5 -I OUTPUT 1 \
  -m owner --uid-owner "$EVALUATOR_UID" -j "$IPV6_CHAIN"

iptables -w 5 -C "$IPV4_CHAIN" \
  -p tcp -d "$PROXY_ADDRESS/32" --dport "$PROXY_PORT" -j ACCEPT
iptables -w 5 -C "$IPV4_CHAIN" -j REJECT --reject-with icmp-admin-prohibited
ip6tables -w 5 -C "$IPV6_CHAIN" -j REJECT --reject-with icmp6-adm-prohibited

finish_guard iptables "$IPV4_GUARD_CHAIN"
finish_guard ip6tables "$IPV6_GUARD_CHAIN"

echo "Pack evaluator egress restricted to ${PROXY_ADDRESS}:${PROXY_PORT}"
