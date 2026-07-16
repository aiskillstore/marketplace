#!/usr/bin/env bash
set -euo pipefail

: "${PACK_EVALUATOR_PROXY_TOKEN:?PACK_EVALUATOR_PROXY_TOKEN is required}"
: "${PACK_DIAGNOSTICS_DIR:?PACK_DIAGNOSTICS_DIR is required}"
readonly PREFLIGHT_TIMEOUT_SECONDS=180
readonly BWRAP=/usr/bin/bwrap
[ -x "$BWRAP" ] || { echo 'bubblewrap is required for evaluator preflight' >&2; exit 1; }

# Empty-root, fresh-PID sandbox for the two real CLI preflights. It deliberately
# mounts the agent runtime and writable identity state but none of the evaluator
# CLI/orchestrator/input/results trees or the GitHub workspace.
readonly -a AGENT_BWRAP=(
  "$BWRAP"
  --die-with-parent
  --new-session
  --unshare-all
  --share-net
  --disable-userns
  --cap-drop ALL
  --tmpfs /
  --proc /proc
  --dev /dev
  --tmpfs /run
  --dir /opt
  --dir /opt/pack-evaluator
  --ro-bind /opt/pack-evaluator/runtime /opt/pack-evaluator/runtime
  --dir /opt/pack-evaluator/codex-home
  --bind /opt/pack-evaluator/codex-home /opt/pack-evaluator/codex-home
  --dir /usr
  --ro-bind /usr /usr
  --symlink usr/bin /bin
  --symlink usr/lib /lib
  --symlink usr/lib64 /lib64
  --dir /etc
  --ro-bind /etc/ssl /etc/ssl
  --ro-bind /etc/ca-certificates /etc/ca-certificates
  --ro-bind /etc/resolv.conf /etc/resolv.conf
  --ro-bind /etc/hosts /etc/hosts
  --ro-bind /etc/nsswitch.conf /etc/nsswitch.conf
  --ro-bind /etc/passwd /etc/passwd
  --ro-bind /etc/group /etc/group
  --dir /home
  --dir /home/packeval
  --bind /home/packeval /home/packeval
  --dir /tmp
  --bind /home/packeval/tmp /tmp
  --setenv HOME /home/packeval
  --setenv CODEX_HOME /opt/pack-evaluator/codex-home
  --setenv TMPDIR /tmp
  --setenv PATH /opt/pack-evaluator/runtime/bin:/usr/bin:/bin
  --setenv CI true
  --setenv NO_COLOR 1
  --setenv NO_PROXY 127.0.0.1,localhost
)

CLAUDE_STDOUT=$(mktemp)
CLAUDE_STDERR=$(mktemp)
CODEX_STDOUT=$(mktemp)
CODEX_STDERR=$(mktemp)
cleanup_files() {
  rm -f "$CLAUDE_STDOUT" "$CLAUDE_STDERR" "$CODEX_STDOUT" "$CODEX_STDERR"
}
trap cleanup_files EXIT

classify_error() {
  local file="$1"
  local exit_code="$2"
  local fatal_http_status="${3:-}"
  local retryable_http_status="${4:-}"
  if [ -n "$fatal_http_status" ]; then
    printf 'deterministic_http\n'
  elif [ -n "$retryable_http_status" ]; then
    printf 'retryable_http\n'
  elif grep -Eqi 'permission denied|read-only file system|unable to open.*database|failed to.*(state|log|session)' "$file"; then
    printf 'state_storage\n'
  elif grep -Eqi '401|403|unauthoriz|authentication|api key' "$file"; then
    printf 'authentication\n'
  elif grep -Eqi '404|model.*not found|unsupported model' "$file"; then
    printf 'model_route\n'
  elif grep -Eqi 'unknown argument|unexpected argument|usage:' "$file"; then
    printf 'cli_arguments\n'
  elif [ "$exit_code" -eq 124 ] || grep -Eqi 'timed out|timeout' "$file"; then
    printf 'timeout\n'
  elif grep -Eqi 'error sending request|failed to send request|connection (reset|refused|closed|aborted)|transport.*(closed|error)|unexpected (eof|end of file)|temporary failure in name resolution|dns.*temporary|tls.*(handshake|temporary)|http[^0-9]*(408|429|502|503|504)|status( code)?[^0-9]*(408|429|502|503|504)' "$file"; then
    printf 'upstream_transport\n'
  elif [ -s "$file" ] || [ "$exit_code" -ne 0 ]; then
    printf 'unknown\n'
  else
    printf 'none\n'
  fi
}

