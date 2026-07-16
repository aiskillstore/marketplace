#!/usr/bin/env node

import { createHash, randomUUID } from 'node:crypto';
import { spawn, spawnSync } from 'node:child_process';
import { createWriteStream, statSync } from 'node:fs';
import { chmod, chown, copyFile, mkdir, readFile, readdir, rename, writeFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { finished } from 'node:stream/promises';
import { fileURLToPath } from 'node:url';

const CLI_SCHEMA = 'pack-generation-evaluation/v2';
const API_SCHEMA = 'skillstore.pack-evaluation/v3';
const STATUS_SCHEMA = 'skillstore.pack-production-status/v1';
const READBACK_SCHEMA = 'skillstore.pack-production-readback/v1';
const SLO_SCHEMA = 'marketplace.pack-production-slo/v1';
const VERIFICATION_SCHEMA = 'marketplace.pack-production-evaluation-verification/v1';
const KNOWN_CLI_EXIT = new Map([
  ['candidate_ready', 0],
  ['quality_rejected', 10],
  ['evaluation_inconclusive', 20],
  ['infrastructure_failed', 30],
]);
const EVALUATOR_OUTPUT_LIMIT_BYTES = 16 * 1024 * 1024;

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

function normalizeJson(value) {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return value;
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (Array.isArray(value)) return value.map(normalizeJson);
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([, entry]) => entry !== undefined)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, entry]) => [key, normalizeJson(entry)]),
    );
  }
  fail('Value is not canonical JSON');
}

