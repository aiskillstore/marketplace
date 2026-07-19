#!/usr/bin/env node

import { spawn } from 'node:child_process';
import {
  createWriteStream,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { basename, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { parseCanonicalShardIndex } from './submission-shard-contract.mjs';
import { parseSelectionPlan } from './submission-selection-plan.mjs';

function fail(message) {
  throw new Error(message);
}

function option(args, name, { required = true, defaultValue = null } = {}) {
  const index = args.indexOf(name);
  if (index === -1) {
    if (required) fail(`missing required option ${name}`);
    return defaultValue;
  }
  if (index === args.length - 1 || args[index + 1].startsWith('--')) fail(`missing value for ${name}`);
  return args[index + 1];
}

function writeManifest(path, manifest) {
  const temporary = `${path}.${process.pid}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(manifest, null, 2)}\n`, { mode: 0o600 });
  renameSync(temporary, path);
}

function collectReports(pendingRoot) {
  const reports = [];
  function walk(directory) {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      const stat = lstatSync(path);
      if (stat.isSymbolicLink()) {
        reports.push({ slug: null, path, invalid: 'symlink' });
      } else if (entry.isDirectory()) {
        walk(path);
      } else if (entry.isFile() && entry.name === 'skill-report.json') {
        reports.push({ slug: basename(dirname(path)), path, invalid: null });
      }
    }
  }
  walk(pendingRoot);
  return reports;
}

function inspectResults(pendingRoot, planned) {
  const reports = collectReports(pendingRoot);
  const counts = new Map();
  const invalid = [];
  for (const report of reports) {
    if (report.invalid !== null || report.slug === null) {
      invalid.push(report.path);
      continue;
    }
    counts.set(report.slug, (counts.get(report.slug) ?? 0) + 1);
  }
  const plannedSet = new Set(planned);
  const succeeded = planned.filter((slug) => counts.get(slug) === 1);
  const failed = planned.filter((slug) => counts.get(slug) !== 1);
  const duplicates = planned.filter((slug) => (counts.get(slug) ?? 0) > 1);
  const unexpected = [...counts.keys()].filter((slug) => !plannedSet.has(slug));
  return { succeeded, failed, duplicates, unexpected, invalid };
}

