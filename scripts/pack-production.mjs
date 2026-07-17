#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';
import { createWriteStream, readFileSync, statSync } from 'node:fs';
import { chmod, chown, copyFile, mkdir, readFile, readdir, rename, writeFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { finished } from 'node:stream/promises';
import { fileURLToPath } from 'node:url';
import {
  EXECUTOR_PREFLIGHT_SKILLS,
  assertProductionExecutionPolicy,
  canonicalJson as canonicalPlanJson,
  createArtifactGate,
  planRuntimeValues,
  readArtifactGate,
  readExecutionPlan as readCanonicalExecutionPlan,
  validateExecutionPlan,
  verifyCliAgainstPlan,
  verifyRuntimeSourceFiles,
  verifySkillsAgainstPlan,
} from './pack-production-plan.mjs';

const RUNTIME_SOURCE_FILES = {
  'scripts/pack-production.mjs': fileURLToPath(import.meta.url),
  'scripts/pack-production-plan.mjs': fileURLToPath(
    new URL('./pack-production-plan.mjs', import.meta.url),
  ),
};

async function readExecutionPlan(file) {
  const plan = await readCanonicalExecutionPlan(file);
  planRuntimeValues(plan);
  await verifyRuntimeSourceFiles(plan, RUNTIME_SOURCE_FILES);
  return plan;
}

const CLI_SCHEMA = 'pack-generation-evaluation/v2';
const API_SCHEMA = 'skillstore.pack-evaluation/v4';
const STATUS_SCHEMA = 'skillstore.pack-production-status/v1';
const SLO_SCHEMA = 'marketplace.pack-production-slo/v1';
const VERIFICATION_SCHEMA = 'marketplace.pack-production-evaluation-verification/v1';
const INFRASTRUCTURE_FAILURE_SCHEMA = 'marketplace.pack-production-infrastructure-failure/v1';
const CLI_EVIDENCE_SCHEMA = 'marketplace.pack-production-cli-evidence/v1';
const CLI_ERROR_DIGESTS_PER_CATEGORY = 16;
const CLI_ERROR_DIGESTS_TOTAL = 64;
const CLI_AGENT_FAILURE_EVIDENCE_LIMIT = 64;
const CLI_ERROR_ITEMS_PER_ARRAY = 256;
const CLI_ERROR_ITEM_LIMIT_BYTES = 4096;
const CANDIDATE_TECHNICAL_ERROR_CODES = Object.freeze({
  evaluation: 'evaluation_reported_error',
  packVerification: 'pack_verification_reported_error',
  baselineVerification: 'baseline_verification_reported_error',
});
const KNOWN_CLI_EXIT = new Map([
  ['candidate_ready', 0],
  ['quality_rejected', 10],
  ['evaluation_inconclusive', 20],
  ['infrastructure_failed', 30],
]);
const EVALUATOR_OUTPUT_LIMIT_BYTES = 16 * 1024 * 1024;
const EXECUTOR_PREFLIGHT_CLI_SCHEMA = 'skillstore.pack-executor-preflight/v1';
const EXECUTOR_PREFLIGHT_TRACE_SCHEMA = 'marketplace.pack-executor-trace-evidence/v1';
const EXPECTED_REPOSITORY = 'aiskillstore/marketplace';
const EXPECTED_WORKFLOW = 'Generate Pack';
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function fail(message) {
  throw new Error(message);
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const args = { command };
  for (let index = 0; index < rest.length; index += 1) {
    const token = rest[index];
    if (!token.startsWith('--')) fail(`Unexpected argument: ${token}`);
    const key = token.slice(2);
    const value = rest[index + 1];
    if (!value || value.startsWith('--')) fail(`Missing value for --${key}`);
    args[key] = value;
    index += 1;
  }
  return args;
}

function required(args, name) {
  const value = args[name];
  if (!value) fail(`--${name} is required`);
  return value;
}

function positiveInteger(value, name, fallback) {
  if (value == null) return fallback;
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1) fail(`--${name} must be a positive integer`);
  return parsed;
}