# A preflight is read-only, isolated, and capped at two attempts. Only an exact
# 408/425/429/5xx response receives one retry. Every other 4xx and failures with
# no exact upstream status fail closed on the first attempt.
should_retry_preflight() {
  local outcome="$1"
  local error_class="$2"
  local attempt="$3"
  if [ "$outcome" != "command_failed" ] || [ "$attempt" -ge 2 ]; then
    return 1
  fi
  case "$error_class" in
    retryable_http) return 0 ;;
    *) return 1 ;;
  esac
}

activity_start_line() {
  if [ -z "${PACK_EVALUATOR_ACTIVITY_FILE:-}" ] || \
     ! sudo test -f "$PACK_EVALUATOR_ACTIVITY_FILE"; then
    printf '1\n'
    return
  fi
  local lines
  lines=$(sudo wc -l "$PACK_EVALUATOR_ACTIVITY_FILE" | awk '{print $1}')
  printf '%s\n' "$((lines + 1))"
}

monitor_preflight_http() {
  local command_pid="$1"
  local start_line="$2"
  local observed
  HTTP_FATAL_STATUS=''
  HTTP_RETRYABLE_STATUS=''
  while true; do
    if [ -n "${PACK_EVALUATOR_ACTIVITY_FILE:-}" ] && \
       sudo test -f "$PACK_EVALUATOR_ACTIVITY_FILE"; then
      observed=$(sudo tail -n "+$start_line" "$PACK_EVALUATOR_ACTIVITY_FILE" 2>/dev/null | jq -cs '
        [ .[] | select(.phase == "response") | .status | select(type == "number") ] as $statuses |
        {
          fatal: ([$statuses[] | select(. >= 400 and . < 500 and . != 408 and . != 425 and . != 429)] | first // null),
          retryable: ([$statuses[] | select(. == 408 or . == 425 or . == 429 or . >= 500)] | last // null)
        }
      ' 2>/dev/null || printf '{"fatal":null,"retryable":null}')
      HTTP_FATAL_STATUS=$(jq -r '.fatal // empty' <<< "$observed")
      HTTP_RETRYABLE_STATUS=$(jq -r '.retryable // empty' <<< "$observed")
      if [ -n "$HTTP_FATAL_STATUS" ]; then
        sudo pkill -TERM -u packeval 2>/dev/null || true
        for _ in $(seq 1 20); do
          if ! kill -0 "$command_pid" 2>/dev/null; then
            break
          fi
          sleep 0.1
        done
        sudo pkill -KILL -u packeval 2>/dev/null || true
        break
      fi
    fi
    if ! kill -0 "$command_pid" 2>/dev/null; then
      break
    fi
    sleep 0.2
  done
}

cleanup_processes() {
  local probe_rc
  sudo pkill -TERM -u packeval 2>/dev/null || true
  for _ in $(seq 1 10); do
    if ! sudo pgrep -u packeval >/dev/null 2>&1; then
      break
    fi
    sleep 0.1
  done
  sudo pkill -KILL -u packeval 2>/dev/null || true
  sleep 0.1
  if sudo pgrep -u packeval >/dev/null 2>&1; then
    return 1
  else
    probe_rc=$?
    if [ "$probe_rc" -ne 1 ]; then
      return 2
    fi
  fi
  return 0
}

CLAUDE_OUTCOME=not_run
CLAUDE_ERROR_CLASS=none
CLAUDE_ATTEMPTS='[]'
RETRY_CLEANUP_OUTCOME=not_needed
for ATTEMPT in 1 2; do
  : > "$CLAUDE_STDOUT"
  : > "$CLAUDE_STDERR"
  STARTED_MS=$(date +%s%3N)
  ACTIVITY_START_LINE=$(activity_start_line)
  set +e
  printf '%s\n' 'Reply with exactly PACK_EVALUATOR_READY and nothing else.' | \
    sudo -u packeval env -i \
      /usr/bin/timeout --signal=TERM --kill-after=5s "${PREFLIGHT_TIMEOUT_SECONDS}s" \
      "${AGENT_BWRAP[@]}" \
        --setenv ANTHROPIC_BASE_URL http://127.0.0.1:18765 \
        --setenv ANTHROPIC_AUTH_TOKEN "$PACK_EVALUATOR_PROXY_TOKEN" \
        /opt/pack-evaluator/runtime/bin/claude \
        --print \
        --output-format text \
        --permission-mode bypassPermissions \
        --model sonnet \
        - \
      > "$CLAUDE_STDOUT" \
      2> "$CLAUDE_STDERR" &
  CLAUDE_COMMAND_PID=$!
  monitor_preflight_http "$CLAUDE_COMMAND_PID" "$ACTIVITY_START_LINE"
  wait "$CLAUDE_COMMAND_PID"
  CLAUDE_EXIT_CODE=$?
  CLAUDE_FATAL_HTTP_STATUS="$HTTP_FATAL_STATUS"
  CLAUDE_RETRYABLE_HTTP_STATUS="$HTTP_RETRYABLE_STATUS"
  set -e
  if [ "$CLAUDE_EXIT_CODE" -ne 0 ]; then
    CLAUDE_OUTCOME=command_failed
  elif [ "$(tr -d '\r\n' < "$CLAUDE_STDOUT")" != 'PACK_EVALUATOR_READY' ]; then
    CLAUDE_OUTCOME=invalid_response
  else
    CLAUDE_OUTCOME=passed
  fi
  DURATION_MS=$(( $(date +%s%3N) - STARTED_MS ))
  STDOUT_BYTES=$(wc -c < "$CLAUDE_STDOUT")
  STDERR_BYTES=$(wc -c < "$CLAUDE_STDERR")
  STDOUT_SHA256=$(sha256sum "$CLAUDE_STDOUT" | awk '{print $1}')
  STDERR_SHA256=$(sha256sum "$CLAUDE_STDERR" | awk '{print $1}')
  CLAUDE_ERROR_CLASS=$(classify_error \
    "$CLAUDE_STDERR" "$CLAUDE_EXIT_CODE" "$CLAUDE_FATAL_HTTP_STATUS" "$CLAUDE_RETRYABLE_HTTP_STATUS")
  CLAUDE_ATTEMPTS=$(jq -c \
    --argjson attempt "$ATTEMPT" \
    --arg outcome "$CLAUDE_OUTCOME" \
    --arg errorClass "$CLAUDE_ERROR_CLASS" \
    --argjson exitCode "$CLAUDE_EXIT_CODE" \
    --argjson durationMs "$DURATION_MS" \
    --argjson stdoutBytes "$STDOUT_BYTES" \
    --argjson stderrBytes "$STDERR_BYTES" \
    --arg stdoutSha256 "$STDOUT_SHA256" \
    --arg stderrSha256 "$STDERR_SHA256" \
    --arg fatalHttpStatus "$CLAUDE_FATAL_HTTP_STATUS" \
    --arg retryableHttpStatus "$CLAUDE_RETRYABLE_HTTP_STATUS" \
    '. + [{
      attempt: $attempt,
      outcome: $outcome,
      errorClass: $errorClass,
      exitCode: $exitCode,
      durationMs: $durationMs,
      stdoutBytes: $stdoutBytes,
      stderrBytes: $stderrBytes,
      stdoutSha256: $stdoutSha256,
      stderrSha256: $stderrSha256,
      fatalHttpStatus: (if $fatalHttpStatus == "" then null else ($fatalHttpStatus | tonumber) end),
      retryableHttpStatus: (if $retryableHttpStatus == "" then null else ($retryableHttpStatus | tonumber) end)
    }]' <<< "$CLAUDE_ATTEMPTS")
  if ! should_retry_preflight \
    "$CLAUDE_OUTCOME" "$CLAUDE_ERROR_CLASS" "$ATTEMPT"; then
    break
  fi
  if cleanup_processes; then
    RETRY_CLEANUP_OUTCOME=passed
  else
    CLEANUP_RC=$?
    if [ "$CLEANUP_RC" -eq 1 ]; then
      RETRY_CLEANUP_OUTCOME=failed
    else
      RETRY_CLEANUP_OUTCOME=probe_failed
    fi
    break
  fi
  sleep 5
done
CODEX_OUTCOME=not_run
CODEX_ERROR_CLASS=none
CODEX_EXIT_CODE=-1
CODEX_ATTEMPTS='[]'
if [ "$CLAUDE_OUTCOME" = "passed" ]; then
  # Only an exact 408/425/429/5xx response receives one bounded retry.
  for ATTEMPT in 1 2; do
    : > "$CODEX_STDOUT"
    : > "$CODEX_STDERR"
    STARTED_MS=$(date +%s%3N)
    ACTIVITY_START_LINE=$(activity_start_line)
    set +e
    printf '%s\n' 'Reply with exactly PACK_EVALUATOR_READY and nothing else.' | \
      sudo -u packeval env -i \
        /usr/bin/timeout --signal=TERM --kill-after=5s "${PREFLIGHT_TIMEOUT_SECONDS}s" \
        "${AGENT_BWRAP[@]}" \
          --setenv PACK_EVALUATOR_PROXY_TOKEN "$PACK_EVALUATOR_PROXY_TOKEN" \
          /opt/pack-evaluator/runtime/bin/codex \
          exec \
          --skip-git-repo-check \
          --sandbox read-only \
          --cd /home/packeval \
          --ephemeral \
          --color never \
          -m gpt-5.5 \
          - \
        > "$CODEX_STDOUT" \
        2> "$CODEX_STDERR" &
    CODEX_COMMAND_PID=$!
    monitor_preflight_http "$CODEX_COMMAND_PID" "$ACTIVITY_START_LINE"
    wait "$CODEX_COMMAND_PID"
    CODEX_EXIT_CODE=$?
    CODEX_FATAL_HTTP_STATUS="$HTTP_FATAL_STATUS"
    CODEX_RETRYABLE_HTTP_STATUS="$HTTP_RETRYABLE_STATUS"
    set -e
    if [ "$CODEX_EXIT_CODE" -ne 0 ]; then
      CODEX_OUTCOME=command_failed
    elif [ "$(tr -d '\r\n' < "$CODEX_STDOUT")" != 'PACK_EVALUATOR_READY' ]; then
      CODEX_OUTCOME=invalid_response
    else
      CODEX_OUTCOME=passed
    fi
    DURATION_MS=$(( $(date +%s%3N) - STARTED_MS ))
    STDOUT_BYTES=$(wc -c < "$CODEX_STDOUT")
    STDERR_BYTES=$(wc -c < "$CODEX_STDERR")
    STDOUT_SHA256=$(sha256sum "$CODEX_STDOUT" | awk '{print $1}')
    STDERR_SHA256=$(sha256sum "$CODEX_STDERR" | awk '{print $1}')
    CODEX_ERROR_CLASS=$(classify_error \
      "$CODEX_STDERR" "$CODEX_EXIT_CODE" "$CODEX_FATAL_HTTP_STATUS" "$CODEX_RETRYABLE_HTTP_STATUS")
    CODEX_ATTEMPTS=$(jq -c \
      --argjson attempt "$ATTEMPT" \
      --arg outcome "$CODEX_OUTCOME" \
      --arg errorClass "$CODEX_ERROR_CLASS" \
      --argjson exitCode "$CODEX_EXIT_CODE" \
      --argjson durationMs "$DURATION_MS" \
      --argjson stdoutBytes "$STDOUT_BYTES" \
      --argjson stderrBytes "$STDERR_BYTES" \
      --arg stdoutSha256 "$STDOUT_SHA256" \
      --arg stderrSha256 "$STDERR_SHA256" \
      --arg fatalHttpStatus "$CODEX_FATAL_HTTP_STATUS" \
      --arg retryableHttpStatus "$CODEX_RETRYABLE_HTTP_STATUS" \
      '. + [{
        attempt: $attempt,
        outcome: $outcome,
        errorClass: $errorClass,
        exitCode: $exitCode,
        durationMs: $durationMs,
        stdoutBytes: $stdoutBytes,
        stderrBytes: $stderrBytes,
        stdoutSha256: $stdoutSha256,
        stderrSha256: $stderrSha256,
        fatalHttpStatus: (if $fatalHttpStatus == "" then null else ($fatalHttpStatus | tonumber) end),
        retryableHttpStatus: (if $retryableHttpStatus == "" then null else ($retryableHttpStatus | tonumber) end)
      }]' <<< "$CODEX_ATTEMPTS")
    if ! should_retry_preflight \
      "$CODEX_OUTCOME" "$CODEX_ERROR_CLASS" "$ATTEMPT"; then
      break
    fi
    if cleanup_processes; then
      RETRY_CLEANUP_OUTCOME=passed
    else
      CLEANUP_RC=$?
      if [ "$CLEANUP_RC" -eq 1 ]; then
        RETRY_CLEANUP_OUTCOME=failed
      else
        RETRY_CLEANUP_OUTCOME=probe_failed
      fi
      break
    fi
    sleep 5
  done
fi

CLAUDE_STDOUT_BYTES=$(wc -c < "$CLAUDE_STDOUT")
CLAUDE_STDERR_BYTES=$(wc -c < "$CLAUDE_STDERR")
CLAUDE_STDOUT_SHA256=$(sha256sum "$CLAUDE_STDOUT" | awk '{print $1}')
CLAUDE_STDERR_SHA256=$(sha256sum "$CLAUDE_STDERR" | awk '{print $1}')
CODEX_STDOUT_BYTES=$(wc -c < "$CODEX_STDOUT")
CODEX_STDERR_BYTES=$(wc -c < "$CODEX_STDERR")
CODEX_STDOUT_SHA256=$(sha256sum "$CODEX_STDOUT" | awk '{print $1}')
CODEX_STDERR_SHA256=$(sha256sum "$CODEX_STDERR" | awk '{print $1}')

if cleanup_processes; then
  CLEANUP_OUTCOME=passed
else
  CLEANUP_RC=$?
  if [ "$CLEANUP_RC" -eq 1 ]; then
    CLEANUP_OUTCOME=failed
  else
    CLEANUP_OUTCOME=probe_failed
  fi
fi

jq -n \
  --arg claudeOutcome "$CLAUDE_OUTCOME" \
  --argjson claudeStdoutBytes "$CLAUDE_STDOUT_BYTES" \
  --argjson claudeStderrBytes "$CLAUDE_STDERR_BYTES" \
  --arg claudeStdoutSha256 "$CLAUDE_STDOUT_SHA256" \
  --arg claudeStderrSha256 "$CLAUDE_STDERR_SHA256" \
  --arg claudeErrorClass "$CLAUDE_ERROR_CLASS" \
  --argjson claudeExitCode "$CLAUDE_EXIT_CODE" \
  --argjson claudeAttempts "$CLAUDE_ATTEMPTS" \
  --arg codexOutcome "$CODEX_OUTCOME" \
  --argjson codexStdoutBytes "$CODEX_STDOUT_BYTES" \
  --argjson codexStderrBytes "$CODEX_STDERR_BYTES" \
  --arg codexStdoutSha256 "$CODEX_STDOUT_SHA256" \
  --arg codexStderrSha256 "$CODEX_STDERR_SHA256" \
  --arg codexErrorClass "$CODEX_ERROR_CLASS" \
  --argjson codexExitCode "$CODEX_EXIT_CODE" \
  --argjson codexAttempts "$CODEX_ATTEMPTS" \
  --arg cleanupOutcome "$CLEANUP_OUTCOME" \
  --arg retryCleanupOutcome "$RETRY_CLEANUP_OUTCOME" \
  '{
    claude: {
      outcome: $claudeOutcome,
      stdoutBytes: $claudeStdoutBytes,
      stderrBytes: $claudeStderrBytes,
      stdoutSha256: $claudeStdoutSha256,
      stderrSha256: $claudeStderrSha256,
      errorClass: $claudeErrorClass,
      exitCode: $claudeExitCode,
      attempts: $claudeAttempts
    },
    codex: {
      outcome: $codexOutcome,
      stdoutBytes: $codexStdoutBytes,
      stderrBytes: $codexStderrBytes,
      stdoutSha256: $codexStdoutSha256,
      stderrSha256: $codexStderrSha256,
      errorClass: $codexErrorClass,
      exitCode: $codexExitCode,
      attempts: $codexAttempts
    },
    cleanup: {
      outcome: $cleanupOutcome,
      retryOutcome: $retryCleanupOutcome
    }
  }' > "$PACK_DIAGNOSTICS_DIR/agent-preflight-diagnostics.json"

