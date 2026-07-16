#!/usr/bin/env bash
set -Eeuo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin

readonly BWRAP=/usr/bin/bwrap
readonly APPARMOR_PARSER=/usr/sbin/apparmor_parser
readonly APPARMOR_PROFILES=/sys/kernel/security/apparmor/profiles
readonly PROFILE_NAME=pack-production-bwrap
readonly PROFILE_TARGET=/etc/apparmor.d/pack-production-bwrap
readonly EVALUATOR_USER=packeval
readonly EVALUATOR_HOME=/home/packeval
readonly EVALUATOR_TMP=/home/packeval/tmp
readonly RUNTIME_ROOT=/opt/pack-evaluator/runtime
readonly CODEX_HOME=/opt/pack-evaluator/codex-home
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly PROFILE_SOURCE="$SCRIPT_DIR/pack-evaluator-bwrap.apparmor"

: "${PACK_EVALUATOR_OUTER_WORKSPACE:?PACK_EVALUATOR_OUTER_WORKSPACE is required}"

diagnose_failure() {
  local exit_code=$?
  trap - ERR
  echo '::error::Pack evaluator bubblewrap/AppArmor preflight failed' >&2
  /usr/sbin/sysctl \
    kernel.apparmor_restrict_unprivileged_userns \
    kernel.apparmor_restrict_unprivileged_unconfined \
    user.max_user_namespaces 2>/dev/null >&2 || true
  /usr/bin/dmesg 2>/dev/null \
    | /usr/bin/grep -Ei 'apparmor="DENIED"|userns|uid_map' \
    | /usr/bin/tail -50 >&2 || true
  exit "$exit_code"
}
trap diagnose_failure ERR

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo 'Pack evaluator bubblewrap configuration must run as root' >&2
  exit 1
fi

# Pin the kernel/security contract alongside the workflow's Ubuntu image.
source /etc/os-release
test "${ID:-}:${VERSION_ID:-}" = 'ubuntu:24.04'
test "$(cat /sys/module/apparmor/parameters/enabled)" = 'Y'
test -x "$APPARMOR_PARSER"
test -r "$APPARMOR_PROFILES"
test -x "$BWRAP"
test "$("$BWRAP" --version)" = 'bubblewrap 0.9.0'
test "$(stat -c '%U:%G' "$BWRAP")" = 'root:root'
test -r "$PROFILE_SOURCE"
test "$(stat -c '%U:%G' "$PROFILE_SOURCE")" = 'root:root'
test "$(stat -c '%U:%G' "${BASH_SOURCE[0]}")" = 'root:root'
test -d "$PACK_EVALUATOR_OUTER_WORKSPACE"
test "${PACK_EVALUATOR_OUTER_WORKSPACE#/}" != "$PACK_EVALUATOR_OUTER_WORKSPACE"
id "$EVALUATOR_USER" >/dev/null
if runuser -u "$EVALUATOR_USER" -- test -w "$BWRAP"; then
  echo 'Evaluator user can modify the bubblewrap executable' >&2
  exit 1
fi
if runuser -u "$EVALUATOR_USER" -- test -w "$PROFILE_SOURCE"; then
  echo 'Evaluator user can modify the AppArmor profile source' >&2
  exit 1
fi
if runuser -u "$EVALUATOR_USER" -- test -w "${BASH_SOURCE[0]}"; then
  echo 'Evaluator user can modify the root helper' >&2
  exit 1
fi
test -d "$EVALUATOR_HOME"
test -d "$EVALUATOR_TMP"
test -x "$RUNTIME_ROOT/bin/node"
test -d "$CODEX_HOME"

readonly RESTRICTED_USERNS_BEFORE="$(sysctl -n kernel.apparmor_restrict_unprivileged_userns)"
readonly MAX_USER_NAMESPACES="$(sysctl -n user.max_user_namespaces)"
test "$RESTRICTED_USERNS_BEFORE" = '1'
test "$MAX_USER_NAMESPACES" -gt 0

# This is the path-scoped mitigation recommended by Ubuntu. Never lower the
# host-wide unprivileged-user-namespace restriction for the whole runner.
install -o root -g root -m 0644 "$PROFILE_SOURCE" "$PROFILE_TARGET"
"$APPARMOR_PARSER" -Q "$PROFILE_TARGET"
"$APPARMOR_PARSER" -r "$PROFILE_TARGET"
grep -F "$PROFILE_NAME " "$APPARMOR_PROFILES" >/dev/null
test "$(stat -c '%U:%G:%a' "$PROFILE_TARGET")" = 'root:root:644'
test "$(sysctl -n kernel.apparmor_restrict_unprivileged_userns)" = '1'