export function canonicalJson(value) {
  return JSON.stringify(normalizeJson(value));
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
  match = line.match(/^\s{0,12}slot ([a-z0-9][a-z0-9-]{0,79}): finding candidates for [A-Za-z0-9 .,+_\/-]{1,200}$/);
  if (match) return `slot ${match[1]}: finding candidates`;
  match = line.match(
    /^\s{0,12}slot ([a-z0-9][a-z0-9-]{0,79}): verifying ([a-z0-9][a-z0-9-]{0,79})$/,
  );
  if (match) return `slot ${match[1]}: verifying ${match[2]}`;
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
  const idleTimer = setInterval(() => {
    if (stalled || terminationRequested) return;
    if (options.externalActivityFile) {
      try {
        const activity = statSync(options.externalActivityFile);
        if (activity.mtimeMs > externalActivityMtimeMs) {
          externalActivityMtimeMs = activity.mtimeMs;
          markActivity();
        }
      } catch (error) {
        if (error?.code !== 'ENOENT' && requestTermination('scenario.activity_probe_failed')) {
          stalled = true;
          onProgress(`[pack-evaluator] scenario=${label} activity probe failed`);
        }
      }
    }
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
    if (manifestSkills.length < 2 || manifestSkillSet.size !== manifestSkills.length) {
      fail('candidate_ready report must contain at least two distinct manifest Skills');
    }
    const slotAssignments = apiSlotAssignments(raw, manifestSkills, requiredSlots);
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
    const baselineScores = Array.isArray(baseline.scores) ? baseline.scores.map(Number) : [];
    const baselineRuns = Number(baseline.runs);
    const baselineErrors = (raw.baselineVerification?.errors ?? []).map(String);
    if (
      baselineRuns !== 3
      || baselineScores.length !== baselineRuns
      || baselineScores.some((score) => !Number.isFinite(score) || score < 0 || score > 10)
    ) {
      fail('candidate_ready baseline lacks exactly three valid run scores');
    }
    candidate = {
      manifest: {
        name: raw.manifest.name,
        slug: raw.manifest.slug,
        description: raw.manifest.description,
        scenarioTags: raw.manifest.scenario_tags,
        riskFlags: raw.manifest.risk_flags,
        skills: manifestSkills,
        slotAssignments,
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
          runs: baselineRuns,
          scores: baselineScores,
          score: baseline.medianScore,
          improvement: summary.medianScore - baseline.medianScore,
          errors: baselineErrors,
        },
        verdicts,
        errors: [
          ...(raw.errors ?? []).map((error) => `evaluation: ${error}`),
          ...(raw.composition?.errors ?? []).map((error) => `composition: ${error}`),
          ...(raw.packVerification?.errors ?? []).map((error) => `pack: ${error}`),
          ...(raw.baselineVerification?.errors ?? []).map((error) => `baseline: ${error}`),
        ],
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
      startedAt: raw.evaluationStartedAt,
      completedAt: raw.evaluationCompletedAt,
    },
    outcome: raw.outcome,
    candidate,
    evidence: { cliReport: raw },
  };
  return { ...unsigned, evidenceDigest: sha256(canonicalJson(unsigned)) };
}

function workflowContext(args, generationId, scenarioId, cli, version, checksum) {
  const runId = required(args, 'run-id');
  if (!/^[1-9][0-9]*$/.test(runId)) fail('--run-id must be a GitHub Actions numeric run id');
  const runAttempt = positiveInteger(args['run-attempt'], 'run-attempt', 1);
  const commitSha = required(args, 'commit-sha');
  if (!/^[0-9a-f]{40}$/.test(commitSha)) fail('--commit-sha must be a 40-character lowercase SHA');
  return {
    generationId,
    scenarioId,
    runId,
    runAttempt,
    commitSha,
    cli,
    cliVersion: version,
    cliSha256: checksum,
    model: args.model ?? 'sonnet',
    judgeModel: args['judge-model'] ?? 'gpt-5.5',
  };
}

async function evaluate(args) {
  const cli = resolve(required(args, 'cli'));
  const plan = await readJson(resolve(required(args, 'plan')));
  const resultsDir = resolve(required(args, 'results-dir'));
  const skillsDir = resolve(required(args, 'skills-dir'));
  if (plan.schemaVersion !== 'pack-production-queue/v1') fail(`Unsupported plan schema: ${plan.schemaVersion}`);
  if (!Array.isArray(plan.scenarios) || plan.scenarios.length < 1 || plan.scenarios.length > 3) {
    fail('Plan must contain one to three scenarios');
  }
  await mkdir(resultsDir, { recursive: true });

  const version = cliVersion(cli);
  const expectedVersion = required(args, 'expected-cli-version');
  if (version !== expectedVersion) fail(`CLI version mismatch: expected ${expectedVersion}, got ${version}`);
  const checksum = await sha256File(cli);
  const evaluationBudgetMs = positiveInteger(
    args['evaluation-budget-ms'],
    'evaluation-budget-ms',
    230 * 60_000,
  );
  const maxScenarioMs = positiveInteger(
    args['scenario-timeout-ms'],
    'scenario-timeout-ms',
    120 * 60_000,
  );
  const scenarioIdleTimeoutMs = positiveInteger(
    args['scenario-idle-timeout-ms'],
    'scenario-idle-timeout-ms',
    20 * 60_000,
  );
  const proxyActivityFile = args['proxy-activity-file'] ? resolve(args['proxy-activity-file']) : null;
  const minimumFallbackMs = positiveInteger(
    args['minimum-fallback-ms'],
    'minimum-fallback-ms',
    45 * 60_000,
  );
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
  let interruptedSignal = null;
  let progressSequence = 0;

  const buildSummary = () => ({
    schemaVersion: 'marketplace.pack-production-evaluate/v1',
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

  for (const [scenarioIndex, scenario] of plan.scenarios.entries()) {
    if (!/^[a-z0-9][a-z0-9-]{0,79}$/.test(scenario.id || '')) fail(`Unsafe scenario id: ${scenario.id}`);
    const remainingBudgetMs = evaluationDeadline - Date.now();
    const scenarioBudgetMs = allocateScenarioBudgetMs({
      remainingBudgetMs,
      remainingScenarios: plan.scenarios.length - scenarioIndex,
      maxScenarioMs,
      minimumFallbackMs,
    });
    if (scenarioBudgetMs < 1) {
      attempts.push({
        planIndex: scenarioIndex,
        scenarioId: scenario.id,
        generationId: null,
        status: 'budget_exhausted',
        durationMs: 0,
      });
      await checkpointSummary();
      break;
    }
    const ordinal = String(scenarioIndex + 1).padStart(2, '0');
    const generationId = randomUUID();
    const context = workflowContext(args, generationId, scenario.id, cli, version, checksum);
    const commandArgs = [
      'pack', 'generate',
      '--scenario', scenario.id,
      '--generation-id', generationId,
      '--skills-dir', skillsDir,
      '--max-candidates', args['max-candidates'] ?? '3',
      '--pick', args.pick ?? '4',
      '--model', context.model,
      '--judge-model', context.judgeModel,
      '--runs', args.runs ?? '1',
      '--final-runs', args['final-runs'] ?? '3',
      '--agent-timeout-ms', args['agent-timeout-ms'] ?? '360000',
      '--agent-max-retries', args['agent-max-retries'] ?? '1',
      '--threshold', args.threshold ?? '7',
      '--baseline-delta', args['baseline-delta'] ?? '1',
      '--auto-publish-threshold', args['auto-publish-threshold'] ?? '8',
      '--json',
    ];
    const partialStdoutFile = resolve(resultsDir, `${ordinal}-${scenario.id}.stdout.partial`);
    const stdoutFile = resolve(resultsDir, `${ordinal}-${scenario.id}.stdout.json`);
    const runLogFile = resolve(resultsDir, `${ordinal}-${scenario.id}.run.log`);
    const baseEnv = {
      ...process.env,
      SKILLSTORE_AGENT_ENV_MODE: 'strict',
    };
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
        scenarioCount: plan.scenarios.length,
        progressSequenceStart: progressSequence,
        timeoutMs: scenarioBudgetMs,
        idleTimeoutMs: scenarioIdleTimeoutMs,
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
      interruptedSignal = result.interruptedSignal;
      attempts.push({ ...attempt, status: 'cancelled', signal: result.interruptedSignal });
      await checkpointSummary();
      break;
    }
    if (result.timedOut) {
      attempts.push({ ...attempt, status: 'timed_out' });
      await checkpointSummary();
      break;
    }
    if (result.stalled) {
      attempts.push({ ...attempt, status: 'stalled' });
      await checkpointSummary();
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
      attempts.push({
        ...attempt,
        status: 'terminal_report_missing',
        exitCode: result.status ?? null,
        signal: result.signal ?? null,
      });
      await checkpointSummary();
      continue;
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
      outcomeReason: raw.outcomeReason,
      file,
    });
    attempts.push({ ...attempt, status: 'completed', outcome: raw.outcome });
    await checkpointSummary();
    if (raw.outcome === 'candidate_ready') break;
  }

  const summary = buildSummary();
  await checkpointSummary();
  process.stdout.write(`${JSON.stringify(summary)}\n`);
  if (interruptedSignal) fail(`Evaluator interrupted by ${interruptedSignal}`);
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
  const cli = resolve(required(args, 'cli'));
  const plan = await readJson(resolve(required(args, 'plan')));
  const resultsDir = resolve(required(args, 'results-dir'));
  const summary = await readJson(resolve(resultsDir, 'evaluate-summary.json'));
  if (plan.schemaVersion !== 'pack-production-queue/v1') fail(`Unsupported plan schema: ${plan.schemaVersion}`);
  if (!Array.isArray(plan.scenarios) || plan.scenarios.length < 1 || plan.scenarios.length > 3) {
    fail('Plan must contain one to three scenarios');
  }
  if (summary.schemaVersion !== 'marketplace.pack-production-evaluate/v1') {
    fail(`Unsupported evaluate summary schema: ${summary.schemaVersion}`);
  }
  if (!Array.isArray(summary.reports) || summary.reports.length < 1 || summary.reports.length > plan.scenarios.length) {
    fail('Evaluate summary report count is outside the immutable plan');
  }
  if (!Array.isArray(summary.attempts) || summary.attempts.length < 1) {
    fail('Evaluate summary attempts are missing');
  }
  const incompleteAttempts = summary.attempts.filter((attempt) => attempt?.status !== 'completed');
  if (incompleteAttempts.length > 0) {
    fail(
      `Evaluate summary contains operationally incomplete attempts: `
      + incompleteAttempts.map((attempt) => `${attempt?.scenarioId ?? 'unknown'}:${attempt?.status ?? 'missing'}`).join(', '),
    );
  }

  const version = cliVersion(cli);
  const expectedVersion = required(args, 'expected-cli-version');
  if (version !== expectedVersion || summary.cliVersion !== version) {
    fail(`Evaluation CLI version mismatch: expected ${expectedVersion}, got ${version}/${summary.cliVersion}`);
  }
  const checksum = await sha256File(cli);
  if (summary.cliSha256 !== checksum) fail('Evaluation CLI checksum differs from the trusted CLI');

  const expectedFiles = [];
  const verifiedFiles = [];
  let selectedGenerationId = null;
  let candidateSeen = false;
  let previousPlanIndex = -1;
  for (const [index, report] of summary.reports.entries()) {
    const planIndex = report.planIndex ?? index;
    if (!Number.isSafeInteger(planIndex) || planIndex < 0 || planIndex >= plan.scenarios.length) {
      fail(`Invalid evaluate summary plan index: ${report.planIndex}`);
    }
    if (planIndex <= previousPlanIndex) fail('Evaluate summary plan indexes are not strictly increasing');
    previousPlanIndex = planIndex;
    const scenario = plan.scenarios[planIndex];
    if (!scenario || report.scenarioId !== scenario.id) fail('Evaluate summary scenario differs from the immutable plan');
    if (!/^[a-z0-9][a-z0-9-]{0,79}$/.test(scenario.id)) fail(`Unsafe scenario id: ${scenario.id}`);
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(report.generationId || '')) {
      fail(`Invalid generation id for ${scenario.id}`);
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
    if (raw.outcome !== report.outcome || raw.outcomeReason !== report.outcomeReason) {
      fail(`Evaluate summary outcome differs from stdout for ${scenario.id}`);
    }
    const context = workflowContext(args, report.generationId, scenario.id, cli, version, checksum);
    const rebuilt = buildApiEvaluation(raw, context);
    const recorded = await readJson(resolve(resultsDir, evaluationFile));
    if (canonicalJson(recorded) !== canonicalJson(rebuilt)) {
      fail(`Evaluation artifact differs from trusted reconstruction for ${scenario.id}`);
    }
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
  const verification = {
    schemaVersion: VERIFICATION_SCHEMA,
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
  const skillSlugs = persistedAttempt?.request?.candidate?.manifest?.skills;
  if (!Array.isArray(skillSlugs) || skillSlugs.length < 1 || skillSlugs.some(
    (slug) => typeof slug !== 'string' || !slug,
  )) {
    fail('Persisted candidate evidence did not contain exact Skill slugs');
  }
  return { generationId, packId, publicSlug, skillSlugs: [...skillSlugs] };
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
  const actualSkillSlugs = Array.isArray(pack.skills)
    ? pack.skills.map((skill) => skill?.slug)
    : [];
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
  return { matched: mismatches.length === 0, mismatches, actualSkillSlugs };
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
  const resultsDir = resolve(required(args, 'results-dir'));
  const token = required(args, 'token');
  const base = apiBase(args);
  const verification = await readJson(resolve(resultsDir, 'evaluation-verification.json'));
  if (verification.schemaVersion !== VERIFICATION_SCHEMA || !Array.isArray(verification.files)) {
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

  const persisted = [];
  for (const file of files) {
    const evaluation = await readJson(resolve(resultsDir, file));
    const response = await apiRequest(`${base}/api/automation/packs/production`, token, {
      method: 'POST',
      body: JSON.stringify(evaluation),
    });
    persisted.push({ file, request: evaluation, response });
  }
  const summary = {
    schemaVersion: 'marketplace.pack-production-persist/v1',
    persisted,
    selected: persisted.find((item) => item.request.outcome === 'candidate_ready')?.response?.data ?? null,
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

function wait(milliseconds) {
  return new Promise((resolveWait) => setTimeout(resolveWait, milliseconds));
}

async function finalize(args) {
  const resultsDir = resolve(required(args, 'results-dir'));
  const persisted = await readJson(resolve(resultsDir, 'persist-summary.json'));
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

  const token = required(args, 'token');
  const base = apiBase(args);
  const generationId = selected.generationId;
  const maxWaitSeconds = positiveInteger(args['max-wait-seconds'], 'max-wait-seconds', 1800);
  const pollSeconds = positiveInteger(args['poll-seconds'], 'poll-seconds', 30);
  const deadline = Date.now() + maxWaitSeconds * 1000;
  let attempt;
  let ready;
  while (Date.now() < deadline) {
    const response = await apiRequest(`${base}/api/automation/packs/production/${generationId}`, token);
    const readback = response?.data;
    attempt = readback?.attempt ?? readback;
    ready = readiness(readback);
    if (ready?.contentReady && ready.translationReady) break;
    if (attempt?.outcome === 'enrichment_failed') {
      fail(`Enrichment failed for ${generationId}: ${attempt.last_error ?? 'unknown error'}`);
    }
    await wait(pollSeconds * 1000);
  }
  if (!ready?.contentReady || !ready.translationReady) {
    await patchStatus(base, token, generationId, {
      outcome: 'enrichment_failed',
      contentStatus: ready?.contentReady ? 'succeeded' : 'failed',
      translationStatus: ready?.translationReady ? 'succeeded' : 'failed',
      error: `enrichment readiness timed out after ${maxWaitSeconds}s`,
    });
    fail(`Enrichment timed out for ${generationId}`);
  }

  await patchStatus(base, token, generationId, {
    outcome: 'review_pending',
    contentStatus: 'succeeded',
    translationStatus: 'succeeded',
    error: null,
  });
  const autoPublishEnabled = (args['auto-publish'] ?? 'true') === 'true';
  if (!autoPublishEnabled || !selected.autoPublishEligible || selected.comparisonOf) {
    const result = {
      outcome: 'review_pending',
      generationId,
      pack: selected.pack,
      reason: selected.comparisonOf
        ? 'comparison candidates require human review'
        : !autoPublishEnabled
          ? 'automatic publish was disabled for this run'
          : 'candidate did not meet the automatic publish gate',
    };
    await writeJson(resolve(resultsDir, 'final-result.json'), result);
    process.stdout.write(`${JSON.stringify(result)}\n`);
    return;
  }

  const publish = await apiRequest(
    `${base}/api/automation/packs/${encodeURIComponent(selected.pack.slug)}/publish`,
    token,
    { method: 'POST', body: JSON.stringify({ generationId }) },
  );
  const publicSlug = publish?.data?.slug;
  if (!publicSlug) fail('Publish response did not include the public slug');
  const expectedPublicPack = buildPublicReadbackExpectation(persisted, selected, publicSlug);

  let publicPack = null;
  let readbackMismatches = [];
  for (let attemptNumber = 1; attemptNumber <= 20; attemptNumber += 1) {
    try {
      const readback = await readExactPublicPack(base, expectedPublicPack);
      publicPack = readback.pack;
      readbackMismatches = readback.mismatches;
      if (publicPack) break;
    } catch (cause) {
      // Production cache/readback may lag; retry within the bounded window.
      readbackMismatches = [cause instanceof Error ? cause.message : String(cause)];
    }
    await wait(15_000);
  }
  const checkedAt = new Date().toISOString();
  if (!publicPack) {
    const readbackError = `exact public Pack readback failed: ${readbackMismatches.join('; ') || 'no matching Pack returned'}`;
    await apiRequest(`${base}/api/automation/packs/production/${generationId}`, token, {
      method: 'POST',
      body: JSON.stringify({
        schemaVersion: READBACK_SCHEMA,
        status: 'failed',
        packSlug: publicSlug,
        checkedAt,
        error: readbackError,
      }),
    }).catch(() => {});
    fail(`Published pack ${publicSlug} failed production readback: ${readbackError}`);
  }

  await apiRequest(`${base}/api/automation/packs/production/${generationId}`, token, {
    method: 'POST',
    body: JSON.stringify({
      schemaVersion: READBACK_SCHEMA,
      status: 'succeeded',
      packSlug: publicSlug,
      checkedAt,
      error: null,
    }),
  });
  const slo = (await apiRequest(`${base}/api/automation/packs/production?windowDays=7`, token))?.data;
  if (slo && !slo.met) {
    process.stderr.write(`::error::Rolling 7-day Pack production SLO is below target: ${slo.publishedReadbackPassed}/${slo.target}\n`);
  }

  const result = {
    outcome: 'published',
    generationId,
    pack: { id: publicPack.id, slug: publicSlug, skillCount: publicPack.skills.length },
    readbackPassed: true,
    rollingSevenDaySlo: slo ?? null,
  };
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
      `::error::Rolling 7-day Pack production SLO is below target: ${result.publishedReadbackPassed}/${result.target}\n`,
    );
  }
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  switch (args.command) {
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
      fail('Usage: pack-production.mjs <evaluate|verify|persist|finalize|slo> [options]');
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`${error.stack ?? error.message ?? String(error)}\n`);
    process.exitCode = 1;
  });
}
