#!/usr/bin/env bash
# dbskill 版本检查：24 小时内最多联网一次，有新版时输出一行用户提醒。

set -uo pipefail

LOCAL_VERSION="${1:-}"
DBS_DIR="$HOME/.dbs"
CACHE_FILE="$DBS_DIR/update_check_at"
REMOTE_URL="${DBS_UPDATE_URL:-https://raw.githubusercontent.com/dontbesilent2025/dbskill/main/UPDATE.json}"
CACHE_TTL=86400

if [[ ! "$LOCAL_VERSION" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
  exit 0
fi

NOW="$(date +%s)"
if [ -f "$CACHE_FILE" ]; then
  LAST_CHECK="$(tr -d '[:space:]' < "$CACHE_FILE" 2>/dev/null || true)"
  if [[ "$LAST_CHECK" =~ ^[0-9]+$ ]] && [ "$NOW" -ge "$LAST_CHECK" ] && [ $((NOW - LAST_CHECK)) -lt "$CACHE_TTL" ]; then
    exit 0
  fi
fi

mkdir -p "$DBS_DIR" 2>/dev/null || exit 0
printf '%s\n' "$NOW" > "$CACHE_FILE" 2>/dev/null || exit 0

PAYLOAD="$(curl -fsS --max-time 5 "$REMOTE_URL" 2>/dev/null || true)"
[ -n "$PAYLOAD" ] || exit 0

parse_with_python() {
  python3 -c '
import json, re, sys
try:
    data = json.load(sys.stdin)
    version = data.get("version", "")
    notice = data.get("notice", "")
    if not isinstance(version, str) or not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version):
        raise ValueError
    if not isinstance(notice, str) or not 1 <= len(notice.strip()) <= 80 or any(ch in notice for ch in "\r\n\t"):
        raise ValueError
    print(f"{version}\t{notice.strip()}", end="")
except Exception:
    sys.exit(1)
'
}

parse_with_node() {
  node -e '
let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => raw += chunk);
process.stdin.on("end", () => {
  try {
    const data = JSON.parse(raw);
    const version = data.version;
    const notice = data.notice;
    if (typeof version !== "string" || !/^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/.test(version)) process.exit(1);
    if (typeof notice !== "string" || notice.trim().length < 1 || notice.trim().length > 80 || /[\r\n\t]/.test(notice)) process.exit(1);
    process.stdout.write(`${version}\t${notice.trim()}`);
  } catch (_) {
    process.exit(1);
  }
});
'
}

if command -v python3 >/dev/null 2>&1; then
  PARSED="$(printf '%s' "$PAYLOAD" | parse_with_python 2>/dev/null || true)"
elif command -v node >/dev/null 2>&1; then
  PARSED="$(printf '%s' "$PAYLOAD" | parse_with_node 2>/dev/null || true)"
else
  exit 0
fi

[[ "$PARSED" == *$'\t'* ]] || exit 0
REMOTE_VERSION="${PARSED%%$'\t'*}"
NOTICE="${PARSED#*$'\t'}"

version_is_higher() {
  local remote_major remote_minor remote_patch local_major local_minor local_patch
  IFS=. read -r remote_major remote_minor remote_patch <<< "$1"
  IFS=. read -r local_major local_minor local_patch <<< "$2"
  if ((10#$remote_major != 10#$local_major)); then
    ((10#$remote_major > 10#$local_major))
  elif ((10#$remote_minor != 10#$local_minor)); then
    ((10#$remote_minor > 10#$local_minor))
  else
    ((10#$remote_patch > 10#$local_patch))
  fi
}

if version_is_higher "$REMOTE_VERSION" "$LOCAL_VERSION"; then
  printf 'dbskill v%s：%s 回复 1，我现在帮你更新。\n' "$REMOTE_VERSION" "$NOTICE"
fi