export function canonicalJson(value) {
  return canonicalPlanJson(value);
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

async function sha256File(file) {
  return sha256(await readFile(file));
}

export function normalizeEvaluatorProgressLine(line) {
  if (typeof line !== 'string' || Buffer.byteLength(line, 'utf8') > 512) return null;
  let match = line.match(
    /^\[1\/5\] scenario ([a-z0-9][a-z0-9-]{0,79})@([0-9A-Za-z._-]{1,32}): [A-Za-z0-9][A-Za-z0-9 .,&()'\/-]{0,159}$/,
  );
  if (match) return `[1/5] scenario ${match[1]}@${match[2]}`;
  match = line.match(/^\[2\/5\] evaluating ([1-9][0-9]*) capability slots independently$/);
  if (match) return `[2/5] evaluating ${match[1]} capability slots independently`;
  if (line === '[3/5] composing a slot-complete pack') return line;
  match = line.match(/^\[4\/5\] verifying the whole pack ([1-9][0-9]*) times with deterministic artifact gates$/);
  if (match) return `[4/5] verifying the whole pack ${match[1]} times`;
  match = line.match(/^\[5\/5\] running ([1-9][0-9]*)-run no-skill baseline$/);
  if (match) return `[5/5] running ${match[1]}-run no-skill baseline`;
  match = line.match(/^\[5\/6\] running ([1-9][0-9]*)-run plan-only baseline with the identical DAG$/);
  if (match) return `[5/6] running ${match[1]}-run plan-only baseline`;
  if (line === '[6/7] running every viable unique finalist end-to-end for the true best-single baseline') {
    return '[6/7] running true best-single tournament';
  }
  match = line.match(/^\[7\/7\] running one leave-one-out comparison for each of ([2-4]) members$/);
  if (match) return `[7/7] running ${match[1]} leave-one-out comparisons`;
  match = line.match(/^\s{0,12}slot ([a-z0-9][a-z0-9-]{0,79}): finding candidates for [A-Za-z0-9 .,+_\/-]{1,200}$/);
  if (match) return `slot ${match[1]}: finding candidates`;
  match = line.match(
    /^\s{0,12}slot ([a-z0-9][a-z0-9-]{0,79}): verifying ([a-z0-9][a-z0-9-]{0,79})$/,
  );
  if (match) return `slot ${match[1]}: verifying ${match[2]}`;
  match = line.match(
    /^\s{0,12}slot ([a-z0-9][a-z0-9-]{0,79}): winner ([a-z0-9][a-z0-9-]{0,159}) after evaluating all ([1-2]) bounded candidates$/,
  );
  if (match) return `slot ${match[1]}: winner ${match[2]} after ${match[3]} candidates`;
  match = line.match(/^\s{0,12}pack ([a-z0-9][a-z0-9-]{0,85}): [a-z0-9-]+(?:, [a-z0-9-]+){1,3}$/);
  if (match) return `pack ${match[1]}: composition selected`;
  match = line.match(/^run ([1-9][0-9]*)\/([1-9][0-9]*): (executing task\.\.\.|judging output\.\.\.)$/);
  if (match) return `run ${match[1]}/${match[2]}: ${match[3]}`;
  match = line.match(
    /^run ([1-9][0-9]*)\/([1-9][0-9]*): score=(10|[0-9])\/10 task_completed=(true|false) used_skill=(true|false)(?: artifacts=(PASS|FAIL))?(?: \[ENV-BLOCKED\])?$/,
  );
  if (!match) return null;
  return `run ${match[1]}/${match[2]}: score=${match[3]}/10 task_completed=${match[4]} used_skill=${match[5]}`
    + (match[6] ? ` artifacts=${match[6]}` : '');
}

export function isSafeEvaluatorProgressLine(line) {
  return normalizeEvaluatorProgressLine(line) !== null;
}

export function allocateScenarioBudgetMs({
  remainingBudgetMs,
  remainingScenarios,
  maxScenarioMs,
  minimumFallbackMs,
}) {
  if (!Number.isSafeInteger(remainingBudgetMs) || remainingBudgetMs < 1) return 0;
  if (!Number.isSafeInteger(remainingScenarios) || remainingScenarios < 1) {
    fail('remainingScenarios must be a positive integer');
  }
  const maximum = Math.max(1, Math.floor(maxScenarioMs));
  const fallback = Math.max(1, Math.floor(minimumFallbackMs));
  if (remainingScenarios === 1) return Math.min(maximum, remainingBudgetMs);
  const reservedForFallbacks = fallback * (remainingScenarios - 1);
  const fairShare = Math.max(1, Math.floor(remainingBudgetMs / remainingScenarios));
  const available = remainingBudgetMs - reservedForFallbacks;
  return Math.min(maximum, Math.max(1, available > 0 ? available : fairShare));
}

function safeActivityToken(value, maximumLength = 128) {
  if (typeof value !== 'string' || value.length < 1 || value.length > maximumLength) return null;
  return /^[A-Za-z0-9_.:/\[\]-]+$/.test(value) ? value : null;
}

const INFRASTRUCTURE_FAILURE_STAGES = new Set([
  'contract_smoke',
  'agent_preflight',
  'evaluation',
]);
const INFRASTRUCTURE_FAILURE_REASONS = new Set([
  'deterministic_http',
  'timeout',
  'stalled',
  'terminal_report_missing',
  'contract_failed',
  'preflight_failed',
  'cancelled',
]);
const INFRASTRUCTURE_ERROR_CATEGORIES = new Set([
  'unknown_model_or_lane',
  'unsupported_parameter',
  'authentication_failed',
  'context_length_exceeded',
  'malformed_request',
  'other',
  'request_body_too_large',
  'model_not_allowed',
  'invalid_output_token_limit',
]);
const INTERRUPTED_SIGNALS = new Set(['SIGINT', 'SIGTERM', 'SIGHUP']);

export function normalizeInterruptedSignal(value) {
  if (!INTERRUPTED_SIGNALS.has(value)) fail('Evaluator interruption signal is not allowlisted');
  return value;
}

export function normalizeInfrastructureFailure(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail('Infrastructure failure evidence must be an object');
  }
  if (value.schemaVersion !== INFRASTRUCTURE_FAILURE_SCHEMA) {
    fail(`Unsupported infrastructure failure schema: ${value.schemaVersion}`);
  }
  if (!INFRASTRUCTURE_FAILURE_STAGES.has(value.stage)) {
    fail(`Unsupported infrastructure failure stage: ${value.stage}`);
  }
  if (!INFRASTRUCTURE_FAILURE_REASONS.has(value.reason)) {
    fail(`Unsupported infrastructure failure reason: ${value.reason}`);
  }
  const diagnosticSha256 = value.diagnosticSha256 == null ? null : value.diagnosticSha256;
  if (
    diagnosticSha256 != null
    && (typeof diagnosticSha256 !== 'string' || !/^[0-9a-f]{64}$/.test(diagnosticSha256))
  ) {
    fail('Infrastructure diagnostic hash is invalid');
  }
  const status = value.status == null ? null : Number(value.status);
  if (status != null && (!Number.isSafeInteger(status) || status < 100 || status > 599)) {
    fail('Infrastructure HTTP status is invalid');
  }
  const errorCategory = value.errorCategory == null ? null : value.errorCategory;
  if (errorCategory != null && !INFRASTRUCTURE_ERROR_CATEGORIES.has(errorCategory)) {
    fail('Infrastructure error category is not allowlisted');
  }
  const signal = value.signal == null ? null : normalizeInterruptedSignal(value.signal);
  if ((value.reason === 'cancelled') !== (signal != null)) {
    fail('Cancelled infrastructure evidence must contain exactly one allowlisted signal');
  }
  return {
    schemaVersion: INFRASTRUCTURE_FAILURE_SCHEMA,
    stage: value.stage,
    reason: value.reason,
    status,
    path: safeActivityToken(value.path),
    model: safeActivityToken(value.model),
    errorCategory,
    diagnosticSha256,
    ...(signal == null ? {} : { signal }),
  };
}

export function buildInfrastructureCliReport({
  scenario,
  context,
  failure,
  startedAt,
  completedAt,
}) {
  const normalizedFailure = normalizeInfrastructureFailure({
    ...failure,
    schemaVersion: INFRASTRUCTURE_FAILURE_SCHEMA,
  });
  return {
    schemaVersion: CLI_SCHEMA,
    generationId: context.generationId,
    evaluationStartedAt: startedAt,
    evaluationCompletedAt: completedAt,
    outcome: 'infrastructure_failed',
    outcomeReason: `${normalizedFailure.stage}:${normalizedFailure.reason}`,
    autoPublishEligible: false,
    scenario,
    slotEvaluations: [],
    manifest: null,
    composition: null,
    packVerification: null,
    baselineVerification: null,
    baselineScoreDelta: null,
    errors: [],
    infrastructureFailure: normalizedFailure,
  };
}

export function deterministicHttpFailureFromActivity(contents) {
  if (typeof contents !== 'string') return null;
  const lines = contents.split('\n').filter(Boolean);
  for (let index = lines.length - 1; index >= 0; index -= 1) {
    let activity;
    try {
      activity = JSON.parse(lines[index]);
    } catch {
      continue;
    }
    if (!['response', 'circuit_open'].includes(activity?.phase)) continue;
    const status = Number(activity.status);
    if (!Number.isSafeInteger(status) || status < 400 || status >= 500 || [408, 425, 429].includes(status)) {
      continue;
    }
    return {
      status,
      path: safeActivityToken(activity.path),
      model: safeActivityToken(activity.model),
      requestNumber: Number.isSafeInteger(activity.requestNumber) ? activity.requestNumber : null,
      errorType: safeActivityToken(activity.errorType),
      errorCode: safeActivityToken(activity.errorCode),
      errorParam: safeActivityToken(activity.errorParam),
      errorCategory: INFRASTRUCTURE_ERROR_CATEGORIES.has(activity.errorCategory)
        ? activity.errorCategory
        : null,
      errorMessageSha256: /^[a-f0-9]{64}$/.test(activity.errorMessageSha256 || '')
        ? activity.errorMessageSha256
        : null,
    };
  }
  return null;
}

function terminateEvaluatorProcesses(uid) {
  const userId = String(uid);
  spawnSync('/usr/bin/pkill', ['-TERM', '-u', userId], { stdio: 'ignore' });
  spawnSync('/bin/sleep', ['0.1'], { stdio: 'ignore' });
  spawnSync('/usr/bin/pkill', ['-KILL', '-u', userId], { stdio: 'ignore' });
  const remaining = spawnSync('/usr/bin/pgrep', ['-u', userId], { stdio: 'ignore' });
  if (remaining.status === 0) fail(`Evaluator uid ${userId} still has live processes`);
}

export async function prepareScenarioRuntime(runtimeRoot, generationId, uid, gid, baseEnv) {
  const scenarioRoot = resolve(runtimeRoot, generationId);
  const home = resolve(scenarioRoot, 'home');
  const tmp = resolve(scenarioRoot, 'tmp');
  const codexHome = resolve(scenarioRoot, 'codex-home');
  const codexLog = resolve(codexHome, 'log');
  const codexSessions = resolve(codexHome, 'sessions');
  const sourceCodexHome = baseEnv.CODEX_HOME;
  if (!sourceCodexHome) fail('CODEX_HOME is required for evaluator identity separation');

  await mkdir(runtimeRoot, { recursive: true, mode: 0o711 });
  await chmod(runtimeRoot, 0o711);
  await mkdir(scenarioRoot, { recursive: true, mode: 0o711 });
  await chmod(scenarioRoot, 0o711);
  await Promise.all([
    mkdir(home, { recursive: true, mode: 0o700 }),
    mkdir(tmp, { recursive: true, mode: 0o700 }),
    // Codex 0.139 creates ephemeral state directly under CODEX_HOME. Keep the
    // directory root-owned and sticky so the evaluator can create only its own
    // state while the immutable root-owned config remains non-replaceable.
    mkdir(codexHome, { recursive: true, mode: 0o1777 }),
    mkdir(codexLog, { recursive: true, mode: 0o700 }),
    mkdir(codexSessions, { recursive: true, mode: 0o700 }),
  ]);
  await Promise.all([
    chown(home, uid, gid),
    chown(tmp, uid, gid),
    chown(codexLog, uid, gid),
    chown(codexSessions, uid, gid),
  ]);
  await Promise.all([
    chmod(home, 0o700),
    chmod(tmp, 0o700),
    chmod(codexHome, 0o1777),
    chmod(codexLog, 0o700),
    chmod(codexSessions, 0o700),
  ]);
  const configFile = resolve(codexHome, 'config.toml');
  await copyFile(resolve(sourceCodexHome, 'config.toml'), configFile);
  await chmod(configFile, 0o444);

  return {
    cwd: home,
    env: {
      ...baseEnv,
      HOME: home,
      TMPDIR: tmp,
      CODEX_HOME: codexHome,
    },
  };
}

export async function runEvaluatorProcess(command, commandArgs, options) {
  const startedAt = Date.now();
  const stdoutStream = createWriteStream(options.stdoutFile, { flags: 'w', mode: 0o600 });
  const stderrStream = createWriteStream(options.stderrFile, { flags: 'w', mode: 0o600 });
  const progressStream = createWriteStream(options.progressFile, { flags: 'a', mode: 0o600 });
  const onProgress = options.onProgress ?? ((message) => process.stderr.write(`${message}\n`));
  const heartbeatMs = positiveInteger(options.heartbeatMs, 'heartbeat-ms', 60_000);
  const timeoutMs = positiveInteger(options.timeoutMs, 'scenario-timeout-ms', 150 * 60_000);
  const idleTimeoutMs = positiveInteger(options.idleTimeoutMs, 'scenario-idle-timeout-ms', 20 * 60_000);
  const killGraceMs = positiveInteger(options.killGraceMs, 'kill-grace-ms', 3_000);
  const label = options.label ?? 'unknown';
  let stdoutBytes = 0;
  let stderrBytes = 0;
  let outputExceeded = false;
  let timedOut = false;
  let stalled = false;
  let interruptedSignal = null;
  let deterministicHttpFailure = null;
  let stderrRemainder = '';
  let killTimer = null;
  let terminationRequested = false;
  const stderrDigest = createHash('sha256');
  let checkpointWrites = Promise.resolve();
  let checkpointError = null;
  let progressSequence = options.progressSequenceStart ?? 0;
  let lastActivityAt = Date.now();
  let externalActivityMtimeMs = 0;

  const markActivity = () => {
    lastActivityAt = Date.now();
  };

  const writeProgressEvent = (event) => {
    const entry = {
      schemaVersion: 'marketplace.pack-production-progress/v1',
      seq: ++progressSequence,
      at: new Date().toISOString(),
      ...event,
    };
    progressStream.write(`${JSON.stringify(entry)}\n`);
    if (options.checkpointFile) {
      const temporary = `${options.checkpointFile}.tmp`;
      checkpointWrites = checkpointWrites
        .then(() => writeFile(temporary, `${JSON.stringify(entry, null, 2)}\n`, { mode: 0o600 }))
        .then(() => rename(temporary, options.checkpointFile))
        .catch((error) => {
          checkpointError ??= error;
        });
    }
  };

  writeProgressEvent({
    event: 'scenario.started',
    scenarioId: label,
    generationId: options.generationId ?? null,
    scenarioIndex: options.scenarioIndex ?? null,
    scenarioCount: options.scenarioCount ?? null,
    timeoutMs,
    idleTimeoutMs,
  });
  onProgress(`[pack-evaluator] scenario=${label} started timeout=${Math.ceil(timeoutMs / 60_000)}m`);

  const child = spawn(command, commandArgs, {
    cwd: options.cwd,
    env: options.env,
    ...(options.uid == null ? {} : { uid: options.uid }),
    ...(options.gid == null ? {} : { gid: options.gid }),
    detached: process.platform !== 'win32',
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  const signalProcessGroup = (signal) => {
    if (process.platform !== 'win32' && child.pid) {
      try {
        process.kill(-child.pid, signal);
        return;
      } catch {
        // The group may already be gone; fall through to the direct child.
      }
    }
    child.kill(signal);
  };

  const requestTermination = (reason, signal = 'SIGTERM') => {
    if (terminationRequested) return false;
    terminationRequested = true;
    writeProgressEvent({
      event: reason,
      scenarioId: label,
      elapsedMs: Date.now() - startedAt,
      signal,
    });
    signalProcessGroup(signal);
    if (killTimer == null) {
      killTimer = setTimeout(() => signalProcessGroup('SIGKILL'), killGraceMs);
    }
    return true;
  };

  const stopForOutputLimit = (kind) => {
    if (outputExceeded) return;
    outputExceeded = true;
    onProgress(`[pack-evaluator] scenario=${label} stopped: ${kind} exceeded 16 MiB`);
    requestTermination('scenario.output_limit_exceeded');
    child.stdout.destroy();
    child.stderr.destroy();
  };

  const writeBoundedStdout = (chunk) => {
    if (outputExceeded) return;
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    const previous = stdoutBytes;
    const remaining = Math.max(0, EVALUATOR_OUTPUT_LIMIT_BYTES - stdoutBytes);
    if (remaining > 0) stdoutStream.write(buffer.subarray(0, remaining));
    stdoutBytes += buffer.length;
    if (previous + buffer.length > EVALUATOR_OUTPUT_LIMIT_BYTES) stopForOutputLimit('stdout');
  };

  const recordSafeProgress = (line) => {
    const message = normalizeEvaluatorProgressLine(line);
    if (!message) return;
    stderrStream.write(`${message}\n`);
    markActivity();
    writeProgressEvent({
      event: 'scenario.progress',
      scenarioId: label,
      elapsedMs: Date.now() - startedAt,
      message,
    });
    onProgress(`[pack-evaluator] scenario=${label} ${message}`);
  };

  child.stdout.on('data', writeBoundedStdout);
  child.stderr.on('data', (chunk) => {
    if (outputExceeded) return;
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    const previous = stderrBytes;
    stderrBytes += buffer.length;
    const remaining = Math.max(0, EVALUATOR_OUTPUT_LIMIT_BYTES - previous);
    if (remaining > 0) stderrDigest.update(buffer.subarray(0, remaining));
    if (previous + buffer.length > EVALUATOR_OUTPUT_LIMIT_BYTES) {
      stopForOutputLimit('stderr');
      return;
    }
    const text = `${stderrRemainder}${chunk.toString('utf8')}`;
    const lines = text.split(/\r?\n/);
    stderrRemainder = lines.pop() ?? '';
    if (stderrRemainder.length > 4096) stderrRemainder = '';
    for (const line of lines) recordSafeProgress(line);
  });

  const heartbeatTimer = setInterval(() => {
    const elapsedMs = Date.now() - startedAt;
    writeProgressEvent({
      event: 'scenario.heartbeat',
      scenarioId: label,
      elapsedMs,
    });
    onProgress(`[pack-evaluator] scenario=${label} heartbeat elapsed=${Math.floor(elapsedMs / 1000)}s`);
  }, heartbeatMs);
  const probeExternalActivity = () => {
    if (options.externalActivityFile) {
      try {
        const activity = statSync(options.externalActivityFile);
        if (activity.mtimeMs > externalActivityMtimeMs) {
          externalActivityMtimeMs = activity.mtimeMs;
          markActivity();
          if (activity.size > 1024 * 1024) {
            requestTermination('scenario.activity_limit_exceeded');
            return;
          }
          deterministicHttpFailure = deterministicHttpFailureFromActivity(
            readFileSync(options.externalActivityFile, 'utf8'),
          );
          if (deterministicHttpFailure && requestTermination('scenario.deterministic_http_failure')) {
            writeProgressEvent({
              event: 'scenario.http_circuit_opened',
              scenarioId: label,
              elapsedMs: Date.now() - startedAt,
              ...deterministicHttpFailure,
            });
            onProgress(
              `[pack-evaluator] scenario=${label} stopped after deterministic HTTP ${deterministicHttpFailure.status}`,
            );
          }
        }
      } catch (error) {
        if (error?.code !== 'ENOENT' && requestTermination('scenario.activity_probe_failed')) {
          stalled = true;
          onProgress(`[pack-evaluator] scenario=${label} activity probe failed`);
        }
      }
    }
  };
  const activityTimer = options.externalActivityFile
    ? setInterval(probeExternalActivity, 500)
    : null;
  const idleTimer = setInterval(() => {
    if (stalled || terminationRequested) return;
    probeExternalActivity();
    if (Date.now() - lastActivityAt >= idleTimeoutMs) {
      if (requestTermination('scenario.stalled')) {
        stalled = true;
        onProgress(`[pack-evaluator] scenario=${label} stalled for ${Math.ceil(idleTimeoutMs / 60_000)}m`);
      }
    }
  }, Math.max(10, Math.min(heartbeatMs, 30_000, Math.floor(idleTimeoutMs / 4))));
  const scenarioTimer = setTimeout(() => {
    if (requestTermination('scenario.timeout')) {
      timedOut = true;
      onProgress(`[pack-evaluator] scenario=${label} reached its ${Math.ceil(timeoutMs / 60_000)}m hard limit`);
    }
  }, timeoutMs);
  const onSignal = (signal) => {
    if (requestTermination('scenario.signal_received', signal)) interruptedSignal = signal;
  };
  const onSigint = () => onSignal('SIGINT');
  const onSigterm = () => onSignal('SIGTERM');
  const onSighup = () => onSignal('SIGHUP');
  process.once('SIGINT', onSigint);
  process.once('SIGTERM', onSigterm);
  process.once('SIGHUP', onSighup);

  let result;
  let processError = null;
  try {
    result = await new Promise((resolveChild, rejectChild) => {
      child.once('error', rejectChild);
      child.once('close', (status, signal) => resolveChild({ status, signal }));
    });
  } catch (error) {
    processError = error;
    writeProgressEvent({
      event: 'scenario.spawn_failed',
      scenarioId: label,
      elapsedMs: Date.now() - startedAt,
      errorCode: error?.code ?? null,
    });
  } finally {
    signalProcessGroup('SIGTERM');
    await new Promise((resolveWait) => setTimeout(resolveWait, 50));
    signalProcessGroup('SIGKILL');
    clearInterval(heartbeatTimer);
    clearInterval(idleTimer);
    if (activityTimer != null) clearInterval(activityTimer);
    clearTimeout(scenarioTimer);
    if (killTimer != null) clearTimeout(killTimer);
    process.removeListener('SIGINT', onSigint);
    process.removeListener('SIGTERM', onSigterm);
    process.removeListener('SIGHUP', onSighup);
    if (stderrRemainder) recordSafeProgress(stderrRemainder);
    writeProgressEvent({
      event: 'scenario.process_exited',
      scenarioId: label,
      elapsedMs: Date.now() - startedAt,
      status: result?.status ?? null,
      signal: result?.signal ?? null,
      timedOut,
      stalled,
      outputExceeded,
      stdoutBytes,
      stderrBytes,
      stderrSha256: stderrDigest.digest('hex'),
      interruptedSignal,
      deterministicHttpFailure,
    });
    stdoutStream.end();
    stderrStream.end();
    progressStream.end();
    await Promise.all([
      finished(stdoutStream),
      finished(stderrStream),
      finished(progressStream),
    ]);
    await checkpointWrites;
  }

  if (processError) throw processError;
  if (checkpointError) throw new Error(`Unable to write evaluator checkpoint: ${checkpointError.message}`);
  return {
    ...result,
    timedOut,
    stalled,
    outputExceeded,
    interruptedSignal,
    deterministicHttpFailure,
    stdoutBytes,
    stderrBytes,
    durationMs: Date.now() - startedAt,
    progressSequence,
  };
}

async function readJson(file) {
  return JSON.parse(await readFile(file, 'utf8'));
}

async function writeJson(file, value) {
  await writeFile(file, `${JSON.stringify(value, null, 2)}\n`);
}

function cliVersion(cli) {
  const result = spawnSync(cli, ['--version'], { encoding: 'utf8' });
  if (result.status !== 0) fail(`Cannot read CLI version: ${result.stderr || result.stdout}`);
  const version = `${result.stdout}\n${result.stderr}`.match(/[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z._-]+)?/)?.[0];
  if (!version) fail('CLI version output is not parseable');
  return version;
}

function artifactReferences(raw) {
  const evidence = raw.packVerification?.artifactEvidence ?? [];
  return [...new Set(evidence.flatMap((run) => {
    const required = (run.requirements ?? []).flatMap((requirement) => requirement.validMatches ?? []);
    if (required.length > 0) return required;
    return (run.artifacts ?? [])
      .filter((artifact) => artifact.valid)
      .map((artifact) => artifact.relativePath);
  }))].slice(0, 20);
}

function apiVerdicts(raw) {
  return (raw.packVerification?.verdicts ?? []).map((verdict) => ({
    usedSkill: Boolean(verdict.used_skill),
    usedSkills: Array.isArray(verdict.used_skills) ? [...new Set(verdict.used_skills.map(String))] : [],
    taskCompleted: Boolean(verdict.task_completed),
    artifactVerified: verdict.artifact_requirements_met === true,
    envBlocked: Boolean(verdict.env_blocked),
    score: Number(verdict.score),
    reason: String(verdict.reason || 'No grader reason supplied'),
    issues: Array.isArray(verdict.issues) ? verdict.issues.map(String) : [],
  }));
}

function requiredCapabilitySlots(raw) {
  if (!Array.isArray(raw.scenario?.capabilitySlots)) {
    fail('candidate_ready scenario lacks capability slot evidence');
  }
  const required = raw.scenario.capabilitySlots
    .filter((slot) => slot?.required === true)
    .map((slot) => String(slot.id ?? ''));
  if (
    required.length < 1
    || new Set(required).size !== required.length
    || required.some((slot) => !/^[a-z0-9][a-z0-9-]{0,79}$/.test(slot))
  ) {
    fail('candidate_ready scenario has invalid required capability slots');
  }
  return required;
}

function apiSlotAssignments(raw, manifestSkills, requiredSlots) {
  const source = raw.manifest?.slot_assignments;
  if (!source || typeof source !== 'object' || Array.isArray(source)) {
    fail('candidate_ready manifest lacks slot assignment evidence');
  }
  const manifestSkillSet = new Set(manifestSkills);
  const assignments = {};
  for (const [slotId, values] of Object.entries(source)) {
    if (!/^[a-z0-9][a-z0-9-]{0,79}$/.test(slotId) || !Array.isArray(values)) {
      fail(`candidate_ready manifest has invalid assignment for slot ${slotId}`);
    }
    const skills = [...new Set(values.map(String))];
    if (skills.length !== values.length || skills.some((skill) => !manifestSkillSet.has(skill))) {
      fail(`candidate_ready slot ${slotId} has duplicate or non-manifest Skills`);
    }
    assignments[slotId] = skills;
  }
  for (const slotId of requiredSlots) {
    if (!Array.isArray(assignments[slotId]) || assignments[slotId].length < 1) {
      fail(`candidate_ready required slot ${slotId} is not assigned`);
    }
  }
  if (Object.keys(assignments).length !== requiredSlots.length) {
    fail('candidate_ready manifest contains non-required capability slot assignments');
  }
  const assignedSkills = new Set(Object.values(assignments).flat());
  if (manifestSkills.some((skill) => !assignedSkills.has(skill))) {
    fail('candidate_ready manifest contains a Skill with no slot assignment');
  }
  return assignments;
}

function object(value, name) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${name} must be an object`);
  return value;
}

function nonEmptyString(value, name, pattern) {
  if (typeof value !== 'string' || !value.trim() || (pattern && !pattern.test(value))) {
    fail(`${name} is missing or invalid`);
  }
  return value;
}

function exactStrings(value, name, { length, pattern, allowDuplicates = false } = {}) {
  if (!Array.isArray(value) || (length != null && value.length !== length)) {
    fail(`${name} must contain exactly ${length} items`);
  }
  const result = value.map((item, index) => nonEmptyString(item, `${name}[${index}]`, pattern));
  if (!allowDuplicates && new Set(result).size !== result.length) fail(`${name} must not contain duplicates`);
  return result;
}

function exactBooleans(value, name, length) {
  if (!Array.isArray(value) || value.length !== length || value.some((item) => typeof item !== 'boolean')) {
    fail(`${name} must contain exactly ${length} boolean items`);
  }
  return [...value];
}

function exactScores(value, name, length = 3) {
  if (!Array.isArray(value) || value.length !== length) fail(`${name} must contain exactly ${length} scores`);
  return value.map((score, index) => {
    const parsed = Number(score);
    if (!Number.isFinite(parsed) || parsed < 0 || parsed > 10) fail(`${name}[${index}] is invalid`);
    return parsed;
  });
}

function median(values) {
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function apiExecutionDag(raw, manifestSkills, slotAssignments, requiredSlots) {
  const source = object(raw.manifest?.execution_dag, 'candidate_ready manifest execution DAG');
  if (source.schema_version !== 'skillstore.pack-execution-dag/v1') {
    fail('candidate_ready execution DAG schema is invalid');
  }
  if (!Array.isArray(source.nodes) || source.nodes.length !== requiredSlots.length) {
    fail('candidate_ready execution DAG nodes must match the required slots');
  }
  const nodes = source.nodes.map((value, index) => {
    const node = object(value, `candidate_ready execution DAG node ${index + 1}`);
    const id = nonEmptyString(node.id, `candidate_ready execution DAG node ${index + 1} id`, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
    const dependsOn = exactStrings(node.depends_on, `candidate_ready execution DAG node ${id} dependencies`, {
      pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
    });
    const artifactIds = exactStrings(node.artifact_ids, `candidate_ready execution DAG node ${id} artifacts`, {
      pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
    });
    return {
      id,
      instruction: nonEmptyString(node.instruction, `candidate_ready execution DAG node ${id} instruction`),
      dependsOn,
      artifactIds,
    };
  });
  if (canonicalJson(nodes.map((node) => node.id)) !== canonicalJson(requiredSlots)) {
    fail('candidate_ready execution DAG nodes must follow the exact required slot order');
  }
  const nodeOrder = new Map(nodes.map((node, index) => [node.id, index]));
  nodes.forEach((node, index) => {
    if (node.dependsOn.some((dependency) => !nodeOrder.has(dependency) || nodeOrder.get(dependency) >= index)) {
      fail(`candidate_ready execution DAG node ${node.id} has an invalid dependency`);
    }
  });
  if (!Array.isArray(source.handoffs)) fail('candidate_ready execution DAG handoffs are missing');
  const handoffs = source.handoffs.map((value, index) => {
    const handoff = object(value, `candidate_ready execution DAG handoff ${index + 1}`);
    if (handoff.contract !== 'validated-artifacts-only') {
      fail(`candidate_ready execution DAG handoff ${index + 1} has an invalid contract`);
    }
    return {
      from: nonEmptyString(handoff.from, `candidate_ready execution DAG handoff ${index + 1} from`),
      to: nonEmptyString(handoff.to, `candidate_ready execution DAG handoff ${index + 1} to`),
      artifactIds: exactStrings(handoff.artifact_ids, `candidate_ready execution DAG handoff ${index + 1} artifacts`, {
        pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
      }),
      contract: 'validated-artifacts-only',
    };
  });
  const expectedHandoffs = nodes.flatMap((node) => node.dependsOn.map((dependency) => `${dependency}->${node.id}`)).sort();
  const actualHandoffs = handoffs.map((handoff) => `${handoff.from}->${handoff.to}`).sort();
  if (canonicalJson(actualHandoffs) !== canonicalJson(expectedHandoffs)) {
    fail('candidate_ready execution DAG handoffs do not exactly match its dependencies');
  }
  if (!Array.isArray(source.skill_bindings) || source.skill_bindings.length !== manifestSkills.length) {
    fail('candidate_ready execution DAG bindings must match all manifest Skills');
  }
  const skillBindings = source.skill_bindings.map((value, index) => {
    const binding = object(value, `candidate_ready execution DAG binding ${index + 1}`);
    const canonicalId = nonEmptyString(binding.canonical_id, `candidate_ready execution DAG binding ${index + 1} canonical id`, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
    const slotIds = exactStrings(binding.slot_ids, `candidate_ready execution DAG binding ${canonicalId} slots`, {
      pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
    });
    return {
      canonicalId,
      contentHash: nonEmptyString(binding.content_hash, `candidate_ready execution DAG binding ${canonicalId} content hash`, /^[0-9a-f]{64}$/),
      version: nonEmptyString(binding.version, `candidate_ready execution DAG binding ${canonicalId} version`),
      slotIds,
    };
  });
  if (canonicalJson(skillBindings.map((binding) => binding.canonicalId)) !== canonicalJson(manifestSkills)) {
    fail('candidate_ready execution DAG bindings must follow manifest Skill order');
  }
  for (const binding of skillBindings) {
    const expectedSlots = requiredSlots.filter((slotId) => slotAssignments[slotId].includes(binding.canonicalId));
    if (canonicalJson(binding.slotIds) !== canonicalJson(expectedSlots)) {
      fail(`candidate_ready execution DAG binding for ${binding.canonicalId} has incorrect slots`);
    }
  }
  const workflowDigest = nonEmptyString(source.workflow_digest, 'candidate_ready execution DAG workflow digest', /^[0-9a-f]{64}$/);
  const bindingDigest = nonEmptyString(source.binding_digest, 'candidate_ready execution DAG binding digest', /^[0-9a-f]{64}$/);
  const expectedWorkflowDigest = sha256(canonicalJson({
    schema_version: source.schema_version,
    nodes: nodes.map((node) => ({
      id: node.id,
      instruction: node.instruction,
      depends_on: node.dependsOn,
      artifact_ids: node.artifactIds,
    })),
    handoffs: handoffs.map((handoff) => ({
      from: handoff.from,
      to: handoff.to,
      artifact_ids: handoff.artifactIds,
      contract: handoff.contract,
    })),
  }));
  const expectedBindingDigest = sha256(canonicalJson({
    workflow_digest: expectedWorkflowDigest,
    skill_bindings: skillBindings.map((binding) => ({
      canonical_id: binding.canonicalId,
      content_hash: binding.contentHash,
      version: binding.version,
      slot_ids: binding.slotIds,
    })),
  }));
  if (workflowDigest !== expectedWorkflowDigest || bindingDigest !== expectedBindingDigest) {
    fail('candidate_ready execution DAG digests do not match canonical evidence');
  }
  const usageGuideMarker = nonEmptyString(source.usage_guide_marker, 'candidate_ready execution DAG usage guide marker');
  if (usageGuideMarker !== `<!-- skillstore-execution-binding:${bindingDigest} -->`) {
    fail('candidate_ready execution DAG usage guide marker does not bind the binding digest');
  }
  return {
    schemaVersion: 'skillstore.pack-execution-dag/v1',
    workflowDigest,
    bindingDigest,
    nodes,
    handoffs,
    skillBindings,
    usageGuideMarker,
  };
}

function validateCandidateTournament(raw, requiredSlots) {
  if (!Array.isArray(raw.slotEvaluations)) fail('candidate_ready slot tournament is missing');
  const bySlot = new Map(raw.slotEvaluations.map((entry) => [entry?.slot?.id, entry]));
  const viableSkills = [];
  for (const slotId of requiredSlots) {
    const tournament = bySlot.get(slotId);
    if (!tournament || !Array.isArray(tournament.candidates) || tournament.candidates.length < 1 || tournament.candidates.length > 4) {
      fail(`candidate_ready slot ${slotId} must retain one to four bounded candidate results`);
    }
    const candidateSlugs = [];
    for (const [index, candidate] of tournament.candidates.entries()) {
      const slug = nonEmptyString(candidate?.slug, `candidate_ready slot ${slotId} candidate ${index + 1}`, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
      if (!candidate?.summary || !Array.isArray(candidate.verdicts) || !Array.isArray(candidate.errors)) {
        fail(`candidate_ready slot ${slotId} candidate ${slug} lacks terminal execution evidence`);
      }
      candidateSlugs.push(slug);
    }
    if (new Set(candidateSlugs).size !== candidateSlugs.length) {
      fail(`candidate_ready slot ${slotId} contains duplicate candidates`);
    }
    if (!Array.isArray(tournament.eligible)) fail(`candidate_ready slot ${slotId} eligible candidates are missing`);
    const expectedEligible = tournament.candidates
      .filter((candidate) => candidate.summary?.passed === true && candidate.summary?.usedSkillEver === true)
      .sort((left, right) =>
        Number(right.summary.artifactsPassed) - Number(left.summary.artifactsPassed)
        || Number(right.summary.medianScore) - Number(left.summary.medianScore)
        || Number(right.summary.minimumScore) - Number(left.summary.minimumScore)
        || Number(right.summary.taskCompletedRate) - Number(left.summary.taskCompletedRate)
        || Number(right.summary.usedSkillRate) - Number(left.summary.usedSkillRate)
        || Number(right.hits) - Number(left.hits)
        || String(left.slug).localeCompare(String(right.slug))
      )
      .map((candidate) => candidate.slug);
    const actualEligible = tournament.eligible.map((candidate) => candidate?.slug);
    if (canonicalJson(actualEligible) !== canonicalJson(expectedEligible) || actualEligible.length < 1) {
      fail(`candidate_ready slot ${slotId} did not retain every viable bounded candidate`);
    }
    if (tournament.winner?.slug !== actualEligible[0]) {
      fail(`candidate_ready slot ${slotId} winner is not the ranked tournament winner`);
    }
    viableSkills.push(...actualEligible);
  }
  return [...new Set(viableSkills)].sort();
}

function apiBestSingle(raw, packScore, executionDag, tournamentViableSkills, evaluationSuite) {
  const source = object(raw.bestSingleEvidence, 'candidate_ready best-single verification');
  if (source.complete !== true) fail('candidate_ready best-single tournament is incomplete');
  const eligibleCandidateSkills = exactStrings(
    source.eligibleCandidateSkills,
    'candidate_ready best-single eligible candidate Skills',
    { pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/ }
  );
  if (canonicalJson([...eligibleCandidateSkills].sort()) !== canonicalJson(tournamentViableSkills)) {
    fail('candidate_ready best-single eligible candidates differ from the complete slot tournament');
  }
  if (!Array.isArray(source.competitors) || source.competitors.length !== eligibleCandidateSkills.length) {
    fail('candidate_ready best-single verification must compare every eligible candidate end to end');
  }
  const competitors = source.competitors.map((value, index) => {
    const competitor = object(value, `candidate_ready best-single competitor ${index + 1}`);
    const skill = nonEmptyString(competitor.skill, `candidate_ready best-single competitor ${index + 1} Skill`, /^[a-z0-9]+(?:-[a-z0-9]+)*$/);
    const verification = object(competitor.verification, `candidate_ready best-single competitor ${skill} verification`);
    const scores = exactScores(verification.summary?.scores, `candidate_ready best-single competitor ${skill} scores`);
    const artifactPasses = exactBooleans(
      verification.artifactEvidence?.map((run) => run?.passed),
      `candidate_ready best-single competitor ${skill} artifact passes`,
      3
    );
    const deterministicPasses = exactBooleans(
      verification.deterministicValidations?.map((run) => run?.passed),
      `candidate_ready best-single competitor ${skill} deterministic passes`,
      3
    );
    const variantIds = exactStrings(
      verification.deterministicValidations?.map((run) => run?.variantId),
      `candidate_ready best-single competitor ${skill} variant ids`,
      { length: 3, pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/ }
    );
    const errors = exactStrings(verification.errors ?? [], `candidate_ready best-single competitor ${skill} errors`);
    if (errors.length > 0) fail(`candidate_ready best-single competitor ${skill} contains technical errors`);
    if (competitor.workflowDigest !== executionDag.workflowDigest) {
      fail(`candidate_ready best-single competitor ${skill} did not use the neutral execution DAG`);
    }
    if (canonicalJson(variantIds) !== canonicalJson(evaluationSuite.variantIds)) {
      fail(`candidate_ready best-single competitor ${skill} did not use the paired variant order`);
    }
    return {
      skill,
      workflowDigest: executionDag.workflowDigest,
      variantIds,
      scores,
      artifactPasses,
      deterministicPasses,
      errors,
    };
  });
  if (canonicalJson(competitors.map((item) => item.skill)) !== canonicalJson(eligibleCandidateSkills)) {
    fail('candidate_ready best-single competitors differ from the eligible candidate set');
  }
  if (canonicalJson(raw.treatmentWorkflowDigests?.bestSingle) !== canonicalJson(
    competitors.map((competitor) => ({ skill: competitor.skill, workflowDigest: competitor.workflowDigest }))
  )) {
    fail('candidate_ready best-single treatment digests are incomplete or inconsistent');
  }
  const ranked = [...competitors].sort((left, right) =>
    right.deterministicPasses.filter(Boolean).length - left.deterministicPasses.filter(Boolean).length
    || right.artifactPasses.filter(Boolean).length - left.artifactPasses.filter(Boolean).length
    || median(right.scores) - median(left.scores)
    || Math.min(...right.scores) - Math.min(...left.scores)
    || left.skill.localeCompare(right.skill)
  );
  const winnerSkill = nonEmptyString(source.winnerSkill, 'candidate_ready best-single winner Skill');
  if (winnerSkill !== ranked[0]?.skill) {
    fail('candidate_ready best-single winner is not the true end-to-end maximum');
  }
  const score = median(ranked[0].scores);
  const improvement = packScore - score;
  if (Number(raw.bestSingleScoreDelta) !== improvement || improvement < 1) {
    fail('candidate_ready Pack must improve on the true best-single baseline by at least one point');
  }
  return { eligibleCandidateSkills, competitors, winnerSkill, score, improvement };
}

function apiAblation(raw, manifestSkills, executionDag, runs) {
  if (!Array.isArray(raw.ablationVerification) || raw.ablationVerification.length !== manifestSkills.length) {
    fail('candidate_ready ablation must contain exactly one treatment per manifest Skill');
  }
  const result = raw.ablationVerification.map((value, index) => {
    const item = object(value, `candidate_ready ablation ${index + 1}`);
    const removedSkill = nonEmptyString(item.removedSkill, `candidate_ready ablation ${index + 1} removed Skill`);
    if (removedSkill !== manifestSkills[index]) fail('candidate_ready ablation must follow manifest Skill order');
    const remainingSkills = exactStrings(item.remainingSkills, `candidate_ready ablation for ${removedSkill} remaining Skills`, {
      length: manifestSkills.length - 1,
      pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
    });
    if (canonicalJson(remainingSkills) !== canonicalJson(manifestSkills.filter((skill) => skill !== removedSkill))) {
      fail(`candidate_ready ablation for ${removedSkill} has the wrong remaining Skills`);
    }
    const binding = executionDag.skillBindings.find((candidate) => candidate.canonicalId === removedSkill);
    if (item.workflowDigest !== executionDag.workflowDigest) {
      fail(`candidate_ready ablation for ${removedSkill} did not use the neutral execution DAG`);
    }
    const boundSlotIds = exactStrings(item.boundSlotIds, `candidate_ready ablation for ${removedSkill} bound slots`, {
      pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
    });
    if (canonicalJson(boundSlotIds) !== canonicalJson(binding.slotIds)) {
      fail(`candidate_ready ablation for ${removedSkill} is not bound to the execution DAG slots`);
    }
    const expectedArtifacts = [...new Set(binding.slotIds.flatMap((slotId) =>
      executionDag.nodes.find((node) => node.id === slotId)?.artifactIds ?? []
    ))];
    const boundArtifactIds = exactStrings(item.boundArtifactIds, `candidate_ready ablation for ${removedSkill} bound artifacts`, {
      pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
    });
    if (canonicalJson(boundArtifactIds) !== canonicalJson(expectedArtifacts)) {
      fail(`candidate_ready ablation for ${removedSkill} is not bound to the execution DAG artifacts`);
    }
    const fullArtifactPasses = exactBooleans(item.fullArtifactPasses, `candidate_ready ablation for ${removedSkill} full results`, runs);
    const artifactPasses = exactBooleans(item.ablatedArtifactPasses, `candidate_ready ablation for ${removedSkill} treatment results`, runs);
    const fullSlotPasses = exactBooleans(item.fullSlotPasses, `candidate_ready ablation for ${removedSkill} full slot results`, runs);
    const slotPasses = exactBooleans(item.ablatedSlotPasses, `candidate_ready ablation for ${removedSkill} treatment slot results`, runs);
    const deterministicMarginalContribution = item.deterministicMarginalContribution === true;
    if (!deterministicMarginalContribution || !fullSlotPasses.every(Boolean) || !slotPasses.every((passed) => !passed)) {
      fail(`candidate_ready ablation for ${removedSkill} did not prove deterministic marginal value`);
    }
    return {
      removedSkill,
      remainingSkills,
      workflowDigest: executionDag.workflowDigest,
      boundSlotIds,
      boundArtifactIds,
      fullSlotPasses,
      slotPasses,
      fullArtifactPasses,
      artifactPasses,
      deterministicMarginalContribution,
    };
  });
  if (canonicalJson(raw.deterministicMarginalSkills) !== canonicalJson(manifestSkills)) {
    fail('candidate_ready every manifest Skill must have deterministic marginal value');
  }
  if (canonicalJson(raw.treatmentWorkflowDigests?.leaveOneOut) !== canonicalJson(
    result.map((item) => ({ removedSkill: item.removedSkill, workflowDigest: executionDag.workflowDigest }))
  )) {
    fail('candidate_ready leave-one-out treatment digests are incomplete or inconsistent');
  }
  return result;
}

function apiEvaluationSuite(raw) {
  const source = object(raw.evaluationSuiteEvidence, 'candidate_ready evaluation suite');
  if (source.schemaVersion !== 'skillstore.pack-evaluation-suite/v1' || source.executed !== true) {
    fail('candidate_ready must execute the v1 paired evaluation suite');
  }
  const variantIds = exactStrings(source.variantIds, 'candidate_ready evaluation suite variant ids', {
    length: 3,
    pattern: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
  });
  if (source.hiddenVariantCount !== 2) fail('candidate_ready evaluation suite must contain exactly two hidden variants');
  const digest = (field, allowDuplicates = false) => exactStrings(source[field], `candidate_ready evaluation suite ${field}`, {
    length: 3,
    pattern: /^[0-9a-f]{64}$/,
    allowDuplicates,
  });
  const taskDigests = digest('taskDigests', true);
  const fixtureDigests = digest('fixtureDigests');
  const validatorDigests = digest('validatorDigests', true);
  if (new Set(taskDigests).size !== 1 || new Set(validatorDigests).size !== 1) {
    fail('candidate_ready paired variants must use identical task and validator contracts');
  }
  return {
    schemaVersion: 'skillstore.pack-evaluation-suite/v1',
    executed: true,
    variantIds,
    hiddenVariantCount: 2,
    taskDigests,
    fixtureDigests,
    validatorDigests,
  };
}

function apiUsageProvenance(raw, executionDag, evaluationSuite) {
  const source = object(raw.usageProvenance, 'candidate_ready usage provenance');
  if (source.deterministic !== true || source.source !== 'runner-trace-v1') {
    fail('candidate_ready requires deterministic runner Skill usage provenance');
  }
  if (!Array.isArray(source.traces) || source.traces.length !== evaluationSuite.variantIds.length) {
    fail('candidate_ready usage provenance must cover every paired variant');
  }
  const bindingById = new Map(executionDag.skillBindings.map((binding) => [binding.canonicalId, binding]));
  const traces = source.traces.map((value, traceIndex) => {
    const trace = object(value, `candidate_ready usage trace ${traceIndex + 1}`);
    if (trace.variantId !== evaluationSuite.variantIds[traceIndex] || !Array.isArray(trace.events) || trace.events.length < 1) {
      fail(`candidate_ready usage trace ${traceIndex + 1} is missing or out of order`);
    }
    const events = trace.events.map((value, eventIndex) => {
      const event = object(value, `candidate_ready usage trace ${traceIndex + 1} event ${eventIndex + 1}`);
      const canonicalId = nonEmptyString(event.canonicalId, 'candidate_ready usage event canonical id');
      const binding = bindingById.get(canonicalId);
      if (
        !binding
        || event.contentHash !== binding.contentHash
        || event.version !== binding.version
        || event.sequence !== eventIndex + 1
      ) {
        fail('candidate_ready usage event does not match the exact bound Skill identity and sequence');
      }
      return {
        canonicalId,
        contentHash: binding.contentHash,
        version: binding.version,
        sequence: event.sequence,
      };
    });
    const observed = new Set(events.map((event) => event.canonicalId));
    if (executionDag.skillBindings.some((binding) => !observed.has(binding.canonicalId))) {
      fail(`candidate_ready usage trace ${trace.variantId} did not execute every bound Skill`);
    }
    return { variantId: trace.variantId, events };
  });
  return { deterministic: true, source: 'runner-trace-v1', traces };
}

const CLI_ERROR_SOURCES = [
  ['evaluation', (raw) => raw.errors],
  ['composition', (raw) => raw.composition],
  ['pack_verification', (raw) => raw.packVerification],
  ['baseline_verification', (raw) => raw.baselineVerification],
  ['slot_evaluation', (raw) => raw.slotEvaluations],
  ['best_single', (raw) => raw.bestSingleEvidence],
  ['ablation', (raw) => raw.ablationVerification],
];
const CLI_OUTCOME_CATEGORIES = Object.freeze({
  candidate_ready: 'passed',
  quality_rejected: 'quality',
  evaluation_inconclusive: 'inconclusive',
  infrastructure_failed: 'infrastructure',
});

function cliOutcomeCategory(outcome) {
  if (!Object.hasOwn(CLI_OUTCOME_CATEGORIES, outcome)) fail(`Unsupported CLI outcome: ${outcome}`);
  return CLI_OUTCOME_CATEGORIES[outcome];
}

function strictErrorStrings(value, name, { required = false } = {}) {
  if (value == null && !required) return [];
  if (!Array.isArray(value)) fail(`${name} must be an array of error strings`);
  if (value.length > CLI_ERROR_ITEMS_PER_ARRAY) {
    fail(`${name} exceeds the bounded error item count`);
  }
  return value.map((item, index) => {
    if (
      typeof item !== 'string'
      || item.length < 1
      || Buffer.byteLength(item, 'utf8') > CLI_ERROR_ITEM_LIMIT_BYTES
    ) {
      fail(`${name}[${index}] must be a bounded non-empty error string`);
    }
    return item;
  });
}

function collectErrorStrings(value, captureRoot = false, result = [], path = 'CLI report') {
  if (captureRoot) {
    result.push(...strictErrorStrings(value, `${path}.errors`, { required: true }));
    return result;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => collectErrorStrings(item, false, result, `${path}[${index}]`));
    return result;
  }
  if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) {
      if (key === 'errors') {
        result.push(...strictErrorStrings(item, `${path}.errors`));
      } else {
        collectErrorStrings(item, false, result, `${path}.${key}`);
      }
    }
  }
  return result;
}

const AGENT_FAILURE_CATEGORIES = new Set([
  'none',
  'spawn_spec',
  'spawn_error',
  'timeout',
  'signal',
  'sandbox_runtime',
  'state_storage',
  'authentication',
  'model_route',
  'cli_arguments',
  'upstream_transport',
  'trace_protocol',
  'nonzero_exit',
  'empty_output',
]);
const AGENT_SPAWN_ERROR_CODES = new Set([
  'EACCES', 'EAGAIN', 'EMFILE', 'ENFILE', 'ENOENT', 'ENOMEM', 'EPERM', 'OTHER',
]);

function boundedAgentExecutionAttempt(value, path) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail(`${path} must be an Agent execution evidence object`);
  }
  if (
    value.schemaVersion !== 'skillstore.agent-execution-evidence/v1'
    || !['claude', 'codex', 'gemini'].includes(value.agent)
    || !Number.isSafeInteger(value.attempt) || value.attempt < 1 || value.attempt > 3
    || typeof value.sandboxed !== 'boolean'
    || !['succeeded', 'failed'].includes(value.outcome)
    || !AGENT_FAILURE_CATEGORIES.has(value.failureCategory)
    || (value.spawnErrorCode !== null && !AGENT_SPAWN_ERROR_CODES.has(value.spawnErrorCode))
    || (value.exitCode !== null && (!Number.isSafeInteger(value.exitCode) || value.exitCode < 0 || value.exitCode > 255))
    || (value.signal !== null && (typeof value.signal !== 'string' || !/^SIG[A-Z0-9]{1,12}$/.test(value.signal)))
    || !Number.isSafeInteger(value.durationMs) || value.durationMs < 0 || value.durationMs > 1_200_000
    || !Number.isSafeInteger(value.stdoutBytes) || value.stdoutBytes < 0 || value.stdoutBytes > EVALUATOR_OUTPUT_LIMIT_BYTES
    || !Number.isSafeInteger(value.stderrBytes) || value.stderrBytes < 0 || value.stderrBytes > EVALUATOR_OUTPUT_LIMIT_BYTES
    || typeof value.stdoutSha256 !== 'string' || !/^[0-9a-f]{64}$/.test(value.stdoutSha256)
    || typeof value.stderrSha256 !== 'string' || !/^[0-9a-f]{64}$/.test(value.stderrSha256)
  ) {
    fail(`${path} is not bounded Agent execution evidence`);
  }
  return {
    agent: value.agent,
    attempt: value.attempt,
    sandboxed: value.sandboxed,
    outcome: value.outcome,
    failureCategory: value.failureCategory,
    spawnErrorCode: value.spawnErrorCode,
    exitCode: value.exitCode,
    signal: value.signal,
    durationMs: value.durationMs,
    stdoutBytes: value.stdoutBytes,
    stderrBytes: value.stderrBytes,
    stdoutSha256: value.stdoutSha256,
    stderrSha256: value.stderrSha256,
  };
}

function collectAgentExecutionInvocations(value, result = [], path = 'CLI report') {
  const stack = [{ value, path, depth: 0 }];
  let visitedNodes = 0;
  while (stack.length > 0) {
    const current = stack.pop();
    visitedNodes += 1;
    if (visitedNodes > 250_000) fail('CLI report exceeds the Agent evidence traversal node budget');
    if (current.depth > 32) fail('CLI report exceeds the Agent evidence traversal depth budget');
    if (Array.isArray(current.value)) {
      if (current.value.length > 10_000) fail(`${current.path} exceeds the traversal container budget`);
      for (let index = current.value.length - 1; index >= 0; index -= 1) {
        stack.push({
          value: current.value[index],
          path: `${current.path}[${index}]`,
          depth: current.depth + 1,
        });
      }
      continue;
    }
    if (!current.value || typeof current.value !== 'object') continue;
    const entries = Object.entries(current.value);
    if (entries.length > 512) fail(`${current.path} exceeds the traversal object-key budget`);
    for (let index = entries.length - 1; index >= 0; index -= 1) {
      const [key, item] = entries[index];
      if (key !== 'agentExecutionEvidence') {
        stack.push({
          value: item,
          path: `${current.path}.${key}`,
          depth: current.depth + 1,
        });
        continue;
      }
      const evidencePath = `${current.path}.${key}`;
      if (!Array.isArray(item) || item.length > 20) {
        fail(`${evidencePath} must be a bounded Agent invocation array`);
      }
      item.forEach((invocation, invocationIndex) => {
        const invocationPath = `${evidencePath}[${invocationIndex}]`;
        if (
          !invocation || typeof invocation !== 'object' || Array.isArray(invocation)
          || !['run', 'judge'].includes(invocation.phase)
          || !Number.isSafeInteger(invocation.run) || invocation.run < 1 || invocation.run > 10
          || typeof invocation.succeeded !== 'boolean'
          || !Array.isArray(invocation.attempts) || invocation.attempts.length > 9
        ) {
          fail(`${invocationPath} must be bounded Agent invocation evidence`);
        }
        result.push({
          phase: invocation.phase,
          run: invocation.run,
          succeeded: invocation.succeeded,
          attempts: invocation.attempts.map((attempt, attemptIndex) =>
            boundedAgentExecutionAttempt(attempt, `${invocationPath}.attempts[${attemptIndex}]`)
          ),
        });
        if (result.length > 512) fail('CLI report exceeds the bounded Agent invocation count');
      });
    }
  }
  return result;
}

function safeAgentExecutionEvidence(raw) {
  const invocations = collectAgentExecutionInvocations(raw);
  const failedInvocations = invocations.filter((invocation) => !invocation.succeeded);
  const failedAttempts = invocations.flatMap((invocation) =>
    invocation.attempts
      .filter((attempt) => attempt.outcome === 'failed')
      .map((attempt) => ({
        phase: invocation.phase,
        run: invocation.run,
        recovered: invocation.succeeded,
        ...attempt,
      }))
  );
  return {
    schemaVersion: 'marketplace.pack-production-agent-execution-evidence/v1',
    invocations: invocations.length,
    attempts: invocations.reduce((count, invocation) => count + invocation.attempts.length, 0),
    failedInvocations: failedInvocations.length,
    failedAttempts: failedAttempts.length,
    recoveredFailedAttempts: failedAttempts.filter((attempt) => attempt.recovered).length,
    capturedFailures: Math.min(failedAttempts.length, CLI_AGENT_FAILURE_EVIDENCE_LIMIT),
    truncated: failedAttempts.length > CLI_AGENT_FAILURE_EVIDENCE_LIMIT,
    failures: failedAttempts.slice(0, CLI_AGENT_FAILURE_EVIDENCE_LIMIT),
  };
}

function isoInstant(value, name) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(value)) {
    fail(`${name} is not a canonical UTC instant`);
  }
  const parsed = new Date(value);
  if (!Number.isFinite(parsed.getTime()) || parsed.toISOString() !== value) {
    fail(`${name} is not a valid UTC instant`);
  }
  return value;
}

function safeInfrastructureEvidence(value) {
  if (value == null) return null;
  const failure = normalizeInfrastructureFailure(value);
  return {
    schemaVersion: INFRASTRUCTURE_FAILURE_SCHEMA,
    stage: failure.stage,
    reason: failure.reason,
    status: failure.status,
    errorCategory: failure.errorCategory,
    diagnosticSha256: failure.diagnosticSha256,
    pathSha256: failure.path == null ? null : sha256(failure.path),
    modelSha256: failure.model == null ? null : sha256(failure.model),
    ...(failure.signal == null ? {} : { signal: failure.signal }),
  };
}

export function buildSafeCliEvidence(raw, context) {
  if (typeof raw.outcomeReason !== 'string') fail('CLI outcome reason must be a string');
  let remainingErrorDigests = CLI_ERROR_DIGESTS_TOTAL;
  const categories = CLI_ERROR_SOURCES.map(([category, read]) => {
    const errors = collectErrorStrings(read(raw), category === 'evaluation', [], category);
    const allDigests = errors.map((error) => sha256(error)).sort();
    const capturedCount = Math.min(
      allDigests.length,
      CLI_ERROR_DIGESTS_PER_CATEGORY,
      remainingErrorDigests,
    );
    const digests = allDigests.slice(0, capturedCount);
    remainingErrorDigests -= digests.length;
    return {
      category,
      count: errors.length,
      capturedCount,
      truncated: capturedCount < errors.length,
      sha256: digests,
    };
  }).filter((entry) => entry.count > 0);
  const totalErrors = categories.reduce((count, entry) => count + entry.count, 0);
  const capturedErrorDigests = categories.reduce((count, entry) => count + entry.capturedCount, 0);
  return {
    schemaVersion: CLI_EVIDENCE_SCHEMA,
    sourceSchemaVersion: CLI_SCHEMA,
    generationId: context.generationId,
    scenarioId: context.scenarioId,
    outcome: raw.outcome,
    outcomeCategory: cliOutcomeCategory(raw.outcome),
    startedAt: isoInstant(raw.evaluationStartedAt, 'CLI evaluation start'),
    completedAt: isoInstant(raw.evaluationCompletedAt, 'CLI evaluation completion'),
    rawReportSha256: sha256(canonicalJson(raw)),
    outcomeReasonSha256: sha256(raw.outcomeReason),
    counts: {
      slotEvaluations: Array.isArray(raw.slotEvaluations) ? raw.slotEvaluations.length : 0,
      manifestSkills: Array.isArray(raw.manifest?.skills) ? raw.manifest.skills.length : 0,
      packVerdicts: Array.isArray(raw.packVerification?.verdicts) ? raw.packVerification.verdicts.length : 0,
      baselineVerdicts: Array.isArray(raw.baselineVerification?.verdicts) ? raw.baselineVerification.verdicts.length : 0,
      errors: totalErrors,
      errorDigestsCaptured: capturedErrorDigests,
      errorDigestsTruncated: capturedErrorDigests < totalErrors,
    },
    errorEvidence: categories,
    agentExecutionEvidence: safeAgentExecutionEvidence(raw),
    infrastructureFailure: safeInfrastructureEvidence(raw.infrastructureFailure),
  };
}

export function buildInfrastructureApiEvaluation({
  scenario,
  context,
  failure,
  startedAt,
  completedAt,
  sourceEvidenceSha256,
}) {
  const normalizedFailure = normalizeInfrastructureFailure({
    ...failure,
    schemaVersion: INFRASTRUCTURE_FAILURE_SCHEMA,
  });
  if (!/^[0-9a-f]{64}$/.test(sourceEvidenceSha256 || '')) {
    fail('Infrastructure source evidence hash is invalid');
  }
  const requiredSlots = requiredCapabilitySlots({ scenario });
  const safeEvidence = {
    schemaVersion: CLI_EVIDENCE_SCHEMA,
    sourceSchemaVersion: 'marketplace.pack-production-cancellation-recovery/v1',
    source: 'cancelled-run-recovery',
    generationId: context.generationId,
    scenarioId: context.scenarioId,
    outcome: 'infrastructure_failed',
    outcomeCategory: 'infrastructure',
    startedAt: isoInstant(startedAt, 'recovery evaluation start'),
    completedAt: isoInstant(completedAt, 'recovery evaluation completion'),
    sourceEvidenceSha256,
    outcomeReasonSha256: sha256(`${normalizedFailure.stage}:${normalizedFailure.reason}`),
    counts: {
      slotEvaluations: 0,
      manifestSkills: 0,
      packVerdicts: 0,
      baselineVerdicts: 0,
      errors: 0,
      errorDigestsCaptured: 0,
      errorDigestsTruncated: false,
    },
    errorEvidence: [],
    agentExecutionEvidence: {
      schemaVersion: 'marketplace.pack-production-agent-execution-evidence/v1',
      invocations: 0,
      attempts: 0,
      failedInvocations: 0,
      failedAttempts: 0,
      recoveredFailedAttempts: 0,
      capturedFailures: 0,
      truncated: false,
      failures: [],
    },
    infrastructureFailure: safeInfrastructureEvidence(normalizedFailure),
  };
  const unsigned = {
    schemaVersion: API_SCHEMA,
    generationId: context.generationId,
    workflow: {
      repository: EXPECTED_REPOSITORY,
      runId: context.runId,
      runAttempt: context.runAttempt,
      runUrl: `https://github.com/${EXPECTED_REPOSITORY}/actions/runs/${context.runId}`,
      commitSha: context.commitSha,
    },
    scenario: {
      id: scenario.id,
      version: String(scenario.version),
      task: scenario.task,
      slug: scenario.slug,
      name: scenario.name,
      tags: scenario.tags,
      requiredCapabilitySlots: requiredSlots,
    },
    evaluator: {
      cliVersion: context.cliVersion,
      cliSha256: context.cliSha256,
      model: context.model,
      judgeModel: context.judgeModel,
      ...(context.executionPlanDigest ? {
        executionPlanDigest: context.executionPlanDigest,
        modelRevision: context.modelRevision,
        modelPinType: context.modelPinType,
        judgeModelRevision: context.judgeModelRevision,
        judgeModelPinType: context.judgeModelPinType,
      } : {}),
      startedAt: safeEvidence.startedAt,
      completedAt: safeEvidence.completedAt,
    },
    outcome: 'infrastructure_failed',
    candidate: null,
    evidence: { cliReport: safeEvidence },
  };
  return { ...unsigned, evidenceDigest: sha256(canonicalJson(unsigned)) };
}