# Prove the host-wide restriction was not disabled: an unprofiled executable
# still cannot create and map an unprivileged user namespace.
if runuser -u "$EVALUATOR_USER" -- \
  env -i /usr/bin/unshare --user --map-root-user /usr/bin/true \
  >/dev/null 2>&1; then
  echo 'Unprofiled user namespace creation unexpectedly succeeded' >&2
  exit 1
fi

readonly EVALUATOR_UID="$(id -u "$EVALUATOR_USER")"
readonly HOST_NET_NAMESPACE="$(readlink /proc/self/ns/net)"
readonly HOST_PID="$$"

# Match the Skillstore executor's namespace/capability contract. --disable-userns
# creates a second user namespace after setup, preventing the Agent from making
# another user namespace and rearranging the mount tree from inside the sandbox.
runuser -u "$EVALUATOR_USER" -- \
  env -i \
  "$BWRAP" \
    --die-with-parent \
    --new-session \
    --unshare-all \
    --share-net \
    --unshare-user \
    --disable-userns \
    --cap-drop ALL \
    --tmpfs / \
    --proc /proc \
    --dev /dev \
    --tmpfs /run \
    --ro-bind "$RUNTIME_ROOT" "$RUNTIME_ROOT" \
    --ro-bind-try /usr /usr \
    --ro-bind-try /bin /bin \
    --ro-bind-try /sbin /sbin \
    --ro-bind-try /lib /lib \
    --ro-bind-try /lib64 /lib64 \
    --ro-bind-try /etc/ca-certificates /etc/ca-certificates \
    --ro-bind-try /etc/group /etc/group \
    --ro-bind-try /etc/hosts /etc/hosts \
    --ro-bind-try /etc/localtime /etc/localtime \
    --ro-bind-try /etc/nsswitch.conf /etc/nsswitch.conf \
    --ro-bind-try /etc/passwd /etc/passwd \
    --ro-bind-try /etc/resolv.conf /etc/resolv.conf \
    --ro-bind-try /etc/ssl /etc/ssl \
    --bind "$EVALUATOR_HOME" "$EVALUATOR_HOME" \
    --bind "$EVALUATOR_TMP" /tmp \
    --bind "$CODEX_HOME" "$CODEX_HOME" \
    --setenv HOME "$EVALUATOR_HOME" \
    --setenv TMPDIR /tmp \
    --setenv CODEX_HOME "$CODEX_HOME" \
    --setenv PATH "$RUNTIME_ROOT/bin:/usr/bin:/bin" \
    --setenv EXPECTED_UID "$EVALUATOR_UID" \
    --setenv EXPECTED_NET_NAMESPACE "$HOST_NET_NAMESPACE" \
    --setenv OUTER_WORKSPACE "$PACK_EVALUATOR_OUTER_WORKSPACE" \
    --setenv OUTER_PID "$HOST_PID" \
    --chdir "$EVALUATOR_HOME" \
    -- \
    /usr/bin/bash -ceu '
      test "$(id -u)" = "$EXPECTED_UID"
      read -r namespace_uid parent_uid map_length < /proc/self/uid_map
      test "$namespace_uid:$parent_uid:$map_length" = "$EXPECTED_UID:0:1"
      awk '\''
        $1 ~ /^Cap(Inh|Prm|Eff|Bnd|Amb):$/ {
          seen += 1
          if ($2 !~ /^0+$/) exit 1
        }
        END { if (seen != 5) exit 1 }
      '\'' /proc/self/status
      test -x /opt/pack-evaluator/runtime/bin/node
      /opt/pack-evaluator/runtime/bin/node --version >/dev/null
      ! test -w /opt/pack-evaluator/runtime
      ! test -e /opt/pack-evaluator/bin
      ! test -e /opt/pack-evaluator/lib
      ! test -e /opt/pack-evaluator/input
      ! test -e /opt/pack-evaluator/results
      test "$(readlink /proc/self/ns/net)" = "$EXPECTED_NET_NAMESPACE"
      ! test -e "$OUTER_WORKSPACE"
      ! test -e "/proc/$OUTER_PID"
      ! env | grep -Eq "SUPABASE|HELM|GITHUB_TOKEN|GH_TOKEN|APP_PRIVATE_KEY|CALLBACK"
      if /usr/bin/unshare --user /usr/bin/true 2>/dev/null; then
        exit 1
      fi
    '

test "$(sysctl -n kernel.apparmor_restrict_unprivileged_userns)" = '1'
echo 'Pack evaluator bubblewrap/AppArmor preflight passed'
