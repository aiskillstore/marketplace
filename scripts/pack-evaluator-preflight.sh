#!/usr/bin/env bash
set -euo pipefail

: "${PACK_EVALUATOR_PROXY_TOKEN:?PACK_EVALUATOR_PROXY_TOKEN is required}"
: "${PACK_DIAGNOSTICS_DIR:?PACK_DIAGNOSTICS_DIR is required}"
: "${PACK_EVALUATOR_MAX_OUTPUT_TOKENS:?PACK_EVALUATOR_MAX_OUTPUT_TOKENS is required}"
: "${PACK_PRODUCTION_CLI_VERSION:?PACK_PRODUCTION_CLI_VERSION is required}"
if ! [[ "$PACK_EVALUATOR_MAX_OUTPUT_TOKENS" =~ ^[1-9][0-9]*$ ]]; then
  echo 'PACK_EVALUATOR_MAX_OUTPUT_TOKENS must be a positive integer' >&2
  exit 1
fi
: "${PACK_EVALUATOR_MARKETPLACE_COMMIT_SHA:?PACK_EVALUATOR_MARKETPLACE_COMMIT_SHA is required}"
: "${PACK_EVALUATOR_CLI_SHA256:?PACK_EVALUATOR_CLI_SHA256 is required}"
if ! [[ "$PACK_EVALUATOR_MARKETPLACE_COMMIT_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  echo 'PACK_EVALUATOR_MARKETPLACE_COMMIT_SHA must be a lowercase Git commit SHA' >&2
  exit 1
fi
if ! [[ "$PACK_EVALUATOR_CLI_SHA256" =~ ^[0-9a-f]{64}$ ]]; then
  echo 'PACK_EVALUATOR_CLI_SHA256 must be a lowercase SHA-256' >&2
  exit 1
fi

readonly PREFLIGHT_TIMEOUT_SECONDS=420
readonly AGENT_TIMEOUT_MS=180000
readonly NODE=/opt/pack-evaluator/bin/node
readonly CLI=/opt/pack-evaluator/bin/skillstore-cli
readonly ORCHESTRATOR=/opt/pack-evaluator/lib/pack-production.mjs
readonly RUNTIME_ROOT=/opt/pack-evaluator/generations
readonly PREFLIGHT_GENERATION_ID=00000000-0000-4000-8000-000000000001
readonly PREFLIGHT_ROOT=/home/packeval/tmp/skillstore-executor-preflight
readonly PREFLIGHT_SKILL_A="$PREFLIGHT_ROOT/input/skill-a"
readonly PREFLIGHT_SKILL_B="$PREFLIGHT_ROOT/input/skill-b"
readonly PREFLIGHT_RAW="$PREFLIGHT_ROOT/raw"
readonly PREFLIGHT_TASK='Invoke Skill pack-executor-preflight-a first and Skill pack-executor-preflight-b second. After both Skills load successfully, reply with exactly PACK_EVALUATOR_READY and nothing else.'
readonly CLI_STDOUT="$(mktemp)"
readonly CLI_STDERR="$(mktemp)"
readonly ACTIVITY_SLICE="$(mktemp)"

for executable in "$NODE" "$CLI" /usr/bin/bwrap /usr/bin/jq /usr/bin/prlimit /usr/bin/setsid /usr/bin/sha256sum; do
  [ -x "$executable" ] || { echo "Required evaluator executable is missing: $executable" >&2; exit 1; }
done
[ -r "$ORCHESTRATOR" ] || { echo 'Pack production orchestrator is missing' >&2; exit 1; }

cleanup_files() {
  rm -f \
    "$CLI_STDOUT" \
    "$CLI_STDERR" \
    "$ACTIVITY_SLICE" \
    "${PREFLIGHT_SKILL_MD_A:-}" \
    "${PREFLIGHT_SKILL_MD_B:-}"
  sudo rm -rf "$PREFLIGHT_ROOT"
  sudo rm -rf "$RUNTIME_ROOT/$PREFLIGHT_GENERATION_ID"
}
trap cleanup_files EXIT

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

summarize_preflight_http_activity() {
  jq -cs '
    def inference_response:
      .phase == "response" and
      (.path == "/v1/messages" or .path == "/v1/responses") and
      (.status | type) == "number";
    [ .[] | select(inference_response) ] as $inference |
    {
      messages200: ([$inference[] | select(.path == "/v1/messages" and .status == 200)] | length),
      responses200: ([$inference[] | select(.path == "/v1/responses" and .status == 200)] | length),
      inferenceFatalStatus: ([$inference[] | select(.status >= 400 and .status < 500 and .status != 408 and .status != 425 and .status != 429) | .status] | first // null),
      inferenceRetryableStatus: ([$inference[] | select(.status == 408 or .status == 425 or .status == 429 or .status >= 500) | .status] | last // null),
      auxiliaryRejectedCount: ([.[] | select(.phase == "response" and .path == "not_allowed" and (.status == 401 or .status == 403))] | length)
    }
  '
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
      observed=$(sudo tail -n "+$start_line" "$PACK_EVALUATOR_ACTIVITY_FILE" 2>/dev/null | \
        summarize_preflight_http_activity 2>/dev/null || \
        printf '{"inferenceFatalStatus":null,"inferenceRetryableStatus":null}')
      HTTP_FATAL_STATUS=$(jq -r '.inferenceFatalStatus // empty' <<< "$observed")
      HTTP_RETRYABLE_STATUS=$(jq -r '.inferenceRetryableStatus // empty' <<< "$observed")
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

should_retry_preflight() {
  local outcome="$1"
  local error_class="$2"
  local attempt="$3"
  [ "$outcome" = 'command_failed' ] && \
    [ "$error_class" = 'retryable_http' ] && \
    [ "$attempt" -lt 2 ]
}

safe_execution_evidence() {
  local source="$1"
  jq -c '
    def sha: type == "string" and test("^[0-9a-f]{64}$");
    def category: . as $value |
      [
        "none", "spawn_spec", "spawn_error", "timeout", "signal",
        "sandbox_runtime", "state_storage", "authentication", "model_route",
        "cli_arguments", "upstream_transport", "trace_protocol",
        "nonzero_exit", "empty_output"
      ] | index($value) != null;
    def spawn_code: . as $value |
      $value == null or (["EACCES", "EAGAIN", "EMFILE", "ENFILE", "ENOENT", "ENOMEM", "EPERM", "OTHER"] | index($value) != null);
    [
      .agentExecutionEvidence[]?
      | select(.phase == "run" or .phase == "judge")
      | select(.run == 1 and (.succeeded | type) == "boolean")
      | {
          phase,
          run,
          succeeded,
          attempts: [
            .attempts[]?
            | select(.schemaVersion == "skillstore.agent-execution-evidence/v1")
            | select(.agent == "claude" or .agent == "codex" or .agent == "gemini")
            | select((.attempt | type) == "number" and .attempt >= 1 and .attempt <= 3)
            | select((.sandboxed | type) == "boolean")
            | select(.outcome == "succeeded" or .outcome == "failed")
            | select(.failureCategory | category)
            | select(.spawnErrorCode | spawn_code)
            | select(.exitCode == null or ((.exitCode | type) == "number" and .exitCode >= 0 and .exitCode <= 255))
            | select(.signal == null or ((.signal | type) == "string" and (.signal | test("^SIG[A-Z0-9]{1,12}$"))))
            | select((.durationMs | type) == "number" and .durationMs >= 0 and .durationMs <= 420000)
            | select((.stdoutBytes | type) == "number" and .stdoutBytes >= 0 and .stdoutBytes <= 67108864)
            | select((.stderrBytes | type) == "number" and .stderrBytes >= 0 and .stderrBytes <= 67108864)
            | select(.stdoutSha256 | sha)
            | select(.stderrSha256 | sha)
            | {
                schemaVersion,
                agent,
                attempt,
                sandboxed,
                outcome,
                failureCategory,
                spawnErrorCode,
                exitCode,
                signal,
                durationMs,
                stdoutBytes,
                stderrBytes,
                stdoutSha256,
                stderrSha256
              }
          ]
        }
    ][0:8]
  ' "$source" 2>/dev/null || printf '[]'
}

safe_runner_trace_evidence() {
  local source="$1"
  jq -c '
    .runnerTraceEvidence as $trace
    | if (
        ($trace | type) == "object"
        and $trace.schemaVersion == "marketplace.pack-executor-trace-evidence/v1"
        and $trace.deterministic == true
        and $trace.traceCount == 1
        and $trace.eventCount == 2
        and ($trace.bindingDigest | type) == "string"
        and ($trace.bindingDigest | test("^[0-9a-f]{64}$"))
      ) then $trace | {
        schemaVersion,
        deterministic,
        traceCount,
        eventCount,
        bindingDigest
      } else null end
  ' "$source" 2>/dev/null || printf 'null\n'
}

safe_outer_execution() {
  local source="$1"
  jq -c '
    .outerExecution as $outer
    | if (
        ($outer | type) == "object" and
        ($outer.spawnErrorCode == null or (["EACCES", "EAGAIN", "EMFILE", "ENFILE", "ENOENT", "ENOMEM", "EPERM", "OTHER"] | index($outer.spawnErrorCode) != null)) and
        ($outer.exitCode == null or (($outer.exitCode | type) == "number" and $outer.exitCode >= 0 and $outer.exitCode <= 255)) and
        ($outer.signal == null or (($outer.signal | type) == "string" and ($outer.signal | test("^SIG[A-Z0-9]{1,12}$")))) and
        (($outer.timedOut | type) == "boolean") and (($outer.stalled | type) == "boolean") and
        (($outer.outputExceeded | type) == "boolean") and
        (($outer.durationMs | type) == "number" and $outer.durationMs >= 0 and $outer.durationMs <= 430000) and
        (($outer.stdoutBytes | type) == "number" and $outer.stdoutBytes >= 0 and $outer.stdoutBytes <= 16777216) and
        (($outer.stderrBytes | type) == "number" and $outer.stderrBytes >= 0 and $outer.stderrBytes <= 16777216) and
        (($outer.stdoutSha256 | type) == "string" and ($outer.stdoutSha256 | test("^[0-9a-f]{64}$"))) and
        (($outer.stderrSha256 | type) == "string" and ($outer.stderrSha256 | test("^[0-9a-f]{64}$")))
      ) then $outer | {
        spawnErrorCode, exitCode, signal, timedOut, stalled, outputExceeded,
        durationMs, stdoutBytes, stderrBytes, stdoutSha256, stderrSha256
      } else {} end
  ' "$source" 2>/dev/null || printf '{}\n'
}

append_command_attempt() {
  local history="$1"
  local record="$2"
  jq -ce --argjson record "$record" '
    if length >= 2 then error("preflight command attempt budget exceeded")
    elif (
      ($record.attempt | type) == "number" and $record.attempt >= 1 and $record.attempt <= 2
      and ($record.outcome == "passed" or $record.outcome == "command_failed")
      and ($record.errorClass | type) == "string" and ($record.errorClass | length) <= 64
      and ($record.exitCode | type) == "number" and $record.exitCode >= 0 and $record.exitCode <= 255
      and ($record.durationMs | type) == "number" and $record.durationMs >= 0 and $record.durationMs <= 430000
      and ($record.stdoutBytes | type) == "number" and $record.stdoutBytes >= 0 and $record.stdoutBytes <= 16777216
      and ($record.stderrBytes | type) == "number" and $record.stderrBytes >= 0 and $record.stderrBytes <= 16777216
      and ($record.stdoutSha256 | type) == "string" and ($record.stdoutSha256 | test("^[0-9a-f]{64}$"))
      and ($record.stderrSha256 | type) == "string" and ($record.stderrSha256 | test("^[0-9a-f]{64}$"))
      and ($record.outerExecution | type) == "object"
      and ($record.agentExecutionEvidence | type) == "array"
      and ($record.agentExecutionEvidence | length) <= 8
      and ($record.runnerTraceEvidence == null or ($record.runnerTraceEvidence | type) == "object")
    ) then . + [{
      attempt: $record.attempt,
      outcome: $record.outcome,
      errorClass: $record.errorClass,
      exitCode: $record.exitCode,
      durationMs: $record.durationMs,
      stdoutBytes: $record.stdoutBytes,
      stderrBytes: $record.stderrBytes,
      stdoutSha256: $record.stdoutSha256,
      stderrSha256: $record.stderrSha256,
      outerExecution: $record.outerExecution,
      agentExecutionEvidence: $record.agentExecutionEvidence,
      runnerTraceEvidence: $record.runnerTraceEvidence
    }]
    else error("invalid bounded preflight command attempt")
    end
  ' <<< "$history"
}

mark_recovered_command_attempts() {
  local history="$1"
  local final_outcome="$2"
  jq -ce --arg finalOutcome "$final_outcome" '
    map(. + {
      recovered: ($finalOutcome == "passed" and .outcome == "command_failed")
    })
  ' <<< "$history"
}

# The two synthetic Skills are immutable inputs for the exact verifyPack trace
# path. They have no network/write instructions and live only in disposable HOME.
sudo rm -rf "$PREFLIGHT_ROOT"
sudo install -d -o packeval -g packeval -m 0700 "$PREFLIGHT_SKILL_A" "$PREFLIGHT_SKILL_B"
sudo install -d -o root -g root -m 0700 "$PREFLIGHT_RAW"
PREFLIGHT_SKILL_MD_A=$(mktemp)
printf '%s\n' \
  '---' \
  'name: pack-executor-preflight-a' \
  'description: Load first, then follow the evaluator task exactly.' \
  '---' \
  '' \
  'Follow the evaluator task exactly. Do not inspect the host or call external tools.' \
  > "$PREFLIGHT_SKILL_MD_A"
PREFLIGHT_SKILL_MD_B=$(mktemp)
printf '%s\n' \
  '---' \
  'name: pack-executor-preflight-b' \
  'description: Load second, then return the exact marker requested by the evaluator.' \
  '---' \
  '' \
  'Follow the evaluator task exactly. Do not inspect the host or call external tools.' \
  > "$PREFLIGHT_SKILL_MD_B"
sudo install -o packeval -g packeval -m 0444 \
  "$PREFLIGHT_SKILL_MD_A" "$PREFLIGHT_SKILL_A/SKILL.md"
sudo install -o packeval -g packeval -m 0444 \
  "$PREFLIGHT_SKILL_MD_B" "$PREFLIGHT_SKILL_B/SKILL.md"
rm -f "$PREFLIGHT_SKILL_MD_A" "$PREFLIGHT_SKILL_MD_B"

COMMAND_ATTEMPTS='[]'
RETRY_CLEANUP_OUTCOME=not_needed
PREFLIGHT_OUTCOME=command_failed
PREFLIGHT_ERROR_CLASS=unknown
HTTP_FATAL_STATUS=''
HTTP_RETRYABLE_STATUS=''
FINAL_EXECUTION_EVIDENCE='[]'
FINAL_RUNNER_TRACE_EVIDENCE='null'
FINAL_OUTER_EXECUTION='{}'

for ATTEMPT in 1 2; do
  : > "$CLI_STDOUT"
  : > "$CLI_STDERR"
  STARTED_MS=$(date +%s%3N)
  ACTIVITY_START_LINE=$(activity_start_line)
  set +e
  setsid sudo env -i \
    PATH=/opt/pack-evaluator/runtime/bin:/usr/bin:/bin \
    HOME=/home/packeval \
    CODEX_HOME=/opt/pack-evaluator/codex-home \
    TMPDIR=/home/packeval/tmp \
    CI=true \
    NO_COLOR=1 \
    SKILLSTORE_AGENTS=codex,claude \
    SKILLSTORE_AGENT_ENV_MODE=strict \
    SKILLSTORE_AGENT_ENV_ALLOWLIST=CODEX_HOME,PACK_EVALUATOR_PROXY_TOKEN,PACK_EVALUATOR_CHROMIUM_PATH,ANTHROPIC_BASE_URL,ANTHROPIC_AUTH_TOKEN,CLAUDE_CODE_MAX_OUTPUT_TOKENS,NO_PROXY,SKILLSTORE_AGENT_SANDBOX_MODE,SKILLSTORE_AGENT_SANDBOX_RUNTIME_ROOT \
    SKILLSTORE_AGENT_SANDBOX_MODE=bwrap \
    SKILLSTORE_AGENT_SANDBOX_RUNTIME_ROOT=/opt/pack-evaluator/runtime \
    PACK_EVALUATOR_CHROMIUM_PATH=/usr/bin/google-chrome \
    PACK_EVALUATOR_PROXY_TOKEN="$PACK_EVALUATOR_PROXY_TOKEN" \
    ANTHROPIC_BASE_URL=http://127.0.0.1:18765 \
    ANTHROPIC_AUTH_TOKEN="$PACK_EVALUATOR_PROXY_TOKEN" \
    CLAUDE_CODE_MAX_OUTPUT_TOKENS="$PACK_EVALUATOR_MAX_OUTPUT_TOKENS" \
    NO_PROXY=127.0.0.1,localhost \
    timeout --signal=TERM --kill-after=5s "${PREFLIGHT_TIMEOUT_SECONDS}s" \
    prlimit --nproc=256:256 --as=6442450944:6442450944 -- \
    "$NODE" "$ORCHESTRATOR" executor-preflight \
    --cli "$CLI" \
    --expected-cli-version "$PACK_PRODUCTION_CLI_VERSION" \
    --skill-a "$PREFLIGHT_SKILL_A" \
    --skill-b "$PREFLIGHT_SKILL_B" \
    --results-dir "$PREFLIGHT_RAW" \
    --evaluator-runtime-root "$RUNTIME_ROOT" \
    --generation-id "$PREFLIGHT_GENERATION_ID" \
    --evaluator-uid "$(id -u packeval)" \
    --evaluator-gid "$(id -g packeval)" \
    --task "$PREFLIGHT_TASK" \
    --model sonnet \
    --judge-model gpt-5.5 \
    --agent-timeout-ms "$AGENT_TIMEOUT_MS" \
    --timeout-ms 360000 \
    --idle-timeout-ms 240000 \
    --proxy-activity-file "$PACK_EVALUATOR_ACTIVITY_FILE" \
    > "$CLI_STDOUT" 2> "$CLI_STDERR" &
  COMMAND_PID=$!
  monitor_preflight_http "$COMMAND_PID" "$ACTIVITY_START_LINE"
  wait "$COMMAND_PID"
  COMMAND_EXIT_CODE=$?
  set -e

  DURATION_MS=$(( $(date +%s%3N) - STARTED_MS ))
  STDOUT_BYTES=$(wc -c < "$CLI_STDOUT")
  STDERR_BYTES=$(wc -c < "$CLI_STDERR")
  STDOUT_SHA256=$(sha256sum "$CLI_STDOUT" | awk '{print $1}')
  STDERR_SHA256=$(sha256sum "$CLI_STDERR" | awk '{print $1}')
  FINAL_EXECUTION_EVIDENCE=$(safe_execution_evidence "$CLI_STDOUT")
  FINAL_RUNNER_TRACE_EVIDENCE=$(safe_runner_trace_evidence "$CLI_STDOUT")
  FINAL_OUTER_EXECUTION=$(safe_outer_execution "$CLI_STDOUT")

  if [ -n "$HTTP_FATAL_STATUS" ]; then
    PREFLIGHT_ERROR_CLASS=deterministic_http
  elif [ -n "$HTTP_RETRYABLE_STATUS" ]; then
    PREFLIGHT_ERROR_CLASS=retryable_http
  else
    PREFLIGHT_ERROR_CLASS=$(jq -r '
      [.[].attempts[]? | select(.outcome == "failed") | .failureCategory] | first // "unknown"
    ' <<< "$FINAL_EXECUTION_EVIDENCE")
  fi

  if [ "$COMMAND_EXIT_CODE" -eq 0 ] && jq -e \
    --argjson projected "$FINAL_EXECUTION_EVIDENCE" '
    .schemaVersion == "marketplace.pack-executor-preflight/v1" and
    .mode == "pack-production-node-uid-nested-bwrap" and
    .outcome == "passed" and
    .errorClass == "none" and
    .outerExecution.exitCode == 0 and
    .outerExecution.signal == null and
    .outerExecution.timedOut == false and
    .outerExecution.stalled == false and
    .outerExecution.outputExceeded == false and
    .verdictCount == 1 and .errorCount == 0 and
    .cleanup.outcome == "passed" and
    .runnerTraceEvidence == $runnerTrace and
    $runnerTrace.schemaVersion == "marketplace.pack-executor-trace-evidence/v1" and
    $runnerTrace.deterministic == true and
    $runnerTrace.traceCount == 1 and
    $runnerTrace.eventCount == 2 and
    (.agentExecutionEvidence == $projected) and
    ($projected | length) == 2 and
    ($projected[0].phase == "run" and $projected[0].run == 1 and $projected[0].succeeded == true) and
    ($projected[1].phase == "judge" and $projected[1].run == 1 and $projected[1].succeeded == true) and
    ($projected[0].attempts | length) == 1 and
    ($projected[1].attempts | length) == 1 and
    ($projected[0].attempts[0].agent == "claude") and
    ($projected[1].attempts[0].agent == "codex") and
    all($projected[].attempts[];
      .attempt == 1 and .sandboxed == true and .outcome == "succeeded" and
      .failureCategory == "none" and .spawnErrorCode == null and
      .exitCode == 0 and .signal == null
    )
  ' --argjson runnerTrace "$FINAL_RUNNER_TRACE_EVIDENCE" "$CLI_STDOUT" >/dev/null 2>&1; then
    PREFLIGHT_OUTCOME=passed
    PREFLIGHT_ERROR_CLASS=none
  else
    PREFLIGHT_OUTCOME=command_failed
  fi

  ATTEMPT_RECORD=$(jq -cn \
    --argjson attempt "$ATTEMPT" \
    --arg outcome "$PREFLIGHT_OUTCOME" \
    --arg errorClass "$PREFLIGHT_ERROR_CLASS" \
    --argjson exitCode "$COMMAND_EXIT_CODE" \
    --argjson durationMs "$DURATION_MS" \
    --argjson stdoutBytes "$STDOUT_BYTES" \
    --argjson stderrBytes "$STDERR_BYTES" \
    --arg stdoutSha256 "$STDOUT_SHA256" \
    --arg stderrSha256 "$STDERR_SHA256" \
    --argjson outerExecution "$FINAL_OUTER_EXECUTION" \
    --argjson agentExecutionEvidence "$FINAL_EXECUTION_EVIDENCE" \
    --argjson runnerTraceEvidence "$FINAL_RUNNER_TRACE_EVIDENCE" \
    '{
      attempt: $attempt,
      outcome: $outcome,
      errorClass: $errorClass,
      exitCode: $exitCode,
      durationMs: $durationMs,
      stdoutBytes: $stdoutBytes,
      stderrBytes: $stderrBytes,
      stdoutSha256: $stdoutSha256,
      stderrSha256: $stderrSha256,
      outerExecution: $outerExecution,
      agentExecutionEvidence: $agentExecutionEvidence,
      runnerTraceEvidence: $runnerTraceEvidence
    }')
  COMMAND_ATTEMPTS=$(append_command_attempt "$COMMAND_ATTEMPTS" "$ATTEMPT_RECORD")

  if ! should_retry_preflight "$PREFLIGHT_OUTCOME" "$PREFLIGHT_ERROR_CLASS" "$ATTEMPT"; then
    break
  fi
  if cleanup_processes; then
    RETRY_CLEANUP_OUTCOME=passed
  else
    CLEANUP_RC=$?
    RETRY_CLEANUP_OUTCOME=$([ "$CLEANUP_RC" -eq 1 ] && printf failed || printf probe_failed)
    break
  fi
  sleep 5
done

COMMAND_ATTEMPTS=$(mark_recovered_command_attempts "$COMMAND_ATTEMPTS" "$PREFLIGHT_OUTCOME")

if cleanup_processes; then
  CLEANUP_OUTCOME=passed
else
  CLEANUP_RC=$?
  CLEANUP_OUTCOME=$([ "$CLEANUP_RC" -eq 1 ] && printf failed || printf probe_failed)
fi

if [ -n "${PACK_EVALUATOR_ACTIVITY_FILE:-}" ] && sudo test -f "$PACK_EVALUATOR_ACTIVITY_FILE"; then
  sudo tail -n "+$ACTIVITY_START_LINE" "$PACK_EVALUATOR_ACTIVITY_FILE" > "$ACTIVITY_SLICE" 2>/dev/null || true
fi
HTTP_EVIDENCE=$(summarize_preflight_http_activity < "$ACTIVITY_SLICE" 2>/dev/null || \
  printf '{"messages200":0,"responses200":0,"inferenceFatalStatus":null,"inferenceRetryableStatus":null,"auxiliaryRejectedCount":0}')
AUXILIARY_REJECTED_COUNT=$(jq -r '.auxiliaryRejectedCount // 0' <<< "$HTTP_EVIDENCE")
if [ "$AUXILIARY_REJECTED_COUNT" -gt 0 ]; then
  echo "::warning::Pack evaluator proxy rejected $AUXILIARY_REJECTED_COUNT auxiliary request(s) outside the inference endpoints"
fi

jq -n \
  --arg outcome "$PREFLIGHT_OUTCOME" \
  --arg errorClass "$PREFLIGHT_ERROR_CLASS" \
  --argjson commandAttempts "$COMMAND_ATTEMPTS" \
  --argjson executionEvidence "$FINAL_EXECUTION_EVIDENCE" \
  --argjson runnerTraceEvidence "$FINAL_RUNNER_TRACE_EVIDENCE" \
  --argjson outerExecution "$FINAL_OUTER_EXECUTION" \
  --argjson http "$HTTP_EVIDENCE" \
  --arg cleanupOutcome "$CLEANUP_OUTCOME" \
  --arg retryCleanupOutcome "$RETRY_CLEANUP_OUTCOME" \
  --arg marketplaceCommitSha "$PACK_EVALUATOR_MARKETPLACE_COMMIT_SHA" \
  --arg cliVersion "$PACK_PRODUCTION_CLI_VERSION" \
  --arg cliSha256 "$PACK_EVALUATOR_CLI_SHA256" \
  '{
    schemaVersion: "marketplace.pack-executor-preflight/v1",
    mode: "pack-production-node-uid-nested-bwrap",
    outcome: $outcome,
    errorClass: $errorClass,
    commandAttempts: $commandAttempts,
    outerExecution: $outerExecution,
    agentExecutionEvidence: $executionEvidence,
    runnerTraceEvidence: $runnerTraceEvidence,
    http: $http,
    cleanup: { outcome: $cleanupOutcome, retryOutcome: $retryCleanupOutcome },
    proofBinding: {
      marketplaceCommitSha: $marketplaceCommitSha,
      cliVersion: $cliVersion,
      cliSha256: $cliSha256
    }
  }' > "$PACK_DIAGNOSTICS_DIR/agent-preflight-diagnostics.json"

if [ -n "${PACK_EVALUATOR_ACTIVITY_FILE:-}" ] && sudo test -f "$PACK_EVALUATOR_ACTIVITY_FILE"; then
  sudo cp "$PACK_EVALUATOR_ACTIVITY_FILE" "$PACK_DIAGNOSTICS_DIR/proxy-activity.ndjson"
  sudo chown "$(id -u):$(id -g)" "$PACK_DIAGNOSTICS_DIR/proxy-activity.ndjson"
  chmod 0600 "$PACK_DIAGNOSTICS_DIR/proxy-activity.ndjson"
fi

if [ "$PREFLIGHT_OUTCOME" != passed ] || \
   [ "$CLEANUP_OUTCOME" != passed ] || \
   { [ "$RETRY_CLEANUP_OUTCOME" != not_needed ] && [ "$RETRY_CLEANUP_OUTCOME" != passed ]; } || \
   [ "$(jq -r '.messages200' <<< "$HTTP_EVIDENCE")" -lt 1 ] || \
   [ "$(jq -r '.responses200' <<< "$HTTP_EVIDENCE")" -lt 1 ]; then
  echo "::error::Pack evaluator same-path preflight failed: outcome=$PREFLIGHT_OUTCOME class=$PREFLIGHT_ERROR_CLASS cleanup=$CLEANUP_OUTCOME retry_cleanup=$RETRY_CLEANUP_OUTCOME"
  exit 1
fi