export function buildApiEvaluation(raw, context) {
  if (raw.schemaVersion !== CLI_SCHEMA) fail(`Unsupported CLI report schema: ${raw.schemaVersion}`);
  if (!KNOWN_CLI_EXIT.has(raw.outcome)) fail(`Unsupported CLI outcome: ${raw.outcome}`);
  if (raw.generationId !== context.generationId) fail('CLI report generationId changed during evaluation');
  if (raw.scenario?.id !== context.scenarioId) fail('CLI report scenario differs from the queue plan');

  const requiredSlots = requiredCapabilitySlots(raw);

  let candidate = null;
  if (raw.outcome === 'candidate_ready') {
    const summary = raw.packVerification?.summary;
    const baseline = raw.baselineVerification?.summary;
    const verdicts = apiVerdicts(raw);
    if (!raw.manifest || !summary || !baseline || verdicts.length === 0) {
      fail('candidate_ready report lacks manifest, pack verification, baseline, or verdicts');
    }
    const references = artifactReferences(raw);
    const artifactKind = raw.scenario.requiredArtifacts?.length > 0 ? 'file' : 'text';
    const produced = artifactKind === 'file' ? references.length > 0 : summary.taskCompletedRate === 1;
    const manifestSkills = Array.isArray(raw.manifest.skills) ? raw.manifest.skills.map(String) : [];
    const manifestSkillSet = new Set(manifestSkills);
    if (manifestSkills.length < 2 || manifestSkills.length > 4 || manifestSkillSet.size !== manifestSkills.length) {
      fail('candidate_ready report must contain two to four distinct manifest Skills');
    }
    const slotAssignments = apiSlotAssignments(raw, manifestSkills, requiredSlots);
    const tournamentViableSkills = validateCandidateTournament(raw, requiredSlots);
    const executionDag = apiExecutionDag(raw, manifestSkills, slotAssignments, requiredSlots);
    if (verdicts.length !== 3) fail('candidate_ready report must contain exactly three final-run verdicts');
    verdicts.forEach((verdict, index) => {
      if (verdict.usedSkill !== (verdict.usedSkills.length > 0)) {
        fail(`candidate_ready run ${index + 1} has inconsistent used_skill and used_skills evidence`);
      }
      if (verdict.usedSkills.length < 2) {
        fail(`candidate_ready run ${index + 1} used fewer than two distinct Skills`);
      }
      if (verdict.usedSkills.some((skill) => !manifestSkillSet.has(skill))) {
        fail(`candidate_ready run ${index + 1} claims Skill use outside the manifest`);
      }
      if (!verdict.taskCompleted || !verdict.artifactVerified || verdict.envBlocked || verdict.score < 7) {
        fail(`candidate_ready run ${index + 1} did not pass the task, artifact, environment, and score gates`);
      }
    });
    const verdictUsedSkills = [...new Set(verdicts.flatMap((verdict) => verdict.usedSkills))].sort();
    const summaryUsedSkills = Array.isArray(summary.usedSkills)
      ? [...new Set(summary.usedSkills.map(String))].sort()
      : [];
    if (canonicalJson(verdictUsedSkills) !== canonicalJson(summaryUsedSkills)) {
      fail('candidate_ready summary usedSkills differs from final-run verdicts');
    }
    if (manifestSkills.some((skill) => !summaryUsedSkills.includes(skill))) {
      fail('candidate_ready manifest contains a Skill with no final-run use evidence');
    }
    const minimumDistinctSkillsUsed = Number(summary.minimumDistinctSkillsUsed);
    const distinctSkillUseRate = Number(summary.distinctSkillUseRate);
    const minimumScore = Number(summary.minimumScore);
    const minimumRunScore = Number(summary.minimumRunScore);
    if (
      minimumDistinctSkillsUsed < 2
      || distinctSkillUseRate !== 1
      || minimumScore < 7
      || minimumRunScore < 7
    ) {
      fail('candidate_ready summary does not satisfy the multi-Skill and per-run score gates');
    }
    if (raw.composition?.fallbackUsed) fail('candidate_ready report used composition fallback');
    const compositionErrors = strictErrorStrings(
      raw.composition?.errors,
      'candidate_ready composition errors',
      { required: true },
    );
    const evaluationErrors = strictErrorStrings(
      raw.errors,
      'candidate_ready evaluation errors',
      { required: true },
    ).filter((error) => !compositionErrors.includes(error));
    const packErrors = strictErrorStrings(
      raw.packVerification?.errors,
      'candidate_ready pack verification errors',
      { required: true },
    );
    const baselineErrors = strictErrorStrings(
      raw.baselineVerification?.errors,
      'candidate_ready baseline verification errors',
      { required: true },
    );
    const technicalErrorCodes = [
      ...(evaluationErrors.length > 0 ? [CANDIDATE_TECHNICAL_ERROR_CODES.evaluation] : []),
      ...(packErrors.length > 0 ? [CANDIDATE_TECHNICAL_ERROR_CODES.packVerification] : []),
      ...(baselineErrors.length > 0 ? [CANDIDATE_TECHNICAL_ERROR_CODES.baselineVerification] : []),
    ];
    const baselineScores = Array.isArray(baseline.scores) ? baseline.scores.map(Number) : [];
    const baselineRuns = Number(baseline.runs);
    if (
      baselineRuns !== 3
      || baselineScores.length !== baselineRuns
      || baselineScores.some((score) => !Number.isFinite(score) || score < 0 || score > 10)
    ) {
      fail('candidate_ready baseline lacks exactly three valid run scores');
    }
    const treatmentWorkflowDigests = object(
      raw.treatmentWorkflowDigests,
      'candidate_ready treatment workflow digests'
    );
    if (
      treatmentWorkflowDigests.fullPack !== executionDag.workflowDigest
      || treatmentWorkflowDigests.planOnly !== executionDag.workflowDigest
    ) {
      fail('candidate_ready full Pack and plan-only baseline must use the same neutral execution DAG');
    }
    const evaluationSuite = apiEvaluationSuite(raw);
    const usageProvenance = apiUsageProvenance(raw, executionDag, evaluationSuite);
    const ablation = apiAblation(raw, manifestSkills, executionDag, verdicts.length);
    const bestSingle = apiBestSingle(
      raw,
      Number(summary.medianScore),
      executionDag,
      tournamentViableSkills,
      evaluationSuite
    );
    candidate = {
      manifest: {
        name: raw.manifest.name,
        slug: raw.manifest.slug,
        description: raw.manifest.description,
        scenarioTags: raw.manifest.scenario_tags,
        riskFlags: raw.manifest.risk_flags,
        skills: manifestSkills,
        slotAssignments,
        executionDag,
        rationale: raw.manifest.rationale,
      },
      fitness: {
        score: summary.medianScore,
        passed: Boolean(summary.passed && summary.usedSkillEver),
        runs: verdicts.length,
        usedSkillRate: summary.usedSkillRate,
        usedSkills: summaryUsedSkills,
        minimumDistinctSkillsUsed,
        distinctSkillUseRate,
        minimumScore,
        minimumRunScore,
        taskCompletionRate: summary.taskCompletedRate,
        envBlockedRate: summary.envBlockedRate,
        compositionFallbackUsed: Boolean(raw.composition?.fallbackUsed),
        artifact: {
          kind: artifactKind,
          produced,
          verified: Boolean(produced && summary.artifactsPassed),
          references,
        },
        baseline: {
          workflowDigest: executionDag.workflowDigest,
          runs: baselineRuns,
          scores: baselineScores,
          score: baseline.medianScore,
          improvement: summary.medianScore - baseline.medianScore,
          errors: baselineErrors.length > 0
            ? [CANDIDATE_TECHNICAL_ERROR_CODES.baselineVerification]
            : [],
        },
        bestSingle,
        treatmentWorkflowDigests: {
          fullPack: treatmentWorkflowDigests.fullPack,
          planOnly: treatmentWorkflowDigests.planOnly,
          bestSingle: treatmentWorkflowDigests.bestSingle.map((item) => ({
            skill: item.skill,
            workflowDigest: item.workflowDigest,
          })),
          leaveOneOut: treatmentWorkflowDigests.leaveOneOut.map((item) => ({
            removedSkill: item.removedSkill,
            workflowDigest: item.workflowDigest,
          })),
        },
        ablation,
        deterministicMarginalSkills: [...manifestSkills],
        evaluationSuite,
        usageProvenance,
        verdicts,
        errors: technicalErrorCodes,
      },
    };
  }

  const unsigned = {
    schemaVersion: API_SCHEMA,
    generationId: context.generationId,
    workflow: {
      repository: 'aiskillstore/marketplace',
      runId: context.runId,
      runAttempt: context.runAttempt,
      runUrl: `https://github.com/aiskillstore/marketplace/actions/runs/${context.runId}`,
      commitSha: context.commitSha,
    },
    scenario: {
      id: raw.scenario.id,
      version: String(raw.scenario.version),
      task: raw.scenario.task,
      slug: raw.scenario.slug,
      name: raw.scenario.name,
      tags: raw.scenario.tags,
      requiredCapabilitySlots: requiredSlots,
    },
    evaluator: {
      cliVersion: context.cliVersion,
      cliSha256: context.cliSha256,
      model: context.model,
      judgeModel: context.judgeModel,
      ...(context.executionPlanDigest ? {
        executionPlanDigest: context.executionPlanDigest,
        modelRevision: context.modelRevision,
        modelPinType: context.modelPinType,
        judgeModelRevision: context.judgeModelRevision,
        judgeModelPinType: context.judgeModelPinType,
      } : {}),
      startedAt: raw.evaluationStartedAt,
      completedAt: raw.evaluationCompletedAt,
    },
    outcome: raw.outcome,
    candidate,
    evidence: { cliReport: buildSafeCliEvidence(raw, context) },
  };
  return { ...unsigned, evidenceDigest: sha256(canonicalJson(unsigned)) };
}

