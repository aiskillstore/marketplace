#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { lstat, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  buildInfrastructureApiEvaluation,
  canonicalJson,
} from './pack-production.mjs';
import {
  CLI_IDENTITY,
  assertProductionExecutionPolicy,
  readExecutionPlan,
} from './pack-production-plan.mjs';

const RECOVERY_SCHEMA = 'marketplace.pack-production-cancellation-recovery/v1';
const SOURCE_SCHEMA = 'marketplace.pack-production-source-run/v1';
const API_SCHEMA = 'skillstore.pack-evaluation/v4';
const INFRASTRUCTURE_SCHEMA = 'marketplace.pack-production-infrastructure-failure/v1';
const CLI_EVIDENCE_SCHEMA = 'marketplace.pack-production-cli-evidence/v1';
const EXPECTED_REPOSITORY = 'aiskillstore/marketplace';
const EXPECTED_WORKFLOW_NAME = 'Generate Pack';
const EXPECTED_WORKFLOW_PATH = '.github/workflows/generate-packs.yml';
const EXPECTED_BRANCH = 'main';
const PLAN_ARTIFACT = 'pack-production-plan';
const DIAGNOSTICS_ARTIFACT = 'pack-production-diagnostics';
const FORBIDDEN_DOWNSTREAM_ARTIFACTS = new Set([
  'pack-production-evaluation',
  'pack-production-persisted',
  'pack-production-final',
]);
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const SHA256_RE = /^[0-9a-f]{64}$/;
const SHA_RE = /^[0-9a-f]{40}$/;
const SAFE_ID_RE = /^[a-z0-9][a-z0-9-]{0,79}$/;
const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const MAX_JSON_BYTES = 2 * 1024 * 1024;
const MAX_PLAN_ARTIFACT_BYTES = 5 * 1024 * 1024;
const MAX_DIAGNOSTICS_ARTIFACT_BYTES = 64 * 1024 * 1024;
const MAX_PROGRESS_BYTES = 4 * 1024 * 1024;
const MAX_PROGRESS_EVENTS = 10_000;

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

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function record(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`${label} must be an object`);
  return value;
}

function safeInteger(value, label) {
  const parsed = Number(value);
  if (!Number.isSafeInteger(parsed) || parsed < 1) fail(`${label} must be a positive integer`);
  return parsed;
}

function isoTimestamp(value, label) {
  if (typeof value !== 'string' || !Number.isFinite(Date.parse(value))) fail(`${label} is not an ISO timestamp`);
  return new Date(value).toISOString();
}

async function readBoundedFile(file, maximumBytes, label) {
  const path = resolve(file);
  const metadata = await lstat(path);
  if (!metadata.isFile() || metadata.isSymbolicLink()) fail(`${label} must be a regular file`);
  if (metadata.size < 1 || metadata.size > maximumBytes) {
    fail(`${label} is outside its ${maximumBytes}-byte bound`);
  }
  return readFile(path);
}

async function readJson(file, maximumBytes = MAX_JSON_BYTES, label = basename(file)) {
  const contents = await readBoundedFile(file, maximumBytes, label);
  try {
    return JSON.parse(contents.toString('utf8'));
  } catch {
    fail(`${label} is not valid JSON`);
  }
}

async function optionalJson(file, maximumBytes = MAX_JSON_BYTES, label = basename(file)) {
  try {
    return await readJson(file, maximumBytes, label);
  } catch (error) {
    if (error?.code === 'ENOENT') return null;
    throw error;
  }
}