function sleep(milliseconds) {
  if (milliseconds <= 0) return Promise.resolve();
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function runCli({ cli, cliArgs, logPath, append }) {
  return new Promise((resolve) => {
    const log = createWriteStream(logPath, { flags: append ? 'a' : 'w', mode: 0o600 });
    let settled = false;
    let spawnError = null;
    const child = spawn(cli, cliArgs, { env: process.env, stdio: ['ignore', 'pipe', 'pipe'] });
    const copy = (stream, destination) => {
      stream.on('data', (chunk) => {
        destination.write(chunk);
        log.write(chunk);
      });
    };
    copy(child.stdout, process.stdout);
    copy(child.stderr, process.stderr);
    child.on('error', (error) => {
      spawnError = error;
    });
    child.on('close', (code, signal) => {
      if (settled) return;
      settled = true;
      log.end(() => resolve({
        code: Number.isInteger(code) ? code : null,
        signal: signal ?? null,
        spawnError: spawnError?.message ?? null,
      }));
    });
  });
}

function attemptStatus(execution, result) {
  if (execution.signal !== null) return 'cancelled';
  if (execution.spawnError !== null || execution.code !== 0 || result.failed.length > 0) return 'failed';
  return 'succeeded';
}

function buildAttempt(number, requested, execution, result) {
  return {
    number,
    phase: number === 1 ? 'first' : 'retry',
    status: attemptStatus(execution, result),
    exitCode: execution.code,
    requested,
    succeeded: requested.filter((slug) => result.succeeded.includes(slug)),
    failed: requested.filter((slug) => !result.succeeded.includes(slug)),
  };
}

async function processShard(config) {
  const selectionPlan = parseSelectionPlan(readFileSync(config.selectionPlan, 'utf8'));
  const planned = selectionPlan.skills.map(({ slug }) => slug);
  const shardIndex = parseCanonicalShardIndex(config.shardIndex);
  const pendingRoot = join(config.resultDir, 'pending');
  const manifestPath = join(config.resultDir, 'shard-manifest.json');
  const logPath = join(config.resultDir, `process-output-${shardIndex}.log`);

  rmSync(config.resultDir, { recursive: true, force: true });
  mkdirSync(pendingRoot, { recursive: true });
  writeFileSync(join(config.resultDir, 'selection-plan.json'), `${JSON.stringify(selectionPlan)}\n`, { mode: 0o600 });

  if (planned.length === 0) {
    writeFileSync(logPath, 'No skills planned; explicit no-op.\n', { mode: 0o600 });
    const manifest = {
      schemaVersion: 1,
      shardIndex,
      status: 'succeeded',
      reasonCode: 'no_skills_planned',
      selectionPlan,
      planned: [],
      succeeded: [],
      failed: [],
      failureCategories: [],
      attempts: [{
        number: 1,
        phase: 'first',
        status: 'skipped',
        exitCode: null,
        requested: [],
        succeeded: [],
        failed: [],
      }],
    };
    writeManifest(manifestPath, manifest);
    return manifest;
  }

  const baseArgs = [
    'skill', 'process', config.githubUrl,
    '--selection-plan', join(config.resultDir, 'selection-plan.json'),
    '--slugs', planned.join(','),
    '--output', config.resultDir,
    '--marketplace-repo', config.marketplaceRepo,
    '--skip-pr',
  ];
  if (config.slugAliasesFile !== '') baseArgs.push('--slug-aliases-file', config.slugAliasesFile);
  if (config.model !== '') baseArgs.push('--model', config.model);

  const firstExecution = await runCli({ cli: config.cli, cliArgs: baseArgs, logPath, append: false });
  const firstResult = inspectResults(pendingRoot, planned);
  const attempts = [buildAttempt(1, planned, firstExecution, firstResult)];

  let terminalExecution = firstExecution;
  let retryRequested = [];
  if (attempts[0].status !== 'succeeded') {
    retryRequested = firstResult.failed.length > 0 ? firstResult.failed : planned;
    await sleep(config.retryDelayMs);
    const retryArgs = [...baseArgs];
    retryArgs[retryArgs.indexOf('--slugs') + 1] = retryRequested.join(',');
    const retryExecution = await runCli({ cli: config.cli, cliArgs: retryArgs, logPath, append: true });
    const retryResult = inspectResults(pendingRoot, planned);
    attempts.push(buildAttempt(2, retryRequested, retryExecution, retryResult));
    terminalExecution = retryExecution;
  }

  const finalResult = inspectResults(pendingRoot, planned);
  const failureCategories = new Set();
  if (terminalExecution.signal !== null) failureCategories.add('cancelled');
  if (terminalExecution.spawnError !== null) failureCategories.add('cli_spawn_failed');
  if (terminalExecution.code !== 0) failureCategories.add('cli_nonzero');
  if (finalResult.failed.some((slug) => !finalResult.duplicates.includes(slug))) failureCategories.add('missing_result');
  if (finalResult.duplicates.length > 0) failureCategories.add('duplicate_result');
  if (finalResult.unexpected.length > 0) failureCategories.add('unexpected_result');
  if (finalResult.invalid.length > 0) failureCategories.add('invalid_result');

  const terminalAttemptSucceeded = attempts.at(-1).status === 'succeeded';
  const succeeded = finalResult.succeeded;
  const failed = finalResult.failed;
  const status = terminalAttemptSucceeded
    && succeeded.length === planned.length
    && failed.length === 0
    && finalResult.duplicates.length === 0
    && finalResult.unexpected.length === 0
    && finalResult.invalid.length === 0
    ? 'succeeded'
    : 'failed';
  const manifest = {
    schemaVersion: 1,
    shardIndex,
    status,
    reasonCode: status === 'succeeded' ? 'processed_all_planned' : 'processing_failed',
    selectionPlan,
    planned,
    succeeded,
    failed,
    failureCategories: status === 'succeeded' ? [] : [...failureCategories].sort(),
    attempts,
  };
  writeManifest(manifestPath, manifest);
  return manifest;
}

async function main() {
  const args = process.argv.slice(2);
  const config = {
    cli: option(args, '--cli'),
    githubUrl: option(args, '--github-url'),
    selectionPlan: option(args, '--selection-plan'),
    resultDir: option(args, '--result-dir'),
    marketplaceRepo: option(args, '--marketplace-repo'),
    shardIndex: option(args, '--shard-index'),
    model: option(args, '--model', { required: false, defaultValue: '' }),
    slugAliasesFile: option(args, '--slug-aliases-file', { required: false, defaultValue: '' }),
    retryDelayMs: Number(option(args, '--retry-delay-ms', { required: false, defaultValue: '10000' })),
  };
  if (!Number.isSafeInteger(config.retryDelayMs) || config.retryDelayMs < 0) fail('--retry-delay-ms must be a non-negative integer');

  let manifest;
  try {
    manifest = await processShard(config);
  } catch (error) {
    let planned = [];
    let selectionPlan = null;
    try {
      selectionPlan = parseSelectionPlan(readFileSync(config.selectionPlan, 'utf8'));
      planned = selectionPlan.skills.map(({ slug }) => slug);
    } catch {
      // The diagnostic manifest below records the stable processing failure.
    }
    const shardIndex = parseCanonicalShardIndex(config.shardIndex);
    mkdirSync(join(config.resultDir, 'pending'), { recursive: true });
    if (existsSync(config.selectionPlan)) {
      writeFileSync(
        join(config.resultDir, 'selection-plan.invalid.json'),
        readFileSync(config.selectionPlan),
        { mode: 0o600 },
      );
    }
    const manifestPath = join(config.resultDir, 'shard-manifest.json');
    const logPath = join(config.resultDir, `process-output-${shardIndex}.log`);
    const message = error instanceof Error ? error.message : String(error);
    writeFileSync(logPath, `Process step failed before a terminal result: ${message}\n`, { flag: existsSync(logPath) ? 'a' : 'w', mode: 0o600 });
    manifest = {
      schemaVersion: 1,
      shardIndex,
      status: 'failed',
      reasonCode: 'process_step_failed',
      selectionPlan,
      planned,
      succeeded: [],
      failed: planned,
      failureCategories: ['process_step_failed'],
      attempts: [{
        number: 1,
        phase: 'first',
        status: 'skipped',
        exitCode: null,
        requested: planned,
        succeeded: [],
        failed: planned,
      }],
    };
    writeManifest(manifestPath, manifest);
  }

  process.stdout.write(`Shard ${manifest.shardIndex}: ${manifest.status} (${manifest.reasonCode}); ${manifest.succeeded.length} succeeded, ${manifest.failed.length} failed\n`);
  // Always return zero after writing the diagnostic manifest. The workflow uploads
  // the archive first, then the explicit terminal-status step fails the job.
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  main().catch((error) => {
    console.error(`::error::Submission shard processing failed: ${error instanceof Error ? error.message : String(error)}`);
    process.exitCode = 1;
  });
}