function workflowContext(plan, cli, version, checksum) {
  const workflow = plan.workflowBinding;
  const models = plan.executionBinding.models;
  return {
    generationId: workflow.generationId,
    scenarioId: workflow.scenarioId,
    runId: workflow.runId,
    runAttempt: workflow.runAttempt,
    commitSha: workflow.headSha,
    cli,
    cliVersion: version,
    cliSha256: checksum,
    model: models.runner.identity,
    modelRevision: models.runner.revision,
    modelPinType: models.runner.pinType,
    judgeModel: models.judge.identity,
    judgeModelRevision: models.judge.revision,
    judgeModelPinType: models.judge.pinType,
    executionPlanDigest: plan.digest,
  };
}

export function validateImmutableProductionPlan(plan) {
  return validateExecutionPlan(plan).scenario;
}

const DEPRECATED_EXECUTION_OVERRIDES = new Set([
  'agent-max-retries',
  'agent-timeout-ms',
  'auto-publish-threshold',
  'baseline-delta',
  'commit-sha',
  'evaluation-budget-ms',
  'expected-cli-version',
  'final-runs',
  'judge-model',
  'max-candidates',
  'minimum-fallback-ms',
  'model',
  'pick',
  'run-attempt',
  'run-id',
  'runs',
  'scenario-idle-timeout-ms',
  'scenario-timeout-ms',
  'threshold',
]);

