import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import {
  chmodSync,
  existsSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  statSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEST_DIR = resolve(fileURLToPath(new URL('.', import.meta.url)));
const REPO_ROOT = resolve(TEST_DIR, '..', '..');
const WORKFLOW = readFileSync(join(REPO_ROOT, '.github/workflows/generate-packs.yml'), 'utf8');

function extractedCleanupFunctions() {
  const start = WORKFLOW.indexOf('          checkpoint_progress() {');
  const end = WORKFLOW.indexOf('          terminate_step() {', start);
  assert.ok(start >= 0 && end > start, 'workflow cleanup functions must be extractable');
  return WORKFLOW.slice(start, end).replace(/^ {10}/gm, '');
}

function processIsRunning(pid) {
  try {
    const stat = readFileSync(`/proc/${pid}/stat`, 'utf8');
    return !/\) Z /.test(stat);
  } catch (error) {
    if (error?.code === 'ENOENT') return false;
    throw error;
  }
}

test('linux bash cleanup publishes diagnostics before bounded process-tree termination', {
  skip: process.platform !== 'linux',
  timeout: 15_000,
}, async () => {
  const directory = mkdtempSync(join(tmpdir(), 'pack-cleanup-linux-'));
  const diagnostics = join(directory, 'pack-diagnostics');
  const targetScript = join(directory, 'target.sh');
  const harnessScript = join(directory, 'harness.sh');
  const readyFile = join(directory, 'ready');
  const grandchildPidFile = join(directory, 'grandchild.pid');
  const termReceivedFile = join(directory, 'term-received');
  const targetPgidFile = join(directory, 'target.pgid');
  writeFileSync(targetScript, [
    '#!/usr/bin/env bash',
    'set -u',
    'trap \'date +%s%N > "$TERM_RECEIVED_FILE"\' TERM',
    'bash -c \'trap "" TERM; printf "%s\\n" "$$" > "$GRANDCHILD_PID_FILE"; while :; do sleep 1; done\' &',
    'while :; do sleep 1; done',
  ].join('\n'));
  chmodSync(targetScript, 0o755);

  writeFileSync(harnessScript, [
    '#!/usr/bin/env bash',
    'set -euo pipefail',
    'mkdir -p "$GITHUB_WORKSPACE/pack-diagnostics"',
    'CHECKPOINT_LOCK="$GITHUB_WORKSPACE/checkpoint.lock"',
    'EVALUATOR_RESULTS_DIR="$GITHUB_WORKSPACE/evaluator-results"',
    'mkdir -p "$EVALUATOR_RESULTS_DIR"',
    'printf \'{"event":"scenario.progress"}\\n\' > "$EVALUATOR_RESULTS_DIR/evaluate-checkpoint.json"',
    'CHECKPOINT_PID=""',
    'EVALUATOR_PID=""',
    'EVALUATOR_FINISHED=false',
    'CLEANUP_DONE=false',
    'PROXY_LOG="$GITHUB_WORKSPACE/proxy.log"',
    'PROXY_ACTIVITY="$GITHUB_WORKSPACE/proxy.activity"',
    ': > "$PROXY_LOG"',
    ': > "$PROXY_ACTIVITY"',
    'group_alive() {',
    '  ps -o stat= -g "$TARGET_PGID" 2>/dev/null | grep -qv \'^[[:space:]]*Z\'',
    '}',
    'sudo() {',
    '  local command_name="$1"',
    '  shift',
    '  case "$command_name" in',
    '    kill) command kill "$@" ;;',
    '    pkill)',
    '      local signal=TERM',
    '      if [ "${1:-}" = "-TERM" ] || [ "${1:-}" = "-KILL" ]; then signal="${1#-}"; fi',
    '      command kill "-$signal" -- "-$TARGET_PGID" 2>/dev/null || true',
    '      ;;',
    '    pgrep) group_alive ;;',
    '    test) command test "$@" ;;',
    '    cp) command cp "$@" ;;',
    '    chown) return 0 ;;',
    '    rm) command rm "$@" ;;',
    '    *) "$command_name" "$@" ;;',
    '  esac',
    '}',
    'export -f sudo',
    extractedCleanupFunctions(),
    'setsid "$TARGET_SCRIPT" &',
    'EVALUATOR_PID=$!',
    'TARGET_PGID=$EVALUATOR_PID',
    'export TARGET_PGID',
    'printf "%s\\n" "$TARGET_PGID" > "$TARGET_PGID_FILE"',
    'while [ ! -s "$GRANDCHILD_PID_FILE" ]; do sleep 0.01; done',
    ': > "$READY_FILE"',
    'trap \'cleanup 143; trap - EXIT; exit 143\' TERM',
    'trap \'cleanup $?\' EXIT',
    'while :; do wait "$EVALUATOR_PID" || true; sleep 0.1; done',
  ].join('\n'));
  chmodSync(harnessScript, 0o755);

  const helper = spawn('bash', [harnessScript], {
    env: {
      ...process.env,
      GITHUB_WORKSPACE: directory,
      TARGET_SCRIPT: targetScript,
      READY_FILE: readyFile,
      GRANDCHILD_PID_FILE: grandchildPidFile,
      TERM_RECEIVED_FILE: termReceivedFile,
      TARGET_PGID_FILE: targetPgidFile,
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  let hardKilled = false;
  let hardKillTimer;
  try {
    for (let attempt = 0; attempt < 500 && !existsSync(readyFile); attempt += 1) {
      await new Promise((resolveWait) => setTimeout(resolveWait, 10));
    }
    assert.equal(existsSync(readyFile), true, 'cleanup harness did not become ready');
    const startedAt = Date.now();
    helper.kill('SIGTERM');
    hardKillTimer = setTimeout(() => {
      hardKilled = true;
      helper.kill('SIGKILL');
    }, 10_000);
    const [status, signal] = await once(helper, 'close');
    clearTimeout(hardKillTimer);
    assert.equal(hardKilled, false, 'cleanup exceeded the outer 10 second hard-kill budget');
    assert.equal(status, 143);
    assert.equal(signal, null);
    assert.ok(Date.now() - startedAt < 7_000, 'cleanup exceeded its inner 7 second budget');

    const marker = join(diagnostics, 'evaluator-interrupted.txt');
    const checkpoint = join(diagnostics, 'evaluate-checkpoint.json');
    assert.equal(readFileSync(marker, 'utf8'), 'evaluator_interrupted=true\n');
    assert.deepEqual(JSON.parse(readFileSync(checkpoint, 'utf8')), {
      event: 'scenario.progress',
    });
    assert.equal(statSync(marker).mode & 0o777, 0o600);
    assert.ok(statSync(marker).mtimeMs <= statSync(termReceivedFile).mtimeMs);
    assert.ok(statSync(checkpoint).mtimeMs <= statSync(termReceivedFile).mtimeMs);
    assert.equal(readdirSync(diagnostics).some((name) => name.includes('.tmp.')), false);
    assert.equal(existsSync(join(directory, 'pack-trusted')), false);

    const grandchildPid = Number(readFileSync(grandchildPidFile, 'utf8'));
    for (let attempt = 0; attempt < 200 && processIsRunning(grandchildPid); attempt += 1) {
      await new Promise((resolveWait) => setTimeout(resolveWait, 10));
    }
    assert.equal(processIsRunning(grandchildPid), false);
  } finally {
    if (hardKillTimer) clearTimeout(hardKillTimer);
    helper.kill('SIGKILL');
    if (existsSync(targetPgidFile)) {
      const pgid = Number(readFileSync(targetPgidFile, 'utf8'));
      try { process.kill(-pgid, 'SIGKILL'); } catch {}
    }
  }
});