async function writeJson(file, value) {
  await mkdir(resolve(file, '..'), { recursive: true });
  await writeFile(resolve(file), `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
}

export function inspectWorkflowRunEvent(event) {
  const root = record(event, 'GitHub event');
  const run = record(root.workflow_run, 'workflow_run');
  const repository = record(root.repository, 'event repository');
  const headRepository = record(run.head_repository, 'workflow_run head repository');
  if (root.action !== 'completed') fail('Recovery accepts only completed workflow_run events');
  if (repository.full_name !== EXPECTED_REPOSITORY || headRepository.full_name !== EXPECTED_REPOSITORY) {
    fail('Recovery source repository is not the trusted Marketplace repository');
  }
  if (run.name !== EXPECTED_WORKFLOW_NAME || run.path !== EXPECTED_WORKFLOW_PATH) {
    fail('Recovery source is not the exact Generate Pack workflow');
  }
  if (run.status !== 'completed' || run.conclusion !== 'cancelled') {
    fail('Recovery accepts only cancelled terminal Generate Pack runs');
  }
  if (!['schedule', 'workflow_dispatch'].includes(run.event)) {
    fail('Recovery rejects Generate Pack runs from any event except schedule or workflow_dispatch');
  }
  if (run.head_branch !== EXPECTED_BRANCH) fail('Recovery source must run on main');
  if (!SHA_RE.test(run.head_sha || '')) fail('Recovery source head SHA is invalid');
  const id = safeInteger(run.id, 'workflow_run.id');
  const runAttempt = safeInteger(run.run_attempt, 'workflow_run.run_attempt');
  const workflowId = safeInteger(run.workflow_id, 'workflow_run.workflow_id');
  const startedAt = isoTimestamp(run.run_started_at, 'workflow_run.run_started_at');
  const completedAt = isoTimestamp(run.updated_at, 'workflow_run.updated_at');
  if (Date.parse(completedAt) < Date.parse(startedAt)) fail('Workflow completion precedes its start');
  return {
    schemaVersion: SOURCE_SCHEMA,
    repository: EXPECTED_REPOSITORY,
    workflowName: EXPECTED_WORKFLOW_NAME,
    workflowPath: EXPECTED_WORKFLOW_PATH,
    workflowId,
    runId: id,
    runAttempt,
    event: run.event,
    conclusion: run.conclusion,
    branch: EXPECTED_BRANCH,
    commitSha: run.head_sha,
    startedAt,
    completedAt,
  };
}

export function verifySourceMetadata({ source, attempt, workflow, comparison, workflowSource }) {
  record(source, 'source run');
  const apiAttempt = record(attempt, 'source attempt API response');
  const expectedWorkflow = record(workflow, 'expected workflow API response');
  const compare = record(comparison, 'source commit comparison');
  if (
    apiAttempt.id !== source.runId
    || apiAttempt.run_attempt !== source.runAttempt
    || apiAttempt.workflow_id !== source.workflowId
    || apiAttempt.name !== source.workflowName
    || apiAttempt.path !== source.workflowPath
    || apiAttempt.event !== source.event
    || apiAttempt.status !== 'completed'
    || apiAttempt.conclusion !== 'cancelled'
    || apiAttempt.head_branch !== source.branch
    || apiAttempt.head_sha !== source.commitSha
    || isoTimestamp(apiAttempt.run_started_at, 'source attempt start') !== source.startedAt
    || isoTimestamp(apiAttempt.updated_at, 'source attempt completion') !== source.completedAt
  ) fail('Source attempt API response differs from the workflow_run event');
  if (
    expectedWorkflow.id !== source.workflowId
    || expectedWorkflow.name !== source.workflowName
    || expectedWorkflow.path !== source.workflowPath
    || expectedWorkflow.state !== 'active'
  ) fail('Generate Pack workflow identity is no longer exact and active');
  if (
    !['ahead', 'identical'].includes(compare.status)
    || compare.base_commit?.sha !== source.commitSha
    || compare.merge_base_commit?.sha !== source.commitSha
  ) fail('Source commit is not an ancestor of the trusted recovery workflow commit');
  if (typeof workflowSource !== 'string' || Buffer.byteLength(workflowSource) > MAX_JSON_BYTES) {
    fail('Source Generate Pack workflow is missing or too large');
  }
  if (!/^name:\s*Generate Pack\s*$/m.test(workflowSource)) fail('Source workflow name contract is missing');
  if (
    !/randomUUID\(\)/.test(workflowSource)
    || !/pack-production-plan\.mjs" create/.test(workflowSource)
    || !/--run-id "\$GITHUB_RUN_ID"/.test(workflowSource)
    || !/--run-attempt "\$GITHUB_RUN_ATTEMPT"/.test(workflowSource)
    || !/--head-sha "\$GITHUB_SHA"/.test(workflowSource)
    || !/--workflow "\$GITHUB_WORKFLOW"/.test(workflowSource)
  ) fail('Source workflow lacks canonical execution Plan creation and workflow binding');
  if (/--(?:model|judge-model|expected-cli-version|agent-timeout-ms|max-candidates)\b/.test(workflowSource)) {
    fail('Source workflow retains a deprecated execution override');
  }
  return { workflowSourceSha256: sha256(workflowSource) };
}

function artifactRun(artifact, source) {
  const run = record(artifact.workflow_run, `artifact ${artifact.name} workflow_run`);
  return run.id === source.runId
    && run.head_sha === source.commitSha
    && run.head_branch === source.branch;
}

export function verifyArtifactIndex(index, source) {
  const payload = record(index, 'artifact index');
  if (!Number.isSafeInteger(payload.total_count) || payload.total_count < 0) {
    fail('Source run artifact count is invalid');
  }
  if (payload.total_count > 100) {
    return { recoverable: false, reason: 'source_artifact_window_exceeds_bound' };
  }
  if (!Array.isArray(payload.artifacts) || payload.artifacts.length !== payload.total_count) {
    fail('Source run artifact index is incomplete');
  }
  for (const artifact of payload.artifacts) {
    record(artifact, 'artifact');
    if (typeof artifact.name !== 'string' || artifact.name.length < 1 || artifact.name.length > 256) {
      fail('Source artifact name is invalid');
    }
    if (!artifactRun(artifact, source)) fail(`Artifact ${artifact.name} is not bound to the source run`);
    safeInteger(artifact.id, `artifact ${artifact.name} id`);
    if (!Number.isSafeInteger(artifact.size_in_bytes) || artifact.size_in_bytes < 1) {
      fail(`Artifact ${artifact.name} has an invalid size`);
    }
    if (
      !Number.isFinite(Date.parse(artifact.created_at))
      || !Number.isFinite(Date.parse(artifact.updated_at))
      || typeof artifact.expired !== 'boolean'
    ) fail(`Artifact ${artifact.name} has invalid lifecycle metadata`);
  }
  const attemptStartedAt = Date.parse(source.startedAt);
  const attemptCompletedAt = Date.parse(source.completedAt);
  const current = payload.artifacts.filter((artifact) => {
    const createdAt = Date.parse(artifact.created_at);
    const updatedAt = Date.parse(artifact.updated_at);
    return Number.isFinite(createdAt)
      && Number.isFinite(updatedAt)
      && createdAt >= attemptStartedAt
      && createdAt <= attemptCompletedAt
      && updatedAt >= createdAt
      && updatedAt <= attemptCompletedAt
      && artifact.expired === false;
  });
  const named = (name) => current.filter((artifact) => artifact.name === name);
  const plan = named(PLAN_ARTIFACT);
  const diagnostics = named(DIAGNOSTICS_ARTIFACT);
  const downstream = current.filter((artifact) => FORBIDDEN_DOWNSTREAM_ARTIFACTS.has(artifact.name));
  if (plan.length !== 1) return { recoverable: false, reason: 'immutable_plan_artifact_missing_or_ambiguous' };
  if (plan[0].size_in_bytes > MAX_PLAN_ARTIFACT_BYTES) {
    return { recoverable: false, reason: 'immutable_plan_artifact_exceeds_bound' };
  }
  if (diagnostics.length > 1) return { recoverable: false, reason: 'diagnostics_artifact_ambiguous' };
  if (diagnostics[0]?.size_in_bytes > MAX_DIAGNOSTICS_ARTIFACT_BYTES) {
    return { recoverable: false, reason: 'diagnostics_artifact_exceeds_bound' };
  }
  if (downstream.length > 0) {
    return {
      recoverable: false,
      reason: 'trusted_evaluation_or_downstream_artifact_exists',
      downstreamArtifacts: downstream.map(({ id, name }) => ({ id, name })),
    };
  }
  return {
    recoverable: true,
    planArtifact: { id: plan[0].id, size: plan[0].size_in_bytes, createdAt: plan[0].created_at },
    diagnosticsArtifact: diagnostics[0]
      ? { id: diagnostics[0].id, size: diagnostics[0].size_in_bytes, createdAt: diagnostics[0].created_at }
      : null,
  };
}

function validateScenario(scenario) {
  const value = record(scenario, 'admitted scenario');
  if (!SAFE_ID_RE.test(value.id || '')) fail('Admitted scenario id is invalid');
  if (
    typeof value.version !== 'string'
    || value.version.length > 32
    || !/^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9._-]+)?$/.test(value.version)
  ) {
    fail('Admitted scenario version is invalid');
  }
  if (typeof value.task !== 'string' || !value.task.trim() || value.task.length > 12_000) {
    fail('Admitted scenario task is invalid');
  }
  if (typeof value.slug !== 'string' || value.slug.length > 86 || !SLUG_RE.test(value.slug)) {
    fail('Admitted scenario slug is invalid');
  }
  if (typeof value.name !== 'string' || !value.name.trim() || value.name.length > 180) {
    fail('Admitted scenario name is invalid');
  }
  if (
    !Array.isArray(value.tags)
    || value.tags.length < 1
    || value.tags.length > 10
    || value.tags.some((tag) => typeof tag !== 'string' || tag.length > 50 || !SAFE_ID_RE.test(tag))
  ) fail('Admitted scenario tags are invalid');
  if (!Array.isArray(value.capabilitySlots) || value.capabilitySlots.length < 1 || value.capabilitySlots.length > 4) {
    fail('Admitted scenario capability slots are outside the production bound');
  }
  const requiredSlots = value.capabilitySlots.filter((slot) => slot?.required === true);
  if (requiredSlots.length < 1 || requiredSlots.some((slot) => !SAFE_ID_RE.test(slot.id || ''))) {
    fail('Admitted scenario has no valid required capability slot');
  }
  if (!Array.isArray(value.requiredArtifacts) || value.requiredArtifacts.length < 1) {
    fail('Admitted scenario has no required artifact contract');
  }
  return value;
}

async function progressBindings(file, scenarioId) {
  let contents;
  try {
    contents = await readBoundedFile(file, MAX_PROGRESS_BYTES, 'evaluator progress');
  } catch (error) {
    if (error?.code === 'ENOENT') return [];
    throw error;
  }
  const lines = contents.toString('utf8').split('\n').filter(Boolean);
  if (lines.length > MAX_PROGRESS_EVENTS) fail('Evaluator progress exceeds the event-count bound');
  const bindings = [];
  let previousSequence = 0;
  for (const line of lines) {
    let event;
    try {
      event = JSON.parse(line);
    } catch {
      fail('Evaluator progress contains malformed JSON');
    }
    if (event.schemaVersion !== 'marketplace.pack-production-progress/v1') {
      fail('Evaluator progress schema is invalid');
    }
    if (!Number.isSafeInteger(event.seq) || event.seq <= previousSequence) fail('Evaluator progress sequence is invalid');
    previousSequence = event.seq;
    if (event.scenarioId != null && event.scenarioId !== scenarioId) {
      fail('Evaluator progress scenario differs from the immutable plan');
    }
    if (event.generationId != null) bindings.push(event.generationId);
  }
  return bindings;
}

async function diagnosticsBinding(diagnosticsDir, scenario, plan, cliIdentity) {
  const directory = resolve(diagnosticsDir);
  let entries;
  try {
    entries = await readdir(directory, { withFileTypes: true });
  } catch (error) {
    if (error?.code === 'ENOENT') return { unsafe: true, reason: 'diagnostics_download_missing_or_invalid' };
    throw error;
  }
  if (entries.length < 1 || entries.length > 1_000 || entries.some((entry) => !entry.isFile())) {
    return { unsafe: true, reason: 'diagnostics_download_missing_or_invalid' };
  }
  const summary = await optionalJson(resolve(directory, 'evaluate-summary.json'));
  const checkpoint = await optionalJson(resolve(directory, 'evaluate-checkpoint.json'));
  const bindings = await progressBindings(resolve(directory, 'evaluate-progress.ndjson'), scenario.id);
  const statuses = [];
  if (summary) {
    if (summary.schemaVersion !== 'marketplace.pack-production-evaluate/v1') fail('Evaluator summary schema is invalid');
    if (summary.executionPlanDigest !== plan.digest) {
      fail('Evaluator summary execution Plan differs from the immutable plan');
    }
    if (summary.cliVersion !== cliIdentity.version || summary.cliSha256 !== cliIdentity.sha256) {
      fail('Evaluator summary CLI identity differs from the immutable plan');
    }
    if (!Array.isArray(summary.reports) || !Array.isArray(summary.attempts)) fail('Evaluator summary is incomplete');
    if (summary.reports.length > 0 || summary.selectedGenerationId != null) {
      return { unsafe: true, reason: 'evaluator_report_recorded_before_cancellation' };
    }
    for (const attempt of summary.attempts) {
      if (attempt?.scenarioId !== scenario.id) fail('Evaluator attempt scenario differs from the immutable plan');
      if (attempt.generationId != null) bindings.push(attempt.generationId);
      if (attempt.status != null) statuses.push(attempt.status);
    }
  }
  if (checkpoint) {
    if (checkpoint.schemaVersion !== 'marketplace.pack-production-progress/v1') fail('Evaluator checkpoint schema is invalid');
    if (checkpoint.scenarioId != null && checkpoint.scenarioId !== scenario.id) {
      fail('Evaluator checkpoint scenario differs from the immutable plan');
    }
    if (checkpoint.generationId != null) bindings.push(checkpoint.generationId);
  }
  const unique = [...new Set(bindings.filter((value) => value != null))];
  if (unique.some((value) => !UUID_RE.test(value))) fail('Evaluator diagnostics contain an invalid generation id');
  if (unique.length > 1) fail('Evaluator diagnostics contain conflicting generation ids');
  if (statuses.some((status) => status === 'completed')) {
    return { unsafe: true, reason: 'completed_evaluator_attempt_has_no_trusted_report' };
  }
  return { generationId: unique[0] ?? null, statuses: [...new Set(statuses)] };
}

function validateCliIdentity(value) {
  const identity = record(value, 'CLI identity');
  if (identity.version !== CLI_IDENTITY.version) {
    fail(`Plan CLI version must be ${CLI_IDENTITY.version}`);
  }
  if (
    identity.assetName !== CLI_IDENTITY.assetName
    || identity.releaseAssetSha256 !== CLI_IDENTITY.releaseAssetSha256
  ) fail('Plan CLI release asset identity is invalid');
  return {
    assetName: identity.assetName,
    version: identity.version,
    sha256: identity.releaseAssetSha256,
  };
}

function planBinding(plan, source, scenario) {
  const binding = plan.workflowBinding;
  const expectedKeys = [
    'repository',
    'workflow',
    'runId',
    'runAttempt',
    'headSha',
    'scenarioId',
    'generationId',
  ];
  if (
    !binding
    || typeof binding !== 'object'
    || Array.isArray(binding)
    || canonicalJson(Object.keys(binding).sort()) !== canonicalJson(expectedKeys.sort())
    || binding.repository !== source.repository
    || binding.workflow !== source.workflowName
    || String(binding.runId) !== String(source.runId)
    || Number(binding.runAttempt) !== source.runAttempt
    || binding.headSha !== source.commitSha
    || binding.scenarioId !== scenario.id
    || binding.generationId !== scenario.generationId
  ) fail('Immutable plan workflow binding differs from the cancelled source run');
}

function unrecoverable(source, reason, evidence = {}) {
  return {
    schemaVersion: RECOVERY_SCHEMA,
    outcome: 'unrecoverable',
    reason,
    source,
    generationId: null,
    evaluationSha256: null,
    persisted: false,
    evidence,
  };
}

export async function prepareCancellationRecovery({
  source,
  attempt,
  workflow,
  comparison,
  workflowSource,
  artifactIndex,
  planDir,
  diagnosticsDir,
  outputDir,
}) {
  const sourceVerification = verifySourceMetadata({ source, attempt, workflow, comparison, workflowSource });
  const artifactVerification = verifyArtifactIndex(artifactIndex, source);
  const output = resolve(outputDir);
  await mkdir(output, { recursive: true });
  if (!artifactVerification.recoverable) {
    const result = unrecoverable(source, artifactVerification.reason, { artifactVerification, sourceVerification });
    await writeJson(resolve(output, 'recovery-result.json'), result);
    return result;
  }

  let plan;
  let cliIdentity;
  try {
    plan = assertProductionExecutionPolicy(
      await readExecutionPlan(resolve(planDir, 'plan.json')),
    );
    cliIdentity = validateCliIdentity(plan.executionBinding.cli);
  } catch (error) {
    const result = unrecoverable(source, error?.code === 'ENOENT'
      ? 'immutable_plan_download_missing'
      : 'immutable_execution_plan_invalid', {
      artifactVerification,
      sourceVerification,
    });
    await writeJson(resolve(output, 'recovery-result.json'), result);
    return result;
  }
  let scenario;
  try {
    scenario = validateScenario(plan.scenario);
    planBinding(plan, source, scenario);
  } catch {
    const result = unrecoverable(source, 'immutable_plan_scenario_or_binding_invalid', {
      artifactVerification,
      sourceVerification,
    });
    await writeJson(resolve(output, 'recovery-result.json'), result);
    return result;
  }
  let diagnostics;
  try {
    diagnostics = artifactVerification.diagnosticsArtifact
      ? await diagnosticsBinding(diagnosticsDir, scenario, plan, cliIdentity)
      : { generationId: null, statuses: [] };
  } catch {
    const result = unrecoverable(source, 'diagnostics_binding_invalid', {
      artifactVerification,
      sourceVerification,
    });
    await writeJson(resolve(output, 'recovery-result.json'), result);
    return result;
  }
  if (diagnostics.unsafe) {
    const result = unrecoverable(source, diagnostics.reason, {
      artifactVerification,
      sourceVerification,
    });
    await writeJson(resolve(output, 'recovery-result.json'), result);
    return result;
  }
  const plannedGenerationId = scenario.generationId ?? null;
  if (!UUID_RE.test(plannedGenerationId || '')) {
    const result = unrecoverable(source, 'immutable_plan_generation_id_invalid', {
      artifactVerification,
      sourceVerification,
    });
    await writeJson(resolve(output, 'recovery-result.json'), result);
    return result;
  }
  if (diagnostics.generationId && plannedGenerationId !== diagnostics.generationId) {
    const result = unrecoverable(source, 'generation_binding_conflict', {
      artifactVerification,
      sourceVerification,
    });
    await writeJson(resolve(output, 'recovery-result.json'), result);
    return result;
  }
  const generationId = plannedGenerationId;

  const recoveryBinding = {
    sourceRunId: source.runId,
    sourceRunAttempt: source.runAttempt,
    sourceCommitSha: source.commitSha,
    scenarioId: scenario.id,
    scenarioVersion: scenario.version,
    generationId,
    generationSource: 'immutable-plan',
    planArtifactId: artifactVerification.planArtifact.id,
    diagnosticsArtifactId: artifactVerification.diagnosticsArtifact?.id ?? null,
    planSha256: sha256(canonicalJson(plan)),
    executionPlanDigest: plan.digest,
    cliIdentitySha256: sha256(canonicalJson(cliIdentity)),
    diagnosticsBindingSha256: artifactVerification.diagnosticsArtifact
      ? sha256(canonicalJson(diagnostics))
      : null,
    cliVersion: cliIdentity.version,
    cliAssetName: cliIdentity.assetName,
    cliSha256: cliIdentity.sha256,
    runner: plan.executionBinding.models.runner,
    judge: plan.executionBinding.models.judge,
    workflowSourceSha256: sourceVerification.workflowSourceSha256,
  };
  const diagnosticSha256 = sha256(canonicalJson(recoveryBinding));
  const context = {
    generationId,
    scenarioId: scenario.id,
    runId: String(source.runId),
    runAttempt: source.runAttempt,
    commitSha: source.commitSha,
    cliVersion: cliIdentity.version,
    cliSha256: cliIdentity.sha256,
    model: plan.executionBinding.models.runner.identity,
    modelRevision: plan.executionBinding.models.runner.revision,
    modelPinType: plan.executionBinding.models.runner.pinType,
    judgeModel: plan.executionBinding.models.judge.identity,
    judgeModelRevision: plan.executionBinding.models.judge.revision,
    judgeModelPinType: plan.executionBinding.models.judge.pinType,
    executionPlanDigest: plan.digest,
  };
  const evaluation = buildInfrastructureApiEvaluation({
    scenario,
    context,
    failure: {
      schemaVersion: INFRASTRUCTURE_SCHEMA,
      stage: 'evaluation',
      reason: 'terminal_report_missing',
      diagnosticSha256,
    },
    startedAt: source.startedAt,
    completedAt: source.completedAt,
    sourceEvidenceSha256: diagnosticSha256,
  });
  const safeEvidence = evaluation.evidence?.cliReport;
  if (
    evaluation.schemaVersion !== API_SCHEMA
    || evaluation.outcome !== 'infrastructure_failed'
    || evaluation.candidate !== null
    || evaluation.generationId !== generationId
    || safeEvidence?.schemaVersion !== CLI_EVIDENCE_SCHEMA
    || safeEvidence?.generationId !== generationId
    || safeEvidence?.scenarioId !== scenario.id
    || safeEvidence?.outcome !== 'infrastructure_failed'
    || safeEvidence?.outcomeCategory !== 'infrastructure'
    || safeEvidence?.source !== 'cancelled-run-recovery'
    || safeEvidence?.sourceEvidenceSha256 !== diagnosticSha256
    || Object.hasOwn(safeEvidence, 'rawReportSha256')
    || safeEvidence?.infrastructureFailure?.reason !== 'terminal_report_missing'
    || safeEvidence?.infrastructureFailure?.errorCategory !== null
    || safeEvidence?.infrastructureFailure?.diagnosticSha256 !== diagnosticSha256
  ) fail('Trusted recovery did not produce the exact sanitized candidate-null contract');
  const evaluationFile = resolve(output, 'candidate-null.evaluation.json');
  await writeJson(evaluationFile, evaluation);
  const evaluationSha256 = sha256(await readFile(evaluationFile));
  const result = {
    schemaVersion: RECOVERY_SCHEMA,
    outcome: 'candidate_null_prepared',
    reason: 'cancelled_run_missing_terminal_evaluator_report',
    source,
    generationId,
    evaluationSha256,
    persisted: false,
    evidence: {
      recoveryBinding,
      diagnosticSha256,
      artifactVerification,
      diagnosticsStatuses: diagnostics.statuses,
    },
  };
  await writeJson(resolve(output, 'recovery-result.json'), result);
  return result;
}

function validatePreparedRecovery(recovery, evaluation, evaluationBytes) {
  const safeEvidence = evaluation.evidence?.cliReport;
  if (
    recovery.schemaVersion !== RECOVERY_SCHEMA
    || recovery.outcome !== 'candidate_null_prepared'
    || recovery.persisted !== false
    || !UUID_RE.test(recovery.generationId || '')
    || recovery.evaluationSha256 !== sha256(evaluationBytes)
  ) fail('Prepared cancellation recovery closure is invalid');
  if (
    evaluation.schemaVersion !== API_SCHEMA
    || evaluation.generationId !== recovery.generationId
    || evaluation.outcome !== 'infrastructure_failed'
    || evaluation.candidate !== null
    || evaluation.workflow?.repository !== EXPECTED_REPOSITORY
    || String(evaluation.workflow?.runId) !== String(recovery.source?.runId)
    || evaluation.workflow?.runAttempt !== recovery.source?.runAttempt
    || evaluation.workflow?.commitSha !== recovery.source?.commitSha
    || safeEvidence?.schemaVersion !== CLI_EVIDENCE_SCHEMA
    || safeEvidence?.generationId !== recovery.generationId
    || safeEvidence?.scenarioId !== evaluation.scenario?.id
    || safeEvidence?.outcome !== 'infrastructure_failed'
    || safeEvidence?.outcomeCategory !== 'infrastructure'
    || safeEvidence?.source !== 'cancelled-run-recovery'
    || safeEvidence?.sourceEvidenceSha256 !== recovery.evidence?.diagnosticSha256
    || Object.hasOwn(safeEvidence, 'rawReportSha256')
    || safeEvidence?.infrastructureFailure?.reason !== 'terminal_report_missing'
    || safeEvidence?.infrastructureFailure?.errorCategory !== null
    || safeEvidence?.infrastructureFailure?.diagnosticSha256 !== recovery.evidence?.diagnosticSha256
  ) fail('Prepared candidate-null evaluation differs from its cancelled source binding');
  const { evidenceDigest, ...unsigned } = evaluation;
  if (!SHA256_RE.test(evidenceDigest || '') || evidenceDigest !== sha256(canonicalJson(unsigned))) {
    fail('Prepared candidate-null evidence digest is invalid');
  }
}

async function boundedResponse(response, maximumBytes = 1024 * 1024) {
  const reader = response.body?.getReader();
  if (!reader) return Buffer.alloc(0);
  const chunks = [];
  let bytes = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      bytes += value.byteLength;
      if (bytes > maximumBytes) {
        await reader.cancel('recovery response bound reached');
        fail('Pack production recovery response exceeded 1 MiB');
      }
      chunks.push(Buffer.from(value));
    }
  } finally {
    reader.releaseLock();
  }
  return Buffer.concat(chunks);
}

export async function persistCancellationRecovery({
  resultFile,
  evaluationFile,
  apiUrl,
  token,
  outputFile,
  fetchImpl = fetch,
}) {
  if (!apiUrl || !token) fail('Recovery API URL and narrow automation token are required');
  const base = new URL(apiUrl);
  if (base.protocol !== 'https:' && base.hostname !== '127.0.0.1') fail('Recovery API URL must use HTTPS');
  const result = await readJson(resultFile, MAX_JSON_BYTES, 'prepared recovery result');
  const evaluationBytes = await readBoundedFile(evaluationFile, MAX_JSON_BYTES, 'candidate-null evaluation');
  let evaluation;
  try {
    evaluation = JSON.parse(evaluationBytes.toString('utf8'));
  } catch {
    fail('Candidate-null evaluation is not valid JSON');
  }
  validatePreparedRecovery(result, evaluation, evaluationBytes);
  const endpoint = new URL('/api/automation/packs/production', `${base.toString().replace(/\/$/, '')}/`);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30_000);
  let response;
  try {
    response = await fetchImpl(endpoint, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: evaluationBytes,
      redirect: 'error',
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }
  const responseBytes = await boundedResponse(response);
  let body;
  try {
    body = responseBytes.length ? JSON.parse(responseBytes.toString('utf8')) : null;
  } catch {
    fail(`Recovery API returned invalid JSON with HTTP ${response.status}`);
  }
  if (!response.ok) fail(`Recovery API rejected candidate-null evidence with HTTP ${response.status}`);
  const data = body?.data;
  if (
    data?.generationId !== evaluation.generationId
    || data?.evaluationOutcome !== 'infrastructure_failed'
    || data?.outcome !== 'infrastructure_failed'
    || data?.pack !== null
    || data?.comparisonOf !== null
    || data?.autoPublishEligible !== false
    || data?.enrichment?.content !== 'not_applicable'
    || data?.enrichment?.translation !== 'not_applicable'
    || data?.enrichment?.contentDispatchNonce !== null
  ) fail('Recovery API response did not prove an exact no-Pack, no-enrichment candidate-null write');
  const persisted = {
    schemaVersion: RECOVERY_SCHEMA,
    outcome: 'candidate_null_persisted',
    reason: result.reason,
    source: result.source,
    generationId: evaluation.generationId,
    evaluationSha256: result.evaluationSha256,
    persisted: true,
    replayed: data.replayed === true,
    response: {
      generationId: data.generationId,
      evaluationOutcome: data.evaluationOutcome,
      outcome: data.outcome,
      pack: null,
      comparisonOf: null,
      autoPublishEligible: false,
      enrichment: {
        content: data.enrichment.content,
        translation: data.enrichment.translation,
        contentDispatchNonce: null,
      },
    },
  };
  await writeJson(outputFile, persisted);
  return persisted;
}

async function inspectCommand(args) {
  const event = await readJson(required(args, 'event'), MAX_JSON_BYTES, 'workflow_run event');
  const source = inspectWorkflowRunEvent(event);
  await writeJson(required(args, 'output'), source);
  process.stdout.write(`${JSON.stringify({ runId: source.runId, runAttempt: source.runAttempt })}\n`);
}

async function prepareCommand(args) {
  const source = await readJson(required(args, 'source-run'));
  const workflowSource = (await readBoundedFile(
    required(args, 'source-workflow'),
    MAX_JSON_BYTES,
    'source workflow',
  )).toString('utf8');
  const result = await prepareCancellationRecovery({
    source,
    attempt: await readJson(required(args, 'source-attempt')),
    workflow: await readJson(required(args, 'expected-workflow')),
    comparison: await readJson(required(args, 'comparison')),
    workflowSource,
    artifactIndex: await readJson(required(args, 'artifact-index')),
    planDir: required(args, 'plan-dir'),
    diagnosticsDir: required(args, 'diagnostics-dir'),
    outputDir: required(args, 'output-dir'),
  });
  process.stdout.write(`${JSON.stringify({ outcome: result.outcome, reason: result.reason })}\n`);
}

async function persistCommand(args) {
  const result = await persistCancellationRecovery({
    resultFile: required(args, 'result'),
    evaluationFile: required(args, 'evaluation'),
    apiUrl: required(args, 'api-url'),
    token: required(args, 'token'),
    outputFile: required(args, 'output'),
  });
  process.stdout.write(`${JSON.stringify({ outcome: result.outcome, replayed: result.replayed })}\n`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.command === 'inspect') return inspectCommand(args);
  if (args.command === 'prepare') return prepareCommand(args);
  if (args.command === 'persist') return persistCommand(args);
  fail('Usage: pack-production-cancellation-recovery.mjs <inspect|prepare|persist> [options]');
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    process.stderr.write(`${error instanceof Error ? error.message : 'Pack production cancellation recovery failed'}\n`);
    process.exitCode = 1;
  });
}