function rejectDeprecatedExecutionOverrides(args, command) {
  const supplied = [...DEPRECATED_EXECUTION_OVERRIDES].filter((name) => Object.hasOwn(args, name));
  if (supplied.length > 0) {
    fail(`${command} rejects deprecated execution override flag(s): ${supplied.map((name) => `--${name}`).join(', ')}`);
  }
}

function safeSpawnErrorCode(value) {
  if (typeof value !== 'string' || value.length === 0) return null;
  return AGENT_SPAWN_ERROR_CODES.has(value) ? value : 'OTHER';
}

export function projectExecutorPreflightEvidence(raw) {
  return collectAgentExecutionInvocations(raw).map((invocation) => ({
    ...invocation,
    attempts: invocation.attempts.map((attempt) => ({
      schemaVersion: 'skillstore.agent-execution-evidence/v1',
      ...attempt,
    })),
  }));
}

function exactExecutorPreflightTraceEvidence(raw, expectedBindings) {
  if (
    raw?.schemaVersion !== EXECUTOR_PREFLIGHT_CLI_SCHEMA
    || raw.outcome !== 'passed'
    || canonicalJson(raw.bindings) !== canonicalJson(expectedBindings)
    || raw.verification?.passed !== true
    || raw.verification?.runs !== 1
    || raw.verification?.verdictCount !== 1
    || raw.verification?.errorCount !== 0
    || raw.verification?.usedSkill !== true
    || canonicalJson(raw.verification?.usedSkills) !== canonicalJson(
      expectedBindings.map((binding) => binding.canonicalId)
    )
    || raw.verification?.taskCompleted !== true
    || raw.verification?.envBlocked !== false
    || !Number.isInteger(raw.verification?.score)
    || raw.verification.score < 1
    || raw.verification.score > 10
    || !Array.isArray(raw.runnerUsageTraces)
    || raw.runnerUsageTraces.length !== 1
  ) return null;
  const trace = raw.runnerUsageTraces[0];
  if (
    trace?.schemaVersion !== 'skillstore.runner-skill-trace/v1'
    || trace.agent !== 'claude'
    || trace.source !== 'claude-stream-json-v1'
    || trace.deterministic !== true
    || !Array.isArray(trace.events)
    || trace.events.length !== expectedBindings.length
  ) return null;
  for (let index = 0; index < expectedBindings.length; index += 1) {
    const event = trace.events[index];
    const binding = expectedBindings[index];
    if (
      event?.sequence !== index + 1
      || event.canonicalId !== binding.canonicalId
      || event.contentHash !== binding.contentHash
      || event.version !== binding.version
    ) return null;
  }
  return {
    schemaVersion: EXECUTOR_PREFLIGHT_TRACE_SCHEMA,
    deterministic: true,
    traceCount: 1,
    eventCount: expectedBindings.length,
    bindingDigest: sha256(canonicalJson(expectedBindings)),
  };
}

function exactExecutorPreflightClosureFromEvidence(raw, invocations, expectedBindings) {
  if (
    !raw || typeof raw !== 'object' || Array.isArray(raw)
  ) return null;
  const runnerTraceEvidence = exactExecutorPreflightTraceEvidence(raw, expectedBindings);
  if (!runnerTraceEvidence) return null;
  if (invocations.length !== 2) return null;
  const expected = [
    { phase: 'run', agent: 'claude' },
    { phase: 'judge', agent: 'codex' },
  ];
  for (let index = 0; index < expected.length; index += 1) {
    const invocation = invocations[index];
    const attempt = invocation?.attempts?.[0];
    if (
      invocation.phase !== expected[index].phase
      || invocation.run !== 1
      || invocation.succeeded !== true
      || invocation.attempts.length !== 1
      || attempt.agent !== expected[index].agent
      || attempt.attempt !== 1
      || attempt.sandboxed !== true
      || attempt.outcome !== 'succeeded'
      || attempt.failureCategory !== 'none'
      || attempt.spawnErrorCode !== null
      || attempt.exitCode !== 0
      || attempt.signal !== null
    ) return null;
  }
  return { agentExecutionEvidence: invocations, runnerTraceEvidence };
}