if [ -n "${PACK_EVALUATOR_ACTIVITY_FILE:-}" ] && \
   sudo test -f "$PACK_EVALUATOR_ACTIVITY_FILE"; then
  sudo cp "$PACK_EVALUATOR_ACTIVITY_FILE" \
    "$PACK_DIAGNOSTICS_DIR/proxy-activity.ndjson"
  sudo chown "$(id -u):$(id -g)" \
    "$PACK_DIAGNOSTICS_DIR/proxy-activity.ndjson"
  chmod 0600 "$PACK_DIAGNOSTICS_DIR/proxy-activity.ndjson"
fi

if [ "$CLAUDE_OUTCOME" != "passed" ] || \
   [ "$CODEX_OUTCOME" != "passed" ] || \
   [ "$CLEANUP_OUTCOME" != "passed" ] || \
   { [ "$RETRY_CLEANUP_OUTCOME" != "not_needed" ] && \
     [ "$RETRY_CLEANUP_OUTCOME" != "passed" ]; }; then
  echo "::error::Pack evaluator model preflight failed: claude=$CLAUDE_OUTCOME codex=$CODEX_OUTCOME cleanup=$CLEANUP_OUTCOME retry_cleanup=$RETRY_CLEANUP_OUTCOME"
  exit 1
fi
