#!/usr/bin/env node

import { createHash, randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import {
  chmod,
  lstat,
  mkdir,
  readFile,
  readdir,
  rename,
  writeFile,
} from 'node:fs/promises';
import { basename, dirname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

export const EXECUTION_PLAN_SCHEMA = 'marketplace.pack-production-execution-plan/v1';
export const ARTIFACT_STATE_SCHEMA = 'marketplace.pack-production-artifact-state/v1';
export const ARTIFACT_GATE_SCHEMA = 'marketplace.pack-production-artifact-gate/v1';
export const EXPECTED_REPOSITORY = 'aiskillstore/marketplace';
export const EXPECTED_WORKFLOW = 'Generate Pack';
export const CLI_IDENTITY = Object.freeze({
  version: '2.14.2',
  assetName: 'skillstore-cli-linux-x64',
  releaseAssetSha256: '21b1967e134622a40ae4d312278fa10d136103f0148887252f61e4e3b4536674',
});
export const MODEL_IDENTITIES = Object.freeze({
  runner: Object.freeze({
    identity: 'claude-sonnet-5',
    revision: 'workflow-pinned alias',
    pinType: 'workflow-pinned alias',
  }),
  judge: Object.freeze({
    identity: 'gpt-5.5',
    revision: 'workflow-pinned alias',
    pinType: 'workflow-pinned alias',
  }),
});

export const EXECUTOR_PREFLIGHT_TASK = [
  'Invoke Skill pack-executor-preflight-a first and Skill pack-executor-preflight-b second.',
  'After both Skills load successfully, reply with exactly PACK_EVALUATOR_READY and nothing else.',
].join(' ');
export const EXECUTOR_PREFLIGHT_SKILLS = Object.freeze([
  Object.freeze({
    canonicalId: 'pack-executor-preflight-a',
    version: '1.0.0',
    contents: [
      '---',
      'name: pack-executor-preflight-a',
      'description: Load first, then follow the evaluator task exactly.',
      '---',
      '',
      'Follow the evaluator task exactly. Do not inspect the host or call external tools.',
      '',
    ].join('\n'),
  }),
  Object.freeze({
    canonicalId: 'pack-executor-preflight-b',
    version: '1.0.0',
    contents: [
      '---',
      'name: pack-executor-preflight-b',
      'description: Load second, then return the exact marker requested by the evaluator.',
      '---',
      '',
      'Follow the evaluator task exactly. Do not inspect the host or call external tools.',
      '',
    ].join('\n'),
  }),
]);

export const EXECUTION_SOURCE_FILES = Object.freeze([
  '.github/workflows/generate-packs.yml',
  'scripts/configure-pack-evaluator-bwrap.sh',
  'scripts/configure-pack-evaluator-egress.sh',
  'scripts/pack-evaluator-bwrap.apparmor',
  'scripts/pack-evaluator-contract-smoke.mjs',
  'scripts/pack-evaluator-preflight.sh',
  'scripts/pack-evaluator-proxy.mjs',
  'scripts/pack-production-plan.mjs',
  'scripts/pack-production.mjs',
]);

const SHA_RE = /^[0-9a-f]{40}$/;
const SHA256_RE = /^[0-9a-f]{64}$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SAFE_SCENARIO_RE = /^[a-z0-9][a-z0-9-]{0,79}$/;
const MAX_PLAN_BYTES = 4 * 1024 * 1024;
const ARTIFACT_TRANSITIONS = new Map([
  ['plan', 'pack-production-plan'],
  ['evaluate', 'pack-production-evaluation'],
  ['persist', 'pack-production-persisted'],
]);

function fail(message) {
  throw new Error(message);
}

function object(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${label} must be an object`);
  return value;
}

function exactKeys(value, expected, label) {
  object(value, label);
  const actual = Object.keys(value).sort();
  if (canonicalJson(actual) !== canonicalJson([...expected].sort())) {
    fail(`${label} has unexpected fields`);
  }
}

function nonEmptyString(value, label) {
  if (typeof value !== 'string' || !value) fail(`${label} must be a non-empty string`);
  return value;
}

function positiveInteger(value, label) {
  if (!Number.isSafeInteger(value) || value < 1) fail(`${label} must be a positive integer`);
  return value;
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

export function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function withoutDigest(value) {
  const { digest: _digest, ...unsigned } = value;
  return unsigned;
}

export function executionPlanDigest(plan) {
  return sha256(canonicalJson(withoutDigest(plan)));
}

function expectedParameters(slotCount) {
  positiveInteger(slotCount, 'Plan capability slot count');
  const maxCandidates = 2;
  const hiddenVariants = 3;
  const maxPackSkills = 4;
  const maxBestSingleCompetitors = slotCount * maxCandidates;
  const estimatedRequests = 2
    + 4
    + (3 * slotCount * maxCandidates)
    + 3
    + (hiddenVariants * (maxPackSkills + 2))
    + (2 * hiddenVariants)
    + (3 * hiddenVariants * maxBestSingleCompetitors)
    + (hiddenVariants * maxPackSkills * (maxPackSkills + 1));
  return {
    generation: {
      autoPublishThreshold: 8,
      baselineDelta: 1,
      finalRuns: 3,
      maxCandidates,
      pick: 4,
      runs: 1,
      threshold: 7,
    },
    proxy: {
      allowedModels: [
        MODEL_IDENTITIES.runner.identity,
        MODEL_IDENTITIES.judge.identity,
      ],
      contractProbes: 2,
      estimatedRequests,
      hiddenVariants,
      maxBestSingleCompetitors,
      maxCliPreflightRequests: 4,
      maxConcurrent: 4,
      maxPackSkills,
      maxRequests: 256,
      port: 18765,
      reservedRequests: estimatedRequests + 64,
      toolLoopHeadroom: 64,
      upstreamUrl: 'https://helm.easymeta.au',
    },
    resources: {
      addressSpaceBytes: 6_442_450_944,
      evaluatorOutputBytes: 16_777_216,
      maxProcesses: 256,
      proxyActivityBytes: 1_048_576,
      resultBytes: 268_435_456,
      resultFiles: 1000,
    },
    retries: {
      agentMaxRetries: 1,
      contractMaxRetries: 0,
      executorPreflightMaxAttempts: 2,
    },
    runtime: {
      claudeCodeVersion: '2.1.210',
      codexVersion: '0.139.0',
    },
    timeoutsMs: {
      agent: 360_000,
      contract: 30_000,
      evaluationBudget: 13_800_000,
      evaluatorHeartbeat: 60_000,
      executorPreflight: 360_000,
      executorPreflightAgent: 180_000,
      executorPreflightHeartbeat: 30_000,
      executorPreflightIdle: 240_000,
      executorPreflightOuterKillGrace: 5_000,
      executorPreflightOuter: 420_000,
      executorPreflightRetryDelay: 5_000,
      minimumFallback: 2_700_000,
      outerEvaluation: 14_400_000,
      outerEvaluationKillGrace: 30_000,
      processKillGrace: 3_000,
      proxyRequest: 600_000,
      proxyTtl: 14_400_000,
      scenario: 7_200_000,
      scenarioIdle: 1_200_000,
    },
    tokens: {
      contractProbeOutput: 16,
      maxOutput: 16_384,
    },
  };
}

export function productionExecutionParameters(slotCount) {
  return structuredClone(expectedParameters(slotCount));
}

function validateModel(value, label) {
  exactKeys(value, ['identity', 'revision', 'pinType'], label);
  nonEmptyString(value.identity, `${label} identity`);
  if (
    value.revision !== 'workflow-pinned alias'
    || value.pinType !== 'workflow-pinned alias'
  ) {
    fail(`${label} must explicitly use workflow-pinned alias because no immutable provider revision is available`);
  }
}

function validateParameters(value) {
  exactKeys(
    value,
    ['generation', 'proxy', 'resources', 'retries', 'runtime', 'timeoutsMs', 'tokens'],
    'Execution Plan parameters',
  );
  for (const [group, entries] of Object.entries(value)) {
    object(entries, `Execution Plan parameters.${group}`);
    for (const [name, entry] of Object.entries(entries)) {
      if (group === 'proxy' && name === 'allowedModels') {
        if (!Array.isArray(entry) || entry.length !== 2 || entry.some((item) => typeof item !== 'string')) {
          fail('Execution Plan proxy allowedModels must contain two model identities');
        }
      } else if (group === 'proxy' && ['upstreamUrl'].includes(name)) {
        nonEmptyString(entry, `Execution Plan parameters.${group}.${name}`);
      } else if (group === 'runtime') {
        nonEmptyString(entry, `Execution Plan parameters.${group}.${name}`);
      } else if (group === 'retries' && name === 'contractMaxRetries' && entry === 0) {
        // The contract probes are intentionally single-attempt.
      } else {
        positiveInteger(entry, `Execution Plan parameters.${group}.${name}`);
      }
    }
  }
  if (value.proxy.reservedRequests > value.proxy.maxRequests) {
    fail('Execution Plan proxy request reservation exceeds its budget');
  }
}

function validateScenario(value) {
  object(value, 'Execution Plan scenario');
  if (!SAFE_SCENARIO_RE.test(value.id || '')) fail('Execution Plan scenario id is invalid');
  if (!UUID_RE.test(value.generationId || '')) fail('Execution Plan scenario generationId is invalid');
  nonEmptyString(value.task, 'Execution Plan scenario task');
  if (!Array.isArray(value.capabilitySlots) || value.capabilitySlots.length < 1 || value.capabilitySlots.length > 4) {
    fail('Execution Plan scenario capability slots are outside the production bound');
  }
  if (!Array.isArray(value.requiredArtifacts) || value.requiredArtifacts.length < 1) {
    fail('Execution Plan scenario requires at least one artifact');
  }
}

function validateSource(value) {
  exactKeys(
    value,
    ['repositoryTreeSha', 'skillsTreeSha', 'skillsManifest', 'files'],
    'Execution Plan source',
  );
  if (!SHA_RE.test(value.repositoryTreeSha || '') || !SHA_RE.test(value.skillsTreeSha || '')) {
    fail('Execution Plan git tree identity is invalid');
  }
  exactKeys(value.skillsManifest, ['sha256', 'fileCount', 'totalBytes'], 'Execution Plan Skills manifest');
  if (
    !SHA256_RE.test(value.skillsManifest.sha256 || '')
    || !Number.isSafeInteger(value.skillsManifest.fileCount)
    || value.skillsManifest.fileCount < 1
    || !Number.isSafeInteger(value.skillsManifest.totalBytes)
    || value.skillsManifest.totalBytes < 1
  ) fail('Execution Plan Skills manifest identity is invalid');
  if (!Array.isArray(value.files) || value.files.length < 1) {
    fail('Execution Plan source file identities are missing');
  }
  const paths = new Set();
  for (const [index, entry] of value.files.entries()) {
    exactKeys(entry, ['path', 'gitBlobSha', 'sha256'], `Execution Plan source file ${index + 1}`);
    if (
      typeof entry.path !== 'string'
      || entry.path.startsWith('/')
      || entry.path.includes('..')
      || paths.has(entry.path)
      || !SHA_RE.test(entry.gitBlobSha || '')
      || !SHA256_RE.test(entry.sha256 || '')
    ) fail(`Execution Plan source file ${index + 1} identity is invalid`);
    paths.add(entry.path);
  }
}

function validateEvaluatorInputs(value, plan) {
  exactKeys(
    value,
    ['configSha256', 'promptSha256', 'rulesSha256', 'scenarioSha256'],
    'Execution Plan evaluator inputs',
  );
  if (Object.values(value).some((digest) => !SHA256_RE.test(digest || ''))) {
    fail('Execution Plan evaluator input digest is invalid');
  }
  const expected = {
    configSha256: sha256(canonicalJson({
      cli: plan.executionBinding.cli,
      models: plan.executionBinding.models,
      parameters: plan.executionBinding.parameters,
    })),
    promptSha256: sha256(plan.scenario.task),
    rulesSha256: sha256(canonicalJson({
      capabilitySlots: plan.scenario.capabilitySlots,
      requiredArtifacts: plan.scenario.requiredArtifacts,
    })),
    scenarioSha256: sha256(canonicalJson(plan.scenario)),
  };
  if (canonicalJson(value) !== canonicalJson(expected)) {
    fail('Execution Plan evaluator input digest differs from its bound bytes');
  }
}

function validateExecutorPreflight(value) {
  exactKeys(value, ['generationId', 'skillA', 'skillB', 'task'], 'Execution Plan executor preflight');
  if (!UUID_RE.test(value.generationId || '')) fail('Execution Plan executor preflight generationId is invalid');
  nonEmptyString(value.task, 'Execution Plan executor preflight task');
  for (const [name, skill] of [['skillA', value.skillA], ['skillB', value.skillB]]) {
    exactKeys(skill, ['canonicalId', 'version', 'contentSha256'], `Execution Plan executor preflight ${name}`);
    nonEmptyString(skill.canonicalId, `Execution Plan executor preflight ${name} canonicalId`);
    nonEmptyString(skill.version, `Execution Plan executor preflight ${name} version`);
    if (!SHA256_RE.test(skill.contentSha256 || '')) {
      fail(`Execution Plan executor preflight ${name} digest is invalid`);
    }
  }
  if (value.skillA.canonicalId === value.skillB.canonicalId) {
    fail('Execution Plan executor preflight Skills must be distinct');
  }
}

export function validateExecutionPlan(plan) {
  exactKeys(
    plan,
    ['schemaVersion', 'digest', 'workflowBinding', 'executionBinding', 'scenario'],
    'Execution Plan',
  );
  if (plan.schemaVersion !== EXECUTION_PLAN_SCHEMA) {
    fail(`Unsupported execution Plan schema: ${plan.schemaVersion}`);
  }
  if (!SHA256_RE.test(plan.digest || '') || plan.digest !== executionPlanDigest(plan)) {
    fail('execution Plan digest mismatch');
  }
  validateScenario(plan.scenario);
  exactKeys(
    plan.workflowBinding,
    ['repository', 'workflow', 'runId', 'runAttempt', 'headSha', 'scenarioId', 'generationId'],
    'Execution Plan workflow binding',
  );
  const workflow = plan.workflowBinding;
  if (
    workflow.repository !== EXPECTED_REPOSITORY
    || workflow.workflow !== EXPECTED_WORKFLOW
    || !/^[1-9][0-9]*$/.test(workflow.runId || '')
    || !Number.isSafeInteger(workflow.runAttempt)
    || workflow.runAttempt < 1
    || !SHA_RE.test(workflow.headSha || '')
    || workflow.scenarioId !== plan.scenario.id
    || workflow.generationId !== plan.scenario.generationId
  ) fail('Execution Plan workflow binding is invalid or internally inconsistent');
  exactKeys(
    plan.executionBinding,
    ['cli', 'evaluatorInputs', 'executorPreflight', 'models', 'parameters', 'source'],
    'Execution Plan execution binding',
  );
  exactKeys(plan.executionBinding.models, ['runner', 'judge'], 'Execution Plan models');
  validateModel(plan.executionBinding.models.runner, 'Execution Plan runner');
  validateModel(plan.executionBinding.models.judge, 'Execution Plan judge');
  exactKeys(
    plan.executionBinding.cli,
    ['assetName', 'releaseAssetSha256', 'version'],
    'Execution Plan CLI',
  );
  nonEmptyString(plan.executionBinding.cli.assetName, 'Execution Plan CLI asset name');
  nonEmptyString(plan.executionBinding.cli.version, 'Execution Plan CLI version');
  if (!SHA256_RE.test(plan.executionBinding.cli.releaseAssetSha256 || '')) {
    fail('Execution Plan CLI release asset SHA-256 is invalid');
  }
  validateParameters(plan.executionBinding.parameters);
  validateEvaluatorInputs(plan.executionBinding.evaluatorInputs, plan);
  validateExecutorPreflight(plan.executionBinding.executorPreflight);
  validateSource(plan.executionBinding.source);
  return plan;
}

export function assertProductionExecutionPolicy(plan) {
  validateExecutionPlan(plan);
  const expected = {
    models: MODEL_IDENTITIES,
  };
  for (const [name, actual] of Object.entries({
    models: plan.executionBinding.models,
  })) {
    if (canonicalJson(actual) !== canonicalJson(expected[name])) {
      fail(`Execution Plan ${name} differs from the production policy`);
    }
  }
  const paths = plan.executionBinding.source.files.map((entry) => entry.path).sort();
  if (canonicalJson(paths) !== canonicalJson([...EXECUTION_SOURCE_FILES].sort())) {
    fail('Execution Plan source file set differs from the production policy');
  }
  return plan;
}

async function readBoundedRegularFile(file, maximumBytes, label) {
  const path = resolve(file);
  const metadata = await lstat(path);
  if (!metadata.isFile() || metadata.isSymbolicLink()) fail(`${label} must be a regular file`);
  if (metadata.size < 1 || metadata.size > maximumBytes) {
    fail(`${label} is outside its ${maximumBytes}-byte bound`);
  }
  return readFile(path);
}

async function readCanonicalJson(file, label) {
  const bytes = await readBoundedRegularFile(file, MAX_PLAN_BYTES, label);
  let value;
  try {
    value = JSON.parse(bytes.toString('utf8'));
  } catch {
    fail(`${label} is not valid JSON`);
  }
  if (!bytes.equals(Buffer.from(canonicalJson(value)))) {
    fail(`${label} must contain canonical JSON bytes`);
  }
  return value;
}

export async function readExecutionPlan(file) {
  return validateExecutionPlan(await readCanonicalJson(file, 'Execution Plan'));
}

export async function verifyRuntimeSourceFiles(plan, runtimeFiles) {
  assertProductionExecutionPolicy(plan);
  if (!runtimeFiles || typeof runtimeFiles !== 'object' || Array.isArray(runtimeFiles)) {
    fail('Runtime source file mapping is required');
  }
  const expectedByPath = new Map(
    plan.executionBinding.source.files.map((entry) => [entry.path, entry]),
  );
  for (const [sourcePath, runtimePath] of Object.entries(runtimeFiles)) {
    const expected = expectedByPath.get(sourcePath);
    if (!expected) fail(`Runtime source is not bound by the execution Plan: ${sourcePath}`);
    if (sha256(await readFile(runtimePath)) !== expected.sha256) {
      fail(`Runtime source differs from the execution Plan: ${sourcePath}`);
    }
  }
  return true;
}

export async function writeCanonicalJsonAtomic(file, value, mode = 0o600) {
  const target = resolve(file);
  await mkdir(dirname(target), { recursive: true });
  const temporary = resolve(dirname(target), `.${basename(target)}.${process.pid}.${randomUUID()}.tmp`);
  try {
    await writeFile(temporary, canonicalJson(value), { mode, flag: 'wx' });
    await chmod(temporary, mode);
    await rename(temporary, target);
  } catch (error) {
    await import('node:fs/promises').then(({ rm }) => rm(temporary, { force: true })).catch(() => {});
    throw error;
  }
}

export async function writeExecutionPlanAtomic(file, plan) {
  validateExecutionPlan(plan);
  await writeCanonicalJsonAtomic(file, plan);
}

function git(repoRoot, args, label) {
  const result = spawnSync('git', args, { cwd: repoRoot, encoding: 'utf8' });
  if (result.status !== 0) fail(`Cannot read ${label}: ${result.stderr || result.stdout}`);
  return result.stdout.trim();
}

async function directoryManifest(root) {
  const base = resolve(root);
  const files = [];
  const visit = async (directory) => {
    const entries = await readdir(directory, { withFileTypes: true });
    entries.sort((left, right) => left.name.localeCompare(right.name));
    for (const entry of entries) {
      const path = resolve(directory, entry.name);
      if (entry.isSymbolicLink()) fail(`Skills input contains a symbolic link: ${path}`);
      if (entry.isDirectory()) {
        await visit(path);
        continue;
      }
      if (!entry.isFile()) fail(`Skills input contains a non-regular entry: ${path}`);
      const bytes = await readFile(path);
      files.push({
        path: relative(base, path).split(sep).join('/'),
        sha256: sha256(bytes),
        size: bytes.length,
      });
    }
  };
  await visit(base);
  if (files.length < 1) fail('Skills input manifest is empty');
  return {
    sha256: sha256(canonicalJson(files)),
    fileCount: files.length,
    totalBytes: files.reduce((total, entry) => total + entry.size, 0),
  };
}

function cliVersion(cli) {
  const result = spawnSync(cli, ['--version'], { encoding: 'utf8' });
  if (result.status !== 0) fail(`Cannot read CLI version: ${result.stderr || result.stdout}`);
  const version = `${result.stdout}\n${result.stderr}`.match(
    /[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z._-]+)?/,
  )?.[0];
  if (!version) fail('CLI version output is not parseable');
  return version;
}

export async function verifyCliAgainstPlan(plan, cliPath) {
  validateExecutionPlan(plan);
  const cli = resolve(cliPath);
  const bytes = await readBoundedRegularFile(cli, 512 * 1024 * 1024, 'Skillstore CLI');
  const identity = plan.executionBinding.cli;
  if (sha256(bytes) !== identity.releaseAssetSha256) {
    fail('CLI bytes differ from the execution Plan release asset SHA-256');
  }
  if (cliVersion(cli) !== identity.version) {
    fail('CLI version differs from the execution Plan');
  }
  return identity;
}

async function sourceIdentity(repoRoot, headSha) {
  const root = resolve(repoRoot);
  const actualHead = git(root, ['rev-parse', 'HEAD'], 'repository HEAD');
  if (actualHead !== headSha) fail('Repository HEAD differs from the execution Plan workflow binding');
  const files = [];
  for (const path of EXECUTION_SOURCE_FILES) {
    const bytes = await readBoundedRegularFile(resolve(root, path), MAX_PLAN_BYTES, `source file ${path}`);
    files.push({
      path,
      gitBlobSha: git(root, ['rev-parse', `HEAD:${path}`], `git blob ${path}`),
      sha256: sha256(bytes),
    });
  }
  return {
    repositoryTreeSha: git(root, ['rev-parse', 'HEAD^{tree}'], 'repository tree'),
    skillsTreeSha: git(root, ['rev-parse', 'HEAD:skills'], 'Skills tree'),
    skillsManifest: await directoryManifest(resolve(root, 'skills')),
    files,
  };
}

export async function verifySourceAgainstPlan(plan, repoRoot) {
  assertProductionExecutionPolicy(plan);
  const actual = await sourceIdentity(repoRoot, plan.workflowBinding.headSha);
  if (canonicalJson(actual) !== canonicalJson(plan.executionBinding.source)) {
    fail('Repository source identity differs from the execution Plan');
  }
  return actual;
}

export async function verifySkillsAgainstPlan(plan, skillsDir) {
  validateExecutionPlan(plan);
  const actual = await directoryManifest(skillsDir);
  if (canonicalJson(actual) !== canonicalJson(plan.executionBinding.source.skillsManifest)) {
    fail('Skills bytes differ from the execution Plan manifest');
  }
  return actual;
}

function parseQueuePlan(bytes) {
  let queue;
  try {
    queue = JSON.parse(bytes.toString('utf8'));
  } catch {
    fail('Queue response is not valid JSON');
  }
  if (
    queue?.schemaVersion !== 'pack-production-queue/v1'
    || queue.source !== 'signals'
    || !Array.isArray(queue.scenarios)
    || queue.scenarios.length !== 1
  ) fail('Execution Plan requires exactly one signal-admitted queue scenario');
  return queue;
}

export async function createExecutionPlan({
  queueFile,
  generationId,
  repository,
  workflow,
  runId,
  runAttempt,
  headSha,
  repoRoot,
  cliPath,
}) {
  if (!UUID_RE.test(generationId || '')) fail('Execution Plan generationId must be a UUID');
  if (
    repository !== EXPECTED_REPOSITORY
    || workflow !== EXPECTED_WORKFLOW
    || !/^[1-9][0-9]*$/.test(runId || '')
    || !Number.isSafeInteger(runAttempt)
    || runAttempt < 1
    || !SHA_RE.test(headSha || '')
  ) fail('Execution Plan workflow invocation is invalid');
  const queueBytes = await readBoundedRegularFile(queueFile, MAX_PLAN_BYTES, 'queue response');
  const queue = parseQueuePlan(queueBytes);
  const plannedScenario = { ...queue.scenarios[0], generationId };
  validateScenario(plannedScenario);
  const parameters = expectedParameters(plannedScenario.capabilitySlots.length);
  const source = await sourceIdentity(repoRoot, headSha);
  const preflight = {
    generationId: '00000000-0000-4000-8000-000000000001',
    skillA: {
      canonicalId: EXECUTOR_PREFLIGHT_SKILLS[0].canonicalId,
      contentSha256: sha256(EXECUTOR_PREFLIGHT_SKILLS[0].contents),
      version: EXECUTOR_PREFLIGHT_SKILLS[0].version,
    },
    skillB: {
      canonicalId: EXECUTOR_PREFLIGHT_SKILLS[1].canonicalId,
      contentSha256: sha256(EXECUTOR_PREFLIGHT_SKILLS[1].contents),
      version: EXECUTOR_PREFLIGHT_SKILLS[1].version,
    },
    task: EXECUTOR_PREFLIGHT_TASK,
  };
  const executionBinding = {
    cli: { ...CLI_IDENTITY },
    evaluatorInputs: null,
    executorPreflight: preflight,
    models: structuredClone(MODEL_IDENTITIES),
    parameters,
    source,
  };
  const unsigned = {
    schemaVersion: EXECUTION_PLAN_SCHEMA,
    workflowBinding: {
      repository,
      workflow,
      runId,
      runAttempt,
      headSha,
      scenarioId: plannedScenario.id,
      generationId,
    },
    executionBinding,
    scenario: plannedScenario,
  };
  executionBinding.evaluatorInputs = {
    configSha256: sha256(canonicalJson({
      cli: executionBinding.cli,
      models: executionBinding.models,
      parameters,
    })),
    promptSha256: sha256(plannedScenario.task),
    rulesSha256: sha256(canonicalJson({
      capabilitySlots: plannedScenario.capabilitySlots,
      requiredArtifacts: plannedScenario.requiredArtifacts,
    })),
    scenarioSha256: sha256(canonicalJson(plannedScenario)),
  };
  const plan = { ...unsigned, digest: sha256(canonicalJson(unsigned)) };
  assertProductionExecutionPolicy(plan);
  await verifyCliAgainstPlan(plan, cliPath);
  return plan;
}

function artifactGateDigest(gate) {
  return sha256(canonicalJson(withoutDigest(gate)));
}

function validateArtifactState(state, plan) {
  exactKeys(
    state,
    ['schemaVersion', 'workflowBinding', 'producer', 'artifact'],
    'Artifact state',
  );
  if (state.schemaVersion !== ARTIFACT_STATE_SCHEMA) {
    fail(`Unsupported artifact state schema: ${state.schemaVersion}`);
  }
  exactKeys(state.producer, ['name', 'status'], 'Artifact producer state');
  exactKeys(state.artifact, ['name', 'status', 'planDigest'], 'Artifact download state');
  if (state.producer.status !== 'success') fail('artifact producer status must be success');
  if (state.artifact.status !== 'downloaded') fail('artifact status must be downloaded');
  if (
    ARTIFACT_TRANSITIONS.get(state.producer.name) !== state.artifact.name
    || state.artifact.planDigest !== plan.digest
    || canonicalJson(state.workflowBinding) !== canonicalJson(plan.workflowBinding)
  ) fail('artifact state differs from the execution Plan');
  return state;
}

export async function createArtifactGate(planFile, stateFile, outputFile) {
  const plan = await readExecutionPlan(planFile);
  const state = validateArtifactState(
    await readCanonicalJson(stateFile, 'Artifact state'),
    plan,
  );
  const unsigned = {
    schemaVersion: ARTIFACT_GATE_SCHEMA,
    planDigest: plan.digest,
    workflowBinding: plan.workflowBinding,
    producer: state.producer,
    artifact: state.artifact,
  };
  const gate = { ...unsigned, digest: sha256(canonicalJson(unsigned)) };
  await writeCanonicalJsonAtomic(outputFile, gate);
  return gate;
}

function validateArtifactGateValue(gate, plan, expectedProducer, expectedArtifact) {
  exactKeys(
    gate,
    ['schemaVersion', 'planDigest', 'workflowBinding', 'producer', 'artifact', 'digest'],
    'Artifact gate',
  );
  if (
    gate.schemaVersion !== ARTIFACT_GATE_SCHEMA
    || !SHA256_RE.test(gate.digest || '')
    || gate.digest !== artifactGateDigest(gate)
  ) fail('Artifact gate digest is invalid');
  validateArtifactState({
    schemaVersion: ARTIFACT_STATE_SCHEMA,
    workflowBinding: gate.workflowBinding,
    producer: gate.producer,
    artifact: gate.artifact,
  }, plan);
  if (
    gate.planDigest !== plan.digest
    || gate.producer.name !== expectedProducer
    || gate.artifact.name !== expectedArtifact
  ) fail('Artifact gate does not authorize this runtime transition');
  return gate;
}

export async function readArtifactGate(file, plan, expectedProducer, expectedArtifact) {
  return validateArtifactGateValue(
    await readCanonicalJson(file, 'Artifact gate'),
    plan,
    expectedProducer,
    expectedArtifact,
  );
}

export function planRuntimeValues(plan) {
  assertProductionExecutionPolicy(plan);
  return {
    digest: plan.digest,
    workflowBinding: plan.workflowBinding,
    cli: plan.executionBinding.cli,
    models: plan.executionBinding.models,
    parameters: plan.executionBinding.parameters,
    executorPreflight: plan.executionBinding.executorPreflight,
  };
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const args = { command };
  for (let index = 0; index < rest.length; index += 1) {
    const token = rest[index];
    if (!token.startsWith('--')) fail(`Unexpected argument: ${token}`);
    const name = token.slice(2);
    const value = rest[index + 1];
    if (!value || value.startsWith('--')) fail(`Missing value for --${name}`);
    args[name] = value;
    index += 1;
  }
  return args;
}

function required(args, name) {
  if (!args[name]) fail(`--${name} is required`);
  return args[name];
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.command === 'create') {
    const plan = await createExecutionPlan({
      queueFile: required(args, 'queue'),
      generationId: required(args, 'generation-id'),
      repository: required(args, 'repository'),
      workflow: required(args, 'workflow'),
      runId: required(args, 'run-id'),
      runAttempt: Number(required(args, 'run-attempt')),
      headSha: required(args, 'head-sha'),
      repoRoot: required(args, 'repo-root'),
      cliPath: required(args, 'cli'),
    });
    await writeExecutionPlanAtomic(required(args, 'output'), plan);
    process.stdout.write(`${JSON.stringify({ digest: plan.digest })}\n`);
    return;
  }
  if (args.command === 'verify-inputs') {
    const plan = await readExecutionPlan(required(args, 'plan'));
    await verifySourceAgainstPlan(plan, required(args, 'repo-root'));
    await verifyCliAgainstPlan(plan, required(args, 'cli'));
    process.stdout.write(`${JSON.stringify({ digest: plan.digest, outcome: 'passed' })}\n`);
    return;
  }
  if (args.command === 'values') {
    const plan = await readExecutionPlan(required(args, 'plan'));
    process.stdout.write(`${JSON.stringify(planRuntimeValues(plan))}\n`);
    return;
  }
  fail('Usage: pack-production-plan.mjs <create|verify-inputs|values> [options]');
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`${error.stack ?? error.message ?? String(error)}\n`);
    process.exitCode = 1;
  });
}