export function exactExecutorPreflightClosure(raw, expectedBindings) {
  if (!Array.isArray(expectedBindings) || expectedBindings.length !== 2) return null;
  const evidence = projectExecutorPreflightEvidence(raw);
  return exactExecutorPreflightClosureFromEvidence(raw, evidence, expectedBindings);
}

export async function executorPreflight(args) {
  rejectDeprecatedExecutionOverrides(args, 'executor-preflight');
  for (const name of ['generation-id', 'idle-timeout-ms', 'task', 'timeout-ms']) {
    if (Object.hasOwn(args, name)) fail(`executor-preflight rejects deprecated execution override flag --${name}`);
  }
  const plan = await readExecutionPlan(resolve(required(args, 'plan')));
  await readArtifactGate(
    resolve(required(args, 'artifact-gate')),
    plan,
    'plan',
    'pack-production-plan',
  );
  const cli = resolve(required(args, 'cli'));
  await verifyCliAgainstPlan(plan, cli);
  const execution = plan.executionBinding;
  const parameters = execution.parameters;
  const resultsDir = resolve(required(args, 'results-dir'));
  const runtimeRoot = resolve(required(args, 'evaluator-runtime-root'));
  const preflightRoot = resolve(required(args, 'preflight-root'));
  const generationId = execution.executorPreflight.generationId;
  const uid = positiveInteger(required(args, 'evaluator-uid'), 'evaluator-uid');
  const gid = positiveInteger(required(args, 'evaluator-gid'), 'evaluator-gid');
  const timeoutMs = parameters.timeoutsMs.executorPreflight;
  const idleTimeoutMs = parameters.timeoutsMs.executorPreflightIdle;
  const agentTimeoutMs = parameters.timeoutsMs.executorPreflightAgent;
  const proxyActivityFile = args['proxy-activity-file']
    ? resolve(args['proxy-activity-file'])
    : null;
  await mkdir(resultsDir, { recursive: true, mode: 0o700 });
  const skillDirectories = await Promise.all(EXECUTOR_PREFLIGHT_SKILLS.map(async (skill, index) => {
    const directory = resolve(preflightRoot, `skill-${index + 1}`);
    await mkdir(directory, { recursive: true, mode: 0o700 });
    await chown(directory, uid, gid);
    const skillFile = resolve(directory, 'SKILL.md');
    await writeFile(skillFile, skill.contents, { mode: 0o444 });
    await chown(skillFile, uid, gid);
    await chmod(skillFile, 0o444);
    return directory;
  }));
  const expectedBindings = await Promise.all([
    execution.executorPreflight.skillA,
    execution.executorPreflight.skillB,
  ].map(async (skill, index) => {
    const contentHash = await sha256File(resolve(skillDirectories[index], 'SKILL.md'));
    if (contentHash !== skill.contentSha256) fail('Executor preflight Skill bytes differ from the execution Plan');
    return {
      canonicalId: skill.canonicalId,
      contentHash,
      version: skill.version,
    };
  }));
  const stdoutFile = resolve(resultsDir, 'executor-preflight.raw.json');
  const stderrFile = resolve(resultsDir, 'executor-preflight.run.log');
  const progressFile = resolve(resultsDir, 'executor-preflight.progress.ndjson');
  const baseEnv = { ...process.env, SKILLSTORE_AGENT_ENV_MODE: 'strict' };
  const startedAt = Date.now();
  let runtime = null;
  let processResult = null;
  let processErrorCode = null;
  let raw = null;
  let closure = null;
  let agentExecutionEvidence = [];
  let cleanupOutcome = 'not_run';
  try {
    terminateEvaluatorProcesses(uid);
    runtime = await prepareScenarioRuntime(runtimeRoot, generationId, uid, gid, baseEnv);
    const manifestFile = resolve(runtime.cwd, 'pack-executor-preflight-manifest.json');
    await writeFile(manifestFile, `${JSON.stringify({
      schemaVersion: 'skillstore.pack-executor-preflight-manifest/v1',
      task: execution.executorPreflight.task,
      skills: expectedBindings.map((binding, index) => ({
        directory: skillDirectories[index],
        ...binding,
      })),
    })}\n`, { mode: 0o444 });
    await chmod(manifestFile, 0o444);
    processResult = await runEvaluatorProcess(cli, [
      'pack', 'executor-preflight',
      '--manifest', manifestFile,
      '--model', execution.models.runner.identity,
      '--judge-model', execution.models.judge.identity,
      '--agent-timeout-ms', String(agentTimeoutMs),
      '--agent-max-retries', String(parameters.retries.agentMaxRetries),
    ], {
      cwd: runtime.cwd,
      env: runtime.env,
      uid,
      gid,
      stdoutFile,
      stderrFile,
      progressFile,
      label: 'executor-preflight',
      generationId,
      timeoutMs,
      idleTimeoutMs,
      heartbeatMs: parameters.timeoutsMs.executorPreflightHeartbeat,
      killGraceMs: parameters.timeoutsMs.processKillGrace,
      ...(proxyActivityFile ? { externalActivityFile: proxyActivityFile } : {}),
      onProgress: () => {},
    });
    try {
      raw = JSON.parse(await readFile(stdoutFile, 'utf8'));
      agentExecutionEvidence = projectExecutorPreflightEvidence(raw);
      closure = exactExecutorPreflightClosureFromEvidence(
        raw,
        agentExecutionEvidence,
        expectedBindings,
      );
    } catch {
      raw = null;
      closure = null;
      agentExecutionEvidence = [];
    }
  } catch (error) {
    processErrorCode = safeSpawnErrorCode(error?.code);
  } finally {
    try {
      terminateEvaluatorProcesses(uid);
      cleanupOutcome = 'passed';
    } catch {
      cleanupOutcome = 'failed';
    }
  }

  const firstFailedAttempt = agentExecutionEvidence
    .flatMap((invocation) => invocation.attempts)
    .find((attempt) => attempt.outcome === 'failed') ?? null;
  let errorClass = 'none';
  if (processResult?.deterministicHttpFailure) errorClass = 'deterministic_http';
  else if (processResult?.timedOut) errorClass = 'timeout';
  else if (processResult?.stalled) errorClass = 'stalled';
  else if (processResult?.outputExceeded) errorClass = 'output_limit';
  else if (processErrorCode) errorClass = 'spawn_error';
  else if (firstFailedAttempt) errorClass = firstFailedAttempt.failureCategory;
  else if (!closure || !processResult || processResult.status !== 0 || processResult.signal !== null) {
    errorClass = 'invalid_report';
  } else if (cleanupOutcome !== 'passed') errorClass = 'cleanup_failed';

  const outcome = errorClass === 'none' ? 'passed' : 'command_failed';
  const stdoutEvidence = await readFile(stdoutFile).catch(() => Buffer.alloc(0));
  const stderrEvidence = await readFile(stderrFile).catch(() => Buffer.alloc(0));
  const summary = {
    schemaVersion: 'marketplace.pack-executor-preflight/v1',
    executionPlanDigest: plan.digest,
    mode: 'pack-production-node-uid-nested-bwrap',
    outcome,
    errorClass,
    outerExecution: {
      spawnErrorCode: processErrorCode,
      exitCode: processResult?.status ?? null,
      signal: processResult?.signal ?? null,
      timedOut: processResult?.timedOut ?? false,
      stalled: processResult?.stalled ?? false,
      outputExceeded: processResult?.outputExceeded ?? false,
      durationMs: Date.now() - startedAt,
      stdoutBytes: stdoutEvidence.length,
      stderrBytes: stderrEvidence.length,
      stdoutSha256: sha256(stdoutEvidence),
      stderrSha256: sha256(stderrEvidence),
    },
    agentExecutionEvidence,
    runnerTraceEvidence: closure?.runnerTraceEvidence ?? null,
    verdictCount: Number.isSafeInteger(raw?.verification?.verdictCount)
      ? raw.verification.verdictCount
      : 0,
    errorCount: Number.isSafeInteger(raw?.verification?.errorCount)
      ? raw.verification.errorCount
      : null,
    cleanup: { outcome: cleanupOutcome },
  };
  process.stdout.write(`${JSON.stringify(summary)}\n`);
  if (outcome !== 'passed') process.exitCode = 1;
  return summary;
}

async function evaluate(args) {
  rejectDeprecatedExecutionOverrides(args, 'evaluate');
  const plan = await readExecutionPlan(resolve(required(args, 'plan')));
  await readArtifactGate(
    resolve(required(args, 'artifact-gate')),
    plan,
    'plan',
    'pack-production-plan',
  );
  const cli = resolve(required(args, 'cli'));
  const resultsDir = resolve(required(args, 'results-dir'));
  const skillsDir = resolve(required(args, 'skills-dir'));
  await verifyCliAgainstPlan(plan, cli);
  await verifySkillsAgainstPlan(plan, skillsDir);
  await mkdir(resultsDir, { recursive: true });

  const version = plan.executionBinding.cli.version;
  const checksum = await sha256File(cli);
  const parameters = plan.executionBinding.parameters;
  const evaluationBudgetMs = parameters.timeoutsMs.evaluationBudget;
  const maxScenarioMs = parameters.timeoutsMs.scenario;
  const scenarioIdleTimeoutMs = parameters.timeoutsMs.scenarioIdle;
  const proxyActivityFile = args['proxy-activity-file'] ? resolve(args['proxy-activity-file']) : null;
  const externalInfrastructureFailure = args['infrastructure-failure-file']
    ? normalizeInfrastructureFailure(await readJson(resolve(args['infrastructure-failure-file'])))
    : null;
  const minimumFallbackMs = parameters.timeoutsMs.minimumFallback;
  const scenarios = [plan.scenario];
  const progressFile = resolve(resultsDir, 'evaluate-progress.ndjson');
  const checkpointFile = resolve(resultsDir, 'evaluate-checkpoint.json');
  await writeFile(progressFile, '', { mode: 0o600 });
  const reports = [];
  const attempts = [];
  const hasEvaluatorIdentity = args['evaluator-uid'] != null || args['evaluator-gid'] != null;
  if (hasEvaluatorIdentity && (args['evaluator-uid'] == null || args['evaluator-gid'] == null)) {
    fail('--evaluator-uid and --evaluator-gid must be supplied together');
  }
  const evaluatorUid = hasEvaluatorIdentity
    ? positiveInteger(args['evaluator-uid'], 'evaluator-uid')
    : undefined;
  const evaluatorGid = hasEvaluatorIdentity
    ? positiveInteger(args['evaluator-gid'], 'evaluator-gid')
    : undefined;
  const evaluatorCwd = hasEvaluatorIdentity
    ? resolve(required(args, 'evaluator-cwd'))
    : process.cwd();
  const evaluatorRuntimeRoot = hasEvaluatorIdentity
    ? resolve(required(args, 'evaluator-runtime-root'))
    : null;
  if (hasEvaluatorIdentity && typeof process.getuid === 'function' && process.getuid() !== 0) {
    fail('Evaluator identity separation requires a root orchestrator');
  }
  const evaluationDeadline = Date.now() + evaluationBudgetMs;
  let progressSequence = 0;

  const buildSummary = () => ({
    schemaVersion: 'marketplace.pack-production-evaluate/v1',
    executionPlanDigest: plan.digest,
    cliVersion: version,
    cliSha256: checksum,
    evaluationBudgetMs,
    attempts,
    reports,
    selectedGenerationId: reports.find((report) => report.outcome === 'candidate_ready')?.generationId ?? null,
  });

  const checkpointSummary = async () => {
    await writeJson(resolve(resultsDir, 'evaluate-summary.json'), buildSummary());
  };

  for (const [scenarioIndex, scenario] of scenarios.entries()) {
    if (!/^[a-z0-9][a-z0-9-]{0,79}$/.test(scenario.id || '')) fail(`Unsafe scenario id: ${scenario.id}`);
    const remainingBudgetMs = evaluationDeadline - Date.now();
    const scenarioBudgetMs = allocateScenarioBudgetMs({
      remainingBudgetMs,
      remainingScenarios: scenarios.length - scenarioIndex,
      maxScenarioMs,
      minimumFallbackMs,
    });
    if (scenarioBudgetMs < 1) {
      attempts.push({
        planIndex: scenarioIndex,
        scenarioId: scenario.id,
        generationId: scenario.generationId,
        status: 'budget_exhausted',
        durationMs: 0,
      });
      await checkpointSummary();
      break;
    }
    const ordinal = String(scenarioIndex + 1).padStart(2, '0');
    const generationId = scenario.generationId;
    const context = workflowContext(plan, cli, version, checksum);
    const commandArgs = [
      'pack', 'generate',
      '--scenario', scenario.id,
      '--generation-id', generationId,
      '--skills-dir', skillsDir,
      '--max-candidates', String(parameters.generation.maxCandidates),
      '--pick', String(parameters.generation.pick),
      '--model', context.model,
      '--judge-model', context.judgeModel,
      '--runs', String(parameters.generation.runs),
      '--final-runs', String(parameters.generation.finalRuns),
      '--agent-timeout-ms', String(parameters.timeoutsMs.agent),
      '--agent-max-retries', String(parameters.retries.agentMaxRetries),
      '--threshold', String(parameters.generation.threshold),
      '--baseline-delta', String(parameters.generation.baselineDelta),
      '--auto-publish-threshold', String(parameters.generation.autoPublishThreshold),
      '--json',
    ];
    const partialStdoutFile = resolve(resultsDir, `${ordinal}-${scenario.id}.stdout.partial`);
    const stdoutFile = resolve(resultsDir, `${ordinal}-${scenario.id}.stdout.json`);
    const runLogFile = resolve(resultsDir, `${ordinal}-${scenario.id}.run.log`);
    const scenarioStartedAt = new Date().toISOString();
    const recordInfrastructureFailure = async (failure, attempt) => {
      const raw = buildInfrastructureCliReport({
        scenario,
        context,
        failure,
        startedAt: scenarioStartedAt,
        completedAt: new Date().toISOString(),
      });
      await writeJson(partialStdoutFile, raw);
      await rename(partialStdoutFile, stdoutFile);
      const evaluation = buildApiEvaluation(raw, context);
      const file = resolve(resultsDir, `${ordinal}-${scenario.id}.evaluation.json`);
      await writeJson(file, evaluation);
      reports.push({
        planIndex: scenarioIndex,
        scenarioId: scenario.id,
        generationId,
        outcome: raw.outcome,
        outcomeCategory: evaluation.evidence.cliReport.outcomeCategory,
        outcomeReasonSha256: evaluation.evidence.cliReport.outcomeReasonSha256,
        file,
      });
      attempts.push({
        planIndex: scenarioIndex,
        scenarioId: scenario.id,
        generationId,
        durationMs: attempt.durationMs ?? 0,
        timeoutMs: scenarioBudgetMs,
        status: 'completed',
        outcome: raw.outcome,
        infrastructureAudit: true,
      });
      await checkpointSummary();
    };
    const baseEnv = {
      ...process.env,
      SKILLSTORE_AGENT_ENV_MODE: 'strict',
    };
    if (externalInfrastructureFailure) {
      await recordInfrastructureFailure(externalInfrastructureFailure, { durationMs: 0 });
      break;
    }
    let runtime = { cwd: evaluatorCwd, env: baseEnv };
    let result;
    try {
      if (hasEvaluatorIdentity) {
        terminateEvaluatorProcesses(evaluatorUid);
        runtime = await prepareScenarioRuntime(
          evaluatorRuntimeRoot,
          generationId,
          evaluatorUid,
          evaluatorGid,
          baseEnv,
        );
      }
      result = await runEvaluatorProcess(cli, commandArgs, {
        cwd: runtime.cwd,
        stdoutFile: partialStdoutFile,
        stderrFile: runLogFile,
        progressFile,
        checkpointFile,
        label: scenario.id,
        generationId,
        scenarioIndex: scenarioIndex + 1,
        scenarioCount: scenarios.length,
        progressSequenceStart: progressSequence,
        timeoutMs: scenarioBudgetMs,
        idleTimeoutMs: scenarioIdleTimeoutMs,
        heartbeatMs: parameters.timeoutsMs.evaluatorHeartbeat,
        killGraceMs: parameters.timeoutsMs.processKillGrace,
        ...(proxyActivityFile ? { externalActivityFile: proxyActivityFile } : {}),
        ...(hasEvaluatorIdentity ? { uid: evaluatorUid, gid: evaluatorGid } : {}),
        env: runtime.env,
      });
    } catch (error) {
      attempts.push({
        planIndex: scenarioIndex,
        scenarioId: scenario.id,
        generationId,
        status: 'spawn_failed',
        durationMs: 0,
        errorCode: error?.code ?? null,
      });
      await checkpointSummary();
      break;
    } finally {
      if (hasEvaluatorIdentity) terminateEvaluatorProcesses(evaluatorUid);
    }
    const attempt = {
      planIndex: scenarioIndex,
      scenarioId: scenario.id,
      generationId,
      durationMs: result.durationMs,
      timeoutMs: scenarioBudgetMs,
    };
    progressSequence = result.progressSequence;
    if (result.interruptedSignal) {
      await recordInfrastructureFailure({
        stage: 'evaluation',
        reason: 'cancelled',
        signal: normalizeInterruptedSignal(result.interruptedSignal),
      }, attempt);
      break;
    }
    if (result.deterministicHttpFailure) {
      await recordInfrastructureFailure({
        stage: 'evaluation',
        reason: 'deterministic_http',
        status: result.deterministicHttpFailure.status,
        path: result.deterministicHttpFailure.path,
        model: result.deterministicHttpFailure.model,
        errorCategory: result.deterministicHttpFailure.errorCategory,
        diagnosticSha256: result.deterministicHttpFailure.errorMessageSha256,
      }, attempt);
      break;
    }
    if (result.timedOut) {
      await recordInfrastructureFailure({
        stage: 'evaluation',
        reason: 'timeout',
      }, attempt);
      break;
    }
    if (result.stalled) {
      await recordInfrastructureFailure({
        stage: 'evaluation',
        reason: 'stalled',
      }, attempt);
      break;
    }
    if (result.outputExceeded) {
      attempts.push({ ...attempt, status: 'output_limit_exceeded' });
      await checkpointSummary();
      continue;
    }
    const stdout = await readFile(partialStdoutFile, 'utf8');
    let raw;
    try {
      raw = JSON.parse(stdout);
    } catch {
      await recordInfrastructureFailure({
        stage: 'evaluation',
        reason: 'terminal_report_missing',
        diagnosticSha256: sha256(stdout),
      }, attempt);
      break;
    }
    const expectedExit = KNOWN_CLI_EXIT.get(raw.outcome);
    if (result.status !== expectedExit) {
      fail(`Evaluator exit/outcome mismatch for ${scenario.id}: exit ${result.status}, outcome ${raw.outcome}`);
    }
    await rename(partialStdoutFile, stdoutFile);
    const evaluation = buildApiEvaluation(raw, context);
    const file = resolve(resultsDir, `${ordinal}-${scenario.id}.evaluation.json`);
    await writeJson(file, evaluation);
    reports.push({
      planIndex: scenarioIndex,
      scenarioId: scenario.id,
      generationId,
      outcome: raw.outcome,
      outcomeCategory: evaluation.evidence.cliReport.outcomeCategory,
      outcomeReasonSha256: evaluation.evidence.cliReport.outcomeReasonSha256,
      file,
    });
    attempts.push({ ...attempt, status: 'completed', outcome: raw.outcome });
    await checkpointSummary();
    if (raw.outcome === 'candidate_ready') break;
  }

  const summary = buildSummary();
  await checkpointSummary();
  process.stdout.write(`${JSON.stringify(summary)}\n`);
  const operationalFailures = attempts.filter((attempt) => attempt.status !== 'completed');
  if (operationalFailures.length > 0) {
    fail(
      `Evaluation contained operationally incomplete attempts: `
      + operationalFailures.map((attempt) => `${attempt.scenarioId}:${attempt.status}`).join(', '),
    );
  }
  if (reports.length === 0) fail('No scenario produced a complete trusted evaluation report');
}

