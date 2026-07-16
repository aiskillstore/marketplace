#!/usr/bin/env bash
set -euo pipefail

: "${PACK_EVALUATOR_PROXY_TOKEN:?PACK_EVALUATOR_PROXY_TOKEN is required}"
: "${PACK_DIAGNOSTICS_DIR:?PACK_DIAGNOSTICS_DIR is required}"

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
  if grep -Eqi 'permission denied|read-only file system|unable to open.*database|failed to.*(state|log|session)' "$file"; then
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
  set +e
  printf '%s\n' 'Reply with exactly PACK_EVALUATOR_READY and nothing else.' | \
    sudo -u packeval env -i \
      PATH=/opt/pack-evaluator/runtime/bin:/opt/pack-evaluator/bin:/usr/bin:/bin \
      HOME=/home/packeval \
      CODEX_HOME=/opt/pack-evaluator/codex-home \
      TMPDIR=/home/packeval/tmp \
      CI=true \
      NO_COLOR=1 \
      ANTHROPIC_BASE_URL=http://127.0.0.1:18765 \
      ANTHROPIC_AUTH_TOKEN="$PACK_EVALUATOR_PROXY_TOKEN" \
      NO_PROXY=127.0.0.1,localhost \
      timeout --signal=TERM --kill-after=5s 60s \
      /opt/pack-evaluator/runtime/bin/claude \
        --print \
        --output-format text \
        --permission-mode bypassPermissions \
        --model sonnet \
        - \
      > "$CLAUDE_STDOUT" \
      2> "$CLAUDE_STDERR"
  CLAUDE_EXIT_CODE=$?
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
  CLAUDE_ERROR_CLASS=$(classify_error "$CLAUDE_STDERR" "$CLAUDE_EXIT_CODE")
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
    '. + [{
      attempt: $attempt,
      outcome: $outcome,
      errorClass: $errorClass,
      exitCode: $exitCode,
      durationMs: $durationMs,
      stdoutBytes: $stdoutBytes,
      stderrBytes: $stderrBytes,
      stdoutSha256: $stdoutSha256,
      stderrSha256: $stderrSha256
    }]' <<< "$CLAUDE_ATTEMPTS")
  if [ "$CLAUDE_OUTCOME" = "passed" ] || \
     [ "$CLAUDE_OUTCOME" != "command_failed" ] || \
     { [ "$CLAUDE_ERROR_CLASS" != "upstream_transport" ] && \
       [ "$CLAUDE_ERROR_CLASS" != "timeout" ]; } || \
     [ "$ATTEMPT" -eq 2 ]; then
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
  # Retry only one narrowly classified transport failure or an explicit
  # timeout. Permission, auth, routing, CLI, response-shape, and unknown
  # failures stay fail-closed.
  for ATTEMPT in 1 2; do
    : > "$CODEX_STDOUT"
    : > "$CODEX_STDERR"
    STARTED_MS=$(date +%s%3N)
    set +e
    printf '%s\n' 'Reply with exactly PACK_EVALUATOR_READY and nothing else.' | \
      sudo -u packeval env -i \
        PATH=/opt/pack-evaluator/runtime/bin:/opt/pack-evaluator/bin:/usr/bin:/bin \
        HOME=/home/packeval \
        CODEX_HOME=/opt/pack-evaluator/codex-home \
        TMPDIR=/home/packeval/tmp \
        CI=true \
        NO_COLOR=1 \
        PACK_EVALUATOR_PROXY_TOKEN="$PACK_EVALUATOR_PROXY_TOKEN" \
        NO_PROXY=127.0.0.1,localhost \
        timeout --signal=TERM --kill-after=5s 60s \
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
        2> "$CODEX_STDERR"
    CODEX_EXIT_CODE=$?
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
    CODEX_ERROR_CLASS=$(classify_error "$CODEX_STDERR" "$CODEX_EXIT_CODE")
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
      '. + [{
        attempt: $attempt,
        outcome: $outcome,
        errorClass: $errorClass,
        exitCode: $exitCode,
        durationMs: $durationMs,
        stdoutBytes: $stdoutBytes,
        stderrBytes: $stderrBytes,
        stdoutSha256: $stdoutSha256,
        stderrSha256: $stderrSha256
      }]' <<< "$CODEX_ATTEMPTS")
    if [ "$CODEX_OUTCOME" = "passed" ] || \
       [ "$CODEX_OUTCOME" != "command_failed" ] || \
       { [ "$CODEX_ERROR_CLASS" != "upstream_transport" ] && \
         [ "$CODEX_ERROR_CLASS" != "timeout" ]; } || \
       [ "$ATTEMPT" -eq 2 ]; then
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

if [ "$CLAUDE_OUTCOME" != "passed" ] || \
   [ "$CODEX_OUTCOME" != "passed" ] || \
   [ "$CLEANUP_OUTCOME" != "passed" ] || \
   { [ "$RETRY_CLEANUP_OUTCOME" != "not_needed" ] && \
     [ "$RETRY_CLEANUP_OUTCOME" != "passed" ]; }; then
  echo "::error::Pack evaluator model preflight failed: claude=$CLAUDE_OUTCOME codex=$CODEX_OUTCOME cleanup=$CLEANUP_OUTCOME retry_cleanup=$RETRY_CLEANUP_OUTCOME"
  exit 1
fi