async function verifyEvaluation(args) {
  rejectDeprecatedExecutionOverrides(args, 'verify');
  const plan = await readExecutionPlan(resolve(required(args, 'plan')));
  await readArtifactGate(
    resolve(required(args, 'artifact-gate')),
    plan,
    'plan',
    'pack-production-plan',
  );
  const cli = resolve(required(args, 'cli'));
  const resultsDir = resolve(required(args, 'results-dir'));
  const summary = await readJson(resolve(resultsDir, 'evaluate-summary.json'));
  if (summary.schemaVersion !== 'marketplace.pack-production-evaluate/v1') {
    fail(`Unsupported evaluate summary schema: ${summary.schemaVersion}`);
  }
  if (summary.executionPlanDigest !== plan.digest) {
    fail('Evaluate summary differs from the execution Plan digest');
  }
  const scenarios = [plan.scenario];
  if (!Array.isArray(summary.reports) || summary.reports.length < 1 || summary.reports.length > scenarios.length) {
    fail('Evaluate summary report count is outside the immutable plan');
  }
  if (!Array.isArray(summary.attempts) || summary.attempts.length !== scenarios.length) {
    fail('Evaluate summary attempts do not exactly cover the immutable plan');
  }
  const incompleteAttempts = summary.attempts.filter((attempt) => attempt?.status !== 'completed');
  if (incompleteAttempts.length > 0) {
    fail(
      `Evaluate summary contains operationally incomplete attempts: `
      + incompleteAttempts.map((attempt) => `${attempt?.scenarioId ?? 'unknown'}:${attempt?.status ?? 'missing'}`).join(', '),
    );
  }
  for (const [planIndex, attempt] of summary.attempts.entries()) {
    const scenario = scenarios[planIndex];
    if (
      attempt?.planIndex !== planIndex
      || attempt.scenarioId !== scenario.id
      || attempt.generationId !== scenario.generationId
    ) fail('Evaluate summary attempt differs from the immutable plan generation binding');
  }

  await verifyCliAgainstPlan(plan, cli);
  const version = plan.executionBinding.cli.version;
  if (summary.cliVersion !== version) {
    fail(`Evaluation CLI version mismatch: expected ${version}, got ${summary.cliVersion}`);
  }
  const checksum = await sha256File(cli);
  if (summary.cliSha256 !== checksum) fail('Evaluation CLI checksum differs from the trusted CLI');

  const expectedFiles = [];
  const verifiedFiles = [];
  const stdoutSanitizations = [];
  let selectedGenerationId = null;
  let candidateSeen = false;
  let previousPlanIndex = -1;
  for (const [index, report] of summary.reports.entries()) {
    const planIndex = report.planIndex ?? index;
    if (!Number.isSafeInteger(planIndex) || planIndex < 0 || planIndex >= scenarios.length) {
      fail(`Invalid evaluate summary plan index: ${report.planIndex}`);
    }
    if (planIndex <= previousPlanIndex) fail('Evaluate summary plan indexes are not strictly increasing');
    previousPlanIndex = planIndex;
    const scenario = scenarios[planIndex];
    if (!scenario || report.scenarioId !== scenario.id) fail('Evaluate summary scenario differs from the immutable plan');
    if (!/^[a-z0-9][a-z0-9-]{0,79}$/.test(scenario.id)) fail(`Unsafe scenario id: ${scenario.id}`);
    if (report.generationId !== scenario.generationId) {
      fail(`Evaluate summary generation id differs from the immutable plan for ${scenario.id}`);
    }
    if (candidateSeen) fail('Evaluate summary contains reports after a ready candidate');

    const ordinal = String(planIndex + 1).padStart(2, '0');
    const prefix = `${ordinal}-${scenario.id}`;
    const stdoutFile = `${prefix}.stdout.json`;
    const evaluationFile = `${prefix}.evaluation.json`;
    if (basename(String(report.file || '')) !== evaluationFile) {
      fail(`Evaluate summary file differs from the deterministic path for ${scenario.id}`);
    }
    const raw = await readJson(resolve(resultsDir, stdoutFile));
    if (
      raw.outcome !== report.outcome
      || report.outcomeCategory !== cliOutcomeCategory(raw.outcome)
      || report.outcomeReasonSha256 !== sha256(String(raw.outcomeReason))
    ) {
      fail(`Evaluate summary outcome differs from stdout for ${scenario.id}`);
    }
    const context = workflowContext(plan, cli, version, checksum);
    const rebuilt = buildApiEvaluation(raw, context);
    const recorded = await readJson(resolve(resultsDir, evaluationFile));
    if (canonicalJson(recorded) !== canonicalJson(rebuilt)) {
      fail(`Evaluation artifact differs from trusted reconstruction for ${scenario.id}`);
    }
    stdoutSanitizations.push({ file: stdoutFile, evidence: rebuilt.evidence.cliReport });
    expectedFiles.push(evaluationFile);
    verifiedFiles.push({ file: evaluationFile, sha256: await sha256File(resolve(resultsDir, evaluationFile)) });
    if (raw.outcome === 'candidate_ready') {
      candidateSeen = true;
      selectedGenerationId = report.generationId;
    }
  }

  if ((summary.selectedGenerationId ?? null) !== selectedGenerationId) {
    fail('Evaluate summary selected generation is inconsistent with verified outcomes');
  }
  const actualFiles = (await readdir(resultsDir)).filter((file) => file.endsWith('.evaluation.json')).sort();
  if (canonicalJson(actualFiles) !== canonicalJson([...expectedFiles].sort())) {
    fail('Evaluation artifact set is not the exact trusted closure');
  }
  // Raw CLI stdout is needed only for this trusted reconstruction. Replace it
  // before the workflow copies the closure into its 90-day artifact.
  await Promise.all(stdoutSanitizations.map(({ file, evidence }) =>
    writeJson(resolve(resultsDir, file), evidence)
  ));
  const verification = {
    schemaVersion: VERIFICATION_SCHEMA,
    executionPlanDigest: plan.digest,
    cliVersion: version,
    cliSha256: checksum,
    selectedGenerationId,
    files: verifiedFiles.sort((left, right) => left.file.localeCompare(right.file)),
  };
  await writeJson(resolve(resultsDir, 'evaluation-verification.json'), verification);
  process.stdout.write(`${JSON.stringify(verification)}\n`);
}

async function apiRequest(url, token, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
  });
  const text = await response.text();
  let body = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = { message: text };
  }
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status} from ${url}: ${text.slice(0, 2000)}`);
    error.status = response.status;
    error.body = body;
    throw error;
  }
  return body;
}

function apiBase(args) {
  return required(args, 'api-url').replace(/\/$/, '');
}

export function planTrustedPersistence(evaluations, selectedGenerationId) {
  if (!Array.isArray(evaluations) || evaluations.some((item) => !item?.evaluation || !item?.file)) {
    fail('Trusted persistence planning requires complete evaluation artifacts');
  }
  const candidates = evaluations.filter(({ evaluation }) => evaluation.outcome === 'candidate_ready');
  const candidateNull = evaluations.filter(({ evaluation }) => evaluation.outcome !== 'candidate_ready');
  for (const { file, evaluation } of candidateNull) {
    if (evaluation.candidate !== null) {
      fail(`Non-candidate evaluation ${file} unexpectedly contains a candidate`);
    }
  }
  const candidateNullPosts = candidateNull.filter(
    ({ evaluation }) => evaluation.schemaVersion === API_SCHEMA,
  );
  const artifactOnly = candidateNull.filter(
    ({ evaluation }) => evaluation.schemaVersion !== API_SCHEMA,
  );
  if (candidates.length > 1) fail('Trusted evaluation closure contains more than one candidate_ready artifact');
  if (candidates.length === 0) {
    if (selectedGenerationId != null) {
      fail('Trusted verification selected a generation without a candidate_ready artifact');
    }
    return { candidate: null, candidateNullPosts, auditOnly: artifactOnly };
  }
  const candidate = candidates[0];
  const evaluation = candidate.evaluation;
  if (
    selectedGenerationId !== evaluation.generationId
    || evaluation.schemaVersion !== API_SCHEMA
    || !evaluation.candidate?.manifest?.executionDag?.bindingDigest
    || !evaluation.candidate?.fitness?.bestSingle
    || !Array.isArray(evaluation.candidate?.fitness?.bestSingle?.competitors)
    || !Array.isArray(evaluation.candidate?.fitness?.ablation)
    || evaluation.candidate?.fitness?.evaluationSuite?.executed !== true
    || evaluation.candidate?.fitness?.usageProvenance?.deterministic !== true
    || !Array.isArray(evaluation.candidate?.fitness?.errors)
    || evaluation.candidate.fitness.errors.length > 0
    || !Array.isArray(evaluation.candidate?.fitness?.baseline?.errors)
    || evaluation.candidate.fitness.baseline.errors.length > 0
  ) {
    fail('candidate_ready evidence is incomplete; persistence and enrichment are forbidden');
  }
  return {
    candidate,
    candidateNullPosts,
    auditOnly: artifactOnly,
  };
}

export function validateCandidateNullPersistResponse(response, evaluation) {
  const data = response?.data;
  if (
    evaluation?.schemaVersion !== API_SCHEMA
    || evaluation?.outcome === 'candidate_ready'
    || evaluation?.candidate !== null
    || data?.generationId !== evaluation.generationId
    || data?.evaluationOutcome !== evaluation.outcome
    || data?.outcome !== evaluation.outcome
    || data?.pack !== null
    || data?.enrichment?.content !== 'not_applicable'
    || data?.enrichment?.translation !== 'not_applicable'
    || data?.enrichment?.contentDispatchNonce !== null
  ) {
    fail('Persist response did not bind the exact candidate-null v4 audit outcome');
  }
  return data;
}

export function buildPublicReadbackExpectation(persisted, selected, publicSlug) {
  const generationId = selected?.generationId;
  const packId = selected?.pack?.id;
  if (typeof generationId !== 'string' || !generationId) {
    fail('Persist response did not bind the selected generation');
  }
  if (typeof packId !== 'string' || !packId) {
    fail('Persist response did not bind the selected Pack id');
  }
  if (typeof publicSlug !== 'string' || !publicSlug) {
    fail('Publish response did not bind the public Pack slug');
  }
  const persistedAttempt = persisted?.persisted?.find(
    (item) => item?.request?.generationId === generationId,
  );
  const evaluation = persistedAttempt?.request;
  const manifest = persistedAttempt?.request?.candidate?.manifest;
  const skillSlugs = manifest?.skills;
  const executionDag = manifest?.executionDag;
  if (!Array.isArray(skillSlugs) || skillSlugs.length < 1 || skillSlugs.some(
    (slug) => typeof slug !== 'string' || !slug,
  )) {
    fail('Persisted candidate evidence did not contain exact Skill slugs');
  }
  if (
    !executionDag
    || !/^[0-9a-f]{64}$/.test(executionDag.workflowDigest || '')
    || !/^[0-9a-f]{64}$/.test(executionDag.bindingDigest || '')
    || !Array.isArray(executionDag.skillBindings)
    || executionDag.skillBindings.length !== skillSlugs.length
  ) {
    fail('Persisted candidate evidence did not contain the exact execution DAG binding');
  }
  const skillBindings = executionDag.skillBindings.map((binding, index) => {
    if (
      binding?.canonicalId !== skillSlugs[index]
      || typeof binding?.version !== 'string'
      || !binding.version
      || !/^[0-9a-f]{64}$/.test(binding?.contentHash || '')
    ) {
      fail(`Persisted candidate Skill binding ${index + 1} is incomplete`);
    }
    return {
      slug: binding.canonicalId,
      version: binding.version,
      contentHash: binding.contentHash,
    };
  });
  return {
    generationId,
    packId,
    publicSlug,
    skillSlugs: [...skillSlugs],
    skillBindings,
    executionDag,
    workflowDigest: executionDag.workflowDigest,
    bindingDigest: executionDag.bindingDigest,
    usageGuideMarker: executionDag.usageGuideMarker,
    executionBinding: {
      schemaVersion: 'skillstore.pack-execution-binding/v1',
      generationId,
      evidenceDigest: evaluation.evidenceDigest,
      workflowDigest: executionDag.workflowDigest,
      bindingDigest: executionDag.bindingDigest,
      usageGuideMarker: executionDag.usageGuideMarker,
      marketplaceCommitSha: evaluation.workflow?.commitSha,
      skills: executionDag.skillBindings,
      executionDag,
    },
  };
}

export function validatePublicPackReadback(pack, expected) {
  const mismatches = [];
  if (!pack || typeof pack !== 'object') {
    return { matched: false, mismatches: ['response data is not a Pack object'], actualSkillSlugs: [] };
  }
  if (pack.id !== expected.packId) {
    mismatches.push(`Pack id mismatch: expected ${expected.packId}, got ${String(pack.id ?? 'missing')}`);
  }
  if (pack.slug !== expected.publicSlug) {
    mismatches.push(`Pack slug mismatch: expected ${expected.publicSlug}, got ${String(pack.slug ?? 'missing')}`);
  }
  // The public Pack detail contract is camelCase even though the database field
  // is review_status.
  if (pack.reviewStatus !== 'approved') {
    mismatches.push(`Pack reviewStatus is ${String(pack.reviewStatus ?? 'missing')}, expected approved`);
  }
  const executionBinding = pack.executionBinding;
  if (!executionBinding || typeof executionBinding !== 'object') {
    mismatches.push('Pack executionBinding is missing');
  } else {
    for (const field of [
      'schemaVersion',
      'generationId',
      'evidenceDigest',
      'workflowDigest',
      'bindingDigest',
      'usageGuideMarker',
      'marketplaceCommitSha',
    ]) {
      if (executionBinding[field] !== expected.executionBinding[field]) {
        mismatches.push(`Pack executionBinding.${field} mismatch`);
      }
    }
    if (canonicalJson(executionBinding.skills) !== canonicalJson(expected.executionBinding.skills)) {
      mismatches.push('Pack executionBinding Skills differ from the evaluated identities');
    }
  }
  if (
    !executionBinding?.executionDag
    || typeof executionBinding.executionDag !== 'object'
    || canonicalJson(executionBinding.executionDag) !== canonicalJson(expected.executionDag)
  ) {
    mismatches.push('Pack executionBinding.executionDag differs from the persisted canonical DAG');
  }
  if (typeof pack.usageGuide !== 'string' || !pack.usageGuide.includes(expected.usageGuideMarker)) {
    mismatches.push('Pack usageGuide is not bound to the canonical DAG marker');
  }
  const actualSkillBindings = Array.isArray(pack.skills)
    ? pack.skills.map((skill) => ({
      slug: skill?.slug,
      version: skill?.version,
      contentHash: skill?.contentHash,
    }))
    : [];
  const actualSkillSlugs = actualSkillBindings.map((binding) => binding.slug);
  if (actualSkillSlugs.some((slug) => typeof slug !== 'string')) {
    mismatches.push('Pack skills contain a missing or invalid slug');
  } else if (
    actualSkillSlugs.length !== expected.skillSlugs.length ||
    actualSkillSlugs.some((slug, index) => slug !== expected.skillSlugs[index])
  ) {
    mismatches.push(
      `Pack Skill slugs mismatch: expected ${expected.skillSlugs.join(',')}, got ${actualSkillSlugs.join(',')}`,
    );
  }
  if (canonicalJson(actualSkillBindings) !== canonicalJson(expected.skillBindings)) {
    mismatches.push('Pack Skill version/contentHash bindings differ from the evaluated identities');
  }
  return { matched: mismatches.length === 0, mismatches, actualSkillSlugs, actualSkillBindings };
}

export async function readExactPublicPack(base, expected, fetchImpl = fetch) {
  const response = await fetchImpl(
    `${base}/api/packs/${encodeURIComponent(expected.publicSlug)}?lang=en`,
    { headers: { Accept: 'application/json', 'Cache-Control': 'no-cache' } },
  );
  if (!response.ok) {
    return { pack: null, mismatches: [`public Pack API returned HTTP ${response.status}`] };
  }
  let body;
  try {
    body = await response.json();
  } catch {
    return { pack: null, mismatches: ['public Pack API returned invalid JSON'] };
  }
  const pack = body?.data;
  const validation = validatePublicPackReadback(pack, expected);
  return {
    pack: validation.matched ? pack : null,
    mismatches: validation.mismatches,
  };
}

async function persist(args) {
  const plan = await readExecutionPlan(resolve(required(args, 'plan')));
  await readArtifactGate(
    resolve(required(args, 'artifact-gate')),
    plan,
    'evaluate',
    'pack-production-evaluation',
  );
  const resultsDir = resolve(required(args, 'results-dir'));
  const verification = await readJson(resolve(resultsDir, 'evaluation-verification.json'));
  if (
    verification.schemaVersion !== VERIFICATION_SCHEMA
    || verification.executionPlanDigest !== plan.digest
    || !Array.isArray(verification.files)
  ) {
    fail('Trusted evaluation verification is missing or invalid');
  }
  const files = (await readdir(resultsDir))
    .filter((file) => file.endsWith('.evaluation.json'))
    .sort();
  if (files.length === 0) fail('No evaluation artifacts found to persist');
  const verifiedFiles = verification.files.map((entry) => entry?.file).sort();
  if (canonicalJson(files) !== canonicalJson(verifiedFiles)) {
    fail('Persist artifact set differs from the trusted evaluation closure');
  }
  for (const entry of verification.files) {
    if (typeof entry?.file !== 'string' || !/^\d{2}-[a-z0-9][a-z0-9-]{0,79}\.evaluation\.json$/.test(entry.file)) {
      fail(`Invalid verification filename: ${entry?.file}`);
    }
    if (!/^[0-9a-f]{64}$/.test(entry?.sha256 || '')) fail(`Invalid verification hash for ${entry?.file}`);
    if (await sha256File(resolve(resultsDir, entry.file)) !== entry.sha256) {
      fail(`Persist artifact hash differs from trusted verification: ${entry.file}`);
    }
  }

  // Read and validate the complete closure before the first write-capable
  // request. Every complete v4 candidate-null outcome is persisted as an audit
  // attempt, while legacy v3 audits remain artifact-only. Candidate-null POSTs
  // must never create placeholder Packs or dispatch enrichment.
  const evaluations = await Promise.all(files.map(async (file) => ({
    file,
    evaluation: await readJson(resolve(resultsDir, file)),
  })));
  if (evaluations.some(({ evaluation }) => evaluation.evaluator?.executionPlanDigest !== plan.digest)) {
    fail('Persist evaluation artifact differs from the execution Plan');
  }
  const persistencePlan = planTrustedPersistence(evaluations, verification.selectedGenerationId ?? null);
  const token = required(args, 'token');
  const base = apiBase(args);
  const persisted = persistencePlan.auditOnly.map(({ file, evaluation }) => ({
    file,
    request: evaluation,
    response: null,
    auditOnly: true,
    persistedRemotely: false,
  }));
  for (const { file, evaluation } of persistencePlan.candidateNullPosts) {
    const response = await apiRequest(`${base}/api/automation/packs/production`, token, {
      method: 'POST',
      body: JSON.stringify(evaluation),
    });
    validateCandidateNullPersistResponse(response, evaluation);
    persisted.push({
      file,
      request: evaluation,
      response,
      auditOnly: true,
      persistedRemotely: true,
    });
  }

  let selected = null;
  if (persistencePlan.candidate) {
    const { file, evaluation } = persistencePlan.candidate;
    const response = await apiRequest(`${base}/api/automation/packs/production`, token, {
      method: 'POST',
      body: JSON.stringify(evaluation),
    });
    selected = response?.data;
    if (
      selected?.generationId !== evaluation.generationId
      || selected?.evaluationOutcome !== 'candidate_ready'
      || !selected?.pack?.id
      || !selected?.pack?.slug
      || selected?.enrichment?.content !== 'dispatched'
      || !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
        .test(selected?.enrichment?.contentDispatchNonce ?? '')
    ) {
      fail('Persist response did not bind and dispatch the exact complete candidate');
    }
    persisted.push({
      file,
      request: evaluation,
      response,
      auditOnly: false,
      persistedRemotely: true,
    });
  }
  const summary = {
    schemaVersion: 'marketplace.pack-production-persist/v1',
    executionPlanDigest: plan.digest,
    persisted,
    selected,
  };
  await writeJson(resolve(resultsDir, 'persist-summary.json'), summary);
  process.stdout.write(`${JSON.stringify(summary)}\n`);
}

function readiness(attempt) {
  const state = attempt.packReadiness ?? attempt.readiness ?? null;
  if (!state) return null;
  if (typeof state.contentReady === 'boolean' && typeof state.translationReady === 'boolean') {
    return {
      contentReady: state.contentReady,
      translationReady: state.translationReady,
      blockers: state.blockers ?? [],
    };
  }
  const cover = state.coverImageUrl ?? state.cover_image_url;
  const guide = state.usageGuideStatus ?? state.usage_guide_status;
  const translation = state.translationStatus ?? state.translation_status;
  return {
    contentReady: Boolean(cover) && guide === 'completed',
    translationReady: translation === 'completed',
    cover,
    guide,
    translation,
  };
}

export function buildSloResult(value, checkedAt = new Date().toISOString()) {
  if (!value || typeof value !== 'object') fail('Pack production SLO response is missing');
  const windowDays = Number(value.windowDays);
  const target = Number(value.target);
  const publishedReadbackPassed = Number(value.publishedReadbackPassed);
  if (windowDays !== 7) fail(`Pack production SLO window must be 7 days, got ${value.windowDays}`);
  if (target !== 2) fail(`Pack production SLO target must be 2, got ${value.target}`);
  if (!Number.isSafeInteger(publishedReadbackPassed) || publishedReadbackPassed < 0) {
    fail('Pack production SLO published count is invalid');
  }
  if (typeof value.met !== 'boolean' || value.met !== (publishedReadbackPassed >= target)) {
    fail('Pack production SLO met flag is inconsistent with its count and target');
  }
  if (typeof value.windowStartedAt !== 'string' || !Number.isFinite(Date.parse(value.windowStartedAt))) {
    fail('Pack production SLO window start is invalid');
  }
  return {
    schemaVersion: SLO_SCHEMA,
    checkedAt,
    windowDays,
    windowStartedAt: value.windowStartedAt,
    target,
    publishedReadbackPassed,
    met: value.met,
  };
}

async function patchStatus(base, token, generationId, body) {
  return apiRequest(`${base}/api/automation/packs/production/${generationId}`, token, {
    method: 'PATCH',
    body: JSON.stringify({ schemaVersion: STATUS_SCHEMA, ...body }),
  });
}

export function validateCurrentContentDispatchNonce(attempt, expectedNonce, generationId) {
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(expectedNonce ?? '')) {
    fail(`Persisted content dispatch nonce is invalid for ${generationId}`);
  }
  if (attempt?.content_dispatch_nonce !== expectedNonce) {
    fail(`Content dispatch ${expectedNonce} was superseded for ${generationId}`);
  }
  return expectedNonce;
}

function wait(milliseconds) {
  return new Promise((resolveWait) => setTimeout(resolveWait, milliseconds));
}

export function buildHardDisabledReviewPendingResult(selected, autoPublishRequested) {
  if (!selected?.generationId || !selected?.pack?.id || !selected?.pack?.slug) {
    fail('Hard-disabled automatic publication requires an exact selected generation and Pack');
  }
  return {
    outcome: 'review_pending',
    generationId: selected.generationId,
    pack: selected.pack,
    reason: 'automatic publish was disabled for this run',
    autoPublishRequested: autoPublishRequested === true,
    publicationMode: 'manual_only',
  };
}

async function finalize(args) {
  const plan = await readExecutionPlan(resolve(required(args, 'plan')));
  await readArtifactGate(
    resolve(required(args, 'artifact-gate')),
    plan,
    'persist',
    'pack-production-persisted',
  );
  const resultsDir = resolve(required(args, 'results-dir'));
  const persisted = await readJson(resolve(resultsDir, 'persist-summary.json'));
  if (persisted.executionPlanDigest !== plan.digest) {
    fail('Persist summary differs from the execution Plan');
  }
  const selected = persisted.selected;
  const rawOutcomes = persisted.persisted.map((item) => item.request.outcome);
  if (!selected) {
    if (rawOutcomes.some((outcome) => outcome === 'infrastructure_failed' || outcome === 'evaluation_inconclusive')) {
      fail(`No candidate was produced because evaluation was not conclusive: ${rawOutcomes.join(', ')}`);
    }
    const result = { outcome: 'quality_rejected', attempts: rawOutcomes.length };
    await writeJson(resolve(resultsDir, 'final-result.json'), result);
    process.stdout.write(`${JSON.stringify(result)}\n`);
    return;
  }

  const persistedCandidate = persisted.persisted.find(
    (item) => item?.request?.generationId === selected.generationId,
  );
  if (
    persistedCandidate?.auditOnly !== false
    || persistedCandidate?.request?.outcome !== 'candidate_ready'
    || persistedCandidate?.response?.data?.generationId !== selected.generationId
    || !persistedCandidate?.request?.candidate?.manifest?.executionDag?.bindingDigest
    || !persistedCandidate?.request?.candidate?.fitness?.bestSingle
    || !Array.isArray(persistedCandidate?.request?.candidate?.fitness?.bestSingle?.competitors)
    || !Array.isArray(persistedCandidate?.request?.candidate?.fitness?.ablation)
    || persistedCandidate?.request?.candidate?.fitness?.evaluationSuite?.executed !== true
    || persistedCandidate?.request?.candidate?.fitness?.usageProvenance?.deterministic !== true
    || persistedCandidate?.response?.data?.enrichment?.contentDispatchNonce
      !== selected?.enrichment?.contentDispatchNonce
  ) {
    fail('Finalize refused an incomplete or audit-only candidate; no enrichment or publish action was taken');
  }

  const token = required(args, 'token');
  const base = apiBase(args);
  const generationId = selected.generationId;
  const contentDispatchNonce = selected.enrichment.contentDispatchNonce;
  const maxWaitSeconds = positiveInteger(args['max-wait-seconds'], 'max-wait-seconds', 1800);
  const pollSeconds = positiveInteger(args['poll-seconds'], 'poll-seconds', 30);
  const maxPollSeconds = positiveInteger(args['max-poll-seconds'], 'max-poll-seconds', 180);
  if (maxPollSeconds < pollSeconds) fail('--max-poll-seconds must be at least --poll-seconds');
  const deadline = Date.now() + maxWaitSeconds * 1000;
  let nextPollSeconds = pollSeconds;
  let attempt;
  let ready;
  while (Date.now() < deadline) {
    const response = await apiRequest(`${base}/api/automation/packs/production/${generationId}`, token);
    const readback = response?.data;
    attempt = readback?.attempt ?? readback;
    validateCurrentContentDispatchNonce(attempt, contentDispatchNonce, generationId);
    ready = readiness(readback);
    if (ready?.contentReady && ready.translationReady) break;
    if (attempt?.outcome === 'enrichment_failed') {
      fail(`Enrichment failed for ${generationId}: ${attempt.last_error ?? 'unknown error'}`);
    }
    const remainingMs = deadline - Date.now();
    if (remainingMs > 0) await wait(Math.min(nextPollSeconds * 1000, remainingMs));
    nextPollSeconds = Math.min(maxPollSeconds, nextPollSeconds * 2);
  }
  if (!ready?.contentReady || !ready.translationReady) {
    await patchStatus(base, token, generationId, {
      outcome: 'enrichment_failed',
      contentDispatchNonce,
      contentStatus: ready?.contentReady ? 'succeeded' : 'failed',
      translationStatus: ready?.translationReady ? 'succeeded' : 'failed',
      error: `enrichment readiness timed out after ${maxWaitSeconds}s`,
    });
    fail(`Enrichment timed out for ${generationId}`);
  }

  await patchStatus(base, token, generationId, {
    outcome: 'review_pending',
    contentDispatchNonce,
    contentStatus: 'succeeded',
    translationStatus: 'succeeded',
    error: null,
  });
  // Automatic publication is hard-disabled in code. A true request is retained
  // as audit evidence but cannot cross the review_pending boundary; the only v4
  // publisher is the Environment-protected generation-bound manual workflow.
  const autoPublishRequested = (args['auto-publish'] ?? 'false') === 'true';
  const result = buildHardDisabledReviewPendingResult(selected, autoPublishRequested);
  await writeJson(resolve(resultsDir, 'final-result.json'), result);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function reportSlo(args) {
  const resultsDir = resolve(required(args, 'results-dir'));
  const token = required(args, 'token');
  const base = apiBase(args);
  await mkdir(resultsDir, { recursive: true });
  const response = await apiRequest(`${base}/api/automation/packs/production?windowDays=7`, token);
  const result = buildSloResult(response?.data);
  await writeJson(resolve(resultsDir, 'slo-result.json'), result);
  if (!result.met) {
    process.stderr.write(
      `::warning::Rolling 7-day Pack production SLO is below target: ${result.publishedReadbackPassed}/${result.target}\n`,
    );
  }
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function artifactGate(args) {
  const gate = await createArtifactGate(
    resolve(required(args, 'plan')),
    resolve(required(args, 'state')),
    resolve(required(args, 'output')),
  );
  process.stdout.write(`${JSON.stringify(gate)}\n`);
}

async function printPlanValues(args) {
  const plan = await readExecutionPlan(resolve(required(args, 'plan')));
  process.stdout.write(`${JSON.stringify(planRuntimeValues(plan))}\n`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  switch (args.command) {
    case 'artifact-gate':
      return artifactGate(args);
    case 'plan-values':
      return printPlanValues(args);
    case 'executor-preflight':
      return executorPreflight(args);
    case 'evaluate':
      return evaluate(args);
    case 'verify':
      return verifyEvaluation(args);
    case 'persist':
      return persist(args);
    case 'finalize':
      return finalize(args);
    case 'slo':
      return reportSlo(args);
    default:
      fail('Usage: pack-production.mjs <artifact-gate|plan-values|executor-preflight|evaluate|verify|persist|finalize|slo> [options]');
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`${error.stack ?? error.message ?? String(error)}\n`);
    process.exitCode = 1;
  });
}
